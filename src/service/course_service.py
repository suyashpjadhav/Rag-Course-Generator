import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Optional
from src.model.rag_pipeline import build_rag_pipeline


def generate_course(
    documents: List[str],
    user_goal: str,
    level: str,
    duration: str,
    usage_context: Optional[str] = None,
    style_instruction: Optional[str] = None,
    coverage_level: str = "focused"
) -> Dict:
    """
    Main entry point for course generation.

    Parameters:
    - documents: Reserved for future document-level filtering
    - user_goal: Primary intent of the user
    - level: Target audience level
    - duration: Time horizon
    - usage_context: Optional context (presentation, teaching, etc.)
    - style_instruction: Optional tone/format guidance
    - coverage_level: 'focused' or 'broad'
    """

    _ = documents  # intentionally unused (future extension)

    rag_chain = build_rag_pipeline(coverage_level=coverage_level)

    query_parts = [
        f"Goal: {user_goal}",
        f"Audience Level: {level}",
        f"Duration: {duration}",
    ]

    if usage_context:
        query_parts.append(f"Usage Context: {usage_context}")

    if style_instruction:
        query_parts.append(f"Style Guidance: {style_instruction}")

    user_query = "\n".join(query_parts)
    response = rag_chain.invoke(user_query)
    content = response.content if hasattr(response, "content") else str(response)

    return {
        "goal": user_goal,
        "level": level,
        "duration": duration,
        "usage_context": usage_context,
        "coverage_level": coverage_level,
        "content": content
    }

