"""Claude (Anthropic) model interface for the Sales Brochure Generator."""

from typing import List, Dict, Any, Optional
import anthropic

from .base_ai_model import BaseAIModel
from ..configs.settings import ANTHROPIC_API_KEY, DEFAULT_CLAUDE_MODEL

class ClaudeModel(BaseAIModel):
    """Claude (Anthropic) model implementation with shared base functionality"""
    
    def __init__(self, api_key: str = None, model: str = None):
        api_key = api_key or ANTHROPIC_API_KEY
        model = model or DEFAULT_CLAUDE_MODEL
        super().__init__(api_key, model, "Claude")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def _validate_api_key(self) -> bool:
        """Validate the Anthropic API key format"""
        
        return (self.api_key and 
                self.api_key.startswith('sk-ant-') and 
                len(self.api_key) > 20)
        
    def _create_completion_with_retry(self, messages: List[Dict[str, str]], 
                                    stream: bool = False, system_prompt: str = None,
                                    response_format_json: bool = False) -> Any:
        """Create Claude completion with retry logic"""
        def make_request():
            kwargs = {
                'model': self.model,
                'max_tokens': 4000,
                'messages': messages,
                'stream': stream
            }
            
            if system_prompt:
                kwargs['system'] = system_prompt
            
            return self.client.messages.create(**kwargs)
        
        return self._retry_with_backoff(make_request)
    
    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text content from Claude response"""
        return response.content[0].text
    
    def _extract_text_from_stream_chunk(self, chunk: Any) -> Optional[str]:
        """Extract text from Claude streaming chunk"""
        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text') and chunk.delta.text:
            return chunk.delta.text
        
        return None