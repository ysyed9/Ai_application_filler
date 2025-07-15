from playwright.async_api import async_playwright, Page, Browser
from typing import List, Dict, Any, Optional
from models import PersonalInfo, ResumeData, FormField
from llm_service import LLMService
import asyncio
import re
import time

class JobApplicationFiller:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.llm_service = LLMService()
        self.form_fields: List[FormField] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start_browser(self):
        """Start the browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for production
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        
        # Set user agent to avoid detection
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def close(self):
        """Close the browser"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def navigate_to_application(self, url: str):
        """Navigate to the job application page"""
        try:
            await self.page.goto(url, wait_until='networkidle')
            await asyncio.sleep(2)  # Wait for page to load
        except Exception as e:
            raise Exception(f"Failed to navigate to {url}: {str(e)}")
    
    async def detect_form_fields(self) -> List[FormField]:
        """Detect form fields on the page"""
        try:
            # Common form field selectors
            field_selectors = [
                'input[type="text"]',
                'input[type="email"]',
                'input[type="tel"]',
                'input[type="number"]',
                'input[type="date"]',
                'textarea',
                'select',
                'input[type="file"]',
                'input[type="radio"]',
                'input[type="checkbox"]'
            ]
            
            detected_fields = []
            
            for selector in field_selectors:
                elements = await self.page.query_selector_all(selector)
                
                for element in elements:
                    field = await self._analyze_field(element, selector)
                    if field:
                        detected_fields.append(field)
            
            self.form_fields = detected_fields
            return detected_fields
            
        except Exception as e:
            raise Exception(f"Error detecting form fields: {str(e)}")
    
    async def _analyze_field(self, element, selector: str) -> Optional[FormField]:
        """Analyze a form field element"""
        try:
            # Get field attributes
            name = await element.get_attribute('name') or await element.get_attribute('id') or ''
            field_type = await element.get_attribute('type') or 'text'
            placeholder = await element.get_attribute('placeholder') or ''
            required = await element.get_attribute('required') is not None
            
            # Get label text
            label_text = await self._get_field_label(element)
            
            # Determine field type
            if 'email' in name.lower() or 'email' in placeholder.lower():
                field_type = 'email'
            elif 'phone' in name.lower() or 'tel' in name.lower():
                field_type = 'phone'
            elif 'date' in name.lower() or field_type == 'date':
                field_type = 'date'
            elif field_type == 'file':
                field_type = 'file'
            elif field_type in ['radio', 'checkbox']:
                field_type = 'select'
            
            return FormField(
                name=name,
                type=field_type,
                label=label_text,
                placeholder=placeholder,
                required=required
            )
            
        except Exception as e:
            print(f"Error analyzing field: {e}")
            return None
    
    async def _get_field_label(self, element) -> str:
        """Get the label text for a form field"""
        try:
            # Try to find associated label
            field_id = await element.get_attribute('id')
            if field_id:
                label = await self.page.query_selector(f'label[for="{field_id}"]')
                if label:
                    return await label.text_content() or ''
            
            # Try to find nearby label
            parent = await element.query_selector('..')
            if parent:
                label = await parent.query_selector('label')
                if label:
                    return await label.text_content() or ''
            
            return ''
        except:
            return ''
    
    async def fill_personal_info(self, personal_info: PersonalInfo):
        """Fill personal information fields"""
        try:
            # Map personal info to form fields
            field_mappings = {
                'first_name': ['first', 'fname', 'given'],
                'last_name': ['last', 'lname', 'surname', 'family'],
                'email': ['email', 'e-mail', 'mail'],
                'phone': ['phone', 'telephone', 'mobile', 'cell'],
                'address': ['address', 'street', 'addr'],
                'city': ['city', 'town'],
                'state': ['state', 'province', 'region'],
                'zip_code': ['zip', 'postal', 'zipcode']
            }
            
            for field in self.form_fields:
                if field.type in ['text', 'email', 'tel']:
                    value = await self._get_field_value(field, personal_info, field_mappings)
                    if value:
                        await self._fill_field(field, value)
            
        except Exception as e:
            raise Exception(f"Error filling personal info: {str(e)}")
    
    async def _get_field_value(self, field: FormField, personal_info: PersonalInfo, mappings: Dict[str, List[str]]) -> Optional[str]:
        """Get the appropriate value for a field based on personal info"""
        field_name = field.name.lower()
        field_label = (field.label or '').lower()
        
        # Check direct mappings
        for info_key, field_patterns in mappings.items():
            for pattern in field_patterns:
                if pattern in field_name or pattern in field_label:
                    if info_key == 'first_name':
                        return personal_info.first_name
                    elif info_key == 'last_name':
                        return personal_info.last_name
                    elif info_key == 'email':
                        return personal_info.email
                    elif info_key == 'phone':
                        return personal_info.phone
                    elif info_key == 'address':
                        return personal_info.address.street
                    elif info_key == 'city':
                        return personal_info.address.city
                    elif info_key == 'state':
                        return personal_info.address.state
                    elif info_key == 'zip_code':
                        return personal_info.address.zip_code
        
        return None
    
    async def _fill_field(self, field: FormField, value: str):
        """Fill a form field with a value"""
        try:
            selector = f'[name="{field.name}"]' if field.name else f'[placeholder="{field.placeholder}"]'
            
            if field.type == 'file':
                # Handle file upload
                await self.page.set_input_files(selector, value)
            else:
                # Fill text field
                await self.page.fill(selector, value)
                await asyncio.sleep(0.5)  # Small delay
                
        except Exception as e:
            print(f"Error filling field {field.name}: {e}")
    
    async def fill_work_history(self, work_history: List[Dict[str, Any]]):
        """Fill work history fields"""
        try:
            for i, job in enumerate(work_history):
                # Look for work history fields
                company_fields = await self.page.query_selector_all(f'[name*="company"][name*="{i+1}"]')
                position_fields = await self.page.query_selector_all(f'[name*="position"][name*="{i+1}"]')
                date_fields = await self.page.query_selector_all(f'[name*="date"][name*="{i+1}"]')
                
                if company_fields:
                    await company_fields[0].fill(job['company'])
                if position_fields:
                    await position_fields[0].fill(job['position'])
                if date_fields:
                    await date_fields[0].fill(job['start_date'])
                    
        except Exception as e:
            print(f"Error filling work history: {e}")
    
    async def fill_diversity_info(self, diversity_info: Dict[str, str]):
        """Fill diversity and military questions"""
        try:
            # Common diversity question patterns
            diversity_patterns = {
                'veteran': ['veteran', 'military', 'armed forces'],
                'disability': ['disability', 'disabled', 'accommodation'],
                'race': ['race', 'ethnicity', 'diversity'],
                'gender': ['gender', 'sex']
            }
            
            for field in self.form_fields:
                field_name = field.name.lower()
                field_label = (field.label or '').lower()
                
                for category, patterns in diversity_patterns.items():
                    for pattern in patterns:
                        if pattern in field_name or pattern in field_label:
                            value = diversity_info.get(category, 'Prefer not to say')
                            await self._fill_field(field, value)
                            
        except Exception as e:
            print(f"Error filling diversity info: {e}")
    
    async def fill_open_ended_questions(self, resume_data: ResumeData):
        """Fill open-ended questions using LLM"""
        try:
            # Find textarea fields (likely open-ended questions)
            textareas = await self.page.query_selector_all('textarea')
            
            for textarea in textareas:
                # Get the question text
                question_text = await self._get_question_text(textarea)
                
                if question_text:
                    # Generate response using LLM
                    context = {
                        'skills': resume_data.skills,
                        'experience': resume_data.summary or '',
                        'education': str(resume_data.education)
                    }
                    
                    response = await self.llm_service.generate_form_response(question_text, context)
                    await textarea.fill(response)
                    
        except Exception as e:
            print(f"Error filling open-ended questions: {e}")
    
    async def _get_question_text(self, element) -> str:
        """Get the question text for a textarea"""
        try:
            # Look for nearby labels or headings
            parent = await element.query_selector('..')
            if parent:
                # Look for label
                label = await parent.query_selector('label')
                if label:
                    return await label.text_content() or ''
                
                # Look for heading
                heading = await parent.query_selector('h1, h2, h3, h4, h5, h6')
                if heading:
                    return await heading.text_content() or ''
            
            return ''
        except:
            return ''
    
    async def submit_application(self) -> Dict[str, Any]:
        """Submit the application form"""
        try:
            # Look for submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")',
                'button:has-text("Send")',
                '[class*="submit"]',
                '[class*="apply"]'
            ]
            
            submit_button = None
            for selector in submit_selectors:
                submit_button = await self.page.query_selector(selector)
                if submit_button:
                    break
            
            if submit_button:
                await submit_button.click()
                await asyncio.sleep(3)  # Wait for submission
                
                # Check if submission was successful
                success_indicators = [
                    'Thank you',
                    'Application submitted',
                    'Success',
                    'Submitted successfully'
                ]
                
                page_content = await self.page.content()
                is_successful = any(indicator.lower() in page_content.lower() for indicator in success_indicators)
                
                return {
                    "submitted": True,
                    "successful": is_successful,
                    "message": "Application submitted successfully" if is_successful else "Application submitted (status unclear)"
                }
            else:
                return {
                    "submitted": False,
                    "successful": False,
                    "message": "Submit button not found"
                }
                
        except Exception as e:
            return {
                "submitted": False,
                "successful": False,
                "message": f"Error submitting application: {str(e)}"
            } 