import os
import json
import requests
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

class LLMService:
    def __init__(self):
        # Set OpenAI API key from environment variable only. Do NOT hardcode secrets here.
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
        self.use_openai = True
        
        # Free tier alternatives
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.use_huggingface = bool(self.huggingface_api_key)
        
        # Initialize OpenAI if available
        if self.use_openai:
            self.openai_client = OpenAI(api_key=self.api_key)
            print("✅ OpenAI API configured successfully")
        else:
            print("⚠️ No OpenAI API key found, using fallback responses")
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using available LLM service"""
        try:
            if self.use_openai:
                return await self._generate_openai_response(prompt, max_tokens)
            elif self.use_huggingface:
                return await self._generate_huggingface_response(prompt, max_tokens)
            else:
                return await self._generate_fallback_response(prompt)
        except Exception as e:
            print(f"LLM service error: {e}")
            return await self._generate_fallback_response(prompt)
    
    async def _generate_openai_response(self, prompt: str, max_tokens: int) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that helps with job applications. Provide professional, concise, and relevant responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {e}")
    
    async def _generate_huggingface_response(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Hugging Face API (free tier)"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/gpt2"
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            return response.json()[0]["generated_text"]
        except Exception as e:
            raise Exception(f"Hugging Face API error: {e}")
    
    async def _generate_fallback_response(self, prompt: str) -> str:
        """Fallback response when no LLM service is available"""
        # Simple rule-based responses for common job application scenarios
        prompt_lower = prompt.lower()
        
        if "why do you want to work" in prompt_lower:
            return "I am excited about this opportunity because it aligns with my career goals and allows me to contribute my skills and experience to a dynamic team. I am particularly drawn to the company's mission and the chance to work on innovative projects."
        
        elif "greatest strength" in prompt_lower:
            return "My greatest strength is my ability to quickly learn new technologies and adapt to changing requirements. I am also highly organized and detail-oriented, which helps me deliver high-quality work consistently."
        
        elif "greatest weakness" in prompt_lower:
            return "My greatest weakness is that I sometimes spend too much time perfecting details. However, I have learned to balance this with meeting deadlines and focusing on the most important aspects of a project."
        
        elif "salary expectation" in prompt_lower:
            return "I am open to discussing salary based on the responsibilities of the role and my experience level. I am primarily focused on finding the right opportunity to grow and contribute."
        
        elif "tell me about yourself" in prompt_lower:
            return "I am a passionate professional with experience in software development. I enjoy solving complex problems and working collaboratively with teams. I am always eager to learn new technologies and take on challenging projects."
        
        elif "experience with" in prompt_lower:
            return "I have hands-on experience with various technologies and frameworks. I am comfortable working with both frontend and backend development, and I enjoy learning new tools and methodologies."
        
        else:
            return "I am excited about this opportunity and believe my skills and experience make me a strong candidate for this position. I am eager to contribute to the team and help achieve the company's goals."
    
    async def generate_form_response(self, question: str, context: Dict[str, Any]) -> str:
        """Generate appropriate response for a specific form question"""
        prompt = f"""
        Generate a professional response for the following job application question:
        
        Question: {question}
        
        Context about the candidate:
        - Skills: {', '.join(context.get('skills', []))}
        - Experience: {context.get('experience', '')}
        - Education: {context.get('education', '')}
        
        Provide a concise, professional response that highlights relevant experience and skills. Keep it under 150 words.
        """
        
        return await self.generate_response(prompt, max_tokens=200)
    
    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description to extract key requirements"""
        prompt = f"""
        Analyze the following job description and extract key information:
        
        {job_description}
        
        Return a JSON object with:
        {{
            "required_skills": ["skill1", "skill2"],
            "preferred_skills": ["skill1", "skill2"],
            "experience_level": "entry/mid/senior",
            "job_type": "full-time/part-time/contract",
            "key_responsibilities": ["responsibility1", "responsibility2"]
        }}
        
        Only return the JSON object, no additional text.
        """
        
        try:
            response = await self.generate_response(prompt)
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback analysis
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_level": "mid",
            "job_type": "full-time",
            "key_responsibilities": []
        }
    
    async def generate_cover_letter(self, job_description: str, resume_data: Dict[str, Any]) -> str:
        """Generate a cover letter based on job description and resume"""
        prompt = f"""
        Generate a professional cover letter for the following job:
        
        Job Description:
        {job_description}
        
        Candidate Information:
        - Skills: {', '.join(resume_data.get('skills', []))}
        - Experience: {resume_data.get('summary', '')}
        - Education: {resume_data.get('education', [])}
        
        Write a compelling cover letter that highlights relevant experience and explains why the candidate is a good fit for this position. Keep it professional and under 300 words.
        """
        
        return await self.generate_response(prompt, max_tokens=500)
    
    async def parse_resume_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """Use AI to parse and structure resume data"""
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
            "summary": "Professional summary if available"
        }}
        
        Resume text:
        {resume_text}
        
        Only return the JSON object, no additional text.
        """
        
        try:
            response = await self.generate_response(prompt, max_tokens=1000)
            json_str = self._extract_json_from_response(response)
            return json.loads(json_str)
        except Exception as e:
            print(f"AI parsing error: {e}")
            return await self._basic_parse(resume_text)
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON string from AI response"""
        # Find JSON object in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            return response[json_start:json_end]
        return "{}"
    
    async def _basic_parse(self, text: str) -> Dict[str, Any]:
        """Basic parsing when AI parsing fails"""
        lines = text.split('\n')
        skills = []
        education = []
        work_experience = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract skills (common patterns)
            if any(skill in line.lower() for skill in ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker']):
                skills.extend([s.strip() for s in line.split(',')])
            
            # Extract education
            if any(word in line.lower() for word in ['university', 'college', 'bachelor', 'master', 'phd', 'degree']):
                education.append(line)
            
            # Extract work experience
            if any(word in line.lower() for word in ['company', 'inc', 'corp', 'ltd', 'llc']):
                work_experience.append(line)
        
        return {
            "contact_info": {
                "name": "",
                "email": "",
                "phone": "",
                "address": ""
            },
            "education": education,
            "work_experience": work_experience,
            "skills": list(set(skills)),
            "summary": ""
        } 