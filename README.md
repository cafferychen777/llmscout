# LLMScout

An LLM-powered tool for discovering and analyzing research papers. LLMScout helps researchers efficiently search, analyze, and manage academic papers from arXiv, leveraging the power of large language models.

## Features

- 🔍 Smart keyword generation using LLM
- 📚 Automated paper search on arXiv
- 📊 Intelligent paper analysis and summarization
- 📥 Batch paper downloading
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
```

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
