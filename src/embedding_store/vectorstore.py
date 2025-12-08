import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config.config import settings   # Use centralized config


def get_embeddings_model():
    """Initialize and return an embedding model."""
    model_name = settings.EMBEDDING_MODEL   # pulled from config

    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print(f"Embedding model '{model_name}' loaded successfully.")
    return embeddings


def create_vectorstore(documents: list[Document]):
    """Create a FAISS vector store from a list of LangChain Documents."""
    if not documents:
        print("No documents provided for vectorstore creation.")
        return None

    embeddings = get_embeddings_model()
    vectorstore = FAISS.from_documents(documents, embeddings)
    print(f"Vectorstore created with {len(documents)} documents.")
    return vectorstore


def save_vectorstore(vectorstore, path: str = None):
    """Save the FAISS vector store to disk."""
    path = path or settings.FAISS_DIR   # fallback to config value

    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(path)
    print(f"Vectorstore saved at: {path}")


def load_vectorstore(path: str = None):
    """Load a FAISS vector store from disk."""
    path = path or settings.FAISS_DIR   # fallback to config value

    embeddings = get_embeddings_model()
    vectorstore = FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print(f"Vectorstore loaded from: {path}")
    return vectorstore
