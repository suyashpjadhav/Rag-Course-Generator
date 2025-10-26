from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_TOKEN: str | None = None
    ELEVENLABS_API_KEY: str | None = None

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 12
    EMBEDDER_MODEL: str = "all-MiniLM-L6-v2"  # local sentence-transformers
    VECTOR_DIM: int = 384

    class Config:
        env_file = ".env"

settings = Settings()
