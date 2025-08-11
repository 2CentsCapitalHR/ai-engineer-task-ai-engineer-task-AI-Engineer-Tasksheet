from docx import Document
import re
from typing import Dict, List, Tuple
import PyPDF2
import pdfplumber
import os

class DocumentParser:
    def __init__(self):
        self.document_types = {
            'articles_of_association': [
                'articles of association', 'aoa', 'articles', 
                'memorandum and articles', 'company constitution'
            ],
            'memorandum_of_association': [
                'memorandum of association', 'moa', 'memorandum',
                'company memorandum'
            ],
            'board_resolution': [
                'board resolution', 'resolution', 'board meeting',
                'directors resolution', 'resolution of', 'incorporating shareholders'
            ],
            'shareholder_resolution': [
                'shareholder resolution', 'shareholders', 'members resolution'
            ],
            'incorporation_form': [
                'incorporation', 'application form', 'registration form',
                'company registration'
            ],
            'ubo_declaration': [
                'ubo', 'ultimate beneficial owner', 'declaration',
                'beneficial ownership'
            ],
            'register_members': [
                'register of members', 'register of directors',
                'members register', 'directors register'
            ],
            'employment_contract': [
                'employment contract', 'employment agreement',
                'service agreement', 'employment terms'
            ],
            'license_application': [
                'license application', 'licensing', 'permit application'
            ],
            'compliance_policy': [
                'compliance policy', 'risk policy', 'internal policy'
            ],
            'commercial_agreement': [
                'commercial agreement', 'service agreement', 'consultancy agreement'
            ]
        }
    
    def parse_document(self, file_path: str) -> Dict:
        """Parse document (docx or pdf) and extract information"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.docx':
                return self._parse_docx(file_path)
            elif file_extension == '.pdf':
                return self._parse_pdf(file_path)
            else:
                return {
                    'error': f'Unsupported file format: {file_extension}',
                    'filename': os.path.basename(file_path),
                    'document_type': 'unknown',
                    'content': '',
                    'sections': {},
                    'word_count': 0,
                    'paragraph_count': 0
                }
                
        except Exception as e:
            return {
                'error': f"Failed to parse document: {str(e)}",
                'filename': os.path.basename(file_path),
                'document_type': 'unknown',
                'content': '',
                'sections': {},
                'word_count': 0,
                'paragraph_count': 0
            }
    
    def _parse_docx(self, file_path: str) -> Dict:
        """Parse DOCX document"""
        doc = Document(file_path)
        
        # Extract text content
        full_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text.strip())
        
        content = '\n'.join(full_text)
        
        if not content.strip():
            return {
                'error': 'Document appears to be empty or unreadable',
                'filename': os.path.basename(file_path),
                'document_type': 'unknown',
                'content': '',
                'sections': {},
                'word_count': 0,
                'paragraph_count': 0
            }
        
        return self._analyze_content(content, file_path)
    
    def _parse_pdf(self, file_path: str) -> Dict:
        """Parse PDF document using multiple methods for better extraction"""
        content = ""
        
        # Method 1: Try pdfplumber (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                content = '\n'.join(text_parts)
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            
        # Method 2: Fallback to PyPDF2 if pdfplumber fails
        if not content.strip():
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_parts = []
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    content = '\n'.join(text_parts)
            except Exception as e:
                print(f"PyPDF2 failed: {e}")
        
        if not content.strip():
            return {
                'error': 'Could not extract text from PDF. The file may be scanned or corrupted.',
                'filename': os.path.basename(file_path),
                'document_type': 'unknown',
                'content': '',
                'sections': {},
                'word_count': 0,
                'paragraph_count': 0
            }
        
        return self._analyze_content(content, file_path)
    
    def _analyze_content(self, content: str, file_path: str) -> Dict:
        """Analyze extracted content"""
        # Clean up content
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = content.strip()
        
        # Identify document type
        doc_type = self.identify_document_type(content)
        
        # Extract key sections
        sections = self.extract_sections(content)
        
        # Count paragraphs (split by double newlines or periods)
        paragraphs = [p.strip() for p in re.split(r'[\n]{2,}|\.[\s]+[A-Z]', content) if p.strip()]
        
        return {
            'filename': os.path.basename(file_path),
            'document_type': doc_type,
            'content': content,
            'sections': sections,
            'word_count': len(content.split()),
            'paragraph_count': len(paragraphs)
        }
    
    def identify_document_type(self, content: str) -> str:
        """Identify document type based on content"""
        content_lower = content.lower()
        
        # Score each document type
        scores = {}
        for doc_type, keywords in self.document_types.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                count = content_lower.count(keyword.lower())
                score += count * len(keyword.split())  # Weight longer phrases more
            scores[doc_type] = score
        
        # Return the document type with highest score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'unknown'
    
    def extract_sections(self, content: str) -> Dict:
        """Extract common legal document sections"""
        sections = {}
        
        # Common patterns for legal documents
        patterns = {
            'company_name': [
                r'company name[:\s]+(.*?)(?:\n|\.)',
                r'name of the company[:\s]+(.*?)(?:\n|\.)',
                r'proposed company name[:\s]+(.*?)(?:\n|\.)'
            ],
            'jurisdiction': [
                r'jurisdiction[:\s]+(.*?)(?:\n|\.)',
                r'governing law[:\s]+(.*?)(?:\n|\.)',
                r'courts?[:\s]+(.*?)(?:\n|\.)'
            ],
            'registered_office': [
                r'registered office[:\s]+(.*?)(?:\n|\.)',
                r'office address[:\s]+(.*?)(?:\n|\.)'
            ],
            'share_capital': [
                r'share capital[:\s]+(.*?)(?:\n|\.)',
                r'capital[:\s]+(.*?)(?:\n|\.)',
                r'nominal value[:\s]+(.*?)(?:\n|\.)'
            ],
            'directors': [
                r'director[s]?[:\s]+(.*?)(?:\n|\.)',
                r'appointment of director[s]?[:\s]+(.*?)(?:\n|\.)'
            ]
        }
        
        for section, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    sections[section] = match.group(1).strip()[:200]  # Limit length
                    break
        
        return sections
