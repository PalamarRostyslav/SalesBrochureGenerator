"""
Sales Brochure Generator - Main Entry Point

A tool for generating company brochures from website content
using AI-powered content analysis and generation.
"""

import click
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.generators.brochure_generator import BrochureGenerator, GenerationOptions
from src.configs.settings import validate_config, SUPPORTED_LANGUAGES, AI_PROVIDERS, get_available_providers
from src.utils.logger import get_logger
from src.ui.ui_launcher import launch_ui

logger = get_logger("main")

def get_api_key_for_provider(provider: str) -> Optional[str]:
    """Get the correct API key for the specified provider."""
    # Mapping provider names
    provider_mapping = {
        'openai': 'OpenAI',
        'claude': 'Claude',
        'anthropic': 'Claude'
    }
    
    provider_key = provider_mapping.get(provider.lower())
    if not provider_key:
        return None
        
    provider_info = AI_PROVIDERS.get(provider_key, {})
    return provider_info.get('api_key')

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Sales Brochure Generator - Create professional brochures from company websites"""
    try:
        validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
        
@cli.command()
@click.argument('company_name')
@click.argument('website_url')
@click.option('--language', '-l', default='en', 
    type=click.Choice(list(SUPPORTED_LANGUAGES.keys())),
    help='Language for the brochure')
@click.option('--stream/--no-stream', default=False,
    help='Enable streaming output')
@click.option('--few-shot/--no-few-shot', default=True,
    help='Use few-shot prompting for better results')
@click.option('--save-metadata/--no-metadata', default=True,
    help='Save generation metadata')
@click.option('--model', '-m', default=None,
    help='AI model to use (overrides default)')
@click.option('--provider', '-p', default='openai',
    type=click.Choice(['openai', 'claude']),
    help='AI provider to use')
def generate(company_name: str, website_url: str, language: str, 
            stream: bool, few_shot: bool, save_metadata: bool, model: Optional[str], provider: str):
    """Generate a brochure for a company from their website
    
    COMPANY_NAME: Name of the company
    WEBSITE_URL: Company website URL (must start with http:// or https://)
    """
    try:
        # Check if the provider is available
        available_providers = [p.lower() for p in get_available_providers()]
        if provider not in available_providers:
            logger.error(f"Provider '{provider}' not available. Configured providers: {available_providers}")
            logger.info("Please configure the required API key in your .env file:")
            sys.exit(1)
        
        # Get the correct API key for the provider
        api_key = get_api_key_for_provider(provider)
        if not api_key:
            logger.error(f"No API key found for provider '{provider}'")
            sys.exit(1)
        
        # Initialize generator with the correct API key
        generator = BrochureGenerator(api_key=api_key, model=model, provider=provider)
        
        # Set up options
        options = GenerationOptions(
            language=language,
            use_few_shot=few_shot,
            stream_output=stream,
            save_metadata=save_metadata
        )
        
        logger.info(f"Generating brochure for {company_name}")
        logger.info(f"Website: {website_url}")
        logger.info(f"Provider: {provider}")
        logger.info(f"Language: {SUPPORTED_LANGUAGES[language]}")
        
        if stream:
            # Stream generation with real-time output
            result = None
            for chunk in generator.stream_brochure_generation(company_name, website_url, options):
                if isinstance(chunk, str):
                    print(chunk, end='', flush=True)
                else:
                    result = chunk
            
            print("\n")  # New line after streaming
            
        else:
            # Regular generation
            result = generator.generate_brochure(company_name, website_url, options)
            logger.safe_print(result.content)
        
        # Display summary
        if result:
            logger.success("Brochure generation completed!")
            logger.info(f"File saved: {result.file_path}")
            logger.info(f"Word count: {result.word_count}")
            logger.info(f"Generation time: {result.generation_time:.2f} seconds")
        
    except Exception as e:
        logger.error("Brochure generation failed", e)
        sys.exit(1)

@cli.command()
@click.argument('company_name')
@click.argument('website_url')
@click.option('--provider', '-p', default=None,
    type=click.Choice(['openai', 'claude']),
    help='AI provider to use (auto-detects if not specified)')
def quick(company_name: str, website_url: str, provider: Optional[str]):
    """Quick brochure generation with default settings
    
    COMPANY_NAME: Name of the company
    WEBSITE_URL: Company website URL
    """
    try:
        # Auto-detect provider if not specified
        if not provider:
            available_providers = [p.lower() for p in get_available_providers()]
            if 'openai' in available_providers:
                provider = 'openai'
            elif 'claude' in available_providers:
                provider = 'claude'
            else:
                logger.error("No AI providers configured. Please set up API keys in .env file.")
                sys.exit(1)
        
        # Get API key for the provider
        api_key = get_api_key_for_provider(provider)
        if not api_key:
            logger.error(f"No API key found for provider '{provider}'")
            sys.exit(1)
        
        generator = BrochureGenerator(api_key=api_key, provider=provider)
        result = generator.generate_brochure(company_name, website_url)
        
        logger.safe_print(result.content)
        logger.success(f"Brochure saved to: {result.file_path}")
        
    except Exception as e:
        logger.error("Quick generation failed", e)
        sys.exit(1)

@cli.command()
def languages():
    """List supported languages for brochure generation"""
    logger.info("Supported languages:")
    for code, name in SUPPORTED_LANGUAGES.items():
        logger.console.print(f"  {code}: {name}")

@cli.command()
@click.option('--days', '-d', default=30, type=int,
    help='Delete files older than this many days')
def cleanup(days: int):
    """Clean up old generated files"""
    try:
        # Use any available provider for cleanup (doesn't matter which)
        available_providers = [p.lower() for p in get_available_providers()]
        if not available_providers:
            logger.error("No AI providers configured. Cannot initialize generator for cleanup.")
            sys.exit(1)
        
        provider = available_providers[0]
        api_key = get_api_key_for_provider(provider)
        generator = BrochureGenerator(api_key=api_key, provider=provider)
        
        deleted_count = generator.cleanup_old_files(days)
        logger.success(f"Cleaned up {deleted_count} files older than {days} days")
        
    except Exception as e:
        logger.error("Cleanup failed", e)
        sys.exit(1)

@cli.command()
@click.option('--provider', '-p', default=None,
    type=click.Choice(['openai', 'claude']),
    help='AI provider to test (tests all if not specified)')
def test(provider: Optional[str]):
    """Test API connection and configuration"""
    try:
        if provider:
            providers_to_test = [provider]
        else:
            providers_to_test = [p.lower() for p in get_available_providers()]
        
        if not providers_to_test:
            logger.error("No AI providers configured. Please set up API keys in .env file.")
            logger.info("Required environment variables:")
            logger.info("  OPENAI_API_KEY=sk-proj-your-openai-key")
            logger.info("  ANTHROPIC_API_KEY=sk-ant-your-anthropic-key")
            sys.exit(1)
        
        for test_provider in providers_to_test:
            logger.step(f"Testing {test_provider} configuration and API connection...")
            
            api_key = get_api_key_for_provider(test_provider)
            if not api_key:
                logger.error(f"No API key found for {test_provider}")
                continue
            
            generator = BrochureGenerator(api_key=api_key, provider=test_provider)
            model_info = generator.ai_model.get_model_info()
            
            logger.success(f"{test_provider.title()} configuration test passed!")
            logger.info(f"Provider: {model_info.get('provider', test_provider)}")
            logger.info(f"Model: {model_info['model']}")
            logger.info(f"API Key Valid: {model_info['api_key_valid']}")
            logger.info(f"Max Retries: {model_info['max_retries']}")
            logger.print_separator()
        
    except Exception as e:
        logger.error("Configuration test failed", e)
        sys.exit(1)

@cli.command()
@click.argument('company_name')
@click.argument('website_url')
@click.option('--output', '-o', type=click.Path(), 
    help='Custom output file path')
@click.option('--provider', '-p', default=None,
    type=click.Choice(['openai', 'claude']),
    help='AI provider to use (auto-detects if not specified)')
def export(company_name: str, website_url: str, output: Optional[str], provider: Optional[str]):
    """Generate and export brochure to a custom location.
    
    COMPANY_NAME: Name of the company
    WEBSITE_URL: Company website URL
    """
    try:
        # Auto-detect provider if not specified
        if not provider:
            available_providers = [p.lower() for p in get_available_providers()]
            if 'openai' in available_providers:
                provider = 'openai'
            elif 'claude' in available_providers:
                provider = 'claude'
            else:
                logger.error("No AI providers configured. Please set up API keys in .env file.")
                sys.exit(1)
        
        # Get API key for the provider
        api_key = get_api_key_for_provider(provider)
        if not api_key:
            logger.error(f"No API key found for provider '{provider}'")
            sys.exit(1)
        
        generator = BrochureGenerator(api_key=api_key, provider=provider)
        result = generator.generate_brochure(company_name, website_url)
        
        if output:
            # Save to custom location
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.content)
            
            logger.success(f"Brochure exported to: {output_path}")
        else:
            logger.safe_print(result.content)
            logger.success(f"Brochure saved to: {result.file_path}")
        
    except Exception as e:
        logger.error("Export failed", e)
        sys.exit(1)

@cli.command()
def ui():
    """Launch the Gradio web interface."""
    try:
        logger.info("Starting Gradio web interface...")
        launch_ui()
        
    except ImportError:
        logger.error("Gradio not installed. Install with: pip install gradio")
        sys.exit(1)
    except Exception as e:
        logger.error("Failed to launch UI", e)
        sys.exit(1)

def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Unexpected error occurred", e)
        sys.exit(1)

if __name__ == "__main__":
    main()