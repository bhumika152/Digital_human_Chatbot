# backend/scripts/ingest_single_pdf.py

from pathlib import Path
from database import SessionLocal
from services.admin_knowledgeBase.kb_ingestion import ingest_policy_pdf

POLICY_DIR = Path("documents/policy_pdfs")

# 🔴 EXACT PDF NAME HERE
TARGET_PDF_NAME = "FTP2023_Chapter03.pdf"

def main():
    db = SessionLocal()

    try:
        pdf_path = POLICY_DIR / TARGET_PDF_NAME

        if not pdf_path.exists():
            print(f"❌ PDF not found: {TARGET_PDF_NAME}")
            return

        print(f"📥 Ingesting ONLY: {pdf_path.name}")

        ingest_policy_pdf(
            db=db,
            file_path=pdf_path,
            document_type="POLICY",
            industry="fintech",
        )

        print("✅ PDF injection completed")

    finally:
        db.close()

if __name__ == "__main__":
    main()
