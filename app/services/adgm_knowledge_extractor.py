"""
Enhanced ADGM Knowledge Extractor with Web Scraping and Document Processing
"""

import os
import json
import asyncio
import aiohttp
import requests
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from typing import Dict, List, Optional
import re
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import mammoth
from urllib.parse import urljoin, urlparse

class ADGMKnowledgeExtractor:
    def __init__(self, chroma_db_path: str = "./data/chroma_db"):
        self.chroma_db_path = chroma_db_path
        self.chroma_client = None
        self.collections = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # ADGM data sources from your README
        self.adgm_sources = {
            'web_pages': [
                {
                    'url': 'https://www.adgm.com/registration-authority/registration-and-incorporation',
                    'category': 'incorporation',
                    'description': 'General Incorporation, AoA, MoA, Registers, UBO, Board Resolutions'
                },
                {
                    'url': 'https://www.adgm.com/setting-up',
                    'category': 'incorporation',
                    'description': 'Incorporation, SPV, LLC, Other Forms & Templates'
                },
                {
                    'url': 'https://www.adgm.com/legal-framework/guidance-and-policy-statements',
                    'category': 'compliance',
                    'description': 'Guidance, Templates, Policy Statements'
                },
                {
                    'url': 'https://www.adgm.com/operating-in-adgm/obligations-of-adgm-registered-entities/annual-filings/annual-accounts',
                    'category': 'compliance',
                    'description': 'Annual Accounts & Filings'
                }
            ],
            'pdf_documents': [
                {
                    'url': 'https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/branch-non-financial-services-20231228.pdf',
                    'category': 'compliance',
                    'doc_type': 'checklist',
                    'description': 'Checklist – Company Set-up (Branch Non-Financial Services)'
                },
                {
                    'url': 'https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/private-company-limited-by-guarantee-non-financial-services-20231228.pdf',
                    'category': 'compliance',
                    'doc_type': 'checklist',
                    'description': 'Checklist – Private Company Limited'
                }
            ],
            'docx_templates': [
                {
                    'url': 'https://assets.adgm.com/download/assets/adgm-ra-resolution-multiple-incorporate-shareholders-LTD-incorporation-v2.docx',
                    'category': 'templates',
                    'doc_type': 'resolution',
                    'description': 'Resolution for Incorporation (LTD – Multiple Shareholders)'
                },
                {
                    'url': 'https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+Template+-+ER+2024+(Feb+2025).docx',
                    'category': 'employment',
                    'doc_type': 'contract',
                    'description': 'Standard Employment Contract Template (2024 update)'
                },
                {
                    'url': 'https://assets.adgm.com/download/assets/Templates_SHReso_AmendmentArticles-v1-20220107.docx',
                    'category': 'templates',
                    'doc_type': 'resolution',
                    'description': 'Shareholder Resolution – Amendment of Articles'
                }
            ]
        }
        
        # Enhanced ADGM knowledge
        self.enhanced_adgm_knowledge = [
            {
                "id": "companies_reg_001",
                "document": "Companies Regulations 2020",
                "content": "Every company incorporated in ADGM must have a registered office within ADGM jurisdiction at Al Maryah Island, Abu Dhabi.",
                "section": "Registration Requirements",
                "regulation_ref": "CR-2020-001",
                "category": "incorporation",
                "keywords": ["registered office", "jurisdiction", "incorporation", "ADGM"]
            },
            {
                "id": "companies_reg_002",
                "document": "Companies Regulations 2020", 
                "content": "Private companies require minimum authorized share capital of AED 150,000. Public companies require minimum AED 2,000,000.",
                "section": "Share Capital Requirements",
                "regulation_ref": "CR-2020-015",
                "category": "capital",
                "keywords": ["share capital", "minimum capital", "private company", "public company", "AED"]
            },
            {
                "id": "company_names_001",
                "document": "Company Names Regulations",
                "content": "Company names must end with appropriate legal suffix: Limited/Ltd for private companies, PLC for public companies, or LLC for limited liability companies. Cannot contain prohibited words: Bank, Insurance, Islamic (unless licensed), Trust, Fund Management.",
                "section": "Company Name Requirements",
                "regulation_ref": "CN-2020-008",
                "category": "incorporation",
                "keywords": ["company name", "legal suffix", "Limited", "LLC", "PLC", "prohibited names"]
            },
            {
                "id": "directors_req_001",
                "document": "Directors Regulations 2020",
                "content": "Every company must have at least one natural person director who is ordinarily resident in the UAE or holds UAE residency visa.",
                "section": "Director Requirements",
                "regulation_ref": "DIR-2020-012",
                "category": "governance",
                "keywords": ["directors", "natural person", "UAE resident", "residency visa"]
            },
            {
                "id": "memorandum_req_001",
                "document": "Memorandum Requirements Guide",
                "content": "Memorandum of Association must include: company name clause, registered office clause, objects clause, liability clause, and share capital clause with subscriber details.",
                "section": "Memorandum Content",
                "regulation_ref": "MEM-2020-001",
                "category": "memorandum",
                "keywords": ["memorandum", "company name clause", "objects clause", "liability clause", "subscribers"]
            }
        ]
    
    async def initialize_knowledge_base(self):
        """Initialize ChromaDB and populate with all ADGM sources"""
        try:
            # Ensure directory exists
            Path(self.chroma_db_path).mkdir(parents=True, exist_ok=True)
            
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create specialized collections
            await self._create_collections()
            
            # Populate with enhanced knowledge
            await self._populate_enhanced_knowledge()
            
            # Scrape and populate from web sources
            await self._populate_from_web_sources()
            
            # Download and process documents
            await self._populate_from_documents()
            
            self.logger.info("✅ ADGM Knowledge Base initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize knowledge base: {str(e)}")
            return False
    
    async def _create_collections(self):
        """Create specialized ChromaDB collections"""
        collection_configs = {
            "adgm_incorporation": "Company formation, incorporation, AoA, MoA templates and requirements",
            "adgm_compliance": "Compliance requirements, annual filings, regulatory guidance", 
            "adgm_employment": "Employment contracts, HR policies and requirements",
            "adgm_templates": "Official ADGM document templates and forms",
            "adgm_web_content": "Content scraped from ADGM website pages"
        }
        
        for name, description in collection_configs.items():
            try:
                collection = self.chroma_client.get_collection(name)
                self.logger.info(f"Retrieved existing collection: {name}")
            except ValueError:
                collection = self.chroma_client.create_collection(
                    name=name,
                    metadata={"description": description}
                )
                self.logger.info(f"Created new collection: {name}")
            
            self.collections[name] = collection
    
    async def _populate_enhanced_knowledge(self):
        """Populate with enhanced ADGM knowledge"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for item in self.enhanced_adgm_knowledge:
                documents.append(item['content'])
                metadatas.append({
                    'document': item['document'],
                    'section': item['section'],
                    'regulation_ref': item['regulation_ref'],
                    'category': item['category'],
                    'keywords': item['keywords'],
                    'source_type': 'enhanced_knowledge',
                    'last_updated': datetime.now().isoformat()
                })
                ids.append(item['id'])
            
            # Add to appropriate collection based on category
            collection_name = "adgm_incorporation"  # Default collection
            if documents:
                self.collections[collection_name].upsert(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                self.logger.info(f"✅ Added {len(documents)} enhanced knowledge documents")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to populate enhanced knowledge: {str(e)}")
    
    async def _populate_from_web_sources(self):
        """Scrape and populate from web sources"""
        for source in self.adgm_sources['web_pages']:
            try:
                await self._process_web_page(source)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                self.logger.error(f"❌ Failed to process web page {source['url']}: {str(e)}")
    
    async def _process_web_page(self, source):
        """Process individual web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source['url'], headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main content
            content_selectors = [
                'main', '.main-content', '.content', 
                '#content', '.page-content', 'article'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # Remove script and style elements
                    for script in content_div(["script", "style"]):
                        script.decompose()
                    content_text = content_div.get_text()
                    break
            
            if not content_text:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                content_text = ' '.join([p.get_text() for p in paragraphs])
            
            # Clean and chunk content
            content_text = self._clean_text(content_text)
            chunks = self._chunk_legal_content(content_text)
            
            # Add to ChromaDB
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    self.collections["adgm_web_content"].upsert(
                        documents=[chunk],
                        metadatas=[{
                            'source_url': source['url'],
                            'category': source['category'],
                            'description': source['description'],
                            'source_type': 'web_page',
                            'chunk_index': i,
                            'extraction_date': datetime.now().isoformat()
                        }],
                        ids=[f"web_{hash(source['url'])}_{i}"]
                    )
            
            self.logger.info(f"✅ Processed web page: {source['url']} ({len(chunks)} chunks)")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing web page {source['url']}: {str(e)}")
    
    async def _populate_from_documents(self):
        """Download and process PDF and DOCX documents"""
        # Process PDFs
        for source in self.adgm_sources['pdf_documents']:
            try:
                await self._process_pdf_document(source)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                self.logger.error(f"❌ Failed to process PDF {source['url']}: {str(e)}")
        
        # Process DOCX templates
        for source in self.adgm_sources['docx_templates']:
            try:
                await self._process_docx_template(source)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                self.logger.error(f"❌ Failed to process DOCX {source['url']}: {str(e)}")
    
    async def _process_pdf_document(self, source):
        """Process PDF document"""
        try:
            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            
            # Save temporarily
            temp_file = f"temp_{hash(source['url'])}.pdf"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # Extract text
            with open(temp_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
            
            # Clean up temp file
            os.remove(temp_file)
            
            # Process content
            full_text = self._clean_text(full_text)
            chunks = self._chunk_legal_content(full_text)
            
            # Determine collection based on category
            collection_name = f"adgm_{source['category']}"
            if collection_name not in self.collections:
                collection_name = "adgm_compliance"
            
            # Add to ChromaDB
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    self.collections[collection_name].upsert(
                        documents=[chunk],
                        metadatas=[{
                            'source_url': source['url'],
                            'category': source['category'],
                            'doc_type': source['doc_type'],
                            'description': source['description'],
                            'source_type': 'pdf_document',
                            'chunk_index': i,
                            'extraction_date': datetime.now().isoformat()
                        }],
                        ids=[f"pdf_{hash(source['url'])}_{i}"]
                    )
            
            self.logger.info(f"✅ Processed PDF: {source['description']} ({len(chunks)} chunks)")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing PDF {source['url']}: {str(e)}")
    
    async def _process_docx_template(self, source):
        """Process DOCX template"""
        try:
            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            
            # Save temporarily
            temp_file = f"temp_{hash(source['url'])}.docx"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # Extract text using mammoth for better formatting
            with open(temp_file, 'rb') as doc_file:
                result = mammoth.extract_raw_text(doc_file)
                full_text = result.value
            
            # Also extract structure using python-docx
            doc = Document(temp_file)
            structured_content = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    structured_content.append({
                        'text': para.text,
                        'style': para.style.name if para.style else 'Normal'
                    })
            
            # Clean up temp file
            os.remove(temp_file)
            
            # Process content
            full_text = self._clean_text(full_text)
            chunks = self._chunk_legal_content(full_text)
            
            # Add to templates collection
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    self.collections["adgm_templates"].upsert(
                        documents=[chunk],
                        metadatas=[{
                            'source_url': source['url'],
                            'category': source['category'],
                            'doc_type': source['doc_type'],
                            'description': source['description'],
                            'source_type': 'docx_template',
                            'chunk_index': i,
                            'extraction_date': datetime.now().isoformat()
                        }],
                        ids=[f"docx_{hash(source['url'])}_{i}"]
                    )
            
            self.logger.info(f"✅ Processed DOCX: {source['description']} ({len(chunks)} chunks)")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing DOCX {source['url']}: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep legal formatting
        text = re.sub(r'[^\w\s\.\,\;\:\(\)\[\]\-\'\"]', ' ', text)
        return text.strip()
    
    def _chunk_legal_content(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chunk content preserving legal structure"""
        if len(text) <= chunk_size:
            return [text]
        
        # Legal section markers
        legal_markers = [
            r'\d+\.\d+\s',  # Article numbers (1.1, 2.3)
            r'Article\s+\d+',  # Article references
            r'Section\s+\d+',  # Section references
            r'Clause\s+\d+',   # Clause references
            r'\([a-z]\)',      # Sub-clauses (a), (b), (c)
        ]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk + ". " + sentence) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    words = current_chunk.split()
                    if len(words) > overlap // 5:  # Approximate word overlap
                        current_chunk = " ".join(words[-(overlap // 5):]) + ". " + sentence
                    else:
                        current_chunk = sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 50]  # Filter very short chunks
    
    def query_knowledge_base(self, query: str, collection_names: List[str] = None, n_results: int = 5) -> Dict:
        """Enhanced query across multiple collections"""
        try:
            if collection_names is None:
                collection_names = list(self.collections.keys())
            
            all_results = []
            
            for collection_name in collection_names:
                if collection_name not in self.collections:
                    continue
                    
                try:
                    results = self.collections[collection_name].query(
                        query_texts=[query],
                        n_results=n_results
                    )
                    
                    # Add collection context to results
                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            all_results.append({
                                'content': doc,
                                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                                'distance': results['distances'][0][i] if results['distances'] else 1.0,
                                'collection': collection_name
                            })
                except Exception as e:
                    self.logger.error(f"Error querying collection {collection_name}: {str(e)}")
            
            # Sort by relevance (distance)
            all_results.sort(key=lambda x: x['distance'])
            
            return {
                "query": query,
                "results": all_results[:n_results],
                "count": len(all_results[:n_results]),
                "total_found": len(all_results)
            }
        
        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            return {"error": f"Query failed: {str(e)}"}
    
    def get_knowledge_stats(self) -> Dict:
        """Get comprehensive knowledge base statistics"""
        try:
            stats = {
                "collections": {},
                "total_documents": 0,
                "last_updated": datetime.now().isoformat(),
                "status": "operational"
            }
            
            for name, collection in self.collections.items():
                try:
                    count = collection.count()
                    stats["collections"][name] = count
                    stats["total_documents"] += count
                except Exception as e:
                    stats["collections"][name] = f"Error: {str(e)}"
            
            return stats
        
        except Exception as e:
            return {"error": f"Stats retrieval failed: {str(e)}"}