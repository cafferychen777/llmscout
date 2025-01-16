"""Tests for the research pipeline."""

import pytest
from research_assistant import ResearchPipeline
from research_assistant.generator import KeywordGenerator
from research_assistant.crawler import ArxivCrawler
from research_assistant.analyzer import AbstractAnalyzer


def test_keyword_generator():
    """Test keyword generation."""
    generator = KeywordGenerator()
    keywords = generator.generate_keywords("test topic")
    assert isinstance(keywords, dict)
    assert "primary" in keywords
    assert isinstance(keywords["primary"], list)


def test_arxiv_crawler():
    """Test arXiv paper crawling."""
    crawler = ArxivCrawler()
    papers = crawler.search_papers(
        keywords={"primary": ["test"]},
        max_results=1
    )
    assert isinstance(papers, list)
    assert len(papers) <= 1
    if papers:
        assert "title" in papers[0]
        assert "abstract" in papers[0]


def test_abstract_analyzer():
    """Test abstract analysis."""
    analyzer = AbstractAnalyzer()
    papers = [
        {
            "title": "Test Paper",
            "abstract": "This is a test abstract.",
            "url": "http://example.com",
        }
    ]
    results = analyzer.analyze_abstracts(papers)
    assert isinstance(results, list)
    assert len(results) == 1
    assert "analysis" in results[0]


def test_pipeline_initialization():
    """Test pipeline initialization."""
    pipeline = ResearchPipeline()
    assert isinstance(pipeline.generator, KeywordGenerator)
    assert isinstance(pipeline.crawler, ArxivCrawler)
    assert isinstance(pipeline.analyzer, AbstractAnalyzer)
