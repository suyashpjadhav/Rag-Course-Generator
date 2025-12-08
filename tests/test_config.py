from src.config.config import settings

print("OpenAI Key:", settings.OPENAI_API_KEY)
print("HuggingFace Key:", settings.HUGGINGFACEHUB_API_TOKEN)
print("ElevenLabs Key:", settings.ELEVENLABS_API_KEY)
print("Embedder model:", settings.EMBEDDING_MODEL)
print("Vector dimension:", settings.VECTOR_DIM)