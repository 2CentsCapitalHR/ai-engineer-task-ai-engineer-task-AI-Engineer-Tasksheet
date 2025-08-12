"""RAG (Retrieval-Augmented Generation) system for ADGM compliance."""

from typing import List, Dict, Optional, Tuple
import logging
from ..config import settings
from .vector_store import ADGMVectorStore
from ..models import DocumentIssue, SeverityLevel

logger = logging.getLogger(__name__)


class ADGMRAGSystem:
    """RAG system for ADGM legal document analysis."""
    
    def __init__(self, vector_store: ADGMVectorStore):
        self.vector_store = vector_store
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration."""
        if settings.default_llm_provider == "openai":
            return self._initialize_openai()
        elif settings.default_llm_provider == "anthropic":
            return self._initialize_anthropic()
        elif settings.default_llm_provider == "gemini":
            return self._initialize_gemini()
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.default_llm_provider}")
    
    def _initialize_openai(self):
        """Initialize OpenAI LLM."""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0.1
            )
        except ImportError:
            logger.error("OpenAI dependencies not installed")
            raise
    
    def _initialize_anthropic(self):
        """Initialize Anthropic LLM."""
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=settings.anthropic_model,
                api_key=settings.anthropic_api_key,
                temperature=0.1
            )
        except ImportError:
            logger.error("Anthropic dependencies not installed")
            raise
    
    def _initialize_gemini(self):
        """Initialize Google Gemini LLM."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.gemini_api_key,
                temperature=0.1
            )
        except ImportError:
            logger.error("Google Generative AI dependencies not installed")
            raise
    
    def analyze_document_compliance(self, document_text: str, document_type: str) -> List[DocumentIssue]:
        """Analyze document for ADGM compliance issues."""
        
        # Retrieve relevant ADGM regulations
        relevant_docs = self.vector_store.search(
            f"{document_type} ADGM compliance requirements regulations",
            n_results=5
        )
        
        # Create context from retrieved documents
        context = self._create_context(relevant_docs)
        
        # Generate compliance analysis prompt
        prompt = self._create_compliance_prompt(document_text, document_type, context)
        
        # Get LLM analysis
        try:
            response = self.llm.invoke(prompt)
            issues = self._parse_compliance_response(response.content)
            return issues
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return []
    
    def identify_red_flags(self, document_text: str, document_type: str) -> List[DocumentIssue]:
        """Identify red flags in the document."""
        
        # Retrieve red flag patterns and examples
        relevant_docs = self.vector_store.search(
            f"{document_type} red flags common issues ADGM",
            n_results=3
        )
        
        context = self._create_context(relevant_docs)
        
        prompt = self._create_red_flag_prompt(document_text, document_type, context)
        
        try:
            response = self.llm.invoke(prompt)
            red_flags = self._parse_red_flag_response(response.content)
            return red_flags
        except Exception as e:
            logger.error(f"Red flag analysis failed: {e}")
            return []
    
    def suggest_improvements(self, document_text: str, document_type: str, issues: List[DocumentIssue]) -> List[str]:
        """Suggest improvements for identified issues."""
        
        if not issues:
            return []
        
        # Retrieve best practices and templates
        relevant_docs = self.vector_store.search(
            f"{document_type} best practices templates ADGM",
            n_results=3
        )
        
        context = self._create_context(relevant_docs)
        
        prompt = self._create_improvement_prompt(document_text, document_type, issues, context)
        
        try:
            response = self.llm.invoke(prompt)
            suggestions = self._parse_improvement_response(response.content)
            return suggestions
        except Exception as e:
            logger.error(f"Improvement suggestion failed: {e}")
            return []
    
    def get_missing_documents(self, uploaded_docs: List[str], process_type: str) -> List[str]:
        """Identify missing documents for a specific process."""
        
        # Retrieve document requirements
        relevant_docs = self.vector_store.get_document_requirements(process_type)
        
        context = self._create_context(relevant_docs)
        
        prompt = self._create_missing_docs_prompt(uploaded_docs, process_type, context)
        
        try:
            response = self.llm.invoke(prompt)
            missing_docs = self._parse_missing_docs_response(response.content)
            return missing_docs
        except Exception as e:
            logger.error(f"Missing documents analysis failed: {e}")
            return []
    
    def _create_context(self, retrieved_docs: List[Dict]) -> str:
        """Create context string from retrieved documents."""
        context_parts = []
        for doc in retrieved_docs:
            title = doc['metadata'].get('title', 'Unknown')
            content = doc['content'][:1000]  # Limit content length
            context_parts.append(f"Document: {title}\nContent: {content}\n")
        
        return "\n".join(context_parts)
    
    def _create_compliance_prompt(self, document_text: str, document_type: str, context: str) -> str:
        """Create prompt for compliance analysis."""
        return f"""
You are an expert ADGM legal compliance analyst. Analyze the following {document_type} document for compliance with ADGM regulations.

ADGM Reference Context:
{context}

Document to Analyze:
{document_text[:3000]}

Please identify compliance issues and provide your analysis in the following JSON format:
{{
    "issues": [
        {{
            "section": "specific section or clause",
            "issue": "description of the compliance issue",
            "severity": "Low|Medium|High|Critical",
            "adgm_reference": "specific ADGM regulation or rule",
            "suggestion": "suggested fix or improvement"
        }}
    ]
}}

Focus on:
1. Jurisdiction clauses (must reference ADGM, not UAE Federal Courts)
2. Required clauses for {document_type}
3. Formatting and structural requirements
4. Compliance with ADGM-specific templates
5. Missing mandatory sections
"""
    
    def _create_red_flag_prompt(self, document_text: str, document_type: str, context: str) -> str:
        """Create prompt for red flag detection."""
        return f"""
You are an expert legal reviewer specializing in ADGM compliance. Identify red flags in this {document_type} document.

ADGM Reference Context:
{context}

Document to Review:
{document_text[:3000]}

Identify red flags in JSON format:
{{
    "red_flags": [
        {{
            "section": "location in document",
            "issue": "red flag description",
            "severity": "Low|Medium|High|Critical",
            "reason": "why this is a red flag",
            "adgm_reference": "relevant ADGM rule"
        }}
    ]
}}

Common red flags to check:
1. Incorrect jurisdiction references
2. Ambiguous or non-binding language
3. Missing signatory sections
4. Improper formatting
5. Non-compliance with ADGM templates
6. Invalid or missing clauses
"""
    
    def _create_improvement_prompt(self, document_text: str, document_type: str, issues: List[DocumentIssue], context: str) -> str:
        """Create prompt for improvement suggestions."""
        issues_text = "\n".join([f"- {issue.issue}" for issue in issues])
        
        return f"""
You are an expert ADGM legal advisor. Provide specific improvement suggestions for this {document_type} document.

ADGM Reference Context:
{context}

Identified Issues:
{issues_text}

Document Excerpt:
{document_text[:2000]}

Provide improvement suggestions in JSON format:
{{
    "suggestions": [
        "specific actionable improvement suggestion",
        "another improvement suggestion"
    ]
}}

Focus on:
1. Specific clause wording improvements
2. Structural changes needed
3. Additional sections to include
4. ADGM compliance enhancements
"""
    
    def _create_missing_docs_prompt(self, uploaded_docs: List[str], process_type: str, context: str) -> str:
        """Create prompt for missing document identification."""
        docs_text = "\n".join([f"- {doc}" for doc in uploaded_docs])
        
        return f"""
You are an ADGM compliance expert. Identify missing documents for {process_type}.

ADGM Reference Context:
{context}

Uploaded Documents:
{docs_text}

Identify missing required documents in JSON format:
{{
    "missing_documents": [
        "name of missing required document",
        "another missing document"
    ],
    "process_identified": "{process_type}",
    "total_required": "number of total required documents"
}}

Consider ADGM requirements for {process_type}.
"""
    
    def _parse_compliance_response(self, response: str) -> List[DocumentIssue]:
        """Parse LLM response for compliance issues."""
        try:
            import json
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                issues = []
                for issue_data in data.get('issues', []):
                    issue = DocumentIssue(
                        document="Current Document",
                        section=issue_data.get('section', ''),
                        issue=issue_data.get('issue', ''),
                        severity=SeverityLevel(issue_data.get('severity', 'Medium')),
                        suggestion=issue_data.get('suggestion', ''),
                        adgm_reference=issue_data.get('adgm_reference', ''),
                        line_number=None
                    )
                    issues.append(issue)
                
                return issues
        except Exception as e:
            logger.error(f"Failed to parse compliance response: {e}")
        
        return []
    
    def _parse_red_flag_response(self, response: str) -> List[DocumentIssue]:
        """Parse LLM response for red flags."""
        # Similar to compliance parsing but for red flags
        return self._parse_compliance_response(response.replace('red_flags', 'issues'))
    
    def _parse_improvement_response(self, response: str) -> List[str]:
        """Parse LLM response for improvement suggestions."""
        try:
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get('suggestions', [])
        except Exception as e:
            logger.error(f"Failed to parse improvement response: {e}")
        
        return []
    
    def _parse_missing_docs_response(self, response: str) -> List[str]:
        """Parse LLM response for missing documents."""
        try:
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get('missing_documents', [])
        except Exception as e:
            logger.error(f"Failed to parse missing docs response: {e}")
        
        return []
