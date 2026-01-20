import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.service.course_service import generate_from_query

query = "Explain process, parameters, and variation in manufacturing SOP"

result = generate_from_query(query)

print("\nRAG + DSPy OUTPUT\n")
print(result)

