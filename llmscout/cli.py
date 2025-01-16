"""Command-line interface for Research Assistant."""

import argparse
import sys

from .config import load_config
from .pipeline import ResearchPipeline


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Research Assistant - Automate your research paper analysis"
    )
    parser.add_argument(
        "--topic", type=str, required=True, help="Research topic to search for"
    )
    parser.add_argument(
        "--date-start",
        type=str,
        default="2023-01-01",
        help="Start date for paper search (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Maximum number of papers to retrieve",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Skip paper downloading",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to store results (overrides OUTPUT_DIR env var)",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to .env file (default: .env in current directory)",
    )

    args = parser.parse_args()

    try:
        # Load configuration from environment
        config = load_config(args.env_file)
        
        # Override output directory if specified
        if args.output_dir:
            config["output"]["base_dir"] = args.output_dir

        pipeline = ResearchPipeline(
            output_dir=config["output"]["base_dir"],
            config=config,
        )
        pipeline.run(
            topic=args.topic,
            date_start=args.date_start,
            max_results=args.max_results,
            download_papers=not args.no_download,
        )
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
