import google.generativeai as genai
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from asyncio_throttle import Throttler
import time

from app.models import DocumentType, DocumentFlag, FlagSeverity, ComplianceCheck
from config import settings

class GeminiAnalyzer:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Rate limiting for API calls
        self.throttler = Throttler(rate_limit=10, period=60)  # 10 requests per minute
        
        # Analysis prompts for different tasks
        self.prompts = self._load_analysis_prompts()
    
    def _load_analysis_prompts(self) -> Dict[str, str]:
        """Load structured prompts for different analysis types"""
        return {
            'document_classification': """
            Analyze this document content and classify its type. 
            
            Document content: {content}
            
            Classify as one of: memorandum, articles, application, board_resolution, unknown
            
            Return only the classification in this JSON format:
            {{
                "document_type": "classification",
                "confidence": 0.95,
                "key_indicators": ["indicator1", "indicator2"]
            }}
            """,
            
            'red_flag_detection': """
            You are a legal compliance expert for Abu Dhabi Global Market (ADGM). 
            Analyze this document for potential legal red flags, violations, or compliance issues.
            
            Document Type: {doc_type}
            Content: {content}
            
            Look for these specific issues:
            - Regulatory violations
            - Missing required information
            - Inconsistent data
            - Prohibited activities
            - Inadequate disclosures
            - Non-compliance with ADGM rules
            
            Return findings in this JSON format:
            {{
                "flags": [
                    {{
                        "severity": "critical|warning|info",
                        "title": "Brief issue title",
                        "description": "Detailed description",
                        "location": "Where in document",
                        "suggested_fix": "Recommendation",
                        "adgm_reference": "Relevant ADGM rule if known"
                    }}
                ],
                "overall_risk_level": "low|medium|high",
                "summary": "Brief overall assessment"
            }}
            """,
            
            'completeness_check': """
            You are reviewing a {doc_type} for ADGM compliance. 
            Check if all required sections and information are present.
            
            Required sections for {doc_type}: {required_sections}
            
            Document content: {content}
            
            Return analysis in this JSON format:
            {{
                "completeness_score": 0.85,
                "missing_sections": ["section1", "section2"],
                "present_sections": ["section3", "section4"],
                "compliance_checks": [
                    {{
                        "section": "section_name",
                        "required": true,
                        "present": false,
                        "compliant": false,
                        "issues": ["issue1", "issue2"],
                        "recommendations": ["rec1", "rec2"]
                    }}
                ]
            }}
            """,
            
            'clause_suggestions': """
            Based on this ADGM {doc_type} analysis, suggest improvements or missing clauses.
            
            Current content: {content}
            Identified issues: {issues}
            
            Provide legally compliant suggestions in JSON format:
            {{
                "suggestions": [
                    {{
                        "section": "section_name",
                        "issue": "what's missing/wrong",
                        "suggested_clause": "recommended clause text",
                        "justification": "why this is needed",
                        "adgm_reference": "relevant regulation"
                    }}
                ],
                "priority": "high|medium|low"
            }}
            """
        }
    
    async def analyze_document(self, content: str, doc_type: DocumentType, analysis_type: str = "full") -> Dict:
        """Main document analysis orchestrator"""
        results = {
            'classification': {},
            'red_flags': {},
            'completeness': {},
            'suggestions': {}
        }
        
        try:
            # Run different analysis types based on request
            if analysis_type in ["full", "classification"]:
                results['classification'] = await self._classify_document(content)
            
            if analysis_type in ["full", "red_flags"]:
                results['red_flags'] = await self._detect_red_flags(content, doc_type)
            
            if analysis_type in ["full", "completeness"]:
                results['completeness'] = await self._check_completeness(content, doc_type)
            
            if analysis_type in ["full", "suggestions"]:
                # Only generate suggestions if issues were found
                if results.get('red_flags', {}).get('flags'):
                    results['suggestions'] = await self._generate_suggestions(
                        content, doc_type, results['red_flags']['flags']
                    )
            
            return results
            
        except Exception as e:
            raise Exception(f"Gemini analysis failed: {str(e)}")
    
    async def _classify_document(self, content: str) -> Dict:
        """Classify document type using Gemini"""
        prompt = self.prompts['document_classification'].format(
            content=content[:3000]  # Limit content for classification
        )
        
        async with self.throttler:
            response = await self._safe_gemini_call(prompt)
            return self._parse_json_response(response, 'classification')
    
    async def _detect_red_flags(self, content: str, doc_type: DocumentType) -> Dict:
        """Detect legal red flags and compliance issues"""
        prompt = self.prompts['red_flag_detection'].format(
            doc_type=doc_type.value,
            content=content[:6000]  # More content for thorough analysis
        )
        
        async with self.throttler:
            response = await self._safe_gemini_call(prompt)
            return self._parse_json_response(response, 'red_flags')
    
    async def _check_completeness(self, content: str, doc_type: DocumentType) -> Dict:
        """Check document completeness against ADGM requirements"""
        required_sections = settings.ADGM_DOCUMENT_TYPES.get(
            doc_type.value, {}
        ).get('required_sections', [])
        
        prompt = self.prompts['completeness_check'].format(
            doc_type=doc_type.value,
            required_sections=', '.join(required_sections),
            content=content[:8000]
        )
        
        async with self.throttler:
            response = await self._safe_gemini_call(prompt)
            return self._parse_json_response(response, 'completeness')
    
    async def _generate_suggestions(self, content: str, doc_type: DocumentType, issues: List) -> Dict:
        """Generate clause suggestions based on identified issues"""
        prompt = self.prompts['clause_suggestions'].format(
            doc_type=doc_type.value,
            content=content[:4000],
            issues=json.dumps(issues[:5])  # Limit to top 5 issues
        )
        
        async with self.throttler:
            response = await self._safe_gemini_call(prompt)
            return self._parse_json_response(response, 'suggestions')
    
    async def _safe_gemini_call(self, prompt: str, max_retries: int = 3) -> str:
        """Make API call with retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=settings.MAX_TOKENS_PER_REQUEST,
                        temperature=0.1,  # Low temperature for consistent analysis
                        top_p=0.8,
                        top_k=40
                    )
                )
                
                if response.text:
                    return response.text.strip()
                else:
                    raise Exception("Empty response from Gemini")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Gemini API failed after {max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                continue
        
        raise Exception("Failed to get response from Gemini")
    
    def _parse_json_response(self, response: str, response_type: str) -> Dict:
        """Parse JSON response from Gemini with error handling"""
        try:
            # Clean response text
            clean_response = response.strip()
            
            # Extract JSON if wrapped in markdown
            if "```json" in clean_response:
                start = clean_response.find("```json") + 7
                end = clean_response.find("```", start)
                clean_response = clean_response[start:end].strip()
            elif "```" in clean_response:
                start = clean_response.find("```") + 3
                end = clean_response.find("```", start)
                clean_response = clean_response[start:end].strip()
            
            # Parse JSON
            parsed = json.loads(clean_response)
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {response_type}: {str(e)}")
            print(f"Raw response: {response[:500]}...")
            
            # Return fallback structure based on response type
            return self._get_fallback_response(response_type, response)
        except Exception as e:
            print(f"Error parsing {response_type} response: {str(e)}")
            return self._get_fallback_response(response_type, response)
    
    def _get_fallback_response(self, response_type: str, raw_response: str) -> Dict:
        """Provide fallback response structure when JSON parsing fails"""
        fallbacks = {
            'classification': {
                'document_type': 'unknown',
                'confidence': 0.0,
                'key_indicators': []
            },
            'red_flags': {
                'flags': [],
                'overall_risk_level': 'medium',
                'summary': f'Analysis completed but response parsing failed: {raw_response[:200]}...'
            },
            'completeness': {
                'completeness_score': 0.5,
                'missing_sections': [],
                'present_sections': [],
                'compliance_checks': []
            },
            'suggestions': {
                'suggestions': [],
                'priority': 'medium'
            }
        }
        
        return fallbacks.get(response_type, {})
    
    async def validate_with_context(self, content: str, context: str) -> Dict:
        """Validate content against specific ADGM context/regulations"""
        prompt = f"""
        As an ADGM legal expert, validate this content against the provided regulatory context.
        
        Content to validate: {content[:4000]}
        
        Regulatory context: {context[:2000]}
        
        Return validation results in JSON format:
        {{
            "compliant": true/false,
            "violations": ["violation1", "violation2"],
            "recommendations": ["rec1", "rec2"],
            "confidence": 0.95
        }}
        """
        
        async with self.throttler:
            response = await self._safe_gemini_call(prompt)
            return self._parse_json_response(response, 'validation')