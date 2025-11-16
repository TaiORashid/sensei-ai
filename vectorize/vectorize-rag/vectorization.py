"""
Sensei.i - Vector Store Module
Handles vector embeddings and similarity search using ChromaDB
"""

from __future__ import annotations

import chromadb
import os
import numpy as np
import re
from typing import Callable, Dict, List, Optional
from pdf_processor import DocumentChunk

try:  # sentence-transformers requires downloading models, so we guard the import.
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - falls back when dependency missing/offline.
    SentenceTransformer = None

USE_SENTENCE_TRANSFORMER = os.getenv("SENSEI_USE_SENTENCE_TRANSFORMER", "").lower() in {
    "1",
    "true",
    "yes",
}


class SimpleEmbedder:
    """
    Offline-friendly fallback embedder using a hashed bag-of-words vector.
    Provides deterministic embeddings without needing to download HF models.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def encode(self, texts: List[str], convert_to_numpy: bool = True) -> np.ndarray:
        vectors = []
        for text in texts:
            vec = np.zeros(self.dimension, dtype=np.float32)
            tokens = re.findall(r"\w+", text.lower())
            for token in tokens:
                idx = hash(token) % self.dimension
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        return np.stack(vectors) if convert_to_numpy else vectors


class VectorStore:
    """Manages vector embeddings and similarity search using ChromaDB"""
    
    def __init__(self, 
                 collection_name: str = "sensei_notes",
                 model_name: str = "all-MiniLM-L6-v2",
                 persist_directory: str = "./chroma_db"):
        """
        Initialize vector store
        
        Args:
            collection_name: Name for the vector collection
            model_name: SentenceTransformer model to use for embeddings
            persist_directory: Where to persist the vector database
        """
        self.embed_fn: Callable[[List[str]], np.ndarray]
        self._initialize_embedder(model_name)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def _initialize_embedder(self, model_name: str) -> None:
        """
        Initialize embedding function, falling back to a simple offline embedder
        if the SentenceTransformer model cannot be loaded (e.g., due to no internet).
        """
        if USE_SENTENCE_TRANSFORMER and SentenceTransformer is not None:
            try:
                model = SentenceTransformer(model_name)
                self.embedding_dimension = model.get_sentence_embedding_dimension()
                self.embed_fn = lambda texts: model.encode(texts, convert_to_numpy=True)
                print(f"Loaded SentenceTransformer model '{model_name}'.")
                return
            except OSError as exc:
                print(
                    f"Could not load SentenceTransformer model '{model_name}' ({exc}). "
                    "Falling back to SimpleEmbedder."
                )
            except Exception as exc:
                print(
                    f"SentenceTransformer unavailable ({exc}). "
                    "Falling back to SimpleEmbedder."
                )
        elif USE_SENTENCE_TRANSFORMER and SentenceTransformer is None:
            print(
                "sentence-transformers package is not available. "
                "Install it or unset SENSEI_USE_SENTENCE_TRANSFORMER to use the fallback."
            )
        else:
            print("Using SimpleEmbedder because SENSEI_USE_SENTENCE_TRANSFORMER is not enabled.")

        simple = SimpleEmbedder()
        self.embedding_dimension = simple.dimension
        self.embed_fn = simple.encode
        print(
            f"Using SimpleEmbedder with dimension {self.embedding_dimension} "
            "for offline vectorization."
        )
        
    def add_documents(self, chunks: List[DocumentChunk], document_id: str):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of DocumentChunk objects
            document_id: Unique identifier for the source document
        """
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_fn(texts)
        
        # Prepare metadata
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{chunk.chunk_index}"
            ids.append(chunk_id)
            
            metadatas.append({
                'document_id': document_id,
                'page_number': str(chunk.page_number),
                'chunk_index': str(chunk.chunk_index),
                'char_count': str(chunk.metadata.get('char_count', 0))
            })
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(chunks)} chunks to vector store for document: {document_id}")
    
    def query(self, 
              query_text: str, 
              n_results: int = 5,
              filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Query vector store for relevant chunks
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of dicts with text, metadata, and similarity scores
        """
        # Generate query embedding
        query_embedding = self.embed_fn([query_text])
        
        # Query collection
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None,
                'id': results['ids'][0][i]
            })
        
        return formatted_results
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a specific document"""
        self.collection.delete(
            where={"document_id": document_id}
        )
        print(f"Deleted all chunks for document: {document_id}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        return {
            'total_chunks': count,
            'embedding_dimension': self.embedding_dimension,
            'collection_name': self.collection.name
        }


# Example usage
if __name__ == "__main__":
    from pdf_processor import DocumentChunk
    
    # Create test chunks
    test_chunks = [
        DocumentChunk(
            text="Machine learning is a subset of AI.",
            page_number=1,
            chunk_index=0,
            metadata={'char_count': 37}
        ),
        DocumentChunk(
            text="Deep learning uses neural networks.",
            page_number=2,
            chunk_index=1,
            metadata={'char_count': 35}
        )
    ]
    
    # Initialize vector store
    vector_store = VectorStore(persist_directory="./test_chroma_db")
    
    # Add documents
    vector_store.add_documents(test_chunks, "test_doc")
    
    # Query
    results = vector_store.query("What is machine learning?", n_results=2)
    print(f"Found {len(results)} results")
    
    # Stats
    stats = vector_store.get_stats()
    print(f"Stats: {stats}")
