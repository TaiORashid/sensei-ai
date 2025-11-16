from typing import Dict, Any
from document_processor import DocumentProcessor, PageContent
from agents.structurization_agent import StructurizationAgent
from agents.highlighter_agent import HighlighterAgent
from agents.explanation_agent import ExplanationAgent
from agents.quiz_agent import QuizAgent
from models import (
    DocumentStructure,
    HighlightedDocument,
    DocumentExplanations,
    Quiz
)


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all agents to process documents
    and generate all required outputs.
    """
    
    def __init__(self):
        """Initialize all agents"""
        self.doc_processor = DocumentProcessor()
        self.structurization_agent = StructurizationAgent()
        self.highlighter_agent = HighlighterAgent()
        self.explanation_agent = ExplanationAgent()
        self.quiz_agent = QuizAgent()
        
    async def process_document(
        self,
        pdf_path: str,
        num_quiz_questions: int = 10
    ) -> Dict[str, Any]:
        """
        Process a PDF document through all agents to generate:
        1. Document structure (topics and subtopics)
        2. Highlighted text sections
        3. Educational explanations
        4. Quiz questions with answers and explanations
        
        Args:
            pdf_path: Path to the PDF file
            num_quiz_questions: Number of quiz questions to generate
            
        Returns:
            Dictionary containing all outputs from all agents
        """
        
        # Step 1: Extract text from PDF
        print("📄 Extracting text from PDF...")
        pages = self.doc_processor.extract_text_from_pdf(pdf_path)
        formatted_doc = self.doc_processor.format_document_for_agent(pages)
        
        # Step 2: Analyze document structure
        print("🗂️  Analyzing document structure...")
        structure = await self.structurization_agent.analyze_structure(formatted_doc)
        
        # Step 3: Highlight important sections (requires structure)
        print("✨ Highlighting important sections...")
        highlights = await self.highlighter_agent.highlight_document(
            formatted_doc,
            structure,
            pages
        )
        
        # Step 4: Generate explanations (requires structure and highlights)
        print("📚 Generating explanations...")
        explanations = await self.explanation_agent.generate_explanations(
            formatted_doc,
            structure,
            highlights
        )
        
        # Step 5: Generate quiz (requires structure)
        print("❓ Generating quiz questions...")
        quiz = await self.quiz_agent.generate_quiz(
            formatted_doc,
            structure,
            num_quiz_questions
        )
        
        print("✅ Document processing complete!")
        
        return {
            "structure": structure.model_dump(),
            "highlights": highlights.model_dump(),
            "explanations": explanations.model_dump(),
            "quiz": quiz.model_dump(),
            "metadata": {
                "total_pages": len(pages),
                "total_topics": len(structure.topics),
                "total_highlights": len(highlights.highlights),
                "total_questions": quiz.total_questions
            }
        }
    
    async def process_single_feature(
        self,
        pdf_path: str,
        feature: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a single feature for a document.
        
        Args:
            pdf_path: Path to the PDF file
            feature: One of 'structure', 'highlights', 'explanations', 'quiz'
            **kwargs: Additional arguments for specific features
            
        Returns:
            Output from the requested feature
        """
        
        pages = self.doc_processor.extract_text_from_pdf(pdf_path)
        formatted_doc = self.doc_processor.format_document_for_agent(pages)
        
        if feature == "structure":
            structure = await self.structurization_agent.analyze_structure(formatted_doc)
            return {"structure": structure.model_dump()}
        
        elif feature == "highlights":
            # Highlights require structure first
            structure_data = kwargs.get("structure")
            if not structure_data:
                structure = await self.structurization_agent.analyze_structure(formatted_doc)
            else:
                structure = DocumentStructure(**structure_data)
            
            highlights = await self.highlighter_agent.highlight_document(
                formatted_doc,
                structure,
                pages
            )
            return {"highlights": highlights.model_dump()}
        
        elif feature == "explanations":
            # Explanations require structure and highlights
            structure_data = kwargs.get("structure")
            highlights_data = kwargs.get("highlights")
            
            if not structure_data:
                structure = await self.structurization_agent.analyze_structure(formatted_doc)
            else:
                structure = DocumentStructure(**structure_data)
            
            if not highlights_data:
                highlights = await self.highlighter_agent.highlight_document(
                    formatted_doc,
                    structure,
                    pages
                )
            else:
                highlights = HighlightedDocument(**highlights_data)
            
            explanations = await self.explanation_agent.generate_explanations(
                formatted_doc,
                structure,
                highlights
            )
            return {"explanations": explanations.model_dump()}
        
        elif feature == "quiz":
            # Quiz requires structure
            structure_data = kwargs.get("structure")
            if not structure_data:
                structure = await self.structurization_agent.analyze_structure(formatted_doc)
            else:
                structure = DocumentStructure(**structure_data)
            
            num_questions = kwargs.get("num_questions", 10)
            quiz = await self.quiz_agent.generate_quiz(
                formatted_doc,
                structure,
                num_questions
            )
            return {"quiz": quiz.model_dump()}
        
        else:
            raise ValueError(f"Unknown feature: {feature}")
