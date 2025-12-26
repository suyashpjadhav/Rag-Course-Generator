import os
import hashlib
import sqlite3
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pinecone import Pinecone
from src.config.config import settings
from src.ingestion.loaders import load_pdf, load_pptx, load_manual_transcript
from src.embedding_store.vectorstore import get_embeddings_model

# Manifest DB path
MANIFEST_DB = os.path.join("data", "manifest.db")
os.makedirs("data", exist_ok=True)

# Pinecone client
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# helpers for manifest DB
def init_manifest_db():
    conn = sqlite3.connect(MANIFEST_DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        doc_id TEXT,
        filename TEXT,
        version INTEGER,
        created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY,
        doc_manifest_id TEXT,
        user_id TEXT,
        doc_id TEXT,
        version INTEGER,
        page_num INTEGER,
        chunk_idx INTEGER,
        chunk_text_preview TEXT,
        chunk_hash TEXT
    )""")
    conn.commit()
    conn.close()

init_manifest_db()

# ID generator
def make_chunk_id(user_id: str, doc_id: str, version: int, page: int, chunk_idx: int, text: str, hash_len: int = 6):
    s = hashlib.sha256(text.encode("utf-8")).hexdigest()[:hash_len]
    return f"user_{user_id}::doc_{doc_id}::v{version}::page_{page:04}::chunk_{chunk_idx:04}::h_{s}"

# Ensure index exists
def create_index_if_not_exists(index_name: str, dimension: int):
    existing = pc.list_indexes().names()
    if index_name in existing:
        print(f"[ingest] Pinecone index '{index_name}' already exists.")
        return
    try:
        pc.create_index(name=index_name, dimension=dimension, metric="cosine")
        print(f"[ingest] Created Pinecone index '{index_name}' (dim={dimension}).")
    except Exception as e:
        print("[ingest] Error creating index:", e)
        raise

# Split documents to chunks
def split_documents(documents: List[Document], chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    out = []
    for doc in documents:
        if not doc.page_content:
            continue
        pieces = splitter.split_text(doc.page_content)
        # use page metadata if present, else 0
        page_num = doc.metadata.get("page") if doc.metadata else 0
        for i, p in enumerate(pieces):
            d = Document(page_content=p, metadata=doc.metadata or {})
            d.metadata.setdefault("page", page_num or 0)
            out.append(d)
    print(f"[ingest] split into {len(out)} chunks")
    return out

# Upsert to Pinecone with manifest logging
def upsert_chunks(chunks: List[Document], user_id: str, doc_id: str, version: int, index_name: str = None, batch_size: int = 64):
    if not chunks:
        print("[ingest] no chunks to upsert")
        return
    index_name = index_name or settings.PINECONE_INDEX_NAME
    embeddings = get_embeddings_model()
    index = pc.Index(index_name)

    conn = sqlite3.connect(MANIFEST_DB)
    cur = conn.cursor()

    vectors = []
    chunk_records = []
    for i, chunk in enumerate(chunks):
        page = int(chunk.metadata.get("page") or 0)
        cid = make_chunk_id(user_id, doc_id, version, page, i+1, chunk.page_content)
        # small preview for metadata
        preview = chunk.page_content[:400]
        chash = hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()[:8]
        # embed (do in batch below)
        vectors.append((cid, chunk.page_content, {"user_id": user_id, "doc_id": doc_id, "version": version, "page": page, "_text_preview": preview, "chunk_hash": chash}))
        chunk_records.append((cid, f"user_{user_id}::doc_{doc_id}::v{version}", user_id, doc_id, version, page, i+1, preview, chash))
    # create embeddings in batches
    ids = [t[0] for t in vectors]
    texts = [t[1] for t in vectors]
    metas = [t[2] for t in vectors]

    # batch embed
    emb_batch_size = batch_size
    emb_vectors = []
    for i in range(0, len(texts), emb_batch_size):
        batch_texts = texts[i:i+emb_batch_size]
        batch_embs = embeddings.embed_documents(batch_texts)
        emb_vectors.extend(batch_embs)

    # prepare tuples for pinecone: (id, vector, metadata)
    pinecone_vectors = []
    for idx, vec in enumerate(emb_vectors):
        pinecone_vectors.append((ids[idx], vec, metas[idx]))

    # upsert in batches
    for i in range(0, len(pinecone_vectors), batch_size):
        batch = pinecone_vectors[i:i+batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"[ingest] Upserted batch {i//batch_size + 1} ({len(batch)} vectors).")
        except Exception as e:
            print("[ingest] upsert error:", e)
            raise

    # write manifest records
    try:
        cur.executemany("""
            INSERT OR REPLACE INTO chunks (id, doc_manifest_id, user_id, doc_id, version, page_num, chunk_idx, chunk_text_preview, chunk_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, chunk_records)
        conn.commit()
    except Exception as e:
        print("[ingest] manifest write error:", e)
    finally:
        conn.close()

    print(f"[ingest] Upsert complete: {len(pinecone_vectors)} vectors to '{index_name}'")

# Main ingestion function
def ingest_files(file_paths: List[str], user_id: str, doc_id: str | None = None, version: int | None = None, manual_texts: List[str] | None = None):
    """
    file_paths: list of local file paths (pdf, pptx)
    user_id: unique uploader id (string)
    doc_id: optional doc identifier (if None, we compute from filename + timestamp)
    version: if None -> auto-increment previous or start at 1
    """
    # ensure index
    create_index_if_not_exists(settings.PINECONE_INDEX_NAME, settings.VECTOR_DIM)

    # doc id and version handling
    if not doc_id:
        doc_id = f"{os.path.basename(file_paths[0])}".replace(" ", "_")
    if version is None:
        # naive version: count existing versions in manifest
        conn = sqlite3.connect(MANIFEST_DB)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents WHERE user_id=? AND doc_id=?", (user_id, doc_id))
        prev = cur.fetchone()[0]
        version = prev + 1
        # insert document manifest entry
        cur.execute("INSERT OR REPLACE INTO documents (id, user_id, doc_id, filename, version, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                    (f"user_{user_id}::doc_{doc_id}::v{version}", user_id, doc_id, ",".join(file_paths), version))
        conn.commit()
        conn.close()

    # load docs
    docs = []
    for f in (file_paths or []):
        if not os.path.exists(f):
            print(f"[ingest] file not found: {f}")
            continue
        if f.lower().endswith(".pdf"):
            docs.extend(load_pdf(f))
        elif f.lower().endswith((".ppt", ".pptx")):
            docs.extend(load_pptx(f))
        else:
            print(f"[ingest] unsupported file type, skipping: {f}")

    if manual_texts:
        for t in manual_texts:
            d = load_manual_transcript(t, source=f"user_{user_id}_manual")
            if d:
                docs.append(d)

    if not docs:
        print("[ingest] No documents loaded; aborting.")
        return

    # chunk
    chunks = split_documents(docs)
    # upsert
    upsert_chunks(chunks, user_id=user_id, doc_id=doc_id, version=version, index_name=settings.PINECONE_INDEX_NAME)
    print("[ingest] Ingestion finished.")
