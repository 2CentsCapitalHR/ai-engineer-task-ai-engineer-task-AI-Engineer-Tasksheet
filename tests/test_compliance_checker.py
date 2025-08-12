"""Tests for compliance checker functionality."""

import pytest
from pathlib import Path

# Add src to path for testing
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.core.compliance_checker import ADGMComplianceChecker
from src.models import DocumentType, SeverityLevel


class TestADGMComplianceChecker:
    """Test cases for ADGMComplianceChecker class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = ADGMComplianceChecker()
    
    def test_check_jurisdiction_compliance(self):
        """Test jurisdiction compliance checking."""
        # Test document with incorrect jurisdiction
        text_with_wrong_jurisdiction = """
        This agreement shall be governed by the laws of UAE Federal Courts.
        Any disputes shall be resolved in Dubai Courts.
        """
        
        issues = self.checker._check_jurisdiction(text_with_wrong_jurisdiction, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        assert len(issues) > 0
        assert any(issue.severity == SeverityLevel.HIGH for issue in issues)
        assert any("jurisdiction" in issue.issue.lower() for issue in issues)
    
    def test_check_jurisdiction_compliance_correct(self):
        """Test jurisdiction compliance with correct ADGM reference."""
        text_with_correct_jurisdiction = """
        This agreement shall be governed by the laws of ADGM.
        Any disputes shall be resolved in ADGM Courts.
        """
        
        issues = self.checker._check_jurisdiction(text_with_correct_jurisdiction, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        # Should have fewer or no jurisdiction issues
        jurisdiction_issues = [issue for issue in issues if "jurisdiction" in issue.issue.lower()]
        assert len(jurisdiction_issues) == 0
    
    def test_check_required_clauses_articles(self):
        """Test required clauses checking for Articles of Association."""
        # Text missing required clauses
        incomplete_text = """
        This is an Articles of Association document.
        It has some content but is missing key clauses.
        """
        
        issues = self.checker._check_required_clauses(incomplete_text, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        assert len(issues) > 0
        assert any("company name" in issue.issue.lower() for issue in issues)
        assert any("share capital" in issue.issue.lower() for issue in issues)
    
    def test_check_required_clauses_complete(self):
        """Test required clauses checking with complete document."""
        complete_text = """
        ARTICLES OF ASSOCIATION
        
        Company Name: Test Company Limited
        Share Capital: The authorized share capital is AED 100,000
        Directors Powers: The directors shall have full powers to manage the company
        """
        
        issues = self.checker._check_required_clauses(complete_text, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        # Should have fewer missing clause issues
        missing_clause_issues = [issue for issue in issues if "missing required clause" in issue.issue.lower()]
        assert len(missing_clause_issues) < 3  # Should find most required clauses
    
    def test_detect_red_flags_ambiguous_language(self):
        """Test red flag detection for ambiguous language."""
        ambiguous_text = """
        The company may do business activities.
        Directors should have powers.
        The company might issue shares.
        Perhaps the company will have meetings.
        """
        
        issues = self.checker._detect_red_flags(ambiguous_text, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        assert len(issues) > 0
        assert any("ambiguous" in issue.issue.lower() for issue in issues)
    
    def test_detect_red_flags_missing_essential_info(self):
        """Test red flag detection for missing essential information."""
        incomplete_aoa = """
        ARTICLES OF ASSOCIATION
        
        This document establishes a company but lacks essential information.
        """
        
        issues = self.checker._detect_red_flags(incomplete_aoa, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        assert len(issues) > 0
        # Should detect missing share capital, registered office, etc.
        missing_issues = [issue for issue in issues if "missing" in issue.issue.lower()]
        assert len(missing_issues) > 0
    
    def test_check_adgm_specific_requirements(self):
        """Test ADGM-specific requirements checking."""
        text_without_adgm_reg = """
        ARTICLES OF ASSOCIATION
        
        Company Name: Test Company Limited
        This company is incorporated in ADGM.
        """
        
        issues = self.checker._check_adgm_specific_requirements(text_without_adgm_reg, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        assert len(issues) > 0
        # Should detect missing ADGM registration number
        reg_issues = [issue for issue in issues if "registration" in issue.issue.lower()]
        assert len(reg_issues) > 0
    
    def test_check_formatting_signature_section(self):
        """Test formatting check for signature sections."""
        structured_content_no_signatures = {
            'sections': [{'text': 'Section 1', 'index': 0}],
            'clauses': [],
            'tables': [],
            'signatures': []  # No signatures
        }
        
        issues = self.checker._check_formatting("Test content", structured_content_no_signatures, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        assert len(issues) > 0
        signature_issues = [issue for issue in issues if "signature" in issue.issue.lower()]
        assert len(signature_issues) > 0
    
    def test_check_formatting_with_signatures(self):
        """Test formatting check with proper signatures."""
        structured_content_with_signatures = {
            'sections': [{'text': 'Section 1', 'index': 0}],
            'clauses': [],
            'tables': [],
            'signatures': [{'text': 'Signature: ___________', 'index': 5}]
        }
        
        issues = self.checker._check_formatting("Test content", structured_content_with_signatures, DocumentType.ARTICLES_OF_ASSOCIATION)
        
        # Should have fewer signature-related issues
        signature_issues = [issue for issue in issues if "signature" in issue.issue.lower()]
        assert len(signature_issues) == 0
    
    def test_comprehensive_compliance_check(self):
        """Test comprehensive compliance check."""
        test_document = """
        ARTICLES OF ASSOCIATION
        
        Company Name: Test Company Limited
        Share Capital: AED 100,000
        Directors Powers: The directors may have some powers
        
        This agreement shall be governed by Dubai Courts.
        """
        
        structured_content = {
            'sections': [{'text': 'Company Name', 'index': 0}],
            'clauses': [],
            'tables': [],
            'signatures': []
        }
        
        issues = self.checker.check_compliance(test_document, DocumentType.ARTICLES_OF_ASSOCIATION, structured_content)
        
        assert len(issues) > 0
        
        # Should find jurisdiction issues
        jurisdiction_issues = [issue for issue in issues if "jurisdiction" in issue.issue.lower()]
        assert len(jurisdiction_issues) > 0
        
        # Should find signature issues
        signature_issues = [issue for issue in issues if "signature" in issue.issue.lower()]
        assert len(signature_issues) > 0
        
        # Check severity levels are assigned
        assert all(hasattr(issue, 'severity') for issue in issues)
        assert all(issue.severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL] for issue in issues)


if __name__ == "__main__":
    pytest.main([__file__])
