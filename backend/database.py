from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import json
import os
from models import UserRecord, get_password_hash

# Create async engine for SQLite
DATABASE_URL = "sqlite+aiosqlite:///./job_applications.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class ApplicationRecord(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    company = Column(String)
    position = Column(String)
    personal_info = Column(JSON, nullable=False)
    resume_data = Column(JSON)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)
    details = Column(JSON)

class PersonalInfoRecord(Base):
    __tablename__ = "personal_info"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    personal_info = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

async def init_db():
    """Initialize the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def save_application(app_id: str, application_data: dict):
    """Save application data to database"""
    async with async_session() as session:
        record = ApplicationRecord(
            id=app_id,
            url=application_data["url"],
            company=application_data.get("company"),
            position=application_data.get("position"),
            personal_info=application_data["personal_info"],
            resume_data=application_data.get("resume_data"),
            status=application_data.get("status", "pending"),
            created_at=datetime.utcnow()
        )
        session.add(record)
        await session.commit()

async def update_application_status(app_id: str, status: str, details: dict = None):
    """Update application status"""
    async with async_session() as session:
        record = await session.get(ApplicationRecord, app_id)
        if record:
            record.status = status
            if status == "completed":
                record.submitted_at = datetime.utcnow()
            if details:
                record.details = details
            await session.commit()

async def save_personal_info(user_id: str, personal_info: dict):
    """Save personal information"""
    async with async_session() as session:
        # Check if record exists
        existing = await session.get(PersonalInfoRecord, user_id)
        if existing:
            existing.personal_info = personal_info
            existing.updated_at = datetime.utcnow()
        else:
            record = PersonalInfoRecord(
                id=user_id,
                user_id=user_id,
                personal_info=personal_info
            )
            session.add(record)
        await session.commit()

async def get_personal_info(user_id: str):
    """Get personal information for a user"""
    async with async_session() as session:
        record = await session.get(PersonalInfoRecord, user_id)
        return record.personal_info if record else None

async def get_application(app_id: str):
    """Get application by ID"""
    async with async_session() as session:
        record = await session.get(ApplicationRecord, app_id)
        return record

async def get_user_applications(user_id: str):
    """Get all applications for a user"""
    async with async_session() as session:
        # This would need to be implemented based on how you track user applications
        # For now, return empty list
        return [] 

# User CRUD
async def create_user(username: str, password: str):
    async with async_session() as session:
        user = UserRecord(
            id=username,  # Use username as ID for simplicity
            username=username,
            password_hash=get_password_hash(password)
        )
        session.add(user)
        await session.commit()
        return user

async def get_user_by_username(username: str):
    async with async_session() as session:
        result = await session.execute(
            UserRecord.__table__.select().where(UserRecord.username == username)
        )
        user = result.fetchone()
        return user

async def update_user_personal_info_id(username: str, personal_info_id: str):
    async with async_session() as session:
        result = await session.execute(
            UserRecord.__table__.update().where(UserRecord.username == username).values(personal_info_id=personal_info_id)
        )
        await session.commit() 