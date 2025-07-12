from src.embedding import get_embedding_model
from vector_store.chroma_client import get_chroma_client

def search_similar_chunks(query: str, top_k=3):
    try:
        model = get_embedding_model()
        embedding = model.encode([query])[0]
        client = get_chroma_client()

        # Check if the collection exists
        if "pdf_chunks" not in [col.name for col in client.list_collections()]:
            return {"error": "No indexed documents found."}

        collection = client.get_collection(name="pdf_chunks")

        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Format response
        formatted = []
        for doc, meta, id_ in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            formatted.append({
                "id": id_,
                "text": doc,
                "source": meta.get("source"),
                "chunk_index": meta.get("chunk_index")
            })

        return {"results": formatted}

    except Exception as e:
        return {"error": str(e)}
