import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Load model once globally
MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def split_into_paragraphs(text: str):
    """
    Split raw text into paragraphs based on double line breaks.
    """
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]

def split_into_sentences(paragraph: str):
    """
    Split a paragraph into sentences.
    """
    return [s.strip() for s in sent_tokenize(paragraph) if s.strip()]

def is_similar(chunk_text, sentence, model, threshold=0.75):
    """
    Compare the semantic similarity between current chunk and next sentence.
    """
    embeddings = model.encode([chunk_text, sentence])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return score >= threshold

def group_sentences(sentences, model, similarity_threshold=0.75, min_chunk_size=2):
    """
    Group sentences into meaningful semantic chunks.
    """
    chunks = []
    current_chunk = []

    for sentence in sentences:
        if not current_chunk:
            current_chunk.append(sentence)
        else:
            chunk_text = " ".join(current_chunk)
            if is_similar(chunk_text, sentence, model, similarity_threshold):
                current_chunk.append(sentence)
            else:
                # If too small, force add next sentence for better context
                if len(current_chunk) < min_chunk_size:
                    current_chunk.append(sentence)
                else:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def chunk_structured_document(content: str, similarity_threshold=0.75):
    """
    Main function to convert full content into meaningful chunks.
    """
    try:
        paragraphs = split_into_paragraphs(content)
        all_chunks = []

        for para in paragraphs:
            sentences = split_into_sentences(para)
            if len(sentences) == 1:
                all_chunks.append(sentences[0])
            else:
                para_chunks = group_sentences(sentences, MODEL, similarity_threshold)
                all_chunks.extend(para_chunks)

        logging.info(f"Chunking complete: {len(all_chunks)} chunks.")
        return all_chunks

    except Exception as e:
        logging.error(f"Chunking error: {e}")
        return []
