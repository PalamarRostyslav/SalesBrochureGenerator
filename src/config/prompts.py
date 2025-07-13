"""Prompt templates for the Sales Brochure Generator"""

# System prompts
LINK_EXTRACTION_SYSTEM_PROMPT = """You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.

You should respond in JSON as in this example:
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}"""

BROCHURE_GENERATION_SYSTEM_PROMPT = """You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.
Include details of company culture, customers and careers/jobs if you have the information."""

LINK_EXTRACTION_EXAMPLES = [
    {
        "role": "user",
        "content": """Here is the list of links on the website of https://example-company.com - please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. Do not include Terms of Service, Privacy, email links.
Links (some might be relative links):
/about
/team
/careers
/contact
/privacy-policy
/terms
/products
mailto:info@example.com"""
    },
    {
        "role": "assistant", 
        "content": """{
    "links": [
        {"type": "about page", "url": "https://example-company.com/about"},
        {"type": "team page", "url": "https://example-company.com/team"},
        {"type": "careers page", "url": "https://example-company.com/careers"},
        {"type": "products page", "url": "https://example-company.com/products"}
    ]
}"""
    }
]

BROCHURE_GENERATION_EXAMPLES = [
    {
        "role": "user",
        "content": """You are looking at a company called: TechCorp
Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.

Landing page:
Webpage Title: TechCorp - Innovative Software Solutions
Webpage Contents: 
TechCorp is a leading software development company specializing in enterprise solutions.
We help businesses transform their operations through cutting-edge technology.
Founded in 2015, we have served over 500 clients worldwide.

About page:
Webpage Title: About TechCorp
Webpage Contents:
Our mission is to democratize technology for businesses of all sizes.
We believe in innovation, collaboration, and excellence.
Our team of 100+ engineers works remotely across 15 countries."""
    },
    {
        "role": "assistant",
        "content": """# TechCorp - Innovative Software Solutions

## About Us
TechCorp is a leading software development company that has been transforming businesses through cutting-edge technology since 2015. We specialize in enterprise solutions that help organizations of all sizes leverage the power of modern technology.

## Our Mission
To democratize technology for businesses worldwide, making innovative solutions accessible and practical for companies of every scale.

## Company Culture
- **Innovation**: We push the boundaries of what's possible
- **Collaboration**: Our global team works together seamlessly
- **Excellence**: We deliver nothing but the highest quality solutions

## Our Team
100+ talented engineers working remotely across 15 countries, bringing diverse perspectives and expertise to every project.

## Track Record
✅ **500+ satisfied clients** worldwide  
✅ **8+ years** of proven experience  
✅ **Global presence** across multiple continents  

*Ready to transform your business? Let's build the future together.*"""
    }
]

def get_language_specific_prompt(language_code: str) -> str:
    """Get language-specific instructions for brochure generation"""
    
    if language_code == 'en':
        return ""
    
    language_instructions = {
        'es': "Please generate the brochure in Spanish.",
        'fr': "Please generate the brochure in French.", 
        'de': "Please generate the brochure in German.",
        'it': "Please generate the brochure in Italian.",
        'pt': "Please generate the brochure in Portuguese.",
        'zh': "Please generate the brochure in Chinese.",
        'ja': "Please generate the brochure in Japanese.",
        'ko': "Please generate the brochure in Korean.",
        'ua': "Please generate the brochure in Ukrainian."
    }
    
    return f"\n\nIMPORTANT: {language_instructions.get(language_code, f'Please generate the brochure in the language with code: {language_code}')}"

def get_link_extraction_prompt(website_url: str, links: list) -> str:
    """Generate the user prompt for link extraction"""
    
    user_prompt = f"Here is the list of links on the website of {website_url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. "
    user_prompt += "Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(links)
    
    return user_prompt

def get_brochure_generation_prompt(company_name: str, website_content: str, language_code: str = 'en') -> str:
    """Generate the user prompt for brochure creation"""
    
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += "Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += website_content
    user_prompt += get_language_specific_prompt(language_code)
    
    return user_prompt