import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
from src.embedding_store.vectorstore import load_vectorstore
from src.config.config import settings

load_dotenv()

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

    else:
        raise ValueError("Invalid LLM_PROVIDER")


def create_retriever(coverage_level: str = "focused"):
    vecstore = load_vectorstore()

    if coverage_level == "broad":
        k = settings.TOP_K * 3 
    else:
        k = settings.TOP_K

    return vecstore.as_retriever(search_kwargs={"k": k})


def create_qa_chain(retriever):
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template="""You are an expert instructional designer and subject-matter explainer.

Your job is to analyze the PROVIDED CONTEXT and transform it into
high-quality educational modules written in a STYLE, DEPTH,
and CLARITY that are CONSISTENT with the way the CONTEXT itself is written.

You must follow these rules strictly:

CONTENT RULES
- Use ONLY the provided CONTEXT.
- Do NOT add external facts, examples, or assumptions.
- Do NOT rely on any unseen or external reference material.
- If the context is insufficient to explain a concept clearly, say:
  "Insufficient context."

STRUCTURE & STYLE RULES
- First, infer the DOMAIN from the context (e.g., manufacturing, finance,
  biology, computer science, operations, etc.).
- Do NOT mention the domain explicitly unless the context itself does.
- Organize content into clear MODULES and SUB-MODULES.
- Each sub-module must explain ONE core idea only.

NAMING RULES (VERY IMPORTANT)
- Module titles should express the BIG IDEA or PURPOSE.
- Sub-module titles must be:
  - Human-readable
  - Conceptual, not academic
  - Derived directly from the language and intent of the context
  - Similar in tone to:
    "Process, parameter, and variation - in plain language"
    "From risk to SOPs at the machine"
    "Checking correctly: good measurement habits"
- Do NOT use textbook-style headings.

EXPLANATION STYLE
For each sub-module:
1. Start with a real-world situation or problem implied by the context.
2. Explain the concept in simple, everyday language.
3. Use analogies ONLY if they already exist in the context.
4. Connect the idea back to the system, process, or workflow described.
5. Clearly explain why this matters in practice.
6. End with a short transfer section that helps the learner apply the idea.

OUTPUT FORMAT (MANDATORY)

### Module Title
Short overview explaining why this module exists.

#### Sub-module Title
(Explain one idea using the layered style described above)

#### Key Takeaways
- 3 to 5 concise, practical points

#### Mini Summary
- 2 to 3 lines reinforcing the main insight

--------------------
CONTEXT:
{context}
--------------------

USER QUERY:
{input}
--------------------

Generate structured educational content now.
"""
    )

    def retrieve_and_format(query):
        docs = retriever.get_relevant_documents(query)
        return "\n\n".join([d.page_content for d in docs])


    rag_chain = (
        {
            "context": RunnableLambda(retrieve_and_format),
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    return rag_chain


def build_rag_pipeline(coverage_level: str = "focused"):
    """
    Builds a full RAG pipeline:
    - Uses persisted vectorstore
    - Retrieves relevant chunks
    - Generates structured educational content

    This function does NOT handle ingestion.
    """
    retriever = create_retriever(coverage_level)
    return create_qa_chain(retriever)
