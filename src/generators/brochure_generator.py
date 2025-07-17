"""Main brochure generator orchestrating all components"""

from typing import Dict, List, Optional, Generator
from datetime import datetime
from dataclasses import dataclass

from ..models.openai_model import OpenAIModel
from ..models.claude_model import ClaudeModel
from ..scrapers.website_scraper import WebsiteScraper, WebsiteContent
from ..utils.file_handler import FileHandler
from ..utils.text_utils import truncate_content, format_company_name, extract_domain
from ..utils.logger import get_logger
from ..configs.settings import MAX_CONTENT_LENGTH, SUPPORTED_LANGUAGES

logger = get_logger(__name__)

@dataclass
class GenerationOptions:
    """Options for brochure generation"""
    language: str = 'en'
    use_few_shot: bool = True
    stream_output: bool = False
    save_metadata: bool = True
    max_content_length: int = MAX_CONTENT_LENGTH

@dataclass
class GenerationResult:
    """Result of brochure generation."""
    content: str
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None
    generation_time: Optional[float] = None
    word_count: Optional[int] = None
    
class BrochureGenerator:
    """Main brochure generator class"""
    
    def __init__(self, api_key: str = None, model: str = None, provider: str = "openai"):
        if provider.lower() == "openai":
            self.ai_model = OpenAIModel(api_key=api_key, model=model)
        elif provider.lower() == "claude" or provider.lower() == "anthropic":
            self.ai_model = ClaudeModel(api_key=api_key, model=model)
        else:
            self.ai_model = OpenAIModel(api_key=api_key, model=model)
            
        self.scraper = WebsiteScraper()
        self.file_handler = FileHandler()
        
        # Test connection on initialization
        if not self.ai_model.test_connection():
            raise ConnectionError(f"Failed to connect to {self.ai_model.provider_name} API")
        
        logger.success("BrochureGenerator initialized successfully")
        
    ## Generating brochure at once
    def generate_brochure(self, company_name: str, website_url: str, 
                options: GenerationOptions = None) -> GenerationResult:
        """Generate a complete brochure for a company."""
        if options is None:
            options = GenerationOptions()
        
        start_time = datetime.now()
        logger.print_header(f"Generating Brochure for {company_name}")
        
        try:
            self._validate_inputs(company_name, website_url, options)
            
            # Step 1: Scrape main website
            main_content = self._scrape_main_website(website_url)
            if not main_content:
                raise ValueError("Failed to scrape main website")
            
            # Step 2: Extract relevant links
            relevant_links = self._extract_relevant_links(website_url, main_content.links)
            
            # Step 3: Scrape additional pages
            additional_content = self._scrape_additional_pages(relevant_links)
            
            # Step 4: Combine all content
            combined_content = self._combine_website_content(main_content, additional_content)
            
            # Step 5: Generate brochure
            if options.stream_output:
                brochure_content = self._generate_streaming_brochure(
                    company_name, combined_content, options
                )
            else:
                brochure_content = self._generate_brochure_content(
                    company_name, combined_content, options
                )
            
            # Step 6: Save results
            file_path = self._save_brochure(brochure_content, company_name, options)
            
            # Step 7: Generate metadata
            metadata = self._generate_metadata(
                company_name, website_url, main_content, additional_content, options, start_time
            )
            
            if options.save_metadata:
                self.file_handler.save_metadata(metadata, company_name)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result = GenerationResult(
                content=brochure_content,
                file_path=str(file_path) if file_path else None,
                metadata=metadata,
                generation_time=generation_time,
                word_count=len(brochure_content.split())
            )
            
            logger.success(f"Brochure generation completed in {generation_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error("Brochure generation failed", e)
            raise
        finally:
            self.scraper.close()
            
    ## Generating brochure by streaming result to the output window
    def stream_brochure_generation(self, company_name: str, website_url: str,
                            options: GenerationOptions = None) -> Generator[str, None, GenerationResult]:
        """Stream brochure generation with real-time output"""
        if options is None:
            options = GenerationOptions(stream_output=True)
        else:
            options.stream_output = True
        
        start_time = datetime.now()
        logger.print_header(f"Streaming Brochure Generation for {company_name}")
        
        try:
            # Prepare content (same as regular generation)
            self._validate_inputs(company_name, website_url, options)
            main_content = self._scrape_main_website(website_url)
            relevant_links = self._extract_relevant_links(website_url, main_content.links)
            additional_content = self._scrape_additional_pages(relevant_links)
            combined_content = self._combine_website_content(main_content, additional_content)
            
            logger.step("Starting streaming generation...")
            logger.print_separator()
            
            # Stream the generation
            full_content = ""
            for chunk in self.ai_model.stream_brochure_generation(
                company_name, combined_content, options.language, options.use_few_shot
            ):
                full_content += chunk
                yield chunk
            
            logger.print_separator()
            
            # Save and return final result
            file_path = self._save_brochure(full_content, company_name, options)
            metadata = self._generate_metadata(
                company_name, website_url, main_content, additional_content, options, start_time
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            yield GenerationResult(
                content=full_content,
                file_path=str(file_path) if file_path else None,
                metadata=metadata,
                generation_time=generation_time,
                word_count=len(full_content.split())
            )
            
        except Exception as e:
            logger.error("Streaming brochure generation failed", e)
            raise
        finally:
            self.scraper.close()
            
    def _validate_inputs(self, company_name: str, website_url: str, options: GenerationOptions):
        """Validate input parameters"""
        if not company_name or not company_name.strip():
            raise ValueError("Company name is required")
        
        if not website_url or not website_url.startswith(('http://', 'https://')):
            raise ValueError("Valid website URL is required")
        
        if options.language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {options.language}")
    
    def _scrape_main_website(self, website_url: str) -> WebsiteContent:
        """Scrape the main website"""
        logger.step("Scraping main website")
        return self.scraper.scrape_website(website_url)
    
    def _extract_relevant_links(self, website_url: str, links: List[str]) -> List[Dict[str, str]]:
        """Extract relevant links using AI"""
        logger.step("Extracting relevant links with AI")
        
        # Filter links to same domain first
        base_domain = extract_domain(website_url)
        filtered_links = self.scraper.filter_relevant_links(links, base_domain)
        
        if not filtered_links:
            logger.warning("No relevant links found")
            return []
        
        # Use AI to select the most relevant links
        result = self.ai_model.extract_links(website_url, filtered_links[:20]) 
        return result.get('links', [])
    
    def _scrape_additional_pages(self, relevant_links: List[Dict[str, str]]) -> Dict[str, WebsiteContent]:
        """Scrape additional relevant pages."""
        if not relevant_links:
            return {}
        
        logger.step(f"Scraping {len(relevant_links)} additional pages")
        
        urls = [link['url'] for link in relevant_links]
        return self.scraper.scrape_multiple_websites(urls)
    
    def _combine_website_content(self, main_content: WebsiteContent, additional_content: Dict[str, WebsiteContent]) -> str:
        """Combine all scraped content into a single string"""
        logger.step("Combining website content")
        
        combined = "Landing page:\n"
        combined += main_content.get_formatted_content()
        
        for url, content in additional_content.items():
            page_type = self._determine_page_type(url, content)
            combined += f"\n\n{page_type}:\n"
            combined += content.get_formatted_content()
        
        # Truncate if too long
        if len(combined) > MAX_CONTENT_LENGTH:
            combined = truncate_content(combined, MAX_CONTENT_LENGTH)
            logger.warning(f"Content truncated to {MAX_CONTENT_LENGTH} characters")
        
        return combined
    
    def _determine_page_type(self, url: str, content: WebsiteContent) -> str:
        """Determine the type of page from URL and content"""
        url_lower = url.lower()
        
        if 'about' in url_lower:
            return "About page"
        elif 'career' in url_lower or 'job' in url_lower:
            return "Careers page"
        elif 'team' in url_lower:
            return "Team page"
        elif 'product' in url_lower or 'service' in url_lower:
            return "Products/Services page"
        elif 'contact' in url_lower:
            return "Contact page"
        else:
            return "Company page"
    
    def _generate_brochure_content(self, company_name: str, content: str, options: GenerationOptions) -> str:
        """Generate brochure content using AI"""
        logger.step("Generating brochure content")
        
        formatted_name = format_company_name(company_name)
        return self.ai_model.generate_brochure(
            formatted_name, content, options.language, options.use_few_shot
        )
    
    def _generate_streaming_brochure(self, company_name: str, content: str, options: GenerationOptions) -> str:
        """Generate brochure with streaming output"""
        logger.step("Starting streaming generation")
        logger.print_separator()
        
        formatted_name = format_company_name(company_name)
        full_content = ""
        
        for chunk in self.ai_model.stream_brochure_generation(
            formatted_name, content, options.language, options.use_few_shot
        ):
            full_content += chunk
            logger.safe_print(chunk)
        
        logger.print_separator()
        return full_content
    
    def _save_brochure(self, content: str, company_name: str, options: GenerationOptions) -> Optional[str]:
        """Save brochure to file"""
        try:
            return self.file_handler.save_brochure(
                content, company_name, options.language
            )
        except Exception as e:
            logger.error("Failed to save brochure", e)
            return None
    
    def _generate_metadata(self, company_name: str, website_url: str,
            main_content: WebsiteContent, 
            additional_content: Dict[str, WebsiteContent],
            options: GenerationOptions, start_time: datetime) -> Dict:
        """Generate metadata for the brochure generation"""
        return {
            'company_name': company_name,
            'website_url': website_url,
            'generation_time': datetime.now().isoformat(),
            'generation_duration_seconds': (datetime.now() - start_time).total_seconds(),
            'language': options.language,
            'model_used': self.ai_model.model,
            'main_page_scraped': True,
            'additional_pages_count': len(additional_content),
            'additional_pages_urls': list(additional_content.keys()),
            'total_content_length': len(self._combine_website_content(main_content, additional_content)),
            'options': {
                'use_few_shot': options.use_few_shot,
                'stream_output': options.stream_output,
                'max_content_length': options.max_content_length
            }
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages for brochure generation"""
        return SUPPORTED_LANGUAGES.copy()
    
    def cleanup_files(self, days_old: int = None) -> int:
        """Clean up old generated files"""
        return self.file_handler.cleanup_files(days_old)