from openai import OpenAI
import yaml
import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from .logger import setup_logger

class KeywordGenerator:
    def __init__(self, config_path: str = 'config/api_keys.yaml'):
        self.logger = setup_logger('keyword_generator')
        self.logger.info("Initializing KeywordGenerator...")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.client = OpenAI(api_key=config['openai_api_key'])
                self.logger.info("Successfully initialized OpenAI client")
        except Exception as e:
            self.logger.error(f"Error initializing KeywordGenerator: {str(e)}")
            raise
        
    def generate_keywords(
        self, 
        topic: str,
        save: bool = False,
        output_dir: str = 'output/keywords',
        filename: str = None
    ) -> Dict[str, List[str]]:
        """
        Generate search keywords for a given research topic
        
        Args:
            topic: 研究主题
            save: 是否保存到文件
            output_dir: 保存目录路径
            filename: 保存的文件名(不含扩展名)。如果为None则使用时间戳_主题名
        """
        self.logger.info(f"Generating keywords for topic: {topic}")
        
        prompt = f'''
        For the research topic: "{topic}"
        Generate a JSON object with search terms specifically focused on watermark attacks in language models.
        Focus on technical terms that would appear in paper titles.
        
        The keywords should follow this structure:
        {{
            "primary": ["exact technical terms"],
            "secondary": [],
            "methodology": [],
            "application": []
        }}

        Guidelines for primary keywords:
        - Include variations of "watermark attack" and "watermarking attack"
        - Include specific attack types (e.g., "watermark removal attack")
        - Use both full terms and common abbreviations (e.g., "LLM watermark attack")
        - Focus on attack-specific terminology
        - Keep terms precise and technical
        
        Example terms:
        - "watermark attack"
        - "LLM watermark removal"
        - "language model watermark attack"
        '''
        
        try:
            self.logger.debug(f"Sending prompt to OpenAI API: {prompt}")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research keyword generator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse JSON response
            keywords = json.loads(response.choices[0].message.content)
            self.logger.info(f"Successfully generated keywords: {json.dumps(keywords, indent=2)}")
            
            # Save to file if requested
            if save:
                # Create output directory if it doesn't exist
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Generate filename if not provided
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{topic.replace(' ', '_')}"
                
                # Add .json extension if not present
                if not filename.endswith('.json'):
                    filename += '.json'
                    
                # Save to file
                with open(output_path / filename, 'w', encoding='utf-8') as f:
                    json.dump(keywords, f, ensure_ascii=False, indent=2)
                    self.logger.info(f"Saved keywords to file: {filename}")
                    
            return keywords
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing OpenAI response: {str(e)}")
            return self._generate_default_keywords(topic)
            
        except Exception as e:
            self.logger.error(f"Error during keyword generation: {str(e)}")
            return self._generate_default_keywords(topic)
            
    def _generate_default_keywords(self, topic: str) -> Dict[str, List[str]]:
        """生成默认关键词，用于错误情况"""
        self.logger.warning("Falling back to default keywords")
        words = topic.lower().split()
        return {
            'primary': [topic] + [' '.join(words[i:i+2]) for i in range(len(words)-1)],
            'secondary': [],
            'methodology': [],
            'application': []
        }