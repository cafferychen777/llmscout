import json
import os
from scripts.downloader import PaperDownloader
from scripts.logger import setup_logger

def download_from_results(results_dir: str):
    """从已有的结果目录下载论文"""
    logger = setup_logger('download_papers')
    
    # 读取分析结果
    analysis_file = os.path.join(results_dir, 'analysis.json')
    if not os.path.exists(analysis_file):
        logger.error(f"Analysis file not found: {analysis_file}")
        return
        
    logger.info(f"Reading analysis from: {analysis_file}")
    with open(analysis_file, 'r') as f:
        papers = json.load(f)
        
    # 创建下载器
    papers_dir = os.path.join(results_dir, 'papers')
    downloader = PaperDownloader(output_dir=papers_dir)
    
    # 下载论文
    download_results = downloader.download_papers(papers)
    
    # 保存下载结果
    results_file = os.path.join(results_dir, 'download_results.json')
    with open(results_file, 'w') as f:
        json.dump(download_results, f, indent=2)
        
    # 打印统计信息
    successful = len([p for p in download_results if p['download_status'] == 'success'])
    failed = len([p for p in download_results if p['download_status'] == 'failed'])
    skipped = len([p for p in download_results if p['download_status'] == 'exists'])
    
    logger.info("\nDownload Summary:")
    logger.info(f"Total papers: {len(papers)}")
    logger.info(f"Successfully downloaded: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Already existed: {skipped}")
    logger.info(f"\nResults saved to: {results_file}")
    logger.info(f"Papers downloaded to: {papers_dir}")

if __name__ == "__main__":
    # 使用最近的结果目录
    results_dir = "results/20250115_185757_watermark_attack_language_model"
    download_from_results(results_dir)
