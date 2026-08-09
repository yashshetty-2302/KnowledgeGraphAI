from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, init_db
from models import Document
from schemas import DocumentUploadResponse, DocumentListResponse
from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.graph_service import GraphService
import os
import shutil
from datetime import datetime
from config import Config

router = APIRouter()

# Global instances to ensure consistency
_processor = None
_embedding_service = None
_vector_store = None
_graph_service = None

def get_processor():
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

def get_graph_service():
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF document."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{datetime.utcnow().timestamp()}_{file.filename}"
    file_path = os.path.join(Config.DATA_DIR, unique_filename)
    
    # Save file
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process document
    try:
        processor = get_processor()
        result = processor.process_document(file_path, file.filename)
        
        # Generate embeddings for chunks
        embedding_service = get_embedding_service()
        chunk_texts = [chunk["text"] for chunk in result["chunks"]]
        embeddings = embedding_service.generate_embeddings(chunk_texts)
        
        # Add to vector store
        vector_store = get_vector_store()
        vector_store.add_chunks(embeddings, result["chunks"])
        
        # Add to knowledge graph
        graph_service = get_graph_service()
        graph_service.add_document_to_graph(result["chunks"], file.filename)
        
        # Save to database
        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            total_pages=result["total_pages"],
            total_chunks=result["total_chunks"]
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return DocumentUploadResponse(
            id=db_document.id,
            filename=db_document.filename,
            original_filename=db_document.original_filename,
            upload_date=db_document.upload_date,
            total_pages=db_document.total_pages,
            total_chunks=db_document.total_chunks
        )
    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("", response_model=List[DocumentListResponse])
async def get_documents(db: Session = Depends(get_db)):
    """Get list of all uploaded documents."""
    documents = db.query(Document).order_by(Document.upload_date.desc()).all()
    return documents
