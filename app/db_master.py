from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from app.config import POSTGRES_URL

Base = declarative_base()

class TenantMaster(Base):
    __tablename__ = "tenants"
    tenant_name = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    db_name = Column(String, unique=True)

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)

def init_master_db():
    Base.metadata.create_all(engine)

def get_tenant(tenant_name: str):
    session = SessionLocal()
    tenant = session.query(TenantMaster).filter_by(tenant_name=tenant_name).first()
    session.close()
    return tenant

def create_tenant(tenant_name: str):
    session = SessionLocal()
    db_name = f"tenant_{tenant_name.replace(' ', '_').lower()}"
    tenant = TenantMaster(tenant_name=tenant_name, db_name=db_name)
    session.add(tenant)
    session.commit()
    session.close()
    return db_name