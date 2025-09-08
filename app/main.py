import os
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from datetime import datetime

from app.db_master import init_master_db, get_tenant, create_tenant
from app.db_tenant import get_tenant_db, store_pdf_data
from app.pdf_utils import extract_pdf_text
from app.ai_utils import summarize_text
from app.storage import save_file

app = FastAPI()

init_master_db()

@app.post("/upload")
async def upload_pdf(tenantName: str = Form(...), file: UploadFile = None):
    if not file:
        return JSONResponse(status_code=400, content={"error": "No file uploaded"})
    tenant = get_tenant(tenantName)
    if not tenant:
        db_name = create_tenant(tenantName)
    else:
        db_name = tenant.db_name

    # Save file
    contents = await file.read()
    filename = f"{tenantName}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = save_file(contents, filename)

    # Extract PDF text
    try:
        pdf_text = extract_pdf_text(file_path)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Could not extract PDF: {str(e)}"})

    # Summarize
    summary = summarize_text(pdf_text)

    # Store in tenant DB
    db = get_tenant_db(db_name)
    record = {
        "file_name": filename,
        "uploaded_at": datetime.utcnow(),
        "pdf_text": pdf_text,
        "summary": summary,
        "file_path": file_path
    }
    store_pdf_data(db, record)

    return {
        "tenant": tenantName,
        "file_name": filename,
        "summary": summary,
        "status": "Success"
    }