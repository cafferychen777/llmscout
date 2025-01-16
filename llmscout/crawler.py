import arxiv
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import pytz
from enum import Enum
import time
from .logger import setup_logger

class SortBy(Enum):
    """论文排序方式"""
    RELEVANCE = "relevance"
    LAST_UPDATED = "last_updated"
    SUBMITTED = "submitted"

class ArxivCrawler:
    def __init__(self):
        self.logger = setup_logger('arxiv_crawler')
        self.logger.info("Initializing ArxivCrawler...")
        self.client = arxiv.Client()
        
    def search_papers(
        self,
        keywords: Dict[str, List[str]],
        max_results: int = 100,
        date_start: Optional[Union[str, datetime]] = None,
        date_end: Optional[Union[str, datetime]] = None,
        sort_by: SortBy = SortBy.SUBMITTED,
        ascending: bool = False,
        categories: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        timeout: int = 30  # 添加超时参数，默认30秒
    ) -> List[Dict]:
        """
        Search papers based on advanced criteria
        
        Args:
            keywords: Dictionary of keywords by category
            max_results: Maximum number of results to return
            date_start: Start date for paper search (format: YYYY-MM-DD or datetime)
            date_end: End date for paper search (format: YYYY-MM-DD or datetime)
            sort_by: How to sort results (relevance, last_updated, submitted)
            ascending: Sort in ascending order if True, descending if False
            categories: List of arXiv categories to filter by (e.g., ["cs.AI", "cs.LG"])
            authors: List of author names to filter by
            timeout: Maximum time in seconds to wait for results
        """
        self.logger.info(f"Starting paper search with parameters:")
        self.logger.info(f"- Keywords: {keywords}")
        self.logger.info(f"- Max results: {max_results}")
        self.logger.info(f"- Date range: {date_start} to {date_end}")
        self.logger.info(f"- Sort by: {sort_by.value}")
        self.logger.info(f"- Categories: {categories}")
        self.logger.info(f"- Authors: {authors}")
        
        try:
            # Process dates
            if isinstance(date_start, str):
                date_start = datetime.strptime(date_start, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
            if isinstance(date_end, str):
                date_end = datetime.strptime(date_end, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
                
            # Construct search query
            query = self._build_query(keywords, categories, authors)
            self.logger.info(f"Constructed search query: {query}")
            
            # Map sort options
            sort_mapping = {
                SortBy.RELEVANCE: arxiv.SortCriterion.Relevance,
                SortBy.LAST_UPDATED: arxiv.SortCriterion.LastUpdatedDate,
                SortBy.SUBMITTED: arxiv.SortCriterion.SubmittedDate
            }
            
            # Configure search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_mapping[sort_by],
                sort_order=arxiv.SortOrder.Ascending if ascending else arxiv.SortOrder.Descending
            )
            
            papers = []
            start_time = time.time()
            
            self.logger.info("Starting to fetch results...")
            for result in self.client.results(search):
                # 检查是否超时
                if time.time() - start_time > timeout:
                    self.logger.warning(f"Search timeout after {timeout} seconds. Returning {len(papers)} papers found so far.")
                    break
                    
                # Apply date filters if specified
                if date_start and result.published < date_start:
                    self.logger.debug(f"Skipping paper published before start date: {result.title}")
                    continue
                if date_end and result.published > date_end:
                    self.logger.debug(f"Skipping paper published after end date: {result.title}")
                    continue
                    
                # Collect paper metadata
                try:
                    paper = {
                        'title': result.title,
                        'abstract': result.summary,
                        'authors': [author.name for author in result.authors],
                        'url': result.pdf_url,
                        'published': result.published.strftime('%Y-%m-%d'),
                        'last_updated': result.updated.strftime('%Y-%m-%d'),
                        'arxiv_id': result.entry_id.split('/')[-1],
                        'primary_category': result.primary_category,
                        'categories': result.categories,
                        'doi': result.doi,
                        'journal_ref': result.journal_ref,
                        'comment': result.comment
                    }
                    papers.append(paper)
                    self.logger.info(f"Found paper: {paper['title']} ({paper['arxiv_id']})")
                except Exception as e:
                    self.logger.error(f"Error processing paper result: {str(e)}")
                    continue
                
            self.logger.info(f"Search completed. Found {len(papers)} papers in total.")
            return papers
            
        except Exception as e:
            self.logger.error(f"Error during paper search: {str(e)}")
            return []
        
    def _build_query(
        self,
        keywords: Dict[str, List[str]],
        categories: Optional[List[str]] = None,
        authors: Optional[List[str]] = None
    ) -> str:
        """构建arXiv搜索查询字符串"""
        self.logger.debug("Building search query...")
        
        # 只使用主要关键词进行搜索，用OR连接
        terms = []
        
        # 添加标题和摘要搜索
        for term in keywords['primary']:
            terms.append(f'(ti:"{term}" OR abs:"{term}")')
        
        # 构建最终查询
        query = ' OR '.join(terms)
        
        self.logger.info(f"Final search query: {query}")
        return query