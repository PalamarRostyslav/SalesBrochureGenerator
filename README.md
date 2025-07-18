# SalesBrochureGenerator

A Python application that automatically generates professional company brochures by analyzing website content using AI-powered content extraction and generation.

## Features ✨

- **🤖 Multi-AI Provider Support**: Choose between OpenAI GPT and Anthropic Claude models
- **🖥️ Web Interface**: Beautiful Gradio UI for easy interaction
- **📱 CLI Interface**: Command-line interface for automation and scripting
- **🌐 Intelligent Web Scraping**: Automatically extracts relevant content from company websites
- **🎯 AI-Powered Content Analysis**: Uses advanced AI models to identify and extract key information
- **🌍 Multi-language Support**: Generate brochures in 10+ languages
- **🎓 Few-shot Prompting**: Enhanced AI responses using example-based learning
- **⚡ Streaming Output**: Real-time brochure generation with live preview
- **📊 Professional Logging**: Comprehensive logging with rich console output
- **📈 Metadata Tracking**: Detailed generation metadata for audit trails
- **🗂️ File Management**: Automatic file organization and cleanup utilities
- **🔧 Production Ready**: Robust error handling, retry logic, and configuration management

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
anthropic>=0.21.0
click>=8.1.0
colorama>=0.4.6
rich>=13.0.0
gradio>=4.0.0
```

### Setup

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Edit `.env` file and add your model API Key:
   
   # OpenAI Configuration
   OPENAI_API_KEY=sk-proj-yourkey
   ANTHROPIC_API_KEY=sk-ant-yourkey

   # Application Settings
   DEFAULT_MODEL=gpt-4o-mini
   DEFAULT_CLAUDE_MODEL=claude-3-haiku-20240307
   LOG_LEVEL=INFO
   OUTPUT_DIR=output/brochures
   MAX_CONTENT_LENGTH=20000
   
   # Request Settings
   REQUEST_TIMEOUT=30
   MAX_RETRIES=3
   

## Usage 💻

### 🖥️ Web Interface (Recommended)

Launch the Gradio web interface:
```bash
python main.py ui
```

Then open your browser to `http://localhost:7860`

**Features:**
- 🎯 Easy-to-use web interface
- 🤖 Choose between OpenAI and Claude
- 📊 Real-time generation progress
- 🌍 Language selection dropdown
- 🔍 API connection testing
- 📋 Example inputs provided

### 📱 Command Line Interface

#### Basic Usage
```bash
# Generate with OpenAI (default)
python main.py generate "Anthropic" "https://anthropic.com"

# Generate with Claude
python main.py generate "OpenAI" "https://openai.com" --provider claude

# Quick generation with default settings
python main.py quick "Tesla" "https://tesla.com"
```

#### Advanced Options
```bash
# Generate in Spanish with Claude and streaming
python main.py generate "Tesla" "https://tesla.com" --provider claude --language es --stream

# Use specific model
python main.py generate "Microsoft" "https://microsoft.com" --provider openai --model gpt-4o

# Export to custom location
python main.py export "Apple" "https://apple.com" --output ./custom/apple_brochure.md
```

#### Utility Commands
```bash
# Test API connections
python main.py test --provider openai
python main.py test --provider claude

# Show configuration status
python main.py status

# List supported languages
python main.py languages

# Launch web interface
python main.py ui

# Clean up old files
python main.py cleanup --days 30
```

### Python API

```python
from src.generators.brochure_generator import BrochureGenerator, GenerationOptions

# Initialize with OpenAI
generator = BrochureGenerator(provider="openai")

# Or initialize with Claude
generator = BrochureGenerator(provider="claude")

# Set generation options
options = GenerationOptions(
    language='es',
    use_few_shot=True,
    stream_output=False,
    save_metadata=True
)

# Generate brochure
result = generator.generate_brochure(
    company_name="Anthropic",
    website_url="https://anthropic.com",
    options=options
)

print(result.content)
print(f"Saved to: {result.file_path}")
```

### Streaming Generation

```python
# Stream generation with real-time output
for chunk in generator.stream_brochure_generation("OpenAI", "https://openai.com"):
    if isinstance(chunk, str):
        print(chunk, end='', flush=True)
    else:
        # Final result
        result = chunk
        break
```

## AI Providers 🤖

### OpenAI GPT Models
- **gpt-4o-mini** (Default) - Fast and cost-effective
- **gpt-4o** - Most capable model
- **gpt-4-turbo** - Balanced performance
- **gpt-3.5-turbo** - Legacy support

### Anthropic Claude Models  
- **claude-3-haiku-20240307** (Default) - Fast and efficient
- **claude-3-sonnet-20240229** - Balanced capabilities
- **claude-3-opus-20240229** - Most powerful

## Configuration ⚙️

### Environment Variables

```bash
# AI Provider Keys (at least one required)
OPENAI_API_KEY=sk-proj-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Default Models
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_CLAUDE_MODEL=claude-3-haiku-20240307

# Application Settings
LOG_LEVEL=INFO
OUTPUT_DIR=output/brochures
MAX_CONTENT_LENGTH=20000
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### Supported Languages

English (en), Spanish (es), French (fr), German (de), Italian (it), Portuguese (pt), Chinese (zh), Japanese (ja), Korean (ko), Ukrainian (ua)

## Project Structure 📁

```
sales-brochure-generator/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py                    # CLI entry point
├── src/
│   ├── models/               # AI model implementations
│   │   ├── base_ai_model.py  # Shared base class
│   │   ├── openai_model.py   # OpenAI GPT interface
│   │   └── claude_model.py   # Anthropic Claude interface
│   ├── scrapers/            # Web scraping
│   │   └── website_scraper.py
│   ├── generators/          # Main orchestration
│   │   └── brochure_generator.py
│   ├── ui/                  # Gradio web interface
│   │   ├── gradio_interface.py
│   │   └── ui_launcher.py
│   ├── utils/               # Utilities (logging, files, text)
│   │   ├── logger.py
│   │   ├── file_handler.py
│   │   └── text_utils.py
│   └── configs/              # Settings and prompts
│       ├── settings.py
│       └── prompts.py
├── output/brochures/        # Generated files
│   └── .gitkeep
└── logs/                    # Application logs
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

## Troubleshooting 🔧

### Common Issues

**API Key Errors:**
```bash
# Test specific provider
python main.py test --provider openai
python main.py test --provider claude
```

**Gradio UI Issues:**
```bash
# Install Gradio if missing
pip install gradio>=4.0.0

# Launch with debug mode
python main.py ui
```

**Memory Issues:**
- Reduce `MAX_CONTENT_LENGTH` in settings
- Use streaming generation for large websites

**Network Timeouts:**
- Increase `REQUEST_TIMEOUT` in settings
- Check firewall settings

### Getting Help

**Web Interface**: Use the "Test API Connection" button to verify setup
**CLI**: Run `python main.py test` to diagnose issues
**Logs**: Check the `logs/` directory for detailed error information

## Performance 📊

- **Average generation time**: 10-20 seconds
- **Content processing**: Up to 20,000 characters
- **Concurrent requests**: Configurable rate limiting
- **Memory usage**: ~50-100MB during generation or even lower
- **Supported file formats**: Markdown (.md), JSON metadata

## Architecture Benefits 🏗️

### Inheritance Pattern
- **Shared functionality** between OpenAI and Claude models
- **Consistent interface** across all AI providers
- **Easy extensibility** for new AI providers
- **Reduced code duplication** and maintenance overhead

### Modular Design
- **Separation of concerns** across different modules
- **Plugin architecture** for easy feature additions
- **Configuration-driven** behavior
- **Comprehensive error handling** and retry logic

## Development 👨‍💻

### Customization

- **Prompts**: Modify prompts in `src/config/prompts.py`
- **Settings**: Adjust settings in `src/config/settings.py`
- **Languages**: Add new languages in `SUPPORTED_LANGUAGES`
- **AI Models**: Extend `BaseAIModel` for new providers

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Roadmap 🗺️

- [ ] **Additional AI Providers**: Google Gemini, Cohere
- [ ] **Output Formats**: HTML, PDF generation  
- [ ] **Batch Processing**: Multiple companies at once
- [ ] **API Endpoints**: RESTful API for integrations
- [ ] **Advanced Analytics**: Generation metrics and insights
- [ ] **CRM Integration**: Salesforce, HubSpot connectors
- [ ] **Custom Templates**: Branding and design templates
- [ ] **Multi-modal**: Image and video content analysis
- [ ] **Real-time Collaboration**: Shared editing features
- [ ] **Enterprise Features**: User management, audit logs
