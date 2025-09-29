from sentence_transformers import SentenceTransformer

def get_embedding_model(model_name="all-mpnet-base-v2"):
    return SentenceTransformer(f"sentence-transformers/{model_name}")
