import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.service.course_service import generate_course

if __name__ == "__main__":
    result = generate_course(
        documents=["DBMS_Full_Notes.pdf"],
        user_goal="Prepare for DBMS semester exam",
        level="Intermediate",
        duration="6 weeks",
        coverage_level="focused"
    )

    print("\nGENERATED COURSE\n")
    print(result["content"])
