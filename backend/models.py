from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
from passlib.context import CryptContext

# User model for authentication
class User(BaseModel):
    username: str
    password: str  # Plaintext for registration, hashed for storage
    personal_info_id: Optional[str] = None

# For DB: SQLAlchemy model
from sqlalchemy import Column, String
from database import Base

class UserRecord(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    personal_info_id = Column(String, nullable=True)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class Education(BaseModel):
    degree: str
    field: str
    institution: str
    graduation_year: str
    gpa: Optional[str] = None

class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: str  # Format: YYYY-MM
    end_date: Optional[str] = None  # Format: YYYY-MM, None for current
    description: str

class DiversityInfo(BaseModel):
    veteran_status: str = "No"  # Yes, No, Prefer not to say
    disability_status: str = "No"  # Yes, No, Prefer not to say
    race_ethnicity: str = "Prefer not to say"
    gender: str = "Prefer not to say"

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: Address
    education: List[Education] = []
    work_history: List[WorkExperience] = []
    skills: List[str] = []
    diversity_info: Optional[DiversityInfo] = None

class ResumeData(BaseModel):
    """Parsed resume data"""
    contact_info: Dict[str, str] = {}
    education: List[Dict[str, Any]] = []
    work_experience: List[Dict[str, Any]] = []
    skills: List[str] = []
    summary: Optional[str] = None
    certifications: List[str] = []
    languages: List[str] = []
    projects: List[Dict[str, Any]] = []

class JobApplication(BaseModel):
    """Job application data"""
    url: str
    company: Optional[str] = None
    position: Optional[str] = None
    personal_info: PersonalInfo
    resume_data: Optional[ResumeData] = None
    status: str = "pending"  # pending, processing, completed, error
    created_at: Optional[date] = None
    submitted_at: Optional[date] = None

class FormField(BaseModel):
    """Detected form field"""
    name: str
    type: str  # text, email, phone, select, textarea, file, etc.
    label: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    value: Optional[str] = None
    options: List[str] = []  # For select/radio fields

class ApplicationStatus(BaseModel):
    """Application processing status"""
    status: str  # starting, processing, completed, error
    message: str
    progress: int  # 0-100
    details: Optional[Dict[str, Any]] = None 