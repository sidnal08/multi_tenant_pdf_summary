from pydantic import BaseModel

class UploadResponse(BaseModel):
    tenant: str
    file_name: str
    summary: str
    status: str

class Tenant(BaseModel):
    tenant_name: str
    created_at: str
    db_name: str