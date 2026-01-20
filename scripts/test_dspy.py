import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.dspy.program import generate_course

context = """
A manufacturing process shows inconsistent quality results.
Operators believe the process is unchanged, but variation exists
in temperature, time, and handling across shifts.
"""

question = "Generate a learning module explaining process, parameters, and variation in simple language."

result = generate_course(
    context=context,
    question=question
)

print("\nGenerated Learning Module\n")
for k, v in result.items():
    print(f"\n{k.upper()}:\n{v}")
