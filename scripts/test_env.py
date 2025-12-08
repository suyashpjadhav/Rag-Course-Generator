import os
from dotenv import load_dotenv

load_dotenv()
print("HF TOKEN:", os.getenv("HUGGINGFACEHUB_API_TOKEN"))
print("Vector dimension:", os.getenv("VECTOR_DIM"))