"""
Zotero integration module for LLMScout.

This module handles the integration with Zotero, allowing users to:
1. Upload papers to a specific Zotero collection
2. Add metadata and tags
3. Manage attachments
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from pyzotero import zotero
from .logger import get_logger

logger = get_logger(__name__)

class ZoteroManager:
    """Manages interactions with Zotero library."""

    def __init__(self, library_id: str, api_key: str, library_type: str = 'user'):
        """
        Initialize ZoteroManager.

        Args:
            library_id: Zotero library ID
            api_key: Zotero API key
            library_type: Type of library ('user' or 'group')
        """
        self.zot = zotero.Zotero(library_id, library_type, api_key)
        self.logger = logger

    def get_or_create_collection(self, collection_name: str) -> str:
        """
        Get or create a collection by name.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection key
        """
        collections = self.zot.collections()
        for collection in collections:
            if collection['data']['name'] == collection_name:
                return collection['key']

        # Create new collection if it doesn't exist
        collection_data = {'name': collection_name}
        response = self.zot.create_collections([collection_data])
        return response['successful']['0']['key']

    def add_paper(self, 
                 filepath: str, 
                 metadata: Dict[str, Any],
                 collection_name: Optional[str] = None,
                 tags: Optional[List[str]] = None) -> str:
        """
        Add a paper to Zotero library.

        Args:
            filepath: Path to the PDF file
            metadata: Paper metadata (title, authors, etc.)
            collection_name: Optional name of collection to add to
            tags: Optional list of tags to add

        Returns:
            Item key of the created item
        """
        # Prepare template
        template = {
            'itemType': 'journalArticle',
            'title': metadata.get('title', ''),
            'creators': [{'creatorType': 'author', 'name': author} 
                        for author in metadata.get('authors', [])],
            'abstractNote': metadata.get('abstract', ''),
            'date': metadata.get('published', ''),
            'DOI': metadata.get('doi', ''),
            'url': metadata.get('url', ''),
            'language': 'en',
            'tags': [{'tag': tag} for tag in (tags or [])]
        }

        # Create item
        item = self.zot.create_items([template])
        item_key = item['successful']['0']['key']

        # Add to collection if specified
        if collection_name:
            collection_key = self.get_or_create_collection(collection_name)
            self.zot.addto_collection(collection_key, [item_key])

        # Attach PDF
        if os.path.exists(filepath):
            self.zot.attachment_simple([filepath], item_key)
        else:
            self.logger.warning(f"File not found: {filepath}")

        self.logger.info(f"Added paper '{metadata.get('title')}' to Zotero")
        return item_key

    def add_papers_batch(self, 
                        papers: List[Dict[str, Any]], 
                        collection_name: Optional[str] = None) -> List[str]:
        """
        Add multiple papers to Zotero library.

        Args:
            papers: List of paper dictionaries containing filepath and metadata
            collection_name: Optional name of collection to add papers to

        Returns:
            List of created item keys
        """
        item_keys = []
        for paper in papers:
            try:
                filepath = paper.get('filepath')
                metadata = paper.get('metadata', {})
                tags = paper.get('tags', [])
                
                item_key = self.add_paper(
                    filepath=filepath,
                    metadata=metadata,
                    collection_name=collection_name,
                    tags=tags
                )
                item_keys.append(item_key)
            except Exception as e:
                self.logger.error(f"Error adding paper {paper.get('metadata', {}).get('title')}: {str(e)}")
                continue

        return item_keys
