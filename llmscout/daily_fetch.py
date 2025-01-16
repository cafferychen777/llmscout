import schedule
import time
from datetime import datetime
from pathlib import Path
from keyword_generator import KeywordGenerator
from arxiv_crawler import ArxivCrawler
from abstract_analyzer import AbstractAnalyzer
import json
from tqdm import tqdm
import os
import sys

class NotificationManager:
    def send_mac_notification(self, title: str, message: str):
        """Send Mac notification"""
        try:
            os.system(f"""
                osascript -e 'tell application "System Events"
                    display notification "{message}" with title "{title}" sound name "default"
                end tell'
            """)
        except Exception as e:
            print(f"Failed to send Mac notification: {str(e)}")

class DailyKeywordFetcher:
    def __init__(
        self,
        topic: str,
        output_dir: str = 'output/daily_keywords',
        config_path: str = 'config/api_keys.yaml'
    ):
        self.topic = topic
        self.output_dir = Path(output_dir)
        self.generator = KeywordGenerator(config_path)
        self.crawler = ArxivCrawler()
        self.analyzer = AbstractAnalyzer(config_path)
        self.notifier = NotificationManager()
        
    def fetch_and_save(self):
        """Fetch keywords, search papers, analyze and save results"""
        try:
            today = datetime.now()
            date_dir = self.output_dir / f"{today.year}" / f"{today.month:02d}"
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Generate keywords
            print(f"[{datetime.now()}] Generating keywords for '{self.topic}'...")
            keywords = self.generator.generate_keywords(
                topic=self.topic,
                save=True,
                output_dir=str(date_dir),
                filename=f"{today.strftime('%Y%m%d')}_keywords_{self.topic.replace(' ', '_')}.json"
            )
            
            # 2. Search papers
            print(f"[{datetime.now()}] Searching papers on arXiv...")
            papers = self.crawler.search_papers(keywords)
            paper_count = len(papers)
            print(f"[{datetime.now()}] Found {paper_count} papers")
            
            # Notify about search results
            notification_title = f"ArXiv Daily Update"
            if not papers:
                notification_msg = f"No new papers found today for: {self.topic}"
                self.notifier.send_mac_notification(notification_title, notification_msg)
                
                empty_result = {
                    "date": today.strftime('%Y-%m-%d'),
                    "topic": self.topic,
                    "papers_found": 0,
                    "message": "No papers found for this date"
                }
                filename = f"{today.strftime('%Y%m%d')}_analysis_{self.topic.replace(' ', '_')}_empty.json"
                with open(date_dir / filename, 'w', encoding='utf-8') as f:
                    json.dump(empty_result, f, ensure_ascii=False, indent=2)
                return
            
            # 3. Analyze papers
            print(f"[{datetime.now()}] Starting paper analysis...")
            analyzed_papers = []
            
            for i, paper in enumerate(tqdm(papers, desc="Analyzing papers")):
                try:
                    print(f"\n[{datetime.now()}] Analyzing paper {i+1}/{paper_count}: {paper['title']}")
                    analysis = self.analyzer.analyze_abstracts([paper])[0]
                    analyzed_papers.append(analysis)
                    
                    if (i + 1) % 10 == 0:
                        self._save_intermediate_results(analyzed_papers, date_dir, today)
                        print(f"[{datetime.now()}] Saved intermediate results for {i+1} papers")
                        
                except Exception as e:
                    print(f"[{datetime.now()}] Error analyzing paper {i+1}: {str(e)}")
                    continue
            
            # 4. Save and notify
            if analyzed_papers:
                self._save_final_results(analyzed_papers, date_dir, today)
                
                # Success notification with paper count
                notification_msg = f"Found and analyzed {len(analyzed_papers)} new papers for: {self.topic}"
                self.notifier.send_mac_notification(notification_title, notification_msg)
            else:
                notification_msg = f"No papers were successfully analyzed for: {self.topic}"
                self.notifier.send_mac_notification(notification_title, notification_msg)
            
        except Exception as e:
            error_msg = f"Error in daily fetch: {str(e)}"
            self.notifier.send_mac_notification("ArXiv Fetch Error", error_msg)
            print(f"[{datetime.now()}] {error_msg}")
            
    def _save_intermediate_results(self, papers, date_dir, today):
        """Save intermediate results with timestamp"""
        if not papers:
            return
        timestamp = today.strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_analysis_{self.topic.replace(' ', '_')}_intermediate.json"
        with open(date_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
            
    def _save_final_results(self, papers, date_dir, today):
        """Save final results"""
        if not papers:
            return
        filename = f"{today.strftime('%Y%m%d')}_analysis_{self.topic.replace(' ', '_')}.json"
        with open(date_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)

def main():
    # Initialize fetcher
    fetcher = DailyKeywordFetcher(
        topic="Longitudinal Microbiome Analysis",
        output_dir="output/daily_keywords"
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once and exit
        fetcher.fetch_and_save()
        return
    
    # Schedule the job to run daily at specific time
    schedule.every().day.at("10:00").do(fetcher.fetch_and_save)
    
    # Run the first time immediately
    fetcher.fetch_and_save()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting daily keyword fetcher...")
    main() 