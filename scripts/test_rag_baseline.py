import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.model.rag_pipeline import build_rag_pipeline

qa_chain = build_rag_pipeline()
query = "Generate structured learning modules explaining the DBMS three schema architecture."

# Pass ONLY the string
result = qa_chain.invoke(query)

print("\nResponse:\n")
if hasattr(result, "content"):
    print(result.content)
else:
    print(result)
