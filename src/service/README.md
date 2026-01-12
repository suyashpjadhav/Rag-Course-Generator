# Course Generation Module

This module implements RAG-based course generation over pre-ingested documents.
It is designed to be integrated into the larger system without modifying core infrastructure.

## Overview

- Uses vector retrieval over ingested content
- Generates structured educational content
- Adapts tone and coverage based on user intent
- Does not hardcode output formats

## Expected User Inputs

Required:
- user_goal: what the user wants to achieve
- audience_level: Beginner | Intermediate | Advanced
- duration: expected learning or usage time

Optional:
- usage_context: presentation | teaching | self-study | documentation
- style_instruction: free-form guidance on tone or format
- coverage_level: focused | broad

## Coverage Behavior

- focused: retrieves the most relevant chunks for concise, goal-aligned output
- broad: retrieves a wider portion of the document for more comprehensive coverage

## Notes

- Document ingestion is handled separately
- This module assumes embeddings are already available in the vector store
- Output structure is intentionally flexible and prompt-driven
