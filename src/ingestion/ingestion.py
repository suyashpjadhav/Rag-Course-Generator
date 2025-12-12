import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config.config import settings
from src.ingestion.loaders import load_pdf, load_pptx, load_manual_transcript
from src.embedding_store.vectorstore import create_index_if_not_exists, upsert_documents_to_pinecone

CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP

def split_documents(documents: List[Document], chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    out = []
    for doc in documents:
        text_chunks = splitter.split_text(doc.page_content)
        for chunk in text_chunks:
            out.append(Document(page_content=chunk, metadata=doc.metadata))
    print(f"[ingestion] split into {len(out)} chunks")
    return out

def ingest_files(file_paths: List[str], manual_texts: List[str] | None = None, index_name: str | None = None):
    index_name = index_name or settings.PINECONE_INDEX_NAME
    # Ensure index exists
    create_index_if_not_exists(index_name, dimension=settings.VECTOR_DIM)

    # Load files
    docs = []
    for f in file_paths:
        f = f.strip()
        if not os.path.exists(f):
            print(f"[ingestion] file not found: {f}")
            continue
        if f.lower().endswith(".pdf"):
            docs.extend(load_pdf(f))
        elif f.lower().endswith((".ppt", ".pptx")):
            docs.extend(load_pptx(f))
        else:
            print(f"[ingestion] unsupported file type, skipping: {f}")

    # Manual texts
    if manual_texts:
        for t in manual_texts:
            d = load_manual_transcript(t)
            if d:
                docs.append(d)

    if not docs:
        print("[ingestion] no documents loaded; aborting ingestion.")
        return

    # Chunk
    chunks = split_documents(docs)

    # Upsert to Pinecone
    upsert_documents_to_pinecone(chunks, index_name=index_name)
    print("[ingestion] Done.")
