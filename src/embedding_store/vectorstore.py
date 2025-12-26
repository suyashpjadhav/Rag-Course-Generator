from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

def get_embeddings_model():
    model_name = settings.EMBEDDING_MODEL
    return HuggingFaceEmbeddings(model_name=model_name)

class PineconeRetrieverWrapper:
    def __init__(self, index_name: str = None):
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        self.index = pc.Index(self.index_name)
        self.embedder = get_embeddings_model()

    def as_retriever(self, search_kwargs: dict = None):
        search_kwargs = search_kwargs or {}
        top_k = search_kwargs.get("k", settings.TOP_K)

        class Retriever:
            def __init__(self, index, embedder, top_k):
                self.index = index
                self.embedder = embedder
                self.top_k = top_k

            def get_relevant_documents(self, query: str):
                q_emb = self.embedder.embed_query(query)
                # using pinecone v4 Index.query
                res = self.index.query(vector=q_emb, top_k=self.top_k, include_metadata=True)
                docs = []
                matches = res.get("matches", []) or res.get("results", [])
                # support both return shapes
                if isinstance(matches, list):
                    iterable = matches
                else:
                    # results shape may be {'results': [{'matches':[...]}]}
                    iterable = []
                    for r in matches:
                        iterable.extend(r.get("matches", []))
                for m in iterable:
                    md = m.get("metadata", {}) or {}
                    # prefer stored preview; if not, leave blank
                    text = md.get("_text_preview", "")
                    docs.append(Document(page_content=text, metadata=md))
                return docs

        return Retriever(self.index, self.embedder, top_k)

def load_vectorstore(index_name: str = None):
    return PineconeRetrieverWrapper(index_name=index_name)
