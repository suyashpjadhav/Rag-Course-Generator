import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.model.rag_pipeline import build_rag_pipeline

qa_chain = build_rag_pipeline()

query = "Explain module 1 from the document."

# Pass ONLY the string
result = qa_chain.invoke(query)

print("\nResponse:\n")
print(result)

# Optional: Print context sources
if "context" in result:
    print("\nSources:")
    for doc in result["context"]:
        metadata = getattr(doc, "metadata", {})
        content_preview = getattr(doc, "page_content", "")[:200]
        print(f"- Metadata: {metadata}, Content preview: {content_preview}")
