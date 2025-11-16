from typing import List
from google import genai
from google.genai import types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, MODEL_NAME
from models import HighlightedDocument, PageHighlight, DocumentStructure
from document_processor import PageContent
import json


class HighlighterAgent:
    """
    Agent responsible for identifying and highlighting important sections
    of the document based on the document structure.
    """
    
    def __init__(self):
        """Initialize the Text Highlighter Agent with Google ADK"""
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = MODEL_NAME
        
    async def highlight_document(
        self,
        document: str,
        structure: DocumentStructure,
        pages: List[PageContent]
    ) -> HighlightedDocument:
        """
        Identify and highlight important sections in the document.
        
        Args:
            document: Full document text with page markers
            structure: Document structure from StructurizationAgent
            pages: List of page contents
            
        Returns:
            HighlightedDocument with all highlights
        """
        
        prompt = self._create_highlight_prompt(document, structure)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            )
        )
        
        highlights_data = json.loads(response.text)
        
        highlights = []
        for h in highlights_data.get("highlights", []):
            highlights.append(PageHighlight(
                page_number=h["page_number"],
                start_char=h["start_char"],
                end_char=h["end_char"],
                text=h["text"],
                topic_id=h["topic_id"],
                importance=h["importance"]
            ))
        
        return HighlightedDocument(
            highlights=highlights,
            total_pages=len(pages)
        )
    
    def _create_highlight_prompt(self, document: str, structure: DocumentStructure) -> str:
        """Create the prompt for highlighting"""
        
        topics_json = json.dumps([
            {
                "id": topic.id,
                "title": topic.title,
                "subtopics": [{"id": st.id, "title": st.title} for st in topic.subtopics]
            }
            for topic in structure.topics
        ], indent=2)
        
        return f"""You are a Text Highlighting Agent. Your task is to identify and mark the most important sections in a document based on its topic structure.

DOCUMENT:
{document}

TOPIC STRUCTURE:
{topics_json}

INSTRUCTIONS:
1. For each topic and subtopic, identify the key sections in the document
2. Mark the beginning and important sections of each topic
3. Provide character positions (start_char, end_char) relative to each page
4. Assign importance levels: "high" (core concepts), "medium" (supporting details), "low" (examples/references)
5. Link each highlight to a topic_id from the structure

Return a JSON object with this structure:
{{
  "highlights": [
    {{
      "page_number": 1,
      "start_char": 0,
      "end_char": 100,
      "text": "excerpt of highlighted text",
      "topic_id": "topic_id_from_structure",
      "importance": "high"
    }}
  ]
}}

Focus on highlighting:
- Topic introductions and definitions
- Key theorems, formulas, or principles
- Important examples
- Section transitions
"""
