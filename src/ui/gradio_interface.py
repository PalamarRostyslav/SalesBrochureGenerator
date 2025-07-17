"""Gradio web interface for the Sales Brochure Generator."""

import gradio as gr
from typing import Optional, Tuple, Generator
import traceback

from ..generators.brochure_generator import BrochureGenerator, GenerationOptions
from ..models.openai_model import OpenAIModel
from ..models.claude_model import ClaudeModel
from ..configs.settings import (SUPPORTED_LANGUAGES, AI_PROVIDERS, get_available_providers, get_default_provider)
from ..utils.logger import get_logger

logger = get_logger("gradio_ui")

class GradioInterface:
    """Gradio web interface for brochure generation"""
    
    def __init__(self):
        self.current_generator = None
        
        self.api_keys = {
            provider: info.get('api_key') 
            for provider, info in AI_PROVIDERS.items() 
            if info.get('api_key')
        }
        
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get cached API key for the specified provider"""
        return self.api_keys.get(provider)
        
    def _create_ai_model(self, provider: str, model: str, api_key: str = None):
        """Create AI model instance based on provider selection."""
        # Use environment API key if none provided
        if not api_key:
            api_key = self._get_api_key(provider)
        
        if provider == "OpenAI":
            return OpenAIModel(api_key=api_key, model=model)
        elif provider == "Claude":
            return ClaudeModel(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
    def _validate_inputs(self, company_name: str, website_url: str, provider: str,
                        model: str) -> Tuple[bool, str]:
        
        if not company_name or not company_name.strip():
            return False, "❌ Company name is required"
        
        if not website_url or not website_url.startswith(('http://', 'https://')):
            return False, "❌ Valid website URL is required (must start with http:// or https://)"
        
        if not provider:
            return False, "❌ AI provider must be selected"
            
        if not model:
            return False, "❌ Model must be selected"
            
        # Check if API key is available for the provider
        api_key = self._get_api_key(provider)
        if not api_key:
            return False, f"❌ {provider} API key not configured in environment"
        
        return True, "✅ All inputs valid"
    
    def update_models_dropdown(self, provider: str) -> gr.Dropdown:
        """Update model dropdown based on selected provider"""
        
        if provider in AI_PROVIDERS:
            models = AI_PROVIDERS[provider]['models']
            default_model = AI_PROVIDERS[provider]['default_model']
            return gr.Dropdown(
                choices=models,
                value=default_model,
                label=f"{provider} Models",
                interactive=True
            )
        return gr.Dropdown(choices=[], value=None, label="Models", interactive=True)
    
    def test_api_connection(self, provider: str, model: str) -> str:
        """Test API connection with configured credentials."""
        try:
            if not provider:
                return "❌ Please select an AI provider"
            
            if not model:
                return "❌ Please select a model"
            
            # Get API key from environment
            api_key = self._get_api_key(provider)
            
            if not api_key:
                return f"❌ {provider} API key not configured in environment variables"
            
            ai_model = self._create_ai_model(provider, model, api_key)
            
            if ai_model.test_connection():
                return f"✅ {provider} API connection successful!"
            else:
                return f"❌ {provider} API connection failed"
                
        except Exception as e:
            logger.error(f"API connection test failed for {provider}", e)
            return f"❌ Connection failed: {str(e)}"
        
    def generate_brochure(self, company_name: str, website_url: str, provider: str,
            model: str, language: str, 
            use_few_shot: bool, stream_output: bool) -> Generator[str, None, None]:
        try:
            is_valid, message = self._validate_inputs(company_name, website_url, provider, model)
            if not is_valid:
                yield message
                return
            
            api_key = self._get_api_key(provider)
            if not api_key:
                yield f"❌ {provider} API key not configured in environment"
                return
            
            # Create AI Model
            ai_model = self._create_ai_model(provider, model, api_key)
            
            generator = BrochureGenerator()
            generator.ai_model = ai_model
            
            # Setting up options
            options = GenerationOptions(
                language=language,
                use_few_shot=use_few_shot,
                stream_output=stream_output,
                save_metadata=True
            )
            
            yield f"🚀 Starting brochure generation for **{company_name}**...\n\n"
            yield f"**Provider:** {provider} ({model})\n"
            yield f"**Language:** {SUPPORTED_LANGUAGES[language]}\n"
            yield f"**Website:** {website_url}\n\n"
            yield "---\n\n"
        
            if stream_output:
                # Stream generation
                full_content = ""
                for chunk in generator.stream_brochure_generation(company_name, website_url, options):
                    if isinstance(chunk, str):
                        full_content += chunk
                        yield full_content
                    else:
                        # Final result with metadata
                        result = chunk
                        yield full_content + f"\n\n---\n\n✅ **Generation completed!**\n"
                        yield full_content + f"\n📁 **File saved:** {result.file_path}\n"
                        yield full_content + f"\n📊 **Word count:** {result.word_count}\n"
                        yield full_content + f"\n⏱️ **Generation time:** {result.generation_time:.2f} seconds"
            else:
                # Regular generation
                yield "⏳ Generating brochure (this may take a moment)...\n\n"
                result = generator.generate_brochure(company_name, website_url, options)
                
                final_output = result.content
                final_output += f"\n\n---\n\n✅ **Generation completed!**\n"
                final_output += f"\n📁 **File saved:** {result.file_path}\n"
                final_output += f"\n📊 **Word count:** {result.word_count}\n"
                final_output += f"\n⏱️ **Generation time:** {result.generation_time:.2f} seconds"
                
                yield final_output
            
        except Exception as e:
            error_msg = f"❌ **Error during generation:** {str(e)}\n\n"
            error_msg += f"**Traceback:**\n```\n{traceback.format_exc()}\n```"
            logger.error("Brochure generation failed in UI", e)
            yield error_msg
            
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface"""
        
        # Get dynamic defaults based on available API keys
        available_providers = get_available_providers()
        default_provider = get_default_provider()
        
        default_provider_info = AI_PROVIDERS.get(default_provider, AI_PROVIDERS["OpenAI"])
        default_models = default_provider_info["models"]
        default_model = default_provider_info["default_model"]
        
        with gr.Blocks(
            title="Sales Brochure Generator",
            theme=gr.themes.Soft(),
            css="""
                .gradio-container {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                .header {
                    text-align: center;
                    padding: 20px;
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
            """
        ) as interface:
            
            # Header
            gr.HTML("""
                <div class="header">
                    <h1>🚀 Sales Brochure Generator</h1>
                    <p>Generate professional company brochures using AI-powered content analysis</p>
                </div>
            """)
            
            # Show warning if no API keys configured
            if not get_available_providers():
                gr.HTML("""
                    <div class="warning">
                        ⚠️ <strong>No API keys detected!</strong> Please configure at least one API key in your .env file:
                        <br>• OPENAI_API_KEY=sk-proj-your-key-here
                        <br>• ANTHROPIC_API_KEY=sk-ant-your-key-here
                    </div>
                """)
            
            with gr.Row():
                # Left Column - Inputs
                with gr.Column(scale=1):
                    gr.Markdown("## 📝 Company Information")
                    
                    company_name = gr.Textbox(
                        label="Company Name",
                        placeholder="e.g., Anthropic",
                        info="Enter the name of the company"
                    )
                    
                    website_url = gr.Textbox(
                        label="Website URL", 
                        placeholder="e.g., https://anthropic.com",
                        info="Company website URL (must start with http:// or https://)"
                    )
                    
                    gr.Markdown("## 🤖 AI Configuration")
                    
                    provider = gr.Dropdown(
                        choices=available_providers,
                        value=default_provider,
                        label="AI Provider",
                        info="Select the AI provider to use"
                    )
                    
                    model = gr.Dropdown(
                        choices=default_models,
                        value=default_model,
                        label="Model",
                        info="Select the AI model"
                    )
                    
                    test_btn = gr.Button("🔍 Test API Connection", variant="secondary")
                    test_result = gr.Textbox(label="Connection Status", interactive=False)
                    
                    gr.Markdown("## ⚙️ Generation Options")
                    
                    language = gr.Dropdown(
                        choices=[(f"{name} ({code})", code) for code, name in SUPPORTED_LANGUAGES.items()],
                        value="en",
                        label="Language",
                        info="Language for the generated brochure"
                    )
                    
                    use_few_shot = gr.Checkbox(
                        value=True,
                        label="Use Few-Shot Prompting",
                        info="Enable example-based prompting for better results"
                    )
                    
                    stream_output = gr.Checkbox(
                        value=True,
                        label="Stream Output",
                        info="Show real-time generation progress"
                    )
                    
                    generate_btn = gr.Button("🎯 Generate Brochure", variant="primary", size="lg")
                
                # Right Column - Output
                with gr.Column(scale=2):
                    gr.Markdown("## 📄 Generated Brochure")
                    
                    output = gr.Markdown(
                        value="Click 'Generate Brochure' to start...",
                        label="Brochure Output"
                    )
            
            # Event handlers
            provider.change(
                fn=self.update_models_dropdown,
                inputs=[provider],
                outputs=[model]
            )
            
            test_btn.click(
                fn=self.test_api_connection,
                inputs=[provider, model],
                outputs=[test_result]
            )
            
            generate_btn.click(
                fn=self.generate_brochure,
                inputs=[company_name, website_url, provider, model, 
                    language, use_few_shot, stream_output],
                outputs=[output]
            )
            
            # Example inputs
            gr.Examples(
                examples=[
                    ["Anthropic", "https://anthropic.com", "OpenAI", "gpt-4o-mini", "en", True, True],
                    ["OpenAI", "https://openai.com", "Claude", "claude-3-haiku-20240307", "en", True, True],
                    ["Tesla", "https://tesla.com", "OpenAI", "gpt-4o-mini", "es", True, True],
                ],
                inputs=[company_name, website_url, provider, model, language, use_few_shot, stream_output],
            )
            
            # Footer
            gr.Markdown("""
                ---
                **💡 Tips:**
                - Test your API connection before generating
                - Use streaming for real-time progress
                - Try different languages for international markets
                - Few-shot prompting usually gives better results
                
                **🔐 Security:** API keys are loaded from environment variables and never exposed in the interface.
                
                **📋 Setup:** Configure your API keys in the .env file:
                ```
                OPENAI_API_KEY=sk-proj-your-openai-key
                ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
                ```
            """)
        
        return interface
    
    def launch(self, share: bool = False, debug: bool = False, server_port: int = 7860):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        
        logger.info(f"Launching Gradio interface on port {server_port}")
        
        interface.launch(
            share=share,
            debug=debug,
            server_port=server_port,
            show_error=True,
            inbrowser=True
        )