import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.embedding_store.vectorstore import load_vectorstore

vs = load_vectorstore()
print("Vectors:", vs.index.ntotal)
