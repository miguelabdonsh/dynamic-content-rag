"""
Crawler optimized for CoinDesk - Ready for RAG
Only extracts from latest-crypto-news and markets
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoinDeskCrawler:
    """Crawler optimized for CoinDesk with duplicate prevention"""
    
    def __init__(self, crawlai_url="http://localhost:11235"):
        self.crawlai_url = crawlai_url
        self.output_dir = Path("data/crawled")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Target sections
        self.base_url = "https://www.coindesk.com"
        self.sections = [
            "https://www.coindesk.com/latest-crypto-news",
            "https://www.coindesk.com/markets"
        ]
        
        # Configuration
        self.max_articles_per_section = 15
        self.request_delay = 2
        
    async def check_crawlai(self):
        """Check CrawlAI"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.crawlai_url}/health") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def crawl_url(self, url: str) -> dict:
        """Crawl URL using CrawlAI API"""
        payload = {
            "urls": [url],
            "browser_config": {"type": "BrowserConfig", "params": {"headless": True}},
            "crawler_config": {
                "type": "CrawlerRunConfig", 
                "params": {
                    "word_count_threshold": 10,
                    "exclude_external_links": False,
                    "process_iframes": False,
                    "cache_mode": "bypass"
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.post(f"{self.crawlai_url}/crawl", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error {response.status} crawling {url}")
                        return {"success": False}
        except Exception as e:
            logger.error(f"Exception crawling {url}: {e}")
            return {"success": False}
    
    def extract_article_links(self, crawl_result: dict) -> list:
        """Extract valid article links"""
        if not crawl_result.get("success") or not crawl_result.get("results"):
            return []
        
        result = crawl_result["results"][0]
        links_data = result.get("links", {})
        links = []
        
        # Process internal and external links
        for link_type in ["internal", "external"]:
            for link_info in links_data.get(link_type, []):
                href = link_info.get("href", "") if isinstance(link_info, dict) else str(link_info)
                
                if href.startswith("/"):
                    full_url = f"{self.base_url}{href}"
                elif href.startswith(self.base_url):
                    full_url = href
                else:
                    continue
                
                if self.is_valid_article(full_url):
                    links.append(full_url)
        
        return list(set(links))[:self.max_articles_per_section]
    
    def is_valid_article(self, url: str) -> bool:
        """Check if it's a valid article"""
        if not url.startswith(self.base_url):
            return False
        
        # Article pattern with date
        if re.search(r'/(?:markets|policy|tech|finance|news|business|opinion)/202[0-9]/\d{2}/\d{2}/.+', url):
            return True
        
        # Valid long articles
        url_parts = url.replace(self.base_url, '').split('/')
        if len(url_parts) >= 4 and len(url_parts[-1]) > 20:
            # Exclude unwanted URLs
            exclude_patterns = [
                r'\.(?:ico|svg|png|jpg|gif|css|js|pdf)$',
                r'/(?:favicon|logo|icon|img|images|static|assets|tag|author|price|newsletters|videos|podcasts|events|advertise|about|contact|privacy|terms|careers|search|feed|rss)',
                r'[#?]'
            ]
            
            return not any(re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns)
        
        return False
    
    def extract_title_from_url(self, url: str) -> str:
        """Extract title from URL"""
        title = url.split('/')[-1]
        title = re.sub(r'[?#].*', '', title)  # Remove parameters
        return title
    
    def article_exists(self, title: str) -> bool:
        """Check if an article with this title already exists"""
        pattern = f"*{title}*.json"
        existing_files = list(self.output_dir.glob(pattern))
        if existing_files:
            logger.info(f"Article already exists: {title}")
            return True
        return False
    
    def clean_content_for_rag(self, markdown: str) -> str:
        """Aggressively clean content for RAG"""
        if not markdown:
            return ""
        
        # Remove unwanted elements in one pass
        markdown = re.sub(r'!\[.*?\]\(.*?\)', '', markdown)  
        markdown = re.sub(r'\[.*?\]\(.*?\)', '', markdown)   
        markdown = re.sub(r'#{1,6}\s*', '', markdown)       
        markdown = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', markdown)  
        markdown = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', markdown)    
        
        lines = markdown.split('\n')
        cleaned_lines = []
        
        # Aggressive patterns for RAG
        skip_patterns = [
            r'^\[.*\$.*\]',          
            r'^\* \[',               
            r'^(?:Sign up|Subscribe|Privacy|Terms|Cookie|English|Back to menu)$',
            r'^(?:News|Markets|Prices|Data|Events|Videos|Podcasts)$',
            r'CoinDesk|coindesk|COINDESK',  
            r'©\s*20\d\d',           
            r'Select Language',       
            r'Share this article',    
            r'Copy link',            
            r'Updated.*Published',    
            r'By \[.*\]',           
            r'DISCLOSURE.*POLICES',   
            r'We Care About.*Privacy', 
            r'About Your Privacy',    
            r'Strictly Necessary',    
            r'Performance Cookies',   
            r'Your device might',     
            r'Information about',     
            r'Consent Leg\.Interest', 
            r'View Illustrations',    
            r'List of IAB Vendors',   
        ]
        
        for line in lines:
            line = line.strip()
            
            # Skip empty or very short lines
            if not line or len(line) < 10:
                continue
            
            # Check patterns to skip
            should_skip = any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns)
            
            # Skip lines that look like navigation or metadata
            if (line.startswith('[') or 
                line.startswith('*') or 
                line.startswith('#') or
                line.startswith('By ') or
                line.endswith(' ago') or
                'linkedin.com' in line.lower() or
                'twitter.com' in line.lower() or
                'facebook.com' in line.lower()):
                should_skip = True
            
            if not should_skip:
                cleaned_lines.append(line)
        
        # Join and clean extra spaces
        content = '\n'.join(cleaned_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)  
        content = re.sub(r'[ \t]+', ' ', content)     
        
        return content.strip()
    
    def extract_article(self, crawl_result: dict, url: str) -> dict:
        """Extract and clean article"""
        if not crawl_result.get("success") or not crawl_result.get("results"):
            return None
        
        result = crawl_result["results"][0]
        markdown_data = result.get("markdown", {})
        
        # Get best available content
        if isinstance(markdown_data, dict):
            markdown = markdown_data.get("fit_markdown") or markdown_data.get("raw_markdown", "")
        else:
            markdown = str(markdown_data) if markdown_data else ""
        
        title = self.extract_title_from_url(url)
        content = self.clean_content_for_rag(markdown)
        
        # Validate minimum content
        if len(content) < 200 or not title:
            return None
        
        return {
            "title": title,
            "url": url,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    
    async def crawl_section(self, section_url: str) -> list:
        """Crawl articles from a section"""
        section_name = section_url.split('/')[-1]
        logger.info(f"Crawling section: {section_name}")
        
        # Get section page
        crawl_result = await self.crawl_url(section_url)
        if not crawl_result.get("success"):
            logger.error(f"Could not get section: {section_name}")
            return []
        
        # Extract links
        article_links = self.extract_article_links(crawl_result)
        if not article_links:
            logger.warning(f"No articles found in {section_name}")
            return []
        
        logger.info(f"Found {len(article_links)} articles in {section_name}")
        
        # Process articles
        articles = []
        for i, article_url in enumerate(article_links, 1):
            logger.info(f"Processing {i}/{len(article_links)}: {article_url}")
            
            # Check if already exists
            title = self.extract_title_from_url(article_url)
            if self.article_exists(title):
                continue
            
            # Crawl article
            article_crawl = await self.crawl_url(article_url)
            article = self.extract_article(article_crawl, article_url)
            
            if article:
                articles.append(article)
                logger.info(f"Extracted: {title[:60]}...")
            else:
                logger.warning(f"Could not extract: {article_url}")
            
            await asyncio.sleep(self.request_delay)
        
        logger.info(f"{section_name} completed: {len(articles)} new articles")
        return articles
    
    def save_article(self, article: dict, section_name: str):
        """Save article if not exists"""
        if self.article_exists(article['title']):
            return
        
        # Generate clean file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = re.sub(r'[^\w\-]', '', article['title'].replace('-', '_'))[:50]
        filename = f"{section_name}_{safe_title}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved: {filename}")
    
    async def run(self):
        """Run crawler"""
        logger.info("Starting optimized CoinDesk Crawler...")
        
        if not await self.check_crawlai():
            logger.error("CrawlAI not available")
            return
        
        try:
            total_new_articles = 0
            
            for section_url in self.sections:
                section_name = section_url.split('/')[-1]
                articles = await self.crawl_section(section_url)
                
                # Save new articles
                for article in articles:
                    self.save_article(article, section_name)
                    total_new_articles += 1
            
            logger.info(f"Crawler completed: {total_new_articles} new articles saved")
            
        except Exception as e:
            logger.error(f"Error in crawler: {e}")

async def main():
    """Main function"""
    crawler = CoinDeskCrawler()
    await crawler.run()

if __name__ == "__main__":
    asyncio.run(main())
