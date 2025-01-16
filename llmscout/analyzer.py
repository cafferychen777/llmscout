from openai import OpenAI
import yaml
from typing import List, Dict
import json
import time
from .logger import setup_logger

class AbstractAnalyzer:
    def __init__(self, config_path: str = 'config/api_keys.yaml'):
        self.logger = setup_logger('abstract_analyzer')
        self.logger.info("Initializing AbstractAnalyzer...")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.client = OpenAI(api_key=config['openai_api_key'])
                self.logger.info("Successfully initialized OpenAI client")
        except Exception as e:
            self.logger.error(f"Error initializing AbstractAnalyzer: {str(e)}")
            raise
            
    def analyze_abstracts(self, papers: List[Dict]) -> List[Dict]:
        """Analyze paper abstracts using LLM"""
        analyzed_papers = []
        total = len(papers)
        
        self.logger.info(f"\nAnalyzing {total} papers...")
        for i, paper in enumerate(papers, 1):
            self.logger.info(f"\nAnalyzing paper {i}/{total}: {paper['title']}")
            try:
                analysis = self._analyze_single_abstract(paper)
                analyzed_papers.append({**paper, **analysis})
                self.logger.info("✓ Analysis complete")
            except Exception as e:
                self.logger.error(f"Error analyzing paper: {str(e)}")
                continue
            time.sleep(1)  # 避免过快请求
            
        self.logger.info(f"\nCompleted analysis of {len(analyzed_papers)} papers")
        return analyzed_papers
        
    def _analyze_single_abstract(self, paper: Dict) -> Dict:
        """Analyze a single paper's abstract"""
        prompt = f"""
        Analyze the following research paper about watermarking and attacks in language models:
        
        Title: {paper['title']}
        Abstract: {paper['abstract']}
        Published: {paper.get('published', 'N/A')}
        
        Generate a detailed analysis in JSON format with the following structure:
        {{
            "summary": "Brief summary of the paper",
            "key_contributions": [
                "contribution1",
                "contribution2"
            ],
            "methodology": {{
                "approach": "Main technical approach",
                "techniques": ["technique1", "technique2"],
                "datasets": ["dataset1", "dataset2"]
            }},
            "findings": [
                "finding1",
                "finding2"
            ],
            "impact": {{
                "strengths": ["strength1", "strength2"],
                "limitations": ["limitation1", "limitation2"],
                "future_work": ["suggestion1", "suggestion2"]
            }},
            "relevance_score": 0-10,
            "watermark_type": "type of watermarking discussed",
            "attack_methods": ["method1", "method2"],
            "defense_strategies": ["strategy1", "strategy2"],
            "evaluation_metrics": ["metric1", "metric2"]
        }}
        
        Guidelines:
        1. relevance_score: Rate from 0-10 how relevant the paper is to watermarking and attacks in language models
        2. Be specific about technical details
        3. Focus on watermarking and attack aspects
        4. Identify practical implications
        5. Note any novel contributions
        """
        
        self.logger.debug(f"Sending paper to OpenAI API for analysis: {paper['title']}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research paper analyzer specializing in AI security and watermarking. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse JSON response
            analysis = json.loads(response.choices[0].message.content)
            self.logger.debug(f"Successfully analyzed paper: {paper['title']}")
            return analysis
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response for paper {paper['title']}: {str(e)}")
            return self._generate_error_analysis()
            
        except Exception as e:
            self.logger.error(f"Error during analysis of paper {paper['title']}: {str(e)}")
            return self._generate_error_analysis()
            
    def _generate_error_analysis(self) -> Dict:
        """生成错误时的默认分析结果"""
        self.logger.warning("Generating error analysis result")
        return {
            "summary": "Error analyzing paper",
            "key_contributions": ["Analysis failed"],
            "methodology": {
                "approach": "Unknown",
                "techniques": [],
                "datasets": []
            },
            "findings": ["Analysis error"],
            "impact": {
                "strengths": [],
                "limitations": ["Analysis failed"],
                "future_work": []
            },
            "relevance_score": 0,
            "watermark_type": "Unknown",
            "attack_methods": [],
            "defense_strategies": [],
            "evaluation_metrics": []
        }