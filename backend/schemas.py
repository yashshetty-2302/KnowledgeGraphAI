from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    upload_date: datetime
    total_pages: int
    total_chunks: int
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    upload_date: datetime
    total_pages: int
    total_chunks: int
    
    class Config:
        from_attributes = True

class Citation(BaseModel):
    document: str
    page: int
    chunk_id: str

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieved_chunks: int
    retrieval_attempts: int
    self_corrected: bool
    evidence_sufficient: bool
    graph_used: bool = False
    graph_entities: List[str] = []
    graph_relationships: List[str] = []

class HealthResponse(BaseModel):
    status: str
    message: str
