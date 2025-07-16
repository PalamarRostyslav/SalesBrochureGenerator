# SalesBrochureGenerator

A Python application that automatically generates professional company brochures by analyzing website content using AI-powered content extraction and generation.

## Features ✨

1. **Intelligent Web Scraping**: Automatically extracts relevant content from company websites
2. **AI-Powered Content Analysis**: Uses OpenAI's GPT models to identify and extract key information
3. **Multi-language Support**: Generate brochures in 10 languages that can be easily extended if needed
4. **Few-shot Prompting**: Enhanced AI responses using example-based learning
5. **Streaming Output**: Real-time brochure generation with live preview
6. **Professional Logging**: Comprehensive logging with rich console output
7. **Metadata Tracking**: Detailed generation metadata for audit trails
8. **File Management**: Automatic file organization and cleanup utilities
9. **CLI Interface**: User-friendly command-line interface
10. **Operationally Sound**: Robust error handling, retry logic, and configuration management

## Supported Languages 🌍

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Ukrainian (ua)

## Installation 📦

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Dependencies

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
openai>=1.0.0
click>=8.1.0
colorama>=0.4.6
rich>=13.0.0
```

### Setup

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Edit `.env` file and add your OpenAI API Key:
   ```env
   OPENAI_API_KEY=sk-proj-your-openai-api-key-here
   ```

## Usage 💻

### Command Line Interface

#### Basic Usage

Generate a brochure for a company:
```bash
python main.py generate "Anthropic" "https://anthropic.com"
```

Quick generation with default settings:
```bash
python main.py quick "OpenAI" "https://openai.com"
```

#### Advanced Options

Generate in Spanish with streaming output:
```bash
python main.py generate "Apple" "https://www.apple.com" --language es --stream
```

Use specific model and save metadata:
```bash
python main.py generate "Microsoft" "https://microsoft.com" --model gpt-4o-mini --save-metadata
```

Export to custom location:
```bash
python main.py export "Apple" "https://apple.com" --output ./custom/apple_brochure.md
```

#### Utility Commands

List supported languages:
```bash
python main.py languages
```

Test API connection:
```bash
python main.py test
```

Clean up old files (older than 30 days):
```bash
python main.py cleanup --days 30
```

Or cleanup all files:
```bash
python main.py cleanup
```

## Examples 📋

### Generated Brochure Sample

```markdown
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
```

## Performance 📊

- Average generation time: 15-20 seconds
- Content processing: Up to 20,000 characters
- Concurrent requests: Configurable rate limiting
- Memory usage: ~50-100MB during generation

## Error Handling 🛡️

The application includes comprehensive error handling for:

- Network connectivity issues
- API rate limits and timeouts
- Invalid website content
- File system errors
- Configuration problems
