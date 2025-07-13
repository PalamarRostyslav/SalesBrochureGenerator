"""Website scraping utilities for the Sales Brochure Generator."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import time

from ..configs.settings import REQUEST_TIMEOUT, MAX_RETRIES
from ..utils.text_utils import clean_text, normalize_url, extract_domain
from ..utils.logger import get_logger
from utils import logger

@dataclass
class WebsiteContent:
    """Data class for website content."""
    url: str
    title: str
    text: str
    links: List[str]
    metadata: Dict[str, str]
    
    def get_formatted_content(self) -> str:
        """Get formatted content for brochure generation."""
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
class WebsiteScraper:
    """Website scraper with error handling and retry logic"""
    def __init__(self, timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _make_request_with_retry(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempting to fetch {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")
                    return None
                time.sleep(2 ** attempt)
        
        return None
    
    def scrape_website(self, url: str) -> Optional[WebsiteContent]:
        """Scrape a single website and extract content"""
        logger.step(f"Scraping website: {url}")
        
        response = self._make_request_with_retry(url)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = "No title found"
            if soup.title and soup.title.string:
                title = clean_text(soup.title.string)
            
            if soup.body:
                # Remove irrelevant elements
                for tag in soup.body(["script", "style", "img", "input", "nav", "footer", "header"]):
                    tag.decompose()
                
                text = soup.body.get_text(separator="\n", strip=True)
                text = clean_text(text)
            else:
                text = ""
            
            links = self._extract_links(soup, url)
            
            content = WebsiteContent(
                url=url,
                title=title,
                text=text,
                links=links
            )
            
            logger.info(f"Successfully scraped {url} - {len(text)} characters, {len(links)} links")
            return content
            
        except Exception as e:
            logger.error(f"Failed to parse content from {url}", e)
            return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize links from HTML"""
        links = []
        seen_links: Set[str] = set()
        
        for link_tag in soup.find_all('a', href=True):
            href = link_tag.get('href')
            normalized = normalize_url(base_url, href)
            
            if normalized and normalized not in seen_links:
                # Filter out unwanted links
                if self._is_relevant_link(normalized, link_tag):
                    links.append(normalized)
                    seen_links.add(normalized)
        
        return links
    
    def _is_relevant_link(self, url: str, tag) -> bool:
        """Check if a link is relevant for brochure generation"""
        # Skip certain file types
        skip_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.jpg', '.png', '.gif'}
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip certain URL patterns
        skip_patterns = ['mailto:', 'tel:', 'javascript:', '#', '/search', '/login', '/register']
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        # Get link text for additional filtering
        link_text = tag.get_text(strip=True).lower()
        
        # Skip links with irrelevant text
        irrelevant_text = {'privacy', 'terms', 'cookie', 'legal', 'disclaimer', 'support', 'help'}
        if any(word in link_text for word in irrelevant_text):
            return False
        
        return True
    
    def get_website_summary(self, url: str) -> Dict[str, any]:
        """Get a summary of website scraping results"""
        content = self.scrape_website(url)
        
        if not content:
            return {
                'success': False,
                'error': 'Failed to scrape website'
            }
        
        return {
            'success': True,
            'url': content.url,
            'title': content.title,
            'content_length': len(content.text),
            'links_count': len(content.links),
            'domain': extract_domain(content.url)
        }
        
    def filter_relevant_links(self, links: List[str], base_domain: str) -> List[str]:
        """Filter links to keep only relevant ones for the same domain"""
        relevant_links = []
        
        relevant_keywords = {
            'about', 'company', 'team', 'careers', 'jobs', 'culture', 
            'mission', 'vision', 'values', 'history', 'leadership',
            'services', 'products', 'solutions', 'portfolio', 'work'
        }
        
        for link in links:
            try:
                parsed = urlparse(link)
                
                # Keep only same domain links
                if base_domain not in parsed.netloc:
                    continue
                
                # Check if URL path contains relevant keywords
                path_lower = parsed.path.lower()
                if any(keyword in path_lower for keyword in relevant_keywords):
                    relevant_links.append(link)
                    
            except Exception:
                continue
        
        return relevant_links
    
    def close(self):
        """Close the session."""
        self.session.close()