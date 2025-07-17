"""Claude (Anthropic) model interface for the Sales Brochure Generator."""

from typing import List, Dict, Any, Optional
import anthropic

from .base_ai_model import BaseAIModel
from ..configs.settings import DEFAULT_CLAUDE_MODEL, AI_PROVIDERS

class ClaudeModel(BaseAIModel):
    """Claude (Anthropic) model implementation with shared base functionality"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        api_key_val = api_key if api_key is not None else AI_PROVIDERS.get('Claude', {}).get('api_key', '')
        model_val = model if model is not None else DEFAULT_CLAUDE_MODEL
        super().__init__(str(api_key_val), str(model_val), "Claude")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self._response_path = ["content", 0, "text"]
    
    def _validate_api_key(self) -> bool:
        """Validate the Anthropic API key format"""
        return bool(self.api_key and self.api_key.startswith('sk-ant-') and len(self.api_key) > 20)
        
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
    
    def _extract_text_from_stream_chunk(self, chunk: Any) -> Optional[str]:
        """Extract text from Claude streaming chunk"""
        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text') and chunk.delta.text:
            return chunk.delta.text
        
        return None