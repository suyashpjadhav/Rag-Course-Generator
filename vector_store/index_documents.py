import os
from src.chunker import chunk_structured_document
from src.embedding import get_embedding_model
from vector_store.chroma_client import get_chroma_client

def index_pdf_chunks(file_path: str, doc_id: str):
    model = get_embedding_model()
    client = get_chroma_client()

    collection = client.get_or_create_collection(name="pdf_chunks")

    text = open(file_path, "r", encoding="utf-8").read()
    chunks = chunk_structured_document(text)
    embeddings = model.encode(chunks).tolist()

    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{doc_id}-{i}"],
            documents=[chunk],
            embeddings=[embeddings[i]],
            metadatas=[{"source": file_path, "chunk_index": i}]
        )

if __name__ == "__main__":
    output_dir = "output"
    files = [f for f in os.listdir(output_dir) if f.endswith("_chunked.txt")]
    print(f"🔢 Found {len(files)} _chunked.txt files to index")

    for filename in files:
        try:
            file_path = os.path.join(output_dir, filename)
            doc_id = os.path.splitext(filename)[0]
            print(f"📄 Indexing: {filename}")
            try:
                index_pdf_chunks(file_path, doc_id)
            except Exception as e:
                print(f"❌ Failed to index {filename}: {e}")
        except Exception as e:
            print(f"❌ Failed to index {filename}: {e}")


