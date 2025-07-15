import PyPDF2
import docx
import re
from typing import Dict, List, Any
from models import ResumeData
from llm_service import LLMService
import os

class ResumeParser:
    def __init__(self):
        self.llm_service = LLMService()
    
    async def parse_resume(self, file_path: str) -> ResumeData:
        """Parse resume file and extract structured data"""
        try:
            # Extract text from file
            text = await self._extract_text(file_path)
            
            # Use AI to parse and structure the data
            structured_data = await self.llm_service.parse_resume_with_ai(text)
            
            return ResumeData(**structured_data)
            
        except Exception as e:
            raise Exception(f"Error parsing resume: {str(e)}")
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or Word document"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return await self._extract_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return await self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading Word document: {str(e)}")
    
    async def _parse_with_llm(self, text: str) -> Dict[str, Any]:
        """Use LLM to parse and structure resume data"""
        prompt = f"""
        Parse the following resume text and extract structured information. Return the data as a JSON object with the following structure:
        
        {{
            "contact_info": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "phone number",
                "address": "full address"
            }},
            "education": [
                {{
                    "degree": "Degree Name",
                    "field": "Field of Study",
                    "institution": "University Name",
                    "graduation_year": "YYYY",
                    "gpa": "GPA if available"
                }}
            ],
            "work_experience": [
                {{
                    "company": "Company Name",
                    "position": "Job Title",
                    "start_date": "YYYY-MM",
                    "end_date": "YYYY-MM or 'Present'",
                    "description": "Job description and achievements"
                }}
            ],
            "skills": ["skill1", "skill2", "skill3"],
            "summary": "Professional summary if available",
            "certifications": ["cert1", "cert2"],
            "languages": ["language1", "language2"],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Project description",
                    "technologies": ["tech1", "tech2"]
                }}
            ]
        }}
        
        Resume text:
        {text}
        
        Extract all available information and return only the JSON object.
        """
        
        try:
            response = await self.llm_service.generate_response(prompt)
            # Clean the response to extract JSON
            json_str = self._extract_json_from_response(response)
            import json
            return json.loads(json_str)
        except Exception as e:
            # Fallback to basic parsing if LLM fails
            return await self._basic_parse(text)
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON in the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            return response[json_start:json_end]
        else:
            raise ValueError("No JSON found in response")
    
    async def _basic_parse(self, text: str) -> Dict[str, Any]:
        """Basic parsing fallback when LLM is not available"""
        # Simple regex-based parsing
        lines = text.split('\n')
        
        contact_info = {}
        education = []
        work_experience = []
        skills = []
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        # Extract skills (common programming languages and tools)
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Angular', 'Vue',
            'Node.js', 'Express', 'Django', 'Flask', 'SQL', 'MongoDB', 'PostgreSQL',
            'Git', 'Docker', 'AWS', 'Azure', 'Linux', 'Windows', 'MacOS',
            'HTML', 'CSS', 'TypeScript', 'PHP', 'Ruby', 'Go', 'Rust'
        ]
        
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                skills.append(skill)
        
        return {
            "contact_info": contact_info,
            "education": education,
            "work_experience": work_experience,
            "skills": skills,
            "summary": None,
            "certifications": [],
            "languages": [],
            "projects": []
        }

# Global instance
resume_parser = ResumeParser()

async def parse_resume(file_path: str) -> ResumeData:
    """Global function to parse resume"""
    return await resume_parser.parse_resume(file_path) 