"""Input validation utilities for the Sales Brochure Generator."""

from ..configs.settings import SUPPORTED_LANGUAGES

class InputValidator:
    @staticmethod
    def validate_all(company_name, website_url, provider, model, language, api_key, raise_on_error=False):
        if not company_name or not company_name.strip():
            msg = "Company name is required"
            if raise_on_error:
                raise ValueError(msg)
            return False, msg
        if not website_url or not website_url.startswith(('http://', 'https://')):
            msg = "Valid website URL is required (must start with http:// or https://)"
            if raise_on_error:
                raise ValueError(msg)
            return False, msg
        if not provider:
            msg = "AI provider must be selected"
            if raise_on_error:
                raise ValueError(msg)
            return False, msg
        if not model:
            msg = "Model must be selected"
            if raise_on_error:
                raise ValueError(msg)
            return False, msg
        if not api_key:
            msg = f"{provider} API key not configured in environment"
            if raise_on_error:
                raise ValueError(msg)
            return False, msg
        if language and language not in SUPPORTED_LANGUAGES:
            msg = f"Unsupported language: {language}"
            if raise_on_error:
                raise ValueError(msg)
            return False, msg
        
        return True, "All inputs valid" 