"""
Sensei.i - PDF Processing Module
Handles PDF text extraction and chunking
"""

import PyPDF2
from typing import List, Dict
from dataclasses import dataclass
import re
import textwrap


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    text: str
    page_number: int
    chunk_index: int
    metadata: Dict


class PDFProcessor:
    """Handles PDF text extraction and preprocessing"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF with page information
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dicts with page_number and text
        """
        pages_data = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    
                    if text.strip():  # Only add non-empty pages
                        pages_data.append({
                            'page_number': page_num + 1,
                            'text': text.strip()
                        })
                        
        except FileNotFoundError:
            print(
                f"PDF '{pdf_path}' not found. Using built-in sample notes so the "
                "system can be exercised without external assets."
            )
            pages_data = self._sample_pages()
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
        
        return pages_data
    
    def chunk_text(self, 
                   pages_data: List[Dict], 
                   chunk_size: int = 512, 
                   overlap: int = 50) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks for better context preservation
        
        Args:
            pages_data: List of page data dicts
            chunk_size: Number of characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        chunk_counter = 0
        
        for page_data in pages_data:
            text = page_data['text']
            page_num = page_data['page_number']
            
            # Split into sentences first for better semantic boundaries
            sentences = self._split_into_sentences(text)
            
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence exceeds chunk_size, save current chunk
                if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                    chunks.append(DocumentChunk(
                        text=current_chunk.strip(),
                        page_number=page_num,
                        chunk_index=chunk_counter,
                        metadata={
                            'char_count': len(current_chunk),
                            'source_page': page_num
                        }
                    ))
                    chunk_counter += 1
                    
                    # Keep overlap by retaining last part of current chunk
                    if overlap > 0:
                        words = current_chunk.split()
                        overlap_words = int(len(words) * (overlap / chunk_size))
                        current_chunk = " ".join(words[-overlap_words:]) + " "
                    else:
                        current_chunk = ""
                
                current_chunk += sentence + " "
            
            # Add remaining text as final chunk for this page
            if current_chunk.strip():
                chunks.append(DocumentChunk(
                    text=current_chunk.strip(),
                    page_number=page_num,
                    chunk_index=chunk_counter,
                    metadata={
                        'char_count': len(current_chunk),
                        'source_page': page_num
                    }
                ))
                chunk_counter += 1
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitter"""
        # Basic sentence splitting (can be enhanced with nltk if needed)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]

    def _sample_pages(self) -> List[Dict]:
        """Provide fallback content when no PDF is available."""
        sample_text = textwrap.dedent("""
            Dynamic arrays are arrays that automatically resize when capacity is exceeded.
            They double their size when they run out of space, providing amortized O(1) append.
            However, insertions in the middle still cost O(n) because elements must shift.
            
            Implementation typically tracks size, capacity, and a pointer to contiguous memory.
            When resizing, a new block is allocated and existing elements are copied over.
            This can temporarily require double the memory during the copy.
        """).strip()
        paragraphs = [p.strip() for p in sample_text.split("\n\n") if p.strip()]
        pages = []
        for idx, paragraph in enumerate(paragraphs, 1):
            pages.append({
                "page_number": idx,
                "text": paragraph
            })
        return pages


# Example usage
if __name__ == "__main__":
    processor = PDFProcessor()
    
    # Test extraction
    pages = processor.extract_text_from_pdf("test.pdf")
    print(f"Extracted {len(pages)} pages")
    
    # Test chunking
    chunks = processor.chunk_text(pages)
    print(f"Created {len(chunks)} chunks")
