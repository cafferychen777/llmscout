"""
Basic usage example of LLMScout.

This example demonstrates how to:
1. Initialize the pipeline
2. Configure search parameters
3. Run a paper analysis
4. Access and process the results
"""

from llmscout import ResearchPipeline

def main():
    # Initialize the pipeline
    pipeline = ResearchPipeline()

    # Basic usage
    pipeline.run(
        topic="watermark attack language model",
        max_results=5,
        date_start="2023-01-01"
    )

    # Advanced usage with custom parameters
    pipeline.run(
        topic="watermark attack language model",
        max_results=10,
        date_start="2023-01-01",
        categories=["cs.AI", "cs.CL"],  # Specific arXiv categories
        sort_by="submitted",
        ascending=False,
        download_papers=True
    )

if __name__ == "__main__":
    main()
