"""
Research Assistant
~~~~~~~~~~~~~~~~

A Python library for automating academic paper research and analysis.
"""

__version__ = "0.1.0"

from .analyzer import AbstractAnalyzer
from .crawler import ArxivCrawler
from .downloader import PaperDownloader
from .generator import KeywordGenerator
from .pipeline import ResearchPipeline

__all__ = [
    "AbstractAnalyzer",
    "ArxivCrawler",
    "PaperDownloader",
    "KeywordGenerator",
    "ResearchPipeline",
]
