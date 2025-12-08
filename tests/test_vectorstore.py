import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.ingestion.ingestion import load_pdf
from src.embedding_store.vectorstore import create_vectorstore, save_vectorstore


docs = load_pdf("C:\\Users\\BIT\\Downloads\\SE\\software_Engg_Chapter_01.pdf")
vectorstore = create_vectorstore(docs)
save_vectorstore(vectorstore)
