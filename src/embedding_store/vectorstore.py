import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


def get_embeddings_model():
    """Initialize and return an embedding model."""
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
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


# In order to not to rebuild embedding every time
def save_vectorstore(vectorstore, path="faiss_index"):
    """Save the FAISS vector store to disk."""
    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(path)
    print(f"Vectorstore saved at: {path}")

def load_vectorstore(path="faiss_index"):
    """Load a FAISS vector store from disk."""
    embeddings = get_embeddings_model()
    vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    print(f"Vectorstore loaded from: {path}")
    return vectorstore
