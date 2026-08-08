import pymupdf  # PyMuPDF
from typing import List, Dict
import os
import uuid
from config import Config

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict]:
        """Extract text from PDF with page numbers."""
        doc = pymupdf.open(file_path)
        pages_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                pages_text.append({
                    "page_number": page_num + 1,
                    "text": text
                })
        
        doc.close()
        return pages_text
    
    def chunk_text(self, pages_text: List[Dict], filename: str) -> List[Dict]:
        """Split text into chunks with metadata."""
        chunks = []
        
        for page_data in pages_text:
            text = page_data["text"]
            page_number = page_data["page_number"]
            
            # Simple chunking by character count
            start = 0
            chunk_id = 0
            
            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]
                
                if chunk_text.strip():
                    chunks.append({
                        "chunk_id": f"{filename}_{chunk_id:03d}",
                        "document": filename,
                        "page": page_number,
                        "text": chunk_text.strip()
                    })
                    chunk_id += 1
                
                start = end - self.chunk_overlap
        
        return chunks
    
    def process_document(self, file_path: str, filename: str) -> Dict:
        """Process document: extract text and chunk."""
        pages_text = self.extract_text_from_pdf(file_path)
        chunks = self.chunk_text(pages_text, filename)
        
        return {
            "pages": pages_text,
            "chunks": chunks,
            "total_pages": len(pages_text),
            "total_chunks": len(chunks)
        }
