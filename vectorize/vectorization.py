

import os
from typing import List, Dict, Optional, Tuple
import PyPDF2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np
from dataclasses import dataclass
import hashlib
import json


def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
    pages_data = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            
            if text.strip():  # Only add non-empty pages
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': text.strip()
                })
    
    return pages_data
def chunk_text(self, pages_data, chunk_size=512, overlap=50):
    chunks = []
    
    for page_data in pages_data:
        text = page_data['text']
        page_num = page_data['page_number']
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence exceeds limit, save chunk
            if len(current_chunk) + len(sentence) > chunk_size:
                chunks.append(DocumentChunk(
                    text=current_chunk.strip(),
                    page_number=page_num,
                    chunk_index=chunk_counter,
                    metadata={'char_count': len(current_chunk)}
                ))
                
                # Keep overlap from previous chunk
                words = current_chunk.split()
                overlap_words = int(len(words) * (overlap / chunk_size))
                current_chunk = " ".join(words[-overlap_words:]) + " "
            
            current_chunk += sentence + " "
