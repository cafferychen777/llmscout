"""Paper downloader module."""

import os
from typing import Optional, Dict, Any, List
import requests
from pathlib import Path
from .logger import get_logger
from .config import get_config
from .zotero_manager import ZoteroManager

logger = get_logger(__name__)

class PaperDownloader:
    """Downloads papers and manages local storage."""

    def __init__(self):
        """Initialize downloader with configuration."""
        self.config = get_config()
        self.download_dir = Path(self.config.get('DOWNLOAD_DIR', './papers'))
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Zotero manager if configured
        self.zotero = None
        if all(key in self.config for key in ['ZOTERO_LIBRARY_ID', 'ZOTERO_API_KEY']):
            try:
                self.zotero = ZoteroManager(
                    library_id=self.config['ZOTERO_LIBRARY_ID'],
                    api_key=self.config['ZOTERO_API_KEY'],
                    library_type=self.config.get('ZOTERO_LIBRARY_TYPE', 'user')
                )
                logger.info("Zotero integration enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Zotero: {str(e)}")

    def download_paper(self, url: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Download a paper from the given URL.

        Args:
            url: URL to download from
            metadata: Paper metadata

        Returns:
            Path to downloaded file or None if download failed
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Create filename from title
            title = metadata.get('title', '').replace('/', '_')[:100]  # Limit length
            filename = f"{title}.pdf"
            filepath = self.download_dir / filename

            # Download file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded paper to {filepath}")

            # Add to Zotero if enabled
            if self.zotero:
                try:
                    collection_name = self.config.get('ZOTERO_COLLECTION')
                    tags = metadata.get('categories', [])
                    self.zotero.add_paper(
                        str(filepath),
                        metadata,
                        collection_name=collection_name,
                        tags=tags
                    )
                    logger.info(f"Added paper to Zotero collection: {collection_name}")
                except Exception as e:
                    logger.error(f"Failed to add paper to Zotero: {str(e)}")

            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to download paper: {str(e)}")
            return None

    def download_papers(self, papers: List[Dict[str, Any]]) -> List[str]:
        """
        Download multiple papers.

        Args:
            papers: List of paper dictionaries containing URLs and metadata

        Returns:
            List of downloaded file paths
        """
        downloaded_paths = []
        for paper in papers:
            url = paper.get('pdf_url')
            if url:
                path = self.download_paper(url, paper)
                if path:
                    downloaded_paths.append(path)
        return downloaded_paths
