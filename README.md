# SalesBrochureGenerator

# A Python application that automatically generates professional company brochures by analyzing website content using AI-powered content extraction and generation.

Features ✨

1) Intelligent Web Scraping: Automatically extracts relevant content from company websites
2) AI-Powered Content Analysis: Uses OpenAI's GPT models to identify and extract key information
3) Multi-language Support: Generate brochures in 10 languages that can be easily extended if needed
4) Few-shot Prompting: Enhanced AI responses using example-based learning
5) Streaming Output: Real-time brochure generation with live preview
6) Professional Logging: Comprehensive logging with rich console output
7) Metadata Tracking: Detailed generation metadata for audit trails
8) File Management: Automatic file organization and cleanup utilities
9) CLI Interface: User-friendly command-line interface
10) Operational focus: Robust error handling, retry logic, and configuration management

Supported Languages 🌍

English (en)
Spanish (es)
French (fr)
German (de)
Italian (it)
Portuguese (pt)
Chinese (zh)
Japanese (ja)
Korean (ko)
Ukrainian (ua)

# Installation 📦

# Prerequisites

1) Python 3.8 or higher
2) OpenAI API key

# Core dependencies
requests>=2.31.0

beautifulsoup4>=4.12.0

python-dotenv>=1.0.0

openai>=1.0.0

# Utilities
click>=8.1.0

colorama>=0.4.6

rich>=13.0.0

# Setup

1) Clone the repository
   
2) Install dependencies
   
3) Configure environnment. Edit .env file and add your OpenaAI API Key:
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Usage 💻

# Command Line Interface

# Basic Usage:
Generate a brochure for a company

python main.py generate "Anthropic" "https://anthropic.com"

# Quick generation with default settings

python main.py quick "OpenAI" "https://openai.com"

Advanced Options
# Generate in Spanish with streaming output

python main.py generate "Apple" "https://www.apple.com" --language es --stream

# Use specific model and save metadata

python main.py generate "Microsoft" "https://microsoft.com" --model gpt-4o-mini --save-metadata

# Export to custom location

python main.py export "Apple" "https://apple.com" --output ./custom/apple_brochure.md


# Utility Commands

# List supported languages
python main.py languages

# Test API connection
python main.py test

# Clean up old files (older than 30 days)
python main.py cleanup --days 30

or cleanup all the files

python main.py cleanup

# Examples 📋

# Generated Brochure Sample


# Anthropic - AI Safety Company

## About Us
Anthropic is an AI safety company focused on building reliable, 
interpretable, and steerable AI systems. Founded in 2021 by 
former OpenAI researchers, we're committed to ensuring AI 
systems are safe and beneficial.

## Our Mission
To develop AI systems that are safe, beneficial, and 
understandable, helping humanity navigate the transformative 
impact of artificial intelligence.

## Products & Services
- **Claude**: Advanced AI assistant for various applications
- **Constitutional AI**: Research methodology for training 
  helpful, harmless, and honest AI systems
- **AI Safety Research**: Cutting-edge research in AI alignment

## Company Culture
- Safety-first approach to AI development
- Collaborative and research-oriented environment
- Commitment to responsible AI practices

Performance 📊

1) Average generation time: 15-20 seconds
2) Content processing: Up to 20,000 characters
3) Concurrent requests: Configurable rate limiting
4) Memory usage: ~50-100MB during generation

Error Handling 🛡️
The application includes comprehensive error handling for:

1) Network connectivity issues
2) API rate limits and timeouts
3) Invalid website content
4) File system errors
5) Configuration problems




