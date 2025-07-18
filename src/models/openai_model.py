"""OpenAI model interface for the Sales Brochure Generator"""

from typing import List, Dict, Any, Optional
from openai import OpenAI

from .base_ai_model import BaseAIModel
from ..configs.settings import DEFAULT_MODEL, AI_PROVIDERS

class OpenAIModel(BaseAIModel):
    """OpenAI model interface with retry logic and error handling"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        api_key_val = api_key if api_key is not None else AI_PROVIDERS.get('OpenAI', {}).get('api_key', '')
        model_val = model if model is not None else DEFAULT_MODEL
        super().__init__(str(api_key_val), str(model_val), "OpenAI")
        self.client = OpenAI(api_key=self.api_key)
        self._response_path = ["choices", 0, "message", "content"]
        
    def _validate_api_key(self) -> bool:
        """Validate the OpenAI API key format"""
        return bool(self.api_key and self.api_key.startswith('sk-'))
        
    def _create_completion_with_retry(self, messages: List[Dict[str, str]], 
                                    stream: bool = False, system_prompt: str = None, 
                                    response_format_json: bool = False) -> Any:
        """Create OpenAI completion with retry logic"""
        def make_request():
            final_messages = messages.copy()
            if system_prompt:
                final_messages.insert(0, {"role": "system", "content": system_prompt})
                
            kwargs = {
                'model': self.model,
                'messages': final_messages,
                'stream': stream
            }
            
            if response_format_json:
                kwargs['response_format'] = {"type": "json_object"}
            
            return self.client.chat.completions.create(**kwargs)
        
        return self._retry_with_backoff(make_request)
    
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