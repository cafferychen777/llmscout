"""
Advanced usage example of LLMScout showing custom analysis workflows.

This example demonstrates how to:
1. Use individual components separately
2. Customize the analysis process
3. Handle the results programmatically
"""

from llmscout.generator import KeywordGenerator
from llmscout.crawler import ArxivCrawler
from llmscout.analyzer import AbstractAnalyzer

def custom_workflow():
    # Initialize components
    generator = KeywordGenerator()
    crawler = ArxivCrawler()
    analyzer = AbstractAnalyzer()

    # Generate keywords
    keywords = generator.generate_keywords(
        topic="watermark attack language model",
        num_keywords=5
    )

    # Search for papers
    papers = crawler.search_papers(
        keywords=keywords,
        max_results=10,
        date_start="2023-01-01"
    )

    # Analyze abstracts
    analysis_results = analyzer.analyze_abstracts(papers)

    # Process results
    for result in analysis_results:
        print(f"Paper: {result['title']}")
        print(f"Relevance: {result['relevance']}")
        print(f"Key findings: {result['key_findings']}")
        print("---")

if __name__ == "__main__":
    custom_workflow()
