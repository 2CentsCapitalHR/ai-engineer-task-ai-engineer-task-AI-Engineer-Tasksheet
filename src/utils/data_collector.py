"""Data collection utilities for ADGM documents and regulations."""

import requests
import os
from pathlib import Path
from typing import List, Dict, Optional
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ADGMDataCollector:
    """Collects ADGM documents and regulations from official sources."""
    
    def __init__(self, data_dir: str = "data/adgm_docs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_document(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """Download a document from URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if not filename:
                # Extract filename from URL or Content-Disposition header
                if 'Content-Disposition' in response.headers:
                    content_disp = response.headers['Content-Disposition']
                    if 'filename=' in content_disp:
                        filename = content_disp.split('filename=')[1].strip('"')
                else:
                    filename = os.path.basename(urlparse(url).path)
                
                if not filename or filename == '/':
                    filename = f"document_{int(time.time())}.pdf"
            
            file_path = self.data_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded: {filename}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
    
    def scrape_page_content(self, url: str) -> Dict[str, str]:
        """Scrape text content from a webpage."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"
            
            # Extract main content
            content_selectors = [
                'main', '.main-content', '.content', 
                'article', '.article', '#content'
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup.find('body')
            
            text_content = content.get_text(separator='\n', strip=True) if content else ""
            
            return {
                'title': title_text,
                'content': text_content,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return {'title': '', 'content': '', 'url': url}
    
    def collect_adgm_reference_data(self) -> List[Dict[str, str]]:
        """Collect ADGM reference data from official sources."""
        
        # ADGM reference URLs from the task description
        reference_urls = [
            "https://www.adgm.com/registration-authority/registration-and-incorporation",
            "https://www.adgm.com/setting-up",
            "https://www.adgm.com/legal-framework/guidance-and-policy-statements",
            "https://www.adgm.com/operating-in-adgm/obligations-of-adgm-registered-entities/annual-filings/annual-accounts",
            "https://www.adgm.com/operating-in-adgm/post-registration-services/letters-and-permits"
        ]
        
        # Document download URLs
        document_urls = [
            "https://assets.adgm.com/download/assets/adgm-ra-resolution-multipleincorporate-shareholders-LTDincorporationv2.docx/186a12846c3911efa4e6c6223862cd87",
            "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+Template+-+ER+2024+(Feb+2025).docx/ee14b252edbe11efa63b12b3a30e5e3a",
            "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+-+ER+2019+-+Short+Version+(May+2024).docx/33b57a92ecfe11ef97a536cc36767ef8",
            "https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/branch-non-financial-services-20231228.pdf",
            "https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/private-company-limited-by-guarantee-non-financial-services-20231228.pdf",
            "https://www.adgm.com/documents/office-of-data-protection/templates/adgm-dpr-2021-appropriate-policy-document.pdf",
            "https://assets.adgm.com/download/assets/Templates_SHReso_AmendmentArticles-v1-20220107.docx/97120d7c5af911efae4b1e183375c0b2?forcedownload=1"
        ]
        
        collected_data = []
        
        # Scrape reference pages
        logger.info("Collecting ADGM reference page content...")
        for url in reference_urls:
            logger.info(f"Scraping: {url}")
            page_data = self.scrape_page_content(url)
            if page_data['content']:
                collected_data.append({
                    'type': 'webpage',
                    'title': page_data['title'],
                    'content': page_data['content'],
                    'source': url,
                    'category': self._categorize_url(url)
                })
            time.sleep(1)  # Be respectful to the server
        
        # Download documents
        logger.info("Downloading ADGM documents...")
        for url in document_urls:
            logger.info(f"Downloading: {url}")
            file_path = self.download_document(url)
            if file_path:
                collected_data.append({
                    'type': 'document',
                    'title': os.path.basename(file_path),
                    'file_path': file_path,
                    'source': url,
                    'category': self._categorize_document(os.path.basename(file_path))
                })
            time.sleep(1)  # Be respectful to the server
        
        return collected_data
    
    def _categorize_url(self, url: str) -> str:
        """Categorize URL based on its path."""
        if 'registration-and-incorporation' in url:
            return 'company_formation'
        elif 'setting-up' in url:
            return 'setup_guidance'
        elif 'legal-framework' in url:
            return 'legal_framework'
        elif 'annual-filings' in url:
            return 'compliance'
        elif 'letters-and-permits' in url:
            return 'permits'
        else:
            return 'general'
    
    def _categorize_document(self, filename: str) -> str:
        """Categorize document based on filename."""
        filename_lower = filename.lower()
        
        if 'employment' in filename_lower or 'contract' in filename_lower:
            return 'employment'
        elif 'resolution' in filename_lower or 'shareholder' in filename_lower:
            return 'company_formation'
        elif 'checklist' in filename_lower:
            return 'compliance'
        elif 'data-protection' in filename_lower or 'policy' in filename_lower:
            return 'compliance'
        else:
            return 'general'


def collect_adgm_data() -> List[Dict[str, str]]:
    """Main function to collect ADGM data."""
    collector = ADGMDataCollector()
    return collector.collect_adgm_reference_data()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = collect_adgm_data()
    print(f"Collected {len(data)} items from ADGM sources")
