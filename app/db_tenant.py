from pymongo import MongoClient
from app.config import MONGODB_URL

def get_tenant_db(db_name: str):
    client = MongoClient(MONGODB_URL)
    return client[db_name]

def store_pdf_data(db, data: dict):
    db.pdf_summaries.insert_one(data)