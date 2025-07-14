from sentence_transformers import SentenceTransformer

def get_embedding_model(model_name="all-MiniLM-L6-v2"):
    return SentenceTransformer(f"sentence-transformers/{model_name}")
