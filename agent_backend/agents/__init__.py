"""
Agent implementations for document processing.

Each agent is specialized for a specific task:
- StructurizationAgent: Topic hierarchy analysis
- HighlighterAgent: Important section identification
- ExplanationAgent: Educational content generation
- QuizAgent: Assessment creation
"""

from .structurization_agent import StructurizationAgent
from .highlighter_agent import HighlighterAgent
from .explanation_agent import ExplanationAgent
from .quiz_agent import QuizAgent

__all__ = [
    "StructurizationAgent",
    "HighlighterAgent",
    "ExplanationAgent",
    "QuizAgent"
]
