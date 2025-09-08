import os
import io
import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import psycopg2
from pymongo import MongoClient
from pdfminer.high_level import extract_text
import openai  # You can use open-source alternatives if desired

# ====== Configurations ======
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "masterdb")

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))

# ====== DB Connections ======
# Master DB: PostgreSQL
def get_postgres_conn():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    )

# Tenant DBs: MongoDB
def get_mongo_client():
    return MongoClient(MONGO_HOST, MONGO_PORT)

# ====== FastAPI App ======
app = FastAPI()

# ====== Data Models ======
class UploadResponse(BaseModel):
    tenantName: str
    summary: str
    fileName: str
    uploadTimestamp: str
    extractedTextLen: int
    message: Optional[str] = None

# ====== Helper Functions ======
def ensure_tenant_in_postgres(tenant_name: str):
    conn = get_postgres_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_name VARCHAR PRIMARY KEY,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """)
    cur.execute("SELECT tenant_name FROM tenants WHERE tenant_name = %s", (tenant_name,))
    exists = cur.fetchone()
    if not exists:
        cur.execute("INSERT INTO tenants (tenant_name) VALUES (%s)", (tenant_name,))
    conn.commit()
    cur.close()
    conn.close()

def ensure_mongo_tenant_db(tenant_name: str):
    client = get_mongo_client()
    db_list = client.list_database_names()
    if tenant_name not in db_list:
        # DB will be created when we insert a document
        pass
    return client[tenant_name]

def extract_pdf_text(pdf_file: UploadFile) -> str:
    pdf_content = pdf_file.file.read()
    pdf_stream = io.BytesIO(pdf_content)
    text = extract_text(pdf_stream)
    return text

def summarize_text(text: str) -> str:
    # Use a small LLM. Here, OpenAI's GPT-3.5-turbo is shown for illustration.
    # You can replace with a local/distilled model if needed.
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following PDF content."},
                {"role": "user", "content": text[:3000]},  # Limit input size
            ],
            max_tokens=200,
        )
        summary = response.choices[0].message['content']
        return summary
    except Exception as e:
        raise Exception(f"AI summarization failed: {str(e)}")

def store_pdf_data_mongo(tenant_db, file_name, extracted_text, summary, timestamp, file_bytes):
    # Store file in GridFS if needed. Here, just as a binary blob.
    record = {
        "file_name": file_name,
        "upload_timestamp": timestamp,
        "extracted_text": extracted_text,
        "summary": summary,
        "file_bytes": file_bytes,
    }
    tenant_db.pdfs.insert_one(record)

# ====== API Endpoint ======
@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    tenantName: str = Form(...),
    file: UploadFile = File(...)
):
    # Step 1: Ensure tenant in master DB
    try:
        ensure_tenant_in_postgres(tenantName)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Master DB error: {str(e)}")

    # Step 2: Ensure tenant DB exists (MongoDB)
    try:
        tenant_db = ensure_mongo_tenant_db(tenantName)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tenant DB error: {str(e)}")

    # Step 3: Extract PDF text
    try:
        extracted_text = extract_pdf_text(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction error: {str(e)}")

    # Step 4: Summarize
    try:
        summary = summarize_text(extracted_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI summarization error: {str(e)}")

    # Step 5: Store results
    upload_ts = datetime.datetime.utcnow().isoformat()
    file_bytes = await file.read()
    try:
        store_pdf_data_mongo(tenant_db, file.filename, extracted_text, summary, upload_ts, file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB store error: {str(e)}")

    return UploadResponse(
        tenantName=tenantName,
        summary=summary,
        fileName=file.filename,
        uploadTimestamp=upload_ts,
        extractedTextLen=len(extracted_text),
        message="PDF successfully processed and stored."
    )