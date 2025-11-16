from google import genai
from google.genai import types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, MODEL_NAME
from models import DocumentStructure, Topic, SubTopic
import json
import uuid


class StructurizationAgent:
    """
    Agent responsible for analyzing document topics and creating
    a hierarchical directory-like structure.
    """
    
    def __init__(self):
        """Initialize the Structurization Agent with Google ADK"""
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = MODEL_NAME
        
    async def analyze_structure(self, document: str) -> DocumentStructure:
        """
        Analyze the document and create a hierarchical topic structure.
        
        Args:
            document: Full document text with page markers
            
        Returns:
            DocumentStructure with topics and subtopics
        """
        
        prompt = self._create_structure_prompt(document)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
            )
        )
        
        structure_data = json.loads(response.text)
        
        topics = []
        for topic_data in structure_data.get("topics", []):
            subtopics = []
            for st_data in topic_data.get("subtopics", []):
                subtopics.append(SubTopic(
                    id=st_data.get("id", str(uuid.uuid4())),
                    title=st_data["title"],
                    page_reference=st_data["page_reference"],
                    char_start=st_data.get("char_start"),
                    char_end=st_data.get("char_end")
                ))
            
            topics.append(Topic(
                id=topic_data.get("id", str(uuid.uuid4())),
                title=topic_data["title"],
                subtopics=subtopics,
                page_range=topic_data["page_range"]
            ))
        
        return DocumentStructure(
            topics=topics,
            document_title=structure_data.get("document_title", "Untitled Document")
        )
    
    def _create_structure_prompt(self, document: str) -> str:
        """Create the prompt for structure analysis"""
        
        return f"""You are a Document Structurization Agent. Your task is to analyze a document and create a hierarchical topic structure that represents its organization.

DOCUMENT:
{document}

INSTRUCTIONS:
1. Identify all major topics in the document
2. For each major topic, identify 2-5 subtopics
3. Note which pages each topic spans
4. Provide page references for where each subtopic begins
5. Create unique IDs for topics and subtopics (use format: topic_1, topic_2, etc.)
6. Determine the overall document title

Return a JSON object with this structure:
{{
  "document_title": "Title of the document",
  "topics": [
    {{
      "id": "topic_1",
      "title": "Main Topic Title",
      "page_range": [1, 5],
      "subtopics": [
        {{
          "id": "topic_1_sub_1",
          "title": "Subtopic Title",
          "page_reference": 1,
          "char_start": 0,
          "char_end": 500
        }}
      ]
    }}
  ]
}}

Guidelines:
- Main topics should be broad, overarching concepts
- Subtopics should be specific aspects or sections within each main topic
- Ensure the structure is hierarchical and logical
- Page references should be accurate based on [PAGE X] markers
- Each topic should have at least 1 subtopic
"""
