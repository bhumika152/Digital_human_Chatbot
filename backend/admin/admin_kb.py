# backend/admin/admin_kb.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import os

from database import get_db
from models import KnowledgeBaseEmbedding
from dependencies.admin_guard import require_admin
from services.admin_knowledgeBase.kb_ingestion import ingest_policy_pdf
from sqlalchemy import func
from uuid import UUID


router = APIRouter(prefix="/admin/kb", tags=["admin-kb"])

UPLOAD_DIR = Path("uploads/kb")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_kb_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),     # FAQ | POLICY | TERMS
    industry: str = Form(None),
    language: str = Form("en"),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    # -----------------------
    # VALIDATION
    # -----------------------
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    if document_type not in {"FAQ", "POLICY", "TERMS", "GUIDELINE", "SUPPORT"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid document type"
        )

    # -----------------------
    # SAVE FILE TEMPORARILY
    # -----------------------
    original_filename = file.filename
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / temp_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -----------------------
    # INGEST DOCUMENT
    # -----------------------
    try:
        ingest_policy_pdf(
            db=db,
            file_path=file_path,
            document_type=document_type,
            industry=industry,
            language=language,
            original_filename=original_filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"KB ingestion failed: {str(e)}"
        )
    finally:
        # cleanup temp file
        if file_path.exists():
            file_path.unlink()

    return {
        "message": "Knowledge base document uploaded successfully",
        "document_type": document_type,
        "industry": industry,
        "language": language,
        "uploaded_by": admin.email
    }

@router.get("/documents")
def list_kb_documents(
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List all KB documents (grouped by document_id)
    """

    documents = (
        db.query(
            KnowledgeBaseEmbedding.document_id,
            KnowledgeBaseEmbedding.document_title,
            KnowledgeBaseEmbedding.document_type,
            KnowledgeBaseEmbedding.industry,
            KnowledgeBaseEmbedding.language,
            KnowledgeBaseEmbedding.version,
            KnowledgeBaseEmbedding.is_active,
            func.count(KnowledgeBaseEmbedding.kb_id).label("chunk_count"),
            func.min(KnowledgeBaseEmbedding.created_at).label("created_at"),
        )
        .group_by(
            KnowledgeBaseEmbedding.document_id,
            KnowledgeBaseEmbedding.document_title,
            KnowledgeBaseEmbedding.document_type,
            KnowledgeBaseEmbedding.industry,
            KnowledgeBaseEmbedding.language,
            KnowledgeBaseEmbedding.version,
            KnowledgeBaseEmbedding.is_active,
        )
        .order_by(func.min(KnowledgeBaseEmbedding.created_at).asc())
        .all()
    )

    return [
        {
            "document_id": str(doc.document_id),
            "title": doc.document_title,
            "document_type": doc.document_type,
            "industry": doc.industry,
            "language": doc.language,
            "version": doc.version,
            "is_active": doc.is_active,
            "chunks": doc.chunk_count,
            "created_at": doc.created_at,
        }
        for doc in documents
    ]

@router.delete("/{document_id}")
def delete_kb_document(
    document_id: UUID,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a KB document (ALL chunks by document_id)
    """

    rows = (
        db.query(KnowledgeBaseEmbedding)
        .filter(KnowledgeBaseEmbedding.document_id == document_id)
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    deleted_count = len(rows)

    for row in rows:
        db.delete(row)

    db.commit()

    return {
        "message": "Knowledge base document deleted successfully",
        "document_id": str(document_id),
        "chunks_deleted": deleted_count,
        "deleted_by": admin.email
    }