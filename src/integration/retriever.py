from typing import List
from langchain_core.documents import Document
from vector_store.query_documents import search_similar_chunks

def retrieve_chunks(
    query: str,
    top_k: int
) -> List[Document]:
    """
    Adapter that converts client Chroma results into LangChain Documents.
    """
    response = search_similar_chunks(query, top_k=top_k)

    if "error" in response:
        return []

    docs = []
    for item in response["results"]:
        docs.append(
            Document(
                page_content=item["text"],
                metadata={
                    "source": item.get("source"),
                    "chunk_index": item.get("chunk_index")
                }
            )
        )

    return docs
