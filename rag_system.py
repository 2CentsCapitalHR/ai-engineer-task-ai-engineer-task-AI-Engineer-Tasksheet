import os
import json
from typing import List, Dict, Any
import openai
from openai import OpenAI

class RAGSystem:
    """Retrieval-Augmented Generation system for ADGM legal knowledge."""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # ADGM knowledge base
        self.adgm_knowledge = self._load_adgm_knowledge()
    
    def _load_adgm_knowledge(self):
        """Load ADGM legal knowledge base."""
        return {
            "company_formation": {
                "required_documents": [
                    "Articles of Association",
                    "Memorandum of Association", 
                    "Incorporation Application Form",
                    "UBO Declaration Form",
                    "Register of Members and Directors"
                ],
                "key_requirements": [
                    "ADGM jurisdiction must be specified in all documents",
                    "Minimum share capital requirements must be met",
                    "At least one director must be ADGM resident",
                    "Registered office must be in ADGM",
                    "Company objects must be clearly defined"
                ],
                "red_flags": [
                    "Reference to UAE Federal Courts instead of ADGM Courts",
                    "Missing ADGM jurisdiction clauses",
                    "Insufficient share capital",
                    "Non-compliant director requirements",
                    "Ambiguous company objects"
                ]
            },
            "licensing": {
                "required_documents": [
                    "License Application Form",
                    "Business Plan",
                    "Financial Projections",
                    "Compliance Manual",
                    "Key Personnel CVs"
                ],
                "key_requirements": [
                    "Business activities must align with ADGM regulations",
                    "Adequate capital and liquidity requirements",
                    "Qualified and experienced key personnel",
                    "Robust compliance framework"
                ]
            },
            "employment": {
                "required_documents": [
                    "Employment Contract",
                    "Job Description",
                    "Salary Certificate",
                    "Benefits Summary"
                ],
                "key_requirements": [
                    "Compliance with ADGM Employment Regulations",
                    "Clear termination clauses",
                    "Minimum wage requirements",
                    "Working hours limitations"
                ]
            },
            "adgm_regulations": {
                "Companies Regulations 2020": {
                    "Article 6": "Jurisdiction and governing law requirements",
                    "Article 12": "Share capital and member requirements",
                    "Article 18": "Director residency requirements",
                    "Article 25": "Registered office requirements"
                },
                "Employment Regulations 2019": {
                    "Section 5": "Minimum wage provisions",
                    "Section 12": "Working hours and overtime",
                    "Section 20": "Termination procedures"
                },
                "Licensing Regulations 2021": {
                    "Chapter 3": "Capital adequacy requirements",
                    "Chapter 5": "Key personnel qualifications",
                    "Chapter 8": "Ongoing compliance obligations"
                }
            }
        }
    
    def retrieve_relevant_knowledge(self, query: str, document_type: str) -> Dict[str, Any]:
        """Retrieve relevant ADGM knowledge for a query."""
        relevant_info = {
            "requirements": [],
            "red_flags": [],
            "regulations": []
        }
        
        # Map document types to knowledge categories
        doc_category_map = {
            "Articles of Association": "company_formation",
            "Memorandum of Association": "company_formation",
            "Board Resolution": "company_formation",
            "Shareholder Resolution": "company_formation",
            "Incorporation Application": "company_formation",
            "UBO Declaration": "company_formation",
            "Register of Members": "company_formation",
            "Employment Contract": "employment",
            "License Application": "licensing"
        }
        
        category = doc_category_map.get(document_type, "company_formation")
        
        if category in self.adgm_knowledge:
            knowledge = self.adgm_knowledge[category]
            relevant_info["requirements"] = knowledge.get("key_requirements", [])
            relevant_info["red_flags"] = knowledge.get("red_flags", [])
        
        # Add relevant regulations
        relevant_info["regulations"] = self.adgm_knowledge["adgm_regulations"]
        
        return relevant_info
    
    def analyze_with_rag(self, document_content: str, document_type: str) -> Dict[str, Any]:
        """Analyze document using RAG approach."""
        # Retrieve relevant knowledge
        knowledge = self.retrieve_relevant_knowledge(document_content, document_type)
        
        # Create enhanced prompt with ADGM knowledge
        prompt = self._create_analysis_prompt(document_content, document_type, knowledge)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ADGM legal analyst specializing in corporate compliance and document review. Provide detailed analysis based on ADGM regulations and requirements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
            else:
                result = {"error": "No content received from AI model"}
            return result
            
        except Exception as e:
            raise Exception(f"Error in RAG analysis: {str(e)}")
    
    def _create_analysis_prompt(self, content: str, doc_type: str, knowledge: Dict) -> str:
        """Create analysis prompt with RAG knowledge."""
        prompt = f"""
        Analyze the following {doc_type} document for ADGM compliance and identify any issues or red flags.

        DOCUMENT CONTENT:
        {content[:3000]}  # Truncate for token limits

        ADGM REQUIREMENTS FOR THIS DOCUMENT TYPE:
        {json.dumps(knowledge['requirements'], indent=2)}

        KNOWN RED FLAGS TO CHECK:
        {json.dumps(knowledge['red_flags'], indent=2)}

        RELEVANT ADGM REGULATIONS:
        {json.dumps(knowledge['regulations'], indent=2)}

        Please analyze the document and provide a JSON response with the following structure:
        {{
            "document_type": "{doc_type}",
            "compliance_score": <0-100>,
            "issues": [
                {{
                    "section": "specific section or clause",
                    "issue": "description of the issue",
                    "severity": "High|Medium|Low",
                    "suggestion": "recommended fix or improvement",
                    "adgm_reference": "specific ADGM regulation or article"
                }}
            ],
            "missing_clauses": [
                "list of required clauses that appear to be missing"
            ],
            "recommendations": [
                "general recommendations for improving compliance"
            ]
        }}

        Focus on:
        1. ADGM jurisdiction and governing law clauses
        2. Compliance with specific ADGM regulations
        3. Missing required information or clauses
        4. Inconsistencies or ambiguous language
        5. Proper formatting and structure
        """
        
        return prompt
    
    def get_adgm_citation(self, topic: str) -> str:
        """Get specific ADGM regulation citation for a topic."""
        citation_map = {
            "jurisdiction": "ADGM Companies Regulations 2020, Article 6",
            "share_capital": "ADGM Companies Regulations 2020, Article 12", 
            "directors": "ADGM Companies Regulations 2020, Article 18",
            "registered_office": "ADGM Companies Regulations 2020, Article 25",
            "employment_wages": "ADGM Employment Regulations 2019, Section 5",
            "working_hours": "ADGM Employment Regulations 2019, Section 12",
            "termination": "ADGM Employment Regulations 2019, Section 20",
            "capital_adequacy": "ADGM Licensing Regulations 2021, Chapter 3",
            "key_personnel": "ADGM Licensing Regulations 2021, Chapter 5"
        }
        
        return citation_map.get(topic, "ADGM Regulations")
