import chromadb

def get_chroma_client():
    return chromadb.PersistentClient(path="vector_store/chroma_db")
