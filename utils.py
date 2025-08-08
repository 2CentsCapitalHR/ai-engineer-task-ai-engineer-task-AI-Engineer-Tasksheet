"""Utility functions for the ADGM Corporate Agent."""

import base64
import io
from typing import Any

def create_download_link(file_data: bytes, filename: str, link_text: str) -> str:
    """Create a download link for file data."""
    b64 = base64.b64encode(file_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_severity_badge(severity: str) -> str:
    """Format severity as a colored badge."""
    color_map = {
        'High': '#FF4B4B',
        'Medium': '#FFA500', 
        'Low': '#00C851'
    }
    color = color_map.get(severity, '#808080')
    return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{severity}</span>'

def extract_document_sections(content: dict) -> list:
    """Extract main sections from document content."""
    sections = []
    
    # Look for headings in paragraphs
    for para in content.get('paragraphs', []):
        text = para['text'].strip()
        style = para.get('style', '')
        
        # Identify headings by style or format
        if ('heading' in style.lower() or 
            text.isupper() or 
            (len(text) < 100 and text.endswith(':'))):
            sections.append(text)
    
    return sections

def validate_document_structure(content: dict) -> dict:
    """Validate basic document structure."""
    validation = {
        'has_content': False,
        'has_tables': False,
        'has_headers': False,
        'paragraph_count': 0,
        'estimated_pages': 0
    }
    
    paragraphs = content.get('paragraphs', [])
    validation['paragraph_count'] = len(paragraphs)
    validation['has_content'] = len(paragraphs) > 0
    validation['has_tables'] = len(content.get('tables', [])) > 0
    validation['has_headers'] = len(content.get('headers', [])) > 0
    
    # Rough page estimation (250 words per page)
    total_words = sum(len(p['text'].split()) for p in paragraphs)
    validation['estimated_pages'] = max(1, total_words // 250)
    
    return validation

def generate_compliance_score(issues: list) -> int:
    """Calculate compliance score based on issues found."""
    if not issues:
        return 100
    
    # Weight issues by severity
    severity_weights = {
        'High': 20,
        'Medium': 10,
        'Low': 5
    }
    
    total_deduction = sum(severity_weights.get(issue['severity'], 5) for issue in issues)
    score = max(0, 100 - total_deduction)
    
    return score

def format_adgm_reference(reference: str) -> str:
    """Format ADGM regulation reference with link if available."""
    if not reference:
        return ""
    
    # Basic formatting
    formatted = reference.replace('ADGM ', '**ADGM** ')
    
    # Add common ADGM links
    if 'Companies Regulations 2020' in reference:
        formatted += ' ([View Regulation](https://en.adgm.com/legal-framework/companies-regulations/))'
    elif 'Employment Regulations 2019' in reference:
        formatted += ' ([View Regulation](https://en.adgm.com/legal-framework/employment-regulations/))'
    elif 'Licensing Regulations' in reference:
        formatted += ' ([View Regulation](https://en.adgm.com/legal-framework/licensing-regulations/))'
    
    return formatted

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for download."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Ensure it has an extension
    if not filename.endswith('.docx'):
        filename += '.docx'
    
    return filename

def create_summary_stats(analysis_results: dict) -> dict:
    """Create summary statistics from analysis results."""
    documents = analysis_results.get('documents_analyzed', [])
    
    stats = {
        'total_documents': len(documents),
        'total_issues': sum(doc.get('issues_found', 0) for doc in documents),
        'high_severity_issues': sum(doc.get('high_severity_issues', 0) for doc in documents),
        'document_types': list(set(doc.get('document_type', 'Unknown') for doc in documents)),
        'avg_compliance_score': 0
    }
    
    # Calculate average compliance score
    if documents:
        scores = [doc.get('analysis', {}).get('compliance_score', 0) for doc in documents]
        if scores:
            stats['avg_compliance_score'] = sum(scores) / len(scores)
    
    return stats
