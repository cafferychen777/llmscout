import os
import requests
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from .logger import setup_logger

class PaperDownloader:
    def __init__(self, output_dir: str = 'papers'):
        self.logger = setup_logger('paper_downloader')
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def download_papers(self, papers: List[Dict], max_workers: int = 5) -> List[Dict]:
        """
        并行下载多篇论文
        
        Args:
            papers: 论文列表，每个论文需要包含 url 和 title
            max_workers: 最大并行下载数
            
        Returns:
            下载结果列表，包含下载状态和本地路径
        """
        self.logger.info(f"\nStarting to download {len(papers)} papers...")
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 创建下载任务
            future_to_paper = {
                executor.submit(self._download_single_paper, paper): paper 
                for paper in papers
            }
            
            # 收集结果
            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error downloading paper {paper.get('title', 'Unknown')}: {str(e)}")
                    results.append({
                        **paper,
                        'download_status': 'failed',
                        'error': str(e)
                    })
                    
        self.logger.info(f"Completed downloading {len(papers)} papers")
        return results
        
    def _download_single_paper(self, paper: Dict) -> Dict:
        """下载单篇论文"""
        title = paper['title']
        url = paper['url']
        
        try:
            # 构建文件名
            filename = self._sanitize_filename(f"{paper['arxiv_id']}_{title}.pdf")
            filepath = os.path.join(self.output_dir, filename)
            
            # 如果文件已存在，跳过下载
            if os.path.exists(filepath):
                self.logger.info(f"Paper already exists: {filename}")
                return {
                    **paper,
                    'download_status': 'exists',
                    'local_path': filepath
                }
                
            # 下载文件
            self.logger.info(f"Downloading: {title}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            self.logger.info(f"Successfully downloaded: {filename}")
            
            # 添加下载信息到论文数据
            return {
                **paper,
                'download_status': 'success',
                'local_path': filepath
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Download failed for {title}: {str(e)}")
            return {
                **paper,
                'download_status': 'failed',
                'error': str(e)
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {title}: {str(e)}")
            return {
                **paper,
                'download_status': 'failed',
                'error': str(e)
            }
            
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
            
        # 限制长度
        max_length = 255 - len('.pdf')  # 考虑文件扩展名
        if len(filename) > max_length:
            filename = filename[:max_length]
            
        return filename
