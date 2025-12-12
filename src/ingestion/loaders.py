# src/ingestion/loaders.py
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_core.documents import Document

def load_pdf(pdf_path: str) -> list[Document]:
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"[loaders] PDF loaded — {len(docs)} pages")
        return docs
    except Exception as e:
        print(f"[loaders] PDF load failed: {e}")
        return []

def load_pptx(ppt_path: str) -> list[Document]:
    try:
        loader = UnstructuredFileLoader(ppt_path)
        docs = loader.load()
        print(f"[loaders] PPTX loaded — {len(docs)} chunks")
        return docs
    except Exception as e:
        print(f"[loaders] PPTX load failed: {e}")
        return []

def load_manual_transcript(transcript_text: str, source: str = "manual_input"):
    if not transcript_text or not transcript_text.strip():
        print("[loaders] empty manual transcript")
        return None
    return Document(page_content=transcript_text.strip(), metadata={"source": source})
