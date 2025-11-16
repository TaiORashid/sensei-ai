"""
Sensei.i - RAG System Module
Main RAG system combining PDF processing and vector retrieval
"""

import os
import hashlib
from typing import Dict, List, Optional
from pdf_processor import PDFProcessor
from vectorization import VectorStore


class RAGSystem:
    """Main RAG system combining PDF processing and vector retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG system
        
        Args:
            persist_directory: Where to persist the vector database
        """
        self.pdf_processor = PDFProcessor()
        self.vector_store = VectorStore(persist_directory=persist_directory)
    
    def process_pdf(self, pdf_path: str, document_id: Optional[str] = None) -> str:
        """
        Process a PDF file and add to vector store
        
        Args:
            pdf_path: Path to PDF file
            document_id: Optional unique ID (auto-generated if not provided)
            
        Returns:
            document_id used for storage
        """
        # Generate document ID if not provided
        if document_id is None:
            document_id = self._generate_document_id(pdf_path)
        
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        pages_data = self.pdf_processor.extract_text_from_pdf(pdf_path)
        print(f"Extracted text from {len(pages_data)} pages")
        
        # Chunk the text
        chunks = self.pdf_processor.chunk_text(pages_data)
        print(f"Created {len(chunks)} chunks")
        
        # Add to vector store
        self.vector_store.add_documents(chunks, document_id)
        
        return document_id
    
    def query(self, 
              query_text: str, 
              n_results: int = 5,
              document_id: Optional[str] = None) -> Dict:
        """
        Query the RAG system
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            document_id: Optional filter to specific document
            
        Returns:
            Dict with query results and context for LLM
        """
        # Build filter if document_id specified
        filter_dict = {'document_id': document_id} if document_id else None
        
        # Query vector store
        results = self.vector_store.query(
            query_text=query_text,
            n_results=n_results,
            filter_dict=filter_dict
        )
        
        # Build context for LLM
        context = self._build_context(results)
        
        return {
            'query': query_text,
            'results': results,
            'context': context,
            'num_results': len(results)
        }
    
    def _build_context(self, results: List[Dict]) -> str:
        """Build formatted context string for LLM from search results"""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            page_num = result['metadata'].get('page_number', 'Unknown')
            text = result['text']
            
            context_parts.append(
                f"[Context {i} - Page {page_num}]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_document_id(self, pdf_path: str) -> str:
        """Generate unique document ID from file path"""
        filename = os.path.basename(pdf_path)
        return hashlib.md5(filename.encode()).hexdigest()[:12]
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return self.vector_store.get_stats()


# Example usage and testing
if __name__ == "__main__":
    # Initialize RAG system
    rag = RAGSystem(persist_directory="./sensei_chroma_db")
    
    # Example: Process a PDF
    # doc_id = rag.process_pdf("path/to/notes.pdf")
    
    # Example: Query the system
    # results = rag.query("What are the key concepts in chapter 2?", n_results=3)
    # print(results['context'])
    
    # Get stats
    stats = rag.get_stats()
    print(f"RAG System Stats: {stats}")
