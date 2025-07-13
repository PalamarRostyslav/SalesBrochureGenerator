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
from src.configs.settings import validate_config, SUPPORTED_LANGUAGES
from src.utils.logger import get_logger

logger = get_logger("main")

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
    help='OpenAI model to use (overrides default)')

def generate(company_name: str, website_url: str, language: str, 
            stream: bool, few_shot: bool, save_metadata: bool, model: Optional[str]):
    """Generate a brochure for a company from their website
    
    COMPANY_NAME: Name of the company
    WEBSITE_URL: Company website URL (must start with http:// or https://)
    """
    try:
        # Initialize generator
        generator = BrochureGenerator(model=model)
        
        # Set up options
        options = GenerationOptions(
            language=language,
            use_few_shot=few_shot,
            stream_output=stream,
            save_metadata=save_metadata
        )
        
        logger.info(f"Generating brochure for {company_name}")
        logger.info(f"Website: {website_url}")
        logger.info(f"Language: {SUPPORTED_LANGUAGES[language]}")
        
        # Stream generation
        if stream:
            result = None
            for chunk in generator.stream_brochure_generation(company_name, website_url, options):
                if isinstance(chunk, str):
                    print(chunk, end='', flush=True)
                else:
                    result = chunk
            
            print("\n")
            
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
def quick(company_name: str, website_url: str):
    """Quick brochure generation with default settings.
    
    COMPANY_NAME: Name of the company
    WEBSITE_URL: Company website URL
    """
    try:
        generator = BrochureGenerator()
        result = generator.generate_brochure(company_name, website_url)
        
        logger.safe_print(result.content)
        logger.success(f"Brochure saved to: {result.file_path}")
        
    except Exception as e:
        logger.error("Quick generation failed", e)
        sys.exit(1)

@cli.command()
def languages():
    """List supported languages for brochure generation."""
    logger.info("Supported languages:")
    for code, name in SUPPORTED_LANGUAGES.items():
        logger.console.print(f"  {code}: {name}")

@cli.command()
@click.option('--days', '-d', default=30, type=int,
    help='Delete files older than this many days')
def cleanup(days: int):
    """Clean up old generated files."""
    try:
        generator = BrochureGenerator()
        deleted_count = generator.cleanup_old_files(days)
        logger.success(f"Cleaned up {deleted_count} files older than {days} days")
        
    except Exception as e:
        logger.error("Cleanup failed", e)
        sys.exit(1)

@cli.command()
def test():
    """Test the OpenAI API connection and configuration."""
    try:
        logger.step("Testing configuration and API connection...")
        
        generator = BrochureGenerator()
        model_info = generator.ai_model.get_model_info()
        
        logger.success("Configuration test passed!")
        logger.info(f"Model: {model_info['model']}")
        logger.info(f"API Key Valid: {model_info['api_key_valid']}")
        logger.info(f"Max Retries: {model_info['max_retries']}")
        
    except Exception as e:
        logger.error("Configuration test failed", e)
        sys.exit(1)

@cli.command()
@click.argument('company_name')
@click.argument('website_url')
@click.option('--output', '-o', type=click.Path(), 
    help='Custom output file path')
def export(company_name: str, website_url: str, output: Optional[str]):
    """Generate and export brochure to a custom location.
    
    COMPANY_NAME: Name of the company
    WEBSITE_URL: Company website URL
    """
    try:
        generator = BrochureGenerator()
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