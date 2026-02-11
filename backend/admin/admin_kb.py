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
