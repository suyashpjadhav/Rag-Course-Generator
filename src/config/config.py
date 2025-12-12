# src/config/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API KEYS
    OPENAI_API_KEY: str | None = None
    HUGGINGFACEHUB_API_TOKEN: str | None = None
    ELEVENLABS_API_KEY: str | None = None

    # PINECONE (global vector DB)
    PINECONE_API_KEY: str | None = None
    PINECONE_ENVIRONMENT: str | None = None
    PINECONE_INDEX_NAME: str = "rag-course-index"

    # EMBEDDINGS
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DIM: int = 384

    # RETRIEVER 
    TOP_K: int = 12
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # LLM SETTINGS
    LLM_PROVIDER: str = "huggingface"
    LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    TEMPERATURE: float = 0.3
    MAX_NEW_TOKENS: int = 512

    class Config:
        env_file = ".env"

settings = Settings()
