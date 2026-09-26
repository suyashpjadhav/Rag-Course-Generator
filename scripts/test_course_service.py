import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.service.course_service import generate_course

if __name__ == "__main__":
    result = generate_course(
        documents=["DBMS_Full_Notes.pdf"],
        user_goal="explain the architecture schema to the professor in viva",
        level="Intermediate",
        duration="10 minutes",
        coverage_level="focused"
    )

    print("\nGENERATED COURSE\n")
    print(result["content"])
