import math
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_openai import ChatOpenAI

from src.embedding_store.vectorstore import get_embeddings_model
from src.config.config import settings

# VECTOR STORE
from vector_store.query_documents import search_similar_chunks

load_dotenv()

# LLM
def get_llm():
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_NEW_TOKENS
        )

    elif settings.LLM_PROVIDER == "huggingface":
        return ChatHuggingFace(
            llm=HuggingFaceEndpoint(
                repo_id=settings.LLM_MODEL,
                task="text-generation",
                temperature=settings.TEMPERATURE,
                max_new_tokens=settings.MAX_NEW_TOKENS
            )
        )

    raise ValueError("Invalid LLM_PROVIDER")

# Retrieval utilities
def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars)."""
    return math.ceil(len(text) / 4)


def dedupe_documents(
    docs: List[Document],
    embeddings,
    similarity_threshold: float = 0.85
) -> List[Document]:
    if not docs:
        return []

    texts = [d.page_content for d in docs]
    vectors = embeddings.embed_documents(texts)

    unique_docs = []
    unique_vectors = []

    for doc, vec in zip(docs, vectors):
        is_duplicate = False
        for uvec in unique_vectors:
            similarity = sum(a * b for a, b in zip(vec, uvec))
            if similarity >= similarity_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_docs.append(doc)
            unique_vectors.append(vec)

    return unique_docs


def token_budget_for_minutes(minutes: int) -> int:
    """
    Approximation:
    1 minute ≈ 700 context tokens
    """
    return minutes * 700


def select_documents_with_token_budget(
    docs: List[Document],
    max_tokens: int
) -> List[Document]:
    selected = []
    used_tokens = 0

    for doc in docs:
        tokens = estimate_tokens(doc.page_content)
        if used_tokens + tokens > max_tokens:
            break
        selected.append(doc)
        used_tokens += tokens

    return selected

# CLIENT RETRIEVAL 
def retrieve_from_client_vector_store(
    query: str,
    coverage_level: str
) -> List[Document]:
    base_k = settings.TOP_K
    k = base_k * 3 if coverage_level == "broad" else base_k

    response = search_similar_chunks(query, top_k=k)

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

# CONTEXT PREPARATION
def retrieve_and_prepare_context(
    query: str,
    coverage_level: str,
    submodule_minutes: int
) -> str:
    # Step 1: Retrieve from client Chroma DB
    docs = retrieve_from_client_vector_store(query, coverage_level)

    # Step 2: Deduplicate semantically
    embeddings = get_embeddings_model()
    docs = dedupe_documents(docs, embeddings)

    # Step 3: Apply time-based token budget
    max_tokens = token_budget_for_minutes(submodule_minutes)
    docs = select_documents_with_token_budget(docs, max_tokens)

    return "\n\n".join(d.page_content for d in docs)

# RAG CHAIN
def create_qa_chain(coverage_level: str):
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template="""
You are an expert instructional designer and subject-matter explainer.

Your job is to analyze the PROVIDED CONTEXT and transform it into
high-quality educational modules written in a STYLE, DEPTH,
and CLARITY that are CONSISTENT with the way the CONTEXT itself is written.

STOP GENERATION RULE:
- Generate at most ONE module at a time.
- Do NOT repeat any section headers.
- End output cleanly after the Mini Summary.

CONTENT RULES:
- Use ONLY the provided CONTEXT.
- Do NOT add external facts, examples, or assumptions.
- Do NOT rely on any unseen or external reference material.
- If the context is insufficient, say "Insufficient context."

OUTPUT FORMAT (MANDATORY):

### Module Title
Short overview explaining why this module exists.

#### Sub-module Title

#### Key Takeaways
- 3 to 5 concise points

#### Mini Summary
- 2 to 3 lines

--------------------
CONTEXT:
{context}
--------------------

USER QUERY:
{input}
--------------------
"""
    )

    rag_chain = (
        {
            "context": RunnableLambda(
                lambda q: retrieve_and_prepare_context(
                    query=q,
                    coverage_level=coverage_level,
                    submodule_minutes=3
                )
            ),
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    return rag_chain

# PIPELINE ENTRY POINT
def build_rag_pipeline(coverage_level: str = "focused"):
    """
    Builds the course-generation RAG pipeline.

    Uses:
    - Client semantic chunking
    - Client Chroma vector store
    - Internal dedup + token budgeting
    - Structured generation
    """
    return create_qa_chain(coverage_level)
