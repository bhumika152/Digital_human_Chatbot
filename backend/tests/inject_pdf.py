from pathlib import Path
from database import SessionLocal
from services.admin_knowledgeBase.kb_ingestion import ingest_policy_pdf

POLICY_DIR = Path("documents/policy_pdfs")

def main():
    db = SessionLocal()

    try:
        pdfs = list(POLICY_DIR.glob("*.pdf"))

        if not pdfs:
            print("❌ No PDFs found")
            return

        print(f"📥 Found {len(pdfs)} PDFs\n")

        for pdf in pdfs:
            print(f"➡️ Ingesting: {pdf.name}")

            ingest_policy_pdf(
                db=db,
                file_path=pdf,
                document_type="POLICY",
                industry="fintech",
            )

        print("\n✅ PDF injection completed")

    finally:
        db.close()

if __name__ == "__main__":
    main()
