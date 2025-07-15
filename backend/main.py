from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import json
import asyncio
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import User, verify_password, get_password_hash
from database import create_user, get_user_by_username, update_user_personal_info_id, get_personal_info, save_personal_info

# Import our modules
from models import PersonalInfo, JobApplication, ResumeData
from database import init_db, get_db
from resume_parser import parse_resume
from form_filler import JobApplicationFiller
from llm_service import LLMService

app = FastAPI(title="AI Job Application Auto-Filler", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    await init_db()

# Pydantic models for API
class JobApplicationRequest(BaseModel):
    url: str
    personal_info: PersonalInfo
    resume_data: Optional[ResumeData] = None

class ApplicationStatus(BaseModel):
    status: str
    message: str
    progress: int
    details: Optional[Dict[str, Any]] = None

# Global storage for application status
application_status = {}

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(lambda: None)):
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
    token = await oauth2_scheme()
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
async def root():
    return {"message": "AI Job Application Auto-Filler API"}

@app.post("/api/parse-resume", response_model=ResumeData)
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """Parse uploaded resume and extract information"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse resume
        resume_data = await parse_resume(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return resume_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@app.post("/api/start-application")
async def start_application(request: JobApplicationRequest):
    """Start the job application auto-fill process"""
    try:
        # Generate unique ID for this application
        app_id = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize status
        application_status[app_id] = {
            "status": "starting",
            "message": "Initializing application...",
            "progress": 0,
            "details": {}
        }
        
        # Start async process
        asyncio.create_task(process_application(app_id, request))
        
        return {"application_id": app_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting application: {str(e)}")

@app.get("/api/application-status/{app_id}")
async def get_application_status(app_id: str):
    """Get the status of a job application process"""
    if app_id not in application_status:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application_status[app_id]

@app.get("/api/sample-personal-info")
async def get_sample_personal_info():
    """Get sample personal information structure"""
    return {
        "personal_info": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-123-4567",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            },
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "University of Technology",
                    "graduation_year": "2020",
                    "gpa": "3.8"
                }
            ],
            "work_history": [
                {
                    "company": "Tech Corp",
                    "position": "Software Engineer",
                    "start_date": "2020-06",
                    "end_date": "2023-12",
                    "description": "Developed web applications using React and Python"
                }
            ],
            "skills": ["Python", "React", "JavaScript", "SQL", "Git"],
            "diversity_info": {
                "veteran_status": "No",
                "disability_status": "No",
                "race_ethnicity": "Prefer not to say",
                "gender": "Prefer not to say"
            }
        }
    }

# Register endpoint
@app.post("/api/register")
async def register(user: User):
    existing = await get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    await create_user(user.username, user.password)
    return {"msg": "User registered successfully"}

# Login endpoint
@app.post("/api/login", response_model=Token)
async def login(user: User):
    db_user = await get_user_by_username(user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Get personal info for logged-in user
@app.get("/api/me/personal-info")
async def get_my_personal_info(current_user=Depends(get_current_user)):
    info = await get_personal_info(current_user.username)
    return info or {}

# Update personal info for logged-in user
@app.post("/api/me/personal-info")
async def update_my_personal_info(personal_info: dict, current_user=Depends(get_current_user)):
    await save_personal_info(current_user.username, personal_info)
    return {"msg": "Personal info updated"}

async def process_application(app_id: str, request: JobApplicationRequest):
    """Process the job application asynchronously"""
    try:
        # Update status
        application_status[app_id]["status"] = "processing"
        application_status[app_id]["message"] = "Analyzing job application form..."
        application_status[app_id]["progress"] = 10
        
        # Initialize form filler
        filler = JobApplicationFiller()
        
        # Update status
        application_status[app_id]["message"] = "Navigating to application page..."
        application_status[app_id]["progress"] = 20
        
        # Navigate to the application page
        await filler.navigate_to_application(request.url)
        
        # Update status
        application_status[app_id]["message"] = "Detecting form fields..."
        application_status[app_id]["progress"] = 40
        
        # Detect form fields
        form_fields = await filler.detect_form_fields()
        
        # Update status
        application_status[app_id]["message"] = "Filling personal information..."
        application_status[app_id]["progress"] = 60
        
        # Fill personal information
        await filler.fill_personal_info(request.personal_info)
        
        # Update status
        application_status[app_id]["message"] = "Filling work history..."
        application_status[app_id]["progress"] = 70
        
        # Fill work history
        if request.personal_info.work_history:
            await filler.fill_work_history(request.personal_info.work_history)
        
        # Update status
        application_status[app_id]["message"] = "Handling diversity questions..."
        application_status[app_id]["progress"] = 80
        
        # Handle diversity/military questions
        if request.personal_info.diversity_info:
            await filler.fill_diversity_info(request.personal_info.diversity_info)
        
        # Update status
        application_status[app_id]["message"] = "Generating open-ended responses..."
        application_status[app_id]["progress"] = 90
        
        # Generate responses for open-ended questions
        if request.resume_data:
            await filler.fill_open_ended_questions(request.resume_data)
        
        # Update status
        application_status[app_id]["message"] = "Submitting application..."
        application_status[app_id]["progress"] = 95
        
        # Submit the application
        submission_result = await filler.submit_application()
        
        # Update final status
        application_status[app_id]["status"] = "completed"
        application_status[app_id]["message"] = "Application submitted successfully!"
        application_status[app_id]["progress"] = 100
        application_status[app_id]["details"] = submission_result
        
        # Clean up
        await filler.close()
        
    except Exception as e:
        application_status[app_id]["status"] = "error"
        application_status[app_id]["message"] = f"Error: {str(e)}"
        application_status[app_id]["progress"] = 0

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 