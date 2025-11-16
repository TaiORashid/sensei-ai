from typing import List, Dict
import PyPDF2
from dataclasses import dataclass


@dataclass
class PageContent:
    """Represents content from a single PDF page"""
    page_number: int
    text: str
    char_count: int


class DocumentProcessor:
    """Handles PDF document extraction and preprocessing"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[PageContent]:
        """
        Extract text from PDF file, page by page.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PageContent objects with text from each page
        """
        pages_data = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    
                    if text.strip():
                        pages_data.append(PageContent(
                            page_number=page_num + 1,
                            text=text.strip(),
                            char_count=len(text.strip())
                        ))
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return pages_data
    
    def format_document_for_agent(self, pages: List[PageContent]) -> str:
        """
        Format extracted pages into a single document string for agent processing.
        
        Args:
            pages: List of PageContent objects
            
        Returns:
            Formatted document string with page markers
        """
        formatted = []
        for page in pages:
            formatted.append(f"[PAGE {page.page_number}]\n{page.text}\n")
        
        return "\n".join(formatted)
    
    def get_page_text(self, pages: List[PageContent], page_number: int) -> str:
        """Get text from a specific page number"""
        for page in pages:
            if page.page_number == page_number:
                return page.text
        return ""
