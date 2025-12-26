from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_core.documents import Document

def load_pdf(pdf_path: str) -> list[Document]:
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"[loaders] PDF loaded — {len(docs)} pages from {pdf_path}")
        # ensure metadata includes source
        for i, d in enumerate(docs):
            d.metadata = d.metadata or {}
            d.metadata.setdefault("source", pdf_path)
            d.metadata.setdefault("page", i+1)
        return docs
    except Exception as e:
        print(f"[loaders] PDF load failed for {pdf_path}: {e}")
        return []

def load_pptx(ppt_path: str) -> list[Document]:
    try:
        loader = UnstructuredFileLoader(ppt_path)
        docs = loader.load()
        print(f"[loaders] PPTX loaded — {len(docs)} chunks from {ppt_path}")
        for i, d in enumerate(docs):
            d.metadata = d.metadata or {}
            d.metadata.setdefault("source", ppt_path)
            d.metadata.setdefault("slide", i+1)
        return docs
    except Exception as e:
        print(f"[loaders] PPTX load failed for {ppt_path}: {e}")
        return []

def load_manual_transcript(transcript_text: str, source: str = "manual_input") -> Document | None:
    if not transcript_text or not transcript_text.strip():
        print("[loaders] empty manual transcript")
        return None
    doc = Document(page_content=transcript_text.strip(), metadata={"source": source})
    return doc
