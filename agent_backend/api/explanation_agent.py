from google import genai
from google.genai import types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, MODEL_NAME
from models import (
    DocumentExplanations,
    TopicExplanation,
    DocumentStructure,
    HighlightedDocument
)
import json


class ExplanationAgent:
    """
    Agent responsible for creating explanations of topics to help
    users understand learning pathways and connections.
    """
    
    def __init__(self):
        """Initialize the Explanation Agent with Google ADK"""
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = MODEL_NAME
        
    async def generate_explanations(
        self,
        document: str,
        structure: DocumentStructure,
        highlights: HighlightedDocument
    ) -> DocumentExplanations:
        """
        Generate explanations for the document and its topics.
        
        Args:
            document: Full document text
            structure: Document structure from StructurizationAgent
            highlights: Highlighted sections from HighlighterAgent
            
        Returns:
            DocumentExplanations with overarching and topic-specific explanations
        """
        
        prompt = self._create_explanation_prompt(document, structure, highlights)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                response_mime_type="application/json",
            )
        )
        
        explanations_data = json.loads(response.text)
        
        topic_explanations = []
        for exp_data in explanations_data.get("topic_explanations", []):
            topic_explanations.append(TopicExplanation(
                topic_id=exp_data["topic_id"],
                topic_title=exp_data["topic_title"],
                explanation=exp_data["explanation"],
                prerequisite_concepts=exp_data.get("prerequisite_concepts", []),
                next_steps=exp_data.get("next_steps", []),
                related_topics=exp_data.get("related_topics", [])
            ))
        
        return DocumentExplanations(
            overarching_explanation=explanations_data.get("overarching_explanation", ""),
            topic_explanations=topic_explanations
        )
    
    def _create_explanation_prompt(
        self,
        document: str,
        structure: DocumentStructure,
        highlights: HighlightedDocument
    ) -> str:
        """Create the prompt for explanation generation"""
        
        structure_json = json.dumps({
            "document_title": structure.document_title,
            "topics": [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "subtopics": [{"id": st.id, "title": st.title} for st in topic.subtopics]
                }
                for topic in structure.topics
            ]
        }, indent=2)
        
        highlights_json = json.dumps([
            {
                "page": h.page_number,
                "text": h.text[:100] + "...",
                "topic_id": h.topic_id,
                "importance": h.importance
            }
            for h in highlights.highlights[:20]  # Sample of highlights
        ], indent=2)
        
        return f"""You are an Explanation Agent. Your task is to create educational explanations that help learners understand the topics in this document and their learning pathway.

DOCUMENT:
{document[:3000]}...  [Document truncated for context]

DOCUMENT STRUCTURE:
{structure_json}

KEY HIGHLIGHTS (sample):
{highlights_json}

INSTRUCTIONS:
1. Create an overarching explanation that introduces what this document teaches (NOT a summary)
2. For each main topic, create an explanation that:
   - Explains what the learner will understand after studying this topic
   - Lists prerequisite concepts needed to understand this topic
   - Suggests next steps for deeper learning
   - Identifies related topics in the document
3. Focus on learning pathways, not content summaries

Return a JSON object with this structure:
{{
  "overarching_explanation": "This document will help you understand... By studying this material, you will be able to...",
  "topic_explanations": [
    {{
      "topic_id": "topic_1",
      "topic_title": "Topic Title",
      "explanation": "After studying this topic, you will understand... This is important because...",
      "prerequisite_concepts": ["Concept 1", "Concept 2"],
      "next_steps": ["Study topic X", "Practice with examples", "Explore advanced application Y"],
      "related_topics": ["topic_2", "topic_3"]
    }}
  ]
}}

Guidelines:
- DO NOT summarize the document content
- Focus on learning outcomes and pathways
- Be encouraging and educational
- Connect topics to show the learning journey
- Keep explanations concise but informative (2-4 sentences per topic)
"""
