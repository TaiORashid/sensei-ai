from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class PageHighlight(BaseModel):
    """Represents a highlighted section in the document"""
    page_number: int
    start_char: int
    end_char: int
    text: str
    topic_id: str
    importance: str = Field(description="high, medium, or low")


class HighlightedDocument(BaseModel):
    """Document with all highlights"""
    highlights: List[PageHighlight]
    total_pages: int


class SubTopic(BaseModel):
    """Represents a subtopic within a main topic"""
    id: str
    title: str
    page_reference: int
    char_start: Optional[int] = None
    char_end: Optional[int] = None


class Topic(BaseModel):
    """Represents a main topic with its subtopics"""
    id: str
    title: str
    subtopics: List[SubTopic]
    page_range: List[int]


class DocumentStructure(BaseModel):
    """Complete hierarchical structure of the document"""
    topics: List[Topic]
    document_title: str


class TopicExplanation(BaseModel):
    """Explanation for a specific topic"""
    topic_id: str
    topic_title: str
    explanation: str
    prerequisite_concepts: List[str]
    next_steps: List[str]
    related_topics: List[str]


class DocumentExplanations(BaseModel):
    """All explanations for the document"""
    overarching_explanation: str
    topic_explanations: List[TopicExplanation]


class QuizChoice(BaseModel):
    """A single choice in a quiz question"""
    choice_id: str
    text: str
    is_correct: bool
    explanation: str


class QuizQuestion(BaseModel):
    """A complete quiz question with all choices and explanations"""
    question_id: str
    question_text: str
    choices: List[QuizChoice]
    topic_id: str
    difficulty: str = Field(description="easy, medium, or hard")
    page_reference: int


class Quiz(BaseModel):
    """Complete quiz for the document"""
    questions: List[QuizQuestion]
    total_questions: int
