import os
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

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
        raise ValueError("Invalid LLM_PROVIDER in .env")


def create_retriever(vectorstore):
    return vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})


def create_qa_chain(retriever):
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template="""
You are an expert course-creation AI.

Your goal is to convert the retrieved context into clean, structured, 
module-wise educational content.

STRICT RULES:
- Use ONLY the given context.
- No external knowledge.
- Convert fragmented text into clear explanations.
- Organize content as modules.

OUTPUT FORMAT (always follow):
### Module Title
Short overview

#### Detailed Explanation
(3 to 5 short paragraphs)

#### Key Points
- bullet 1
- bullet 2

#### Examples
(include only if present in context)

#### Mini Summary
(short, crisp)

-------------------------------------
CONTEXT:
{context}

USER REQUEST:
{input}
-------------------------------------

Generate the final structured course content below:
"""
    )

    # Combine retrieved documents into a single formatted string
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    # LCEL RAG pipeline
    rag_chain = (
        {
            "context": retriever | format_docs,
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    return rag_chain


def build_rag_pipeline():
    vectorstore = load_vectorstore()
    retriever = create_retriever(vectorstore)
    return create_qa_chain(retriever)
