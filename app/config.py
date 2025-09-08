import os

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@postgres:5432/masterdb")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/data/uploads")