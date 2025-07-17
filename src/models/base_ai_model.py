"""Base AI model interface with shared functionality."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional
import time

from ..configs.settings import MAX_RETRIES
from ..configs.prompts import (
    LINK_EXTRACTION_EXAMPLES,
    LINK_EXTRACTION_SYSTEM_PROMPT,
    BROCHURE_GENERATION_EXAMPLES,
    BROCHURE_GENERATION_SYSTEM_PROMPT,
    get_brochure_generation_prompt
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BaseAIModel(ABC):
    """Abstract base class for AI models with shared functionality"""
    
    def __init__(self, api_key: str, model: str, provider_name: str):
        self.api_key = api_key
        self.model = model
        self.provider_name = provider_name
        self.max_retries = MAX_RETRIES
        
        if not self.api_key:
            raise ValueError(f"{provider_name} API key is required")
        
        logger.info(f"Initialized {provider_name} model: {self.model}")
    
    @abstractmethod
    def _validate_api_key(self) -> bool:
        """Validate the API key format (provider-specific)"""
        pass
    
    @abstractmethod
    def _create_completion_with_retry(self, messages: List[Dict[str, str]], 
                                    stream: bool = False, system_prompt: str = None, **kwargs) -> Any:
        """Create completion with retry logic (provider-specific)"""
        pass
    
    def _get_response_text(self, response: Any, path: list) -> str:
        """Extract text from a nested response object using a path list."""
        for key in path:
            if isinstance(response, dict):
                response = response[key]
            elif isinstance(key, int):
                response = response[key]
            else:
                response = getattr(response, key, None)
            if response is None:
                raise ValueError(f"Invalid response path: {path}")
        return response

    def _extract_text_from_response(self, response: Any) -> str:
        """Default implementation, expects subclass to set self._response_path."""
        if hasattr(self, "_response_path"):
            return self._get_response_text(response, self._response_path)
        raise NotImplementedError("Subclasses must define _response_path or override this method.")
    
    @abstractmethod
    def _extract_text_from_stream_chunk(self, chunk: Any) -> Optional[str]:
        """Extract text from streaming chunk (provider-specific)"""
        pass
    
    def _retry_with_backoff(self, operation_func, *args, **kwargs):
        """Generic retry logic"""
        for attempt in range(self.max_retries):
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.max_retries} attempts failed", e)
                    raise
                time.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    def _prepare_messages_with_examples(self, user_prompt: str, examples: List[Dict], 
                    use_few_shot: bool = True) -> List[Dict[str, str]]:
        """Prepare messages with optional few-shot examples"""
        messages = []
        
        if use_few_shot:
            for example in examples:
                if example["role"] != "system":
                    messages.append(example)
        
        messages.append({"role": "user", "content": user_prompt})
        return messages
    
    def extract_links(self, website_url: str, links: List[str], use_few_shot: bool = True) -> Dict[str, Any]:
        """Extract relevant links using AI with optional few-shot prompting"""
        logger.step(f"Extracting relevant links using {self.provider_name}")
        
        user_prompt = f"""Here is the list of links on the website of {website_url} - please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. Do not include Terms of Service, Privacy, email links.
                    Links (some might be relative links):
                    {chr(10).join(links)}"""
        
        messages = self._prepare_messages_with_examples(
            user_prompt, LINK_EXTRACTION_EXAMPLES, use_few_shot
        )
        
        try:
            import json
            response = self._create_completion_with_retry(
                messages=messages, 
                system_prompt=LINK_EXTRACTION_SYSTEM_PROMPT,
                response_format_json=True
            )
            result = self._extract_text_from_response(response)
            parsed_result = json.loads(result)
            
            logger.info(f"Extracted {len(parsed_result.get('links', []))} relevant links")
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {self.provider_name}", e)
            raise
        except Exception as e:
            logger.error("Failed to extract links", e)
            raise
    
    def generate_brochure(self, company_name: str, content: str, language: str = 'en', 
                use_few_shot: bool = True) -> str:
        """Generate brochure content using AI with optional few-shot prompting"""
        logger.step(f"Generating brochure for {company_name} in {language} using {self.provider_name}")
        
        user_prompt = get_brochure_generation_prompt(company_name, content, language)
        messages = self._prepare_messages_with_examples(
            user_prompt, BROCHURE_GENERATION_EXAMPLES, use_few_shot
        )
        
        try:
            response = self._create_completion_with_retry(
                messages=messages,
                system_prompt=BROCHURE_GENERATION_SYSTEM_PROMPT
            )
            result = self._extract_text_from_response(response)
            
            logger.success(f"Brochure generated successfully with {self.provider_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate brochure with {self.provider_name}", e)
            raise
    
    def stream_brochure_generation(self, company_name: str, content: str, 
                            language: str = 'en', use_few_shot: bool = True) -> Generator[str, None, None]:
        """Generate brochure content with streaming response"""
        logger.step(f"Streaming brochure generation for {company_name} using {self.provider_name}")
    
        user_prompt = get_brochure_generation_prompt(company_name, content, language)
        messages = self._prepare_messages_with_examples(
            user_prompt, BROCHURE_GENERATION_EXAMPLES, use_few_shot
        )
        
        try:
            stream = self._create_completion_with_retry(
                messages=messages, 
                stream=True,
                system_prompt=BROCHURE_GENERATION_SYSTEM_PROMPT
            )
            
            for chunk in stream:
                text = self._extract_text_from_stream_chunk(chunk)
                if text:
                    yield text
            
            logger.success(f"Streaming brochure generation completed with {self.provider_name}")
            
        except Exception as e:
            logger.error(f"Failed to stream brochure generation with {self.provider_name}", e)
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'model': self.model,
            'provider': self.provider_name.lower(),
            'api_key_valid': self._validate_api_key(),
            'max_retries': self.max_retries
        }
    
    def test_connection(self) -> bool:
        """Test the API connection."""
        logger.step(f"Testing {self.provider_name} API connection")
        
        try:
            test_messages = [
                {"role": "user", "content": "Hello, this is a connection test. Please respond with 'OK'."}
            ]
            
            response = self._create_completion_with_retry(messages=test_messages)
            result = self._extract_text_from_response(response).strip()
            
            if "OK" in result.upper():
                logger.success(f"{self.provider_name} API connection test successful")
                return True
            else:
                logger.warning(f"Unexpected response from {self.provider_name} API: {result}")
                return False
                
        except Exception as e:
            logger.error(f"{self.provider_name} API connection test failed", e)
            return False