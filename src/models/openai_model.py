"""OpenAI model interface for the Sales Brochure Generator"""

import json
from typing import List, Dict, Any, Generator, Optional
from openai import OpenAI
import time

from ..configs.settings import OPENAI_API_KEY, DEFAULT_MODEL, MAX_RETRIES
from ..configs.prompts import (
    LINK_EXTRACTION_SYSTEM_PROMPT, 
    BROCHURE_GENERATION_SYSTEM_PROMPT,
    LINK_EXTRACTION_EXAMPLES,
    BROCHURE_GENERATION_EXAMPLES,
    get_brochure_generation_prompt
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIModel:
    """OpenAI model interface with retry logic and error handling"""
    
    def __init__(self, api_key: str = None, model:str = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or DEFAULT_MODEL
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = MAX_RETRIES
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        logger.info(f"Initialized OpenAI model: {self.model}")
        
    def _validate_api_key(self) -> bool:
        """Validate the OpenAI API key format."""
        return (self.api_key and 
                self.api_key.startswith('sk-'))
        
    def _create_completion_with_retry(self, messages: List[Dict[str, str]], 
                                    stream: bool = False, response_format: Dict[str, str] = None) -> Any:
        for attempt in range(self.max_retries):
            try:
                kwargs = {
                    'model': self.model,
                    'messages': messages,
                    'stream': stream
                }
                
                if response_format:
                    kwargs['response_format'] = response_format
                    
                response = self.client.chat.completions.create(**kwargs)
                return response;
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.max_retries} attempts failed", e)
                    raise
                time.sleep(2 ** attempt)
                
        raise Exception("Max retries exceeded")
    
    def extract_links(self, website_url: str, links: List[str], use_few_shot: bool = True) -> Dict[str, Any]:
        """Extract relevant links using OpenAI with optional few-shot prompting"""
        logger.step("Extracting relevant links using AI")
        
        user_prompt = f"""Here is the list of links on the website of {website_url} - please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. Do not include Terms of Service, Privacy, email links.
                                    Links (some might be relative links):
                                    {chr(10).join(links)}"""
        
        messages = [{"role": "system", "content": LINK_EXTRACTION_SYSTEM_PROMPT}]
        if use_few_shot:
            messages.extend(LINK_EXTRACTION_EXAMPLES)
            
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self._create_completion_with_retry(messages=messages, response_format={"type":"json_object"})
            
            result = response.choices[0].message.content
            parsed_result = json.loads(result)
            
            logger.info(f"Extracted {len(parsed_result.get('links', []))} relevant links")
            return parsed_result
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON response from OpenAI", e)
            raise
        except Exception as e:
            logger.error("Failed to extract links", e)
            raise
        
    def generate_brochure(self, company_name: str, content:str, language: str = 'en', use_few_shot: bool = True)->str:
        """Generate brochure content using OpenAI with optional few-shot prompting"""
        logger.step(f"Generating brochure for {company_name} in {language}")
        
        user_prompt = get_brochure_generation_prompt(company_name, content, language)
        messages = [{"role":"system", "content":BROCHURE_GENERATION_SYSTEM_PROMPT}]
        
        if use_few_shot:
            messages.extend(BROCHURE_GENERATION_EXAMPLES)
            
        messages.append({"role":"user", "content": user_prompt})
        
        try:
            response = self._create_completion_with_retry(messages)
            result = response.choices[0].message.content
            
            logger.success("Brochure generated successfully")
            return result
        
        except Exception as e:
            logger.error("Failed to generate brochure", e)
            raise
        
    def stream_brochure_generation(self, company_name: str, content: str, 
            language: str = 'en', use_few_shot: bool = True) -> Generator[str, None, None]:
        """Generate brochure content with streaming response"""
        logger.step(f"Streaming brochure generation for {company_name}")
            
        user_prompt = get_brochure_generation_prompt(company_name, content, language)
        
        messages = [{"role": "system", "content": BROCHURE_GENERATION_SYSTEM_PROMPT}]
        
        if use_few_shot:
            messages.extend(BROCHURE_GENERATION_EXAMPLES)
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            stream = self._create_completion_with_retry(messages=messages, stream=True)
            
            for chunk in stream:
                if (hasattr(chunk, 'choices') and 
                    len(chunk.choices) > 0 and 
                    hasattr(chunk.choices[0], 'delta') and 
                    chunk.choices[0].delta and
                    hasattr(chunk.choices[0].delta, 'content') and 
                    chunk.choices[0].delta.content is not None):
                    
                    yield chunk.choices[0].delta.content
            
            logger.success("Streaming brochure generation completed")
            
        except Exception as e:
            logger.error("Failed to stream brochure generation", e)
            raise
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model': self.model,
            'api_key_valid': self._validate_api_key(),
            'max_retries': self.max_retries
        }
    
    def test_connection(self) -> bool:
        """Test the OpenAI API connection"""
        logger.step("Testing OpenAI API connection")
        
        try:
            test_messages = [
                {"role": "user", "content": "Hello, this is a connection test. IMPORTANT !!! Please respond with only one word - 'OK'."}
            ]
            
            response = self._create_completion_with_retry(messages=test_messages)
            result = response.choices[0].message.content.strip()
            
            if "OK" in result.upper():
                logger.success("OpenAI API connection test successful")
                return True
            else:
                logger.warning(f"Unexpected response from API: {result}")
                return False
                
        except Exception as e:
            logger.error("OpenAI API connection test failed", e)
            return False