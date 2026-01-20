import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.text_processor import extract_text_from_pdf, clean_text
from src.chunker import chunk_structured_document
from vector_store.chroma_client import get_chroma_client
from src.embedding import get_embedding_model
import os

PDF_PATH = "data/DBMS_Full_Notes.pdf"
OUTPUT_DIR = "output"
DOC_ID = "DBMS_Full_Notes"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Extract text
raw_text = extract_text_from_pdf(PDF_PATH)
cleaned_text = clean_text(raw_text)

# 2. Chunk semantically
chunks = chunk_structured_document(cleaned_text)

# 3. Save chunked text (for traceability)
chunked_file = os.path.join(OUTPUT_DIR, f"{DOC_ID}_chunked.txt")
with open(chunked_file, "w", encoding="utf-8") as f:
    f.write("\n\n".join(chunks))

print(f"Chunked file saved: {chunked_file}")

# 4. Index into Chroma
model = get_embedding_model()
client = get_chroma_client()
collection = client.get_or_create_collection(name="pdf_chunks")

embeddings = model.encode(chunks).tolist()

for i, chunk in enumerate(chunks):
    collection.add(
        ids=[f"{DOC_ID}-{i}"],
        documents=[chunk],
        embeddings=[embeddings[i]],
        metadatas=[{"source": PDF_PATH, "chunk_index": i}]
    )

print(f"Indexed {len(chunks)} chunks into ChromaDB")
