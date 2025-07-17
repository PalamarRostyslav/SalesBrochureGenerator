"""Text processing utilities for the Sales Brochure Generator"""

import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause encoding issues
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    text = text.strip()
    
    return text

def truncate_content(content: str, max_length: int) -> str:
    """Truncate content to specified maximum length"""
    if len(content) <= max_length:
        return content
    
    # Try to truncate at the last complete sentence
    truncated = content[:max_length]
    last_sentence_end = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_sentence_end > max_length * 0.8:
        return content[:last_sentence_end + 1]
    else:
        return content[:max_length] + "..."

def normalize_url(base_url: str, link: str) -> Optional[str]:
    """Normalize and validate URLs"""
    if not link:
        return None
    
    # Skip non-HTTP links
    if link.startswith(('mailto:', 'tel:', 'javascript:', '#')):
        return None
    
    if not link.startswith(('http://', 'https://')):
        normalized = urljoin(base_url, link)
    else:
        normalized = link
    
    # Validate URL structure
    try:
        parsed = urlparse(normalized)
        if not parsed.netloc:
            return None
        return normalized
    except Exception:
        return None

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return url

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem compatibility"""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_.')
    
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized

def format_company_name(name: str) -> str:
    """Format company name for consistent usage"""
    if not name:
        return "Unknown Company"
    
    cleaned = clean_text(name)
    suffixes = ['inc', 'corp', 'ltd', 'llc', 'co']
    words = cleaned.split()
    
    formatted_words = []
    for word in words:
        lower_word = word.lower().rstrip('.,')
        if lower_word in suffixes:
            formatted_words.append(word.upper())
        else:
            formatted_words.append(word.title())
    
    return ' '.join(formatted_words)

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract relevant keywords from text content"""
    if not text:
        return []

    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in keywords[:max_keywords]]

def validate_content_quality(content: str) -> dict:
    """Validate content quality and provide metrics"""
    if not content:
        return {
            'is_valid': False,
            'word_count': 0,
            'char_count': 0,
            'issues': ['Content is empty']
        }
    
    issues = []
    word_count = len(content.split())
    char_count = len(content)
    
    if word_count < 10:
        issues.append('Content too short (less than 10 words)')
    
    if char_count > 50000:
        issues.append('Content too long (over 50,000 characters)')
    
    try:
        content.encode('utf-8')
    except UnicodeEncodeError:
        issues.append('Content contains encoding issues')
    
    return {
        'is_valid': len(issues) == 0,
        'word_count': word_count,
        'char_count': char_count,
        'issues': issues
    }

class ContentCombiner:
    @staticmethod
    def combine(main_content, additional_content, max_length):
        """Combine all scraped content into a single string, truncating if too long"""
        combined = "Landing page:\n"
        combined += main_content.get_formatted_content()
        for url, content in additional_content.items():
            page_type = ContentCombiner._determine_page_type(url, content)
            combined += f"\n\n{page_type}:\n"
            combined += content.get_formatted_content()
        if len(combined) > max_length:
            from .text_utils import truncate_content
            combined = truncate_content(combined, max_length)
        return combined

    @staticmethod
    def _determine_page_type(url, content):
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

class LinkExtractor:
    @staticmethod
    def extract(ai_model, scraper, website_url, links):
        """Filter links to same domain and use AI to select the most relevant"""
        from .text_utils import extract_domain
        base_domain = extract_domain(website_url)
        filtered_links = scraper.filter_relevant_links(links, base_domain)
        if not filtered_links:
            return []
        result = ai_model.extract_links(website_url, filtered_links[:20])
        return result.get('links', [])