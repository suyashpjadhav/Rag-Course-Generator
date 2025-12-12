import os
import math
from typing import Iterable, List, Dict, Any
import pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config.config import settings

UPSERT_BATCH_SIZE = 128

def get_embeddings_model():
    """
    Initialize and return HuggingFaceEmbeddings (langchain_huggingface).
    """
    model_name = settings.EMBEDDING_MODEL
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print(f"[vectorstore] Embedding model '{model_name}' loaded successfully.")
    return embeddings

def init_pinecone():
    """
    Initialize pinecone client.
    """
    api_key = settings.PINECONE_API_KEY
    env = settings.PINECONE_ENVIRONMENT
    if not api_key or not env:
        raise ValueError("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set in env.")
    pinecone.init(api_key=api_key, environment=env)
    return pinecone

def create_index_if_not_exists(index_name: str, dimension: int):
    init_pinecone()
    if index_name in pinecone.list_indexes():
        print(f"[vectorstore] Pinecone index '{index_name}' already exists.")
        return
    pinecone.create_index(index_name, dimension=dimension, metric="cosine")
    print(f"[vectorstore] Pinecone index '{index_name}' created (dim={dimension}).")

def upsert_documents_to_pinecone(documents: List[Document], index_name: str = None):
    """
    Upsert documents (as chunks) into Pinecone. Documents are LangChain Document objects.
    Each vector's metadata will include document metadata and optionally snippet text.
    """
    if not documents:
        print("[vectorstore] No documents to upsert.")
        return

    index_name = index_name or settings.PINECONE_INDEX_NAME
    embeddings = get_embeddings_model()
    init_pinecone()
    index = pinecone.Index(index_name)

    # Prepare texts for embedding
    texts = [doc.page_content for doc in documents]
    # Embed in batches
    all_vectors = []
    for i in range(0, len(texts), UPSERT_BATCH_SIZE):
        batch_texts = texts[i:i+UPSERT_BATCH_SIZE]
        batch_embeddings = embeddings.embed_documents(batch_texts)
        for j, emb in enumerate(batch_embeddings):
            idx = str(i + j)
            metadata = documents[i + j].metadata or {}
            # include a short preview for safer downstream usage
            metadata["_text_preview"] = documents[i + j].page_content[:400]
            all_vectors.append((idx, emb, metadata))

    # Upsert in batches
    for i in range(0, len(all_vectors), UPSERT_BATCH_SIZE):
        batch = all_vectors[i:i+UPSERT_BATCH_SIZE]
        index.upsert(vectors=batch)
        print(f"[vectorstore] Upserted batch {i // UPSERT_BATCH_SIZE + 1}")

    print(f"[vectorstore] Total upserted vectors: {len(all_vectors)}")

def load_vectorstore(index_name: str = None):
    """
    Return a lightweight wrapper object with as_retriever(search_kwargs) using Pinecone.
    This wrapper behaves similarly to a LangChain vectorstore for your pipeline.
    """
    index_name = index_name or settings.PINECONE_INDEX_NAME
    init_pinecone()
    index = pinecone.Index(index_name)
    embeddings = get_embeddings_model()

    # We'll create a simple retriever wrapper using the pinecone index and embeddings
    class PineconeRetriever:
        def __init__(self, index, embedder):
            self.index = index
            self.embedder = embedder

        def as_retriever(self, search_kwargs: Dict[str, Any] = None):
            search_kwargs = search_kwargs or {}
            top_k = search_kwargs.get("k", settings.TOP_K)

            class RetrieverInner:
                def __init__(self, index, embedder, top_k):
                    self.index = index
                    self.embedder = embedder
                    self.top_k = top_k

                def get_relevant_documents(self, query: str):
                    # embed the query
                    q_emb = self.embedder.embed_query(query)
                    # query pinecone
                    res = self.index.query(q_emb, top_k=self.top_k, include_metadata=True)
                    docs = []
                    for match in res.get("matches", []):
                        md = match.get("metadata", {})
                        content = md.get("_text_preview", "")
                        docs.append(Document(page_content=content, metadata=md))
                    return docs

            return RetrieverInner(self.index, self.embedder, top_k)

    return PineconeRetriever(index, embeddings)
