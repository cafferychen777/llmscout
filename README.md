# LLMScout

An LLM-powered tool for discovering and analyzing research papers. LLMScout helps researchers efficiently search, analyze, and manage academic papers from arXiv, leveraging the power of large language models.

## Features

- 🔍 Smart keyword generation using LLM
- 📚 Automated paper search on arXiv
- 📊 Intelligent paper analysis and summarization
- 📥 Batch paper downloading
- 📝 Zotero integration for paper management
- 📝 Detailed logging and progress tracking
- ⏸️ Resume capability for interrupted operations

## Installation

```bash
pip install llmscout
```

Or install from source:

```bash
git clone https://github.com/cafferychen777/llmscout.git
cd llmscout
pip install -e .
```

## Quick Start

1. Set up your environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-api-key-here
```

2. Use in Python:
```python
from llmscout import ResearchPipeline

# Initialize the pipeline
pipeline = ResearchPipeline()

# Run the complete analysis
pipeline.run(
    topic="watermark attack language model",
    max_results=10,
    date_start="2023-01-01"
)
```

3. Or use the command-line interface:
```bash
llmscout --topic "watermark attack language model" --max-results 10
```

## Environment Variables

The following environment variables can be configured in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional
OPENAI_MODEL=gpt-4              # Default: gpt-4
OPENAI_TEMPERATURE=0.7          # Default: 0.7
OPENAI_MAX_TOKENS=1000          # Default: 1000

# Output directories
OUTPUT_DIR=./results            # Default: ./results
DOWNLOAD_DIR=./papers          # Default: ./papers
LOG_DIR=./logs                 # Default: ./logs

# Zotero configuration (optional)
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_API_KEY=your_api_key
ZOTERO_LIBRARY_TYPE=user  # or 'group'
ZOTERO_COLLECTION=LLMScout  # default collection name
```

## Zotero Integration

LLMScout can automatically add downloaded papers to your Zotero library. To use this feature:

1. Get your Zotero library ID:
   - Go to [Zotero Web Library](https://www.zotero.org/settings/keys)
   - Your library ID is shown in the URL when viewing your library

2. Create a Zotero API key:
   - Go to [Zotero Settings > API Keys](https://www.zotero.org/settings/keys/new)
   - Create a new key with read/write permissions
   - Save the generated API key

3. Configure LLMScout:
   - Add your Zotero credentials to `.env` file
   - Papers will be automatically added to the specified collection

## Documentation

For detailed documentation, visit [our documentation site](https://llmscout.readthedocs.io/).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{llmscout,
  title = {LLMScout: An LLM-Powered Tool for Research Paper Discovery and Analysis},
  author = {Caffery Chen},
  year = {2025},
  url = {https://github.com/cafferychen777/llmscout}
}
