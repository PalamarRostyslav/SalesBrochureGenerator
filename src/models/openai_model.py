"""OpenAI model interface for the Sales Brochure Generator"""

from typing import List, Dict, Any, Optional
from openai import OpenAI

from .base_ai_model import BaseAIModel
from ..configs.settings import OPENAI_API_KEY, DEFAULT_MODEL
from ..utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIModel(BaseAIModel):
    """OpenAI model interface with retry logic and error handling"""
    
    def __init__(self, api_key: str = None, model: str = None):
        api_key = api_key or OPENAI_API_KEY
        model = model or DEFAULT_MODEL
        super().__init__(api_key, model, "OpenAI")
        
        self.client = OpenAI(api_key=self.api_key)
        
    def _validate_api_key(self) -> bool:
        """Validate the OpenAI API key format"""
        return (self.api_key and 
                self.api_key.startswith('sk-'))
        
    def _create_completion_with_retry(self, messages: List[Dict[str, str]], 
                                    stream: bool = False, json_mode: bool = False) -> Any:
        """Create OpenAI completion with retry logic"""
        def make_request():
            kwargs = {
                'model': self.model,
                'messages': messages,
                'stream': stream
            }
            
            if json_mode:
                kwargs['response_format'] = {"type": "json_object"}
            
            return self.client.chat.completions.create(**kwargs)
        
        return self._retry_with_backoff(make_request)
    
    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text content from OpenAI response"""
        return response.choices[0].message.content
    
    def _extract_text_from_stream_chunk(self, chunk: Any) -> Optional[str]:
        """Extract text from OpenAI streaming chunk"""
        if (hasattr(chunk, 'choices') and 
            len(chunk.choices) > 0 and 
            hasattr(chunk.choices[0], 'delta') and 
            chunk.choices[0].delta and
            hasattr(chunk.choices[0].delta, 'content') and 
            chunk.choices[0].delta.content is not None):
            
            return chunk.choices[0].delta.content
        return None