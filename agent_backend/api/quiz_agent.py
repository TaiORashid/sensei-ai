from google import genai
from google.genai import types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, MODEL_NAME
from models import Quiz, QuizQuestion, QuizChoice, DocumentStructure
import json
import uuid


class QuizAgent:
    """
    Agent responsible for generating quiz questions with multiple choice
    answers and detailed explanations.
    """
    
    def __init__(self):
        """Initialize the Quiz Agent with Google ADK"""
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = MODEL_NAME
        
    async def generate_quiz(
        self,
        document: str,
        structure: DocumentStructure,
        num_questions: int = 10
    ) -> Quiz:
        """
        Generate quiz questions based on the document.
        
        Args:
            document: Full document text
            structure: Document structure for topic-based questions
            num_questions: Number of questions to generate
            
        Returns:
            Quiz with questions, choices, and explanations
        """
        
        prompt = self._create_quiz_prompt(document, structure, num_questions)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            )
        )
        
        quiz_data = json.loads(response.text)
        
        questions = []
        for q_data in quiz_data.get("questions", []):
            choices = []
            for c_data in q_data.get("choices", []):
                choices.append(QuizChoice(
                    choice_id=c_data.get("choice_id", str(uuid.uuid4())),
                    text=c_data["text"],
                    is_correct=c_data["is_correct"],
                    explanation=c_data["explanation"]
                ))
            
            questions.append(QuizQuestion(
                question_id=q_data.get("question_id", str(uuid.uuid4())),
                question_text=q_data["question_text"],
                choices=choices,
                topic_id=q_data.get("topic_id", ""),
                difficulty=q_data.get("difficulty", "medium"),
                page_reference=q_data.get("page_reference", 1)
            ))
        
        return Quiz(
            questions=questions,
            total_questions=len(questions)
        )
    
    def _create_quiz_prompt(
        self,
        document: str,
        structure: DocumentStructure,
        num_questions: int
    ) -> str:
        """Create the prompt for quiz generation"""
        
        structure_json = json.dumps({
            "topics": [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "page_range": topic.page_range
                }
                for topic in structure.topics
            ]
        }, indent=2)
        
        return f"""You are a Quiz Generation Agent. Your task is to create comprehensive multiple-choice questions based on the document content.

DOCUMENT:
{document}

DOCUMENT STRUCTURE:
{structure_json}

INSTRUCTIONS:
Generate {num_questions} multiple-choice quiz questions following these rules:

1. Each question must have exactly 4 choices (A, B, C, D)
2. Exactly 1 choice is correct, 3 are wrong
3. Each choice (correct AND incorrect) must have a detailed explanation
4. Explanations for correct answers should explain WHY it's correct
5. Explanations for wrong answers should explain WHY it's incorrect and what the misconception is
6. Distribute questions across different topics
7. Vary difficulty levels (easy, medium, hard)
8. Reference the page number where the answer can be found

Return a JSON object with this structure:
{{
  "questions": [
    {{
      "question_id": "q_1",
      "question_text": "What is...?",
      "topic_id": "topic_1",
      "difficulty": "medium",
      "page_reference": 5,
      "choices": [
        {{
          "choice_id": "q_1_a",
          "text": "Choice A text",
          "is_correct": true,
          "explanation": "This is correct because... The document states on page 5 that..."
        }},
        {{
          "choice_id": "q_1_b",
          "text": "Choice B text",
          "is_correct": false,
          "explanation": "This is incorrect because... While it might seem like..., the document actually indicates..."
        }},
        {{
          "choice_id": "q_1_c",
          "text": "Choice C text",
          "is_correct": false,
          "explanation": "This is incorrect because..."
        }},
        {{
          "choice_id": "q_1_d",
          "text": "Choice D text",
          "is_correct": false,
          "explanation": "This is incorrect because..."
        }}
      ]
    }}
  ]
}}

Guidelines:
- Questions should test understanding, not just memorization
- Wrong answers should be plausible but clearly incorrect
- Explanations should be educational and reference the document
- Ensure questions cover all major topics proportionally
- Make explanations detailed enough to aid learning (2-3 sentences minimum)
"""
