import os
import json
import hashlib
from datetime import datetime
from scripts.generator import KeywordGenerator
from scripts.crawler import ArxivCrawler, SortBy
from scripts.analyzer import AbstractAnalyzer
from scripts.downloader import PaperDownloader
from scripts.utils import save_json
from scripts.logger import setup_logger

class PipelineState:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.state_file = os.path.join(output_dir, 'pipeline_state.json')
        self.load_state()
        
    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                'params_hash': None,
                'completed_steps': [],
                'current_step': None,
                'error': None
            }
            
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def step_completed(self, step_name: str):
        if step_name not in self.state['completed_steps']:
            self.state['completed_steps'].append(step_name)
        self.state['current_step'] = None
        self.state['error'] = None
        self.save_state()
        
    def set_current_step(self, step_name: str):
        self.state['current_step'] = step_name
        self.save_state()
        
    def set_error(self, error: str):
        self.state['error'] = error
        self.save_state()
        
    def is_step_completed(self, step_name: str) -> bool:
        return step_name in self.state['completed_steps']
        
    @staticmethod
    def generate_params_hash(params: dict) -> str:
        """生成参数的哈希值，用于判断是否使用相同参数"""
        # 将参数转换为排序后的字符串
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

def test_pipeline(
    topic: str = "watermark attack language model",
    date_start: str = "2023-01-01",
    max_results: int = 50,
    categories: list = None,
    sort_by: SortBy = SortBy.SUBMITTED,
    ascending: bool = False,
    download_papers: bool = True
):
    """测试完整的论文分析流程，支持断点续传"""
    # 设置日志记录器
    logger = setup_logger('pipeline')
    logger.info("Starting test pipeline...")
    
    # 生成参数哈希
    params = {
        'topic': topic,
        'date_start': date_start,
        'max_results': max_results,
        'categories': categories,
        'sort_by': sort_by.value if sort_by else None,
        'ascending': ascending,
        'download_papers': download_papers
    }
    params_hash = PipelineState.generate_params_hash(params)
    
    # 查找最近的未完成运行
    results_dir = None
    for dir_name in sorted(os.listdir('results'), reverse=True):
        dir_path = os.path.join('results', dir_name)
        state_file = os.path.join(dir_path, 'pipeline_state.json')
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
                if state['params_hash'] == params_hash:
                    results_dir = dir_path
                    logger.info(f"Found previous run: {dir_path}")
                    break
                    
    # 如果没有找到相同参数的运行，创建新目录
    if not results_dir:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        topic_slug = topic.lower().replace(' ', '_')
        results_dir = os.path.join('results', f'{timestamp}_{topic_slug}')
        os.makedirs(results_dir, exist_ok=True)
        logger.info(f"Created new output directory: {results_dir}")
        
    # 初始化或加载状态
    state = PipelineState(results_dir)
    state.state['params_hash'] = params_hash
    state.save_state()
    
    try:
        # 初始化组件
        logger.info("\nInitializing components...")
        generator = KeywordGenerator()
        crawler = ArxivCrawler()
        analyzer = AbstractAnalyzer()
        if download_papers:
            downloader = PaperDownloader(output_dir=os.path.join(results_dir, 'papers'))
            
        # 1. 生成关键词
        if not state.is_step_completed('generate_keywords'):
            logger.info("\n1. Testing keyword generation...")
            state.set_current_step('generate_keywords')
            keywords = generator.generate_keywords(topic)
            logger.info(f"Generated keywords: {json.dumps(keywords, indent=2)}")
            save_json(keywords, os.path.join(results_dir, 'keywords.json'))
            logger.info(f"Keywords saved to {os.path.join(results_dir, 'keywords.json')}")
            state.step_completed('generate_keywords')
        else:
            logger.info("\n1. Loading existing keywords...")
            with open(os.path.join(results_dir, 'keywords.json'), 'r') as f:
                keywords = json.load(f)
        
        # 2. 搜索论文
        if not state.is_step_completed('search_papers'):
            logger.info("\n2. Testing paper crawling...")
            state.set_current_step('search_papers')
            papers = crawler.search_papers(
                keywords=keywords,
                max_results=max_results,
                date_start=date_start,
                date_end=None,
                sort_by=sort_by,
                ascending=ascending,
                categories=categories,
                authors=None
            )
            logger.info(f"Found {len(papers)} papers")
            save_json(papers, os.path.join(results_dir, 'papers.json'))
            logger.info(f"Papers saved to {os.path.join(results_dir, 'papers.json')}")
            state.step_completed('search_papers')
        else:
            logger.info("\n2. Loading existing paper search results...")
            with open(os.path.join(results_dir, 'papers.json'), 'r') as f:
                papers = json.load(f)
        
        # 3. 分析摘要
        if not state.is_step_completed('analyze_abstracts'):
            logger.info("\n3. Testing abstract analysis...")
            state.set_current_step('analyze_abstracts')
            analyzed_papers = analyzer.analyze_abstracts(papers)
            logger.info(f"Analyzed {len(analyzed_papers)} papers")
            save_json(analyzed_papers, os.path.join(results_dir, 'analysis.json'))
            logger.info(f"Analysis results saved to {os.path.join(results_dir, 'analysis.json')}")
            state.step_completed('analyze_abstracts')
        else:
            logger.info("\n3. Loading existing analysis results...")
            with open(os.path.join(results_dir, 'analysis.json'), 'r') as f:
                analyzed_papers = json.load(f)
        
        # 4. 下载论文
        if download_papers and not state.is_step_completed('download_papers'):
            logger.info("\n4. Downloading papers...")
            state.set_current_step('download_papers')
            download_results = downloader.download_papers(analyzed_papers)
            logger.info(f"Downloaded {len([p for p in download_results if p['download_status'] == 'success'])} papers")
            save_json(download_results, os.path.join(results_dir, 'download_results.json'))
            logger.info(f"Download results saved to {os.path.join(results_dir, 'download_results.json')}")
            state.step_completed('download_papers')
        elif download_papers:
            logger.info("\n4. Papers already downloaded")
            with open(os.path.join(results_dir, 'download_results.json'), 'r') as f:
                download_results = json.load(f)
        
        # 5. 生成总结
        if not state.is_step_completed('generate_summary'):
            logger.info("\n5. Generating summary...")
            state.set_current_step('generate_summary')
            summary = {
                'total_papers': len(papers),
                'date_range': {
                    'start': date_start,
                    'end': 'present'
                },
                'topic': topic,
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'downloads': {
                    'total_attempted': len(papers),
                    'successful': len([p for p in download_results if p['download_status'] == 'success']) if download_papers else 0,
                    'failed': len([p for p in download_results if p['download_status'] == 'failed']) if download_papers else 0,
                    'skipped': len([p for p in download_results if p['download_status'] == 'exists']) if download_papers else 0
                } if download_papers else None
            }
            save_json(summary, os.path.join(results_dir, 'summary.json'))
            logger.info(f"Summary saved to {os.path.join(results_dir, 'summary.json')}")
            state.step_completed('generate_summary')
            
        logger.info("\nTest pipeline completed successfully!")
        logger.info(f"All results saved in: {results_dir}")
        
    except Exception as e:
        error_msg = f"Pipeline error: {str(e)}"
        logger.error(error_msg)
        state.set_error(error_msg)
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Research paper analysis pipeline')
    parser.add_argument('--topic', type=str, default="watermark attack language model",
                      help='Research topic to search for')
    parser.add_argument('--date_start', type=str, default="2023-01-01",
                      help='Start date for paper search (YYYY-MM-DD)')
    parser.add_argument('--max_results', type=int, default=50,
                      help='Maximum number of papers to retrieve')
    parser.add_argument('--no_download', action='store_true',
                      help='Skip paper downloading')
    
    args = parser.parse_args()
    
    test_pipeline(
        topic=args.topic,
        date_start=args.date_start,
        max_results=args.max_results,
        categories=None,
        sort_by=SortBy.SUBMITTED,
        ascending=False,
        download_papers=not args.no_download
    )