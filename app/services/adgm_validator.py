import os
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.models import DocumentType, DocumentFlag, FlagSeverity, ComplianceCheck
from app.services.adgm_knowledge_extractor import ADGMKnowledgeExtractor
from config import settings

class ADGMValidator:
    """Comprehensive ADGM Validator with Knowledge Base Integration"""
    
    def __init__(self):
        self.knowledge_extractor = ADGMKnowledgeExtractor()
        self.knowledge_initialized = False
        self.chroma_client = None
        self.adgm_collection = None
        
        # Document type to collection mapping
        self.collection_mapping = {
            DocumentType.MEMORANDUM: ['adgm_incorporation', 'adgm_templates'],
            DocumentType.ARTICLES: ['adgm_incorporation', 'adgm_templates'],
            DocumentType.APPLICATION: ['adgm_incorporation', 'adgm_compliance'],
            DocumentType.BOARD_RESOLUTION: ['adgm_templates', 'adgm_compliance'],
            DocumentType.EMPLOYMENT_CONTRACT: ['adgm_employment']
        }
        
        # ADGM-specific validation rules
        self.validation_rules = self._load_validation_rules()
        self.mandatory_sections = self._load_mandatory_sections()
        
        # Initialize basic knowledge base
        self._initialize_basic_knowledge_base()
        
    async def initialize_knowledge_base(self):
        """Initialize the comprehensive knowledge base"""
        try:
            success = await self.knowledge_extractor.initialize_knowledge_base()
            if success:
                self.knowledge_initialized = True
                self.chroma_client = self.knowledge_extractor.chroma_client
                
                # Set primary collection reference
                if 'adgm_incorporation' in self.knowledge_extractor.collections:
                    self.adgm_collection = self.knowledge_extractor.collections['adgm_incorporation']
                
                print("✅ Enhanced ADGM knowledge base with web scraping initialized")
                
                # Print stats
                stats = self.knowledge_extractor.get_knowledge_stats()
                print(f"📊 Knowledge base statistics: {stats}")
                
                return True
            else:
                print("⚠️ Knowledge base initialization failed, using fallback mode")
                return False
        except Exception as e:
            print(f"⚠️ Knowledge base error: {str(e)}, using fallback mode")
            return False
    
    def _initialize_basic_knowledge_base(self):
        """Initialize basic ChromaDB for fallback mode"""
        try:
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for ADGM documents
            try:
                self.adgm_collection = self.chroma_client.get_collection("adgm_regulations")
            except ValueError:
                # Collection doesn't exist, create it
                self.adgm_collection = self.chroma_client.create_collection(
                    name="adgm_regulations",
                    metadata={"description": "ADGM regulations and compliance requirements"}
                )
                
                # Load initial ADGM knowledge if collection is empty
                self._load_initial_adgm_knowledge()
            
        except Exception as e:
            print(f"Failed to initialize basic ChromaDB: {str(e)}")
            self.chroma_client = None
            self.adgm_collection = None
    
    def _load_initial_adgm_knowledge(self):
        """Load basic ADGM knowledge into ChromaDB for fallback"""
        try:
            # Basic ADGM regulations
            basic_knowledge = [
                {
                    "id": "companies_reg_basic_1",
                    "document": "Companies Regulations 2020",
                    "content": "Every company incorporated in ADGM must have a registered office within ADGM jurisdiction.",
                    "section": "Registration Requirements",
                    "regulation_ref": "CR-2020-001"
                },
                {
                    "id": "companies_reg_basic_2", 
                    "document": "Companies Regulations 2020",
                    "content": "Minimum share capital requirements vary by company type. Private companies require minimum AED 150,000.",
                    "section": "Share Capital",
                    "regulation_ref": "CR-2020-015"
                },
                {
                    "id": "directors_reg_basic_1",
                    "document": "Directors Regulations",
                    "content": "Every company must have at least one natural person director who is ordinarily resident in the UAE.",
                    "section": "Director Requirements", 
                    "regulation_ref": "DIR-2020-012"
                }
            ]
            
            # Add documents to collection
            documents = [item["content"] for item in basic_knowledge]
            metadatas = [{k: v for k, v in item.items() if k != "content"} for item in basic_knowledge]
            ids = [item["id"] for item in basic_knowledge]
            
            self.adgm_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Loaded {len(basic_knowledge)} basic ADGM regulation documents")
            
        except Exception as e:
            print(f"Failed to load basic ADGM knowledge: {str(e)}")
    
    def _load_validation_rules(self) -> Dict:
        """Load ADGM-specific validation rules"""
        return {
            "memorandum": {
                "required_clauses": [
                    "company name clause",
                    "registered office clause", 
                    "objects clause",
                    "liability clause",
                    "share capital clause"
                ],
                "prohibited_terms": [
                    "bank", "insurance", "islamic", "trust", "fund management"
                ],
                "format_requirements": {
                    "min_sections": 6,
                    "requires_signature": True,
                    "requires_date": True
                }
            },
            "articles": {
                "required_clauses": [
                    "share rights clause",
                    "director powers clause",
                    "meeting procedures clause", 
                    "dividend policy clause",
                    "transfer restrictions clause"
                ],
                "prohibited_terms": [],
                "format_requirements": {
                    "min_sections": 10,
                    "requires_signature": True,
                    "requires_date": True
                }
            },
            "application": {
                "required_fields": [
                    "company name",
                    "business activities",
                    "directors information",
                    "shareholders information",
                    "registered office"
                ],
                "validation_checks": [
                    "valid_activity_codes",
                    "director_qualifications", 
                    "capital_adequacy"
                ]
            },
            "board_resolution": {
                "required_elements": [
                    "meeting date",
                    "attendees list",
                    "resolutions passed",
                    "chairman signature"
                ],
                "format_requirements": {
                    "requires_quorum": True,
                    "requires_voting_record": True
                }
            }
        }
    
    def _load_mandatory_sections(self) -> Dict:
        """Load mandatory sections for each document type"""
        return {
            DocumentType.MEMORANDUM: [
                "Company Name",
                "Registered Office", 
                "Objects",
                "Share Capital",
                "Liability of Members",
                "Subscriber Details"
            ],
            DocumentType.ARTICLES: [
                "Share Classes and Rights",
                "Board of Directors",
                "General Meetings", 
                "Dividend Policy",
                "Transfer of Shares",
                "Accounts and Audit"
            ],
            DocumentType.APPLICATION: [
                "Company Details",
                "Business Activities",
                "Directors Information",
                "Shareholders Information", 
                "Financial Projections"
            ],
            DocumentType.BOARD_RESOLUTION: [
                "Meeting Details",
                "Attendees",
                "Resolutions",
                "Voting Record",
                "Signatures"
            ]
        }
    
    async def validate_document_compliance(self, content: str, doc_type: DocumentType, structure: Dict) -> List[ComplianceCheck]:
        """Main compliance validation function with enhanced knowledge base integration"""
        compliance_checks = []
        
        try:
            # Get mandatory sections for this document type
            mandatory_sections = self.mandatory_sections.get(doc_type, [])
            
            # Check each mandatory section
            for section in mandatory_sections:
                check = await self._validate_section(content, section, doc_type, structure)
                compliance_checks.append(check)
            
            # Perform document-specific validations
            specific_checks = await self._perform_specific_validations(content, doc_type)
            compliance_checks.extend(specific_checks)
            
            # Enhanced validation using knowledge base if available
            if self.knowledge_initialized:
                enhanced_checks = await self._comprehensive_knowledge_validation(content, doc_type, structure)
                compliance_checks.extend(enhanced_checks)
            
            return compliance_checks
            
        except Exception as e:
            print(f"Compliance validation error: {str(e)}")
            return []
    
    async def _comprehensive_knowledge_validation(self, content: str, doc_type: DocumentType, structure: Dict) -> List[ComplianceCheck]:
        """Comprehensive validation against knowledge base"""
        checks = []
        
        try:
            # Get relevant collections for this document type
            relevant_collections = self.collection_mapping.get(doc_type, ['adgm_incorporation'])
            
            # Query for document-specific requirements
            requirements_query = f"{doc_type.value if hasattr(doc_type, 'value') else str(doc_type)} requirements mandatory sections"
            requirements_results = self.knowledge_extractor.query_knowledge_base(
                requirements_query, 
                collection_names=relevant_collections,
                n_results=8
            )
            
            # Query for compliance rules
            compliance_query = f"{doc_type.value if hasattr(doc_type, 'value') else str(doc_type)} compliance ADGM regulations"
            compliance_results = self.knowledge_extractor.query_knowledge_base(
                compliance_query,
                collection_names=relevant_collections,
                n_results=5
            )
            
            # Check against requirements
            if requirements_results.get('results'):
                requirement_checks = await self._validate_against_requirements(
                    content, requirements_results['results'], doc_type
                )
                checks.extend(requirement_checks)
            
            # Check against compliance rules
            if compliance_results.get('results'):
                compliance_checks = await self._validate_against_compliance_rules(
                    content, compliance_results['results'], doc_type
                )
                checks.extend(compliance_checks)
            
            # Template matching for specific document types
            if doc_type in [DocumentType.MEMORANDUM, DocumentType.ARTICLES, DocumentType.BOARD_RESOLUTION]:
                template_checks = await self._validate_against_templates(content, doc_type)
                checks.extend(template_checks)
        
        except Exception as e:
            print(f"Comprehensive knowledge validation error: {str(e)}")
        
        return checks
    
    async def _validate_against_requirements(self, content: str, requirements: List[Dict], doc_type: DocumentType) -> List[ComplianceCheck]:
        """Validate content against knowledge base requirements"""
        checks = []
        
        for req_item in requirements:
            req_content = req_item.get('content', '')
            req_metadata = req_item.get('metadata', {})
            
            # Extract key requirements from the content
            requirements_list = self._extract_requirements_from_text(req_content)
            
            for requirement in requirements_list:
                # Check if requirement is met in the document
                is_present = self._check_requirement_presence(content, requirement)
                is_compliant = is_present and self._validate_requirement_quality(content, requirement)
                
                issues = []
                recommendations = []
                
                if not is_present:
                    issues.append(f"Missing requirement: {requirement[:100]}...")
                    recommendations.append(f"Add section addressing: {requirement[:100]}...")
                elif not is_compliant:
                    issues.append(f"Requirement inadequately addressed: {requirement[:100]}...")
                    recommendations.append(f"Improve section covering: {requirement[:100]}...")
                
                if issues:  # Only add checks for issues found
                    check = ComplianceCheck(
                        section=f"KB Requirement: {req_metadata.get('section', 'Unknown')}",
                        required=True,
                        present=is_present,
                        compliant=is_compliant,
                        issues=issues,
                        recommendations=recommendations
                    )
                    checks.append(check)
        
        return checks
    
    async def _validate_against_compliance_rules(self, content: str, compliance_rules: List[Dict], doc_type: DocumentType) -> List[ComplianceCheck]:
        """Validate against specific compliance rules"""
        checks = []
        
        for rule_item in compliance_rules:
            rule_content = rule_item.get('content', '')
            rule_metadata = rule_item.get('metadata', {})
            
            # Extract compliance rules
            rules = self._extract_compliance_rules(rule_content)
            
            for rule in rules:
                violation = self._check_compliance_violation(content, rule)
                
                if violation:
                    check = ComplianceCheck(
                        section=f"Compliance Rule: {rule_metadata.get('regulation_ref', 'Unknown')}",
                        required=True,
                        present=True,
                        compliant=False,
                        issues=[violation],
                        recommendations=[f"Address compliance issue: {rule[:100]}..."]
                    )
                    checks.append(check)
        
        return checks
    
    async def _validate_against_templates(self, content: str, doc_type: DocumentType) -> List[ComplianceCheck]:
        """Validate against official ADGM templates"""
        checks = []
        
        try:
            # Query for templates
            template_query = f"{doc_type.value if hasattr(doc_type, 'value') else str(doc_type)} template structure"
            template_results = self.knowledge_extractor.query_knowledge_base(
                template_query,
                collection_names=['adgm_templates'],
                n_results=3
            )
            
            if template_results.get('results'):
                for template_item in template_results['results']:
                    template_content = template_item.get('content', '')
                    template_metadata = template_item.get('metadata', {})
                    
                    # Check template structure compliance
                    structure_issues = self._compare_with_template_structure(content, template_content)
                    
                    if structure_issues:
                        check = ComplianceCheck(
                            section=f"Template Compliance: {template_metadata.get('description', 'Unknown')}",
                            required=False,
                            present=True,
                            compliant=False,
                            issues=structure_issues,
                            recommendations=[f"Align with official template: {template_metadata.get('description', '')}"]
                        )
                        checks.append(check)
        
        except Exception as e:
            print(f"Template validation error: {str(e)}")
        
        return checks
    
    async def _validate_section(self, content: str, section: str, doc_type: DocumentType, structure: Dict) -> ComplianceCheck:
        """Validate individual section compliance"""
        
        # Check if section exists in document
        present = self._section_exists(content, section, structure)
        
        # Get ADGM requirements for this section
        requirements = await self._get_section_requirements(section, doc_type)
        
        # Validate section content if present
        issues = []
        recommendations = []
        compliant = present
        
        if present:
            section_content = self._extract_section_content(content, section, structure)
            validation_result = await self._validate_section_content(
                section_content, section, doc_type, requirements
            )
            
            issues = validation_result.get('issues', [])
            recommendations = validation_result.get('recommendations', [])
            compliant = validation_result.get('compliant', False)
        else:
            issues.append(f"Required section '{section}' is missing")
            recommendations.append(f"Add {section} section as required by ADGM regulations")
        
        return ComplianceCheck(
            section=section,
            required=True,
            present=present,
            compliant=compliant,
            issues=issues,
            recommendations=recommendations
        )
    
    def _section_exists(self, content: str, section: str, structure: Dict) -> bool:
        """Check if section exists in document"""
        
        # Check in headings
        headings = structure.get('headings', [])
        for heading in headings:
            if section.lower() in heading.get('text', '').lower():
                return True
        
        # Check in content using keywords
        section_keywords = {
            "company name": ["name of", "company name", "corporate name"],
            "registered office": ["registered office", "principal office", "head office"],
            "objects": ["objects", "business objects", "company objects"],
            "share capital": ["share capital", "capital", "authorized capital"],
            "liability": ["liability", "member liability", "limited liability"],
            "directors": ["directors", "board", "management"],
            "meetings": ["meetings", "general meeting", "shareholders meeting"]
        }
        
        keywords = section_keywords.get(section.lower(), [section.lower()])
        content_lower = content.lower()
        
        return any(keyword in content_lower for keyword in keywords)
    
    async def _get_section_requirements(self, section: str, doc_type: DocumentType) -> Dict:
        """Get ADGM requirements for specific section"""
        
        # First try enhanced knowledge base if available
        if self.knowledge_initialized:
            try:
                results = self.knowledge_extractor.query_knowledge_base(
                    f"{section} {doc_type.value if hasattr(doc_type, 'value') else str(doc_type)} requirements",
                    n_results=3
                )
                
                if results.get('results'):
                    requirements = {
                        'regulations': [r.get('content', '') for r in results['results']],
                        'references': [r.get('metadata', {}) for r in results['results']],
                        'source': 'enhanced_knowledge_base'
                    }
                    return requirements
            except Exception as e:
                print(f"Error querying enhanced knowledge base: {str(e)}")
        
        # Fallback to basic ChromaDB if available
        if self.adgm_collection:
            try:
                results = self.adgm_collection.query(
                    query_texts=[f"{section} {doc_type.value if hasattr(doc_type, 'value') else str(doc_type)} requirements"],
                    n_results=3
                )
                
                requirements = {
                    'regulations': results['documents'][0] if results['documents'] else [],
                    'references': results['metadatas'][0] if results['metadatas'] else [],
                    'source': 'basic_knowledge_base'
                }
                
                return requirements
                
            except Exception as e:
                print(f"Error querying basic ADGM knowledge base: {str(e)}")
        
        # Final fallback to hardcoded requirements
        return self._get_fallback_requirements(section, doc_type)
    
    def _get_fallback_requirements(self, section: str, doc_type: DocumentType) -> Dict:
        """Fallback requirements when knowledge bases are unavailable"""
        fallback_requirements = {
            "company name": {
                "must_include": ["Limited", "LLC", "PJSC"],
                "cannot_include": ["Bank", "Insurance"],
                "format": "Must end with appropriate legal suffix"
            },
            "registered office": {
                "must_include": ["ADGM", "Abu Dhabi"],
                "format": "Must be within ADGM jurisdiction"
            },
            "share capital": {
                "minimum": "AED 150,000 for private companies",
                "currency": "AED or USD accepted",
                "format": "Must specify authorized and issued capital"
            }
        }
        
        return fallback_requirements.get(section.lower(), {})
    
    def _extract_section_content(self, content: str, section: str, structure: Dict) -> str:
        """Extract content for specific section"""
        
        # Find section in structured content
        sections = structure.get('sections', [])
        for struct_section in sections:
            if section.lower() in struct_section.get('title', '').lower():
                return ' '.join(struct_section.get('content', []))
        
        # Fallback: extract using pattern matching
        lines = content.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section.lower() in line.lower() and any(char in line for char in ':.-'):
                in_section = True
                section_content.append(line)
            elif in_section:
                if self._is_new_section_start(line):
                    break
                section_content.append(line)
        
        return '\n'.join(section_content)
    
    def _is_new_section_start(self, line: str) -> bool:
        """Check if line indicates start of new section"""
        indicators = ['article', 'section', 'clause', 'part', 'chapter']
        line_lower = line.lower().strip()
        
        # Check for numbered sections
        if re.match(r'^\d+\.', line_lower):
            return True
        
        # Check for section indicators
        return any(indicator in line_lower for indicator in indicators)
    
    async def _validate_section_content(self, content: str, section: str, doc_type: DocumentType, requirements: Dict) -> Dict:
        """Validate specific section content against requirements"""
        
        issues = []
        recommendations = []
        compliant = True
        
        # Validate based on section type
        if section.lower() == "company name":
            name_validation = self._validate_company_name(content)
            issues.extend(name_validation['issues'])
            recommendations.extend(name_validation['recommendations'])
            compliant = compliant and name_validation['compliant']
        
        elif section.lower() == "share capital":
            capital_validation = self._validate_share_capital(content)
            issues.extend(capital_validation['issues'])
            recommendations.extend(capital_validation['recommendations'])  
            compliant = compliant and capital_validation['compliant']
        
        elif section.lower() == "registered office":
            office_validation = self._validate_registered_office(content)
            issues.extend(office_validation['issues'])
            recommendations.extend(office_validation['recommendations'])
            compliant = compliant and office_validation['compliant']
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_company_name(self, content: str) -> Dict:
        """Validate company name compliance"""
        issues = []
        recommendations = []
        compliant = True
        
        content_upper = content.upper()
        
        # Check for required legal suffix
        legal_suffixes = ['LIMITED', 'LTD', 'LLC', 'PJSC', 'PLC']
        has_suffix = any(suffix in content_upper for suffix in legal_suffixes)
        
        if not has_suffix:
            issues.append("Company name must include legal suffix (Limited, LLC, etc.)")
            recommendations.append("Add appropriate legal suffix to company name")
            compliant = False
        
        # Check for prohibited terms
        prohibited_terms = ['BANK', 'INSURANCE', 'ISLAMIC', 'TRUST']
        for term in prohibited_terms:
            if term in content_upper:
                issues.append(f"Company name contains prohibited term: {term}")
                recommendations.append(f"Remove or replace prohibited term: {term}")
                compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_share_capital(self, content: str) -> Dict:
        """Validate share capital compliance"""
        issues = []
        recommendations = []
        compliant = True
        
        # Extract capital amounts
        capital_pattern = r'(AED|USD)\s*([0-9,]+)'
        matches = re.findall(capital_pattern, content, re.IGNORECASE)
        
        if not matches:
            issues.append("Share capital amount not clearly specified")
            recommendations.append("Clearly specify share capital amount in AED or USD")
            compliant = False
        else:
            # Check minimum capital requirement (AED 150,000 for private companies)
            for currency, amount_str in matches:
                try:
                    amount = int(amount_str.replace(',', ''))
                    if currency.upper() == 'AED' and amount < 150000:
                        issues.append(f"Share capital {currency} {amount_str} below minimum requirement")
                        recommendations.append("Increase share capital to meet minimum AED 150,000 requirement")
                        compliant = False
                except ValueError:
                    issues.append("Invalid share capital amount format")
                    compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_registered_office(self, content: str) -> Dict:
        """Validate registered office compliance"""
        issues = []
        recommendations = []
        compliant = True
        
        content_upper = content.upper()
        
        # Check for ADGM jurisdiction
        adgm_indicators = ['ADGM', 'ABU DHABI GLOBAL MARKET', 'AL MARYAH ISLAND']
        has_adgm = any(indicator in content_upper for indicator in adgm_indicators)
        
        if not has_adgm:
            issues.append("Registered office must be within ADGM jurisdiction")
            recommendations.append("Specify registered office address within ADGM")
            compliant = False
        
        # Check for complete address
        address_components = ['FLOOR', 'BUILDING', 'STREET', 'P.O.', 'UAE']
        missing_components = [comp for comp in address_components if comp not in content_upper]
        
        if len(missing_components) > 2:
            issues.append("Incomplete registered office address")
            recommendations.append("Provide complete address including building, floor, and P.O. Box")
            compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    async def _perform_specific_validations(self, content: str, doc_type: DocumentType) -> List[ComplianceCheck]:
        """Perform document-type specific validations"""
        specific_checks = []
        
        try:
            if doc_type == DocumentType.MEMORANDUM:
                specific_checks.extend(await self._validate_memorandum_specific(content))
            elif doc_type == DocumentType.ARTICLES:
                specific_checks.extend(await self._validate_articles_specific(content))
            elif doc_type == DocumentType.APPLICATION:
                specific_checks.extend(await self._validate_application_specific(content))
            elif doc_type == DocumentType.BOARD_RESOLUTION:
                specific_checks.extend(await self._validate_resolution_specific(content))
                
        except Exception as e:
            print(f"Specific validation error for {doc_type}: {str(e)}")
        
        return specific_checks
    
    async def _validate_memorandum_specific(self, content: str) -> List[ComplianceCheck]:
        """Memorandum-specific validations"""
        checks = []
        
        # Check for subscriber signatures
        signature_check = ComplianceCheck(
            section="Subscriber Signatures",
            required=True,
            present="signature" in content.lower() or "signed" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if not signature_check.present:
            signature_check.issues.append("Subscriber signatures missing")
            signature_check.recommendations.append("Add subscriber signatures section")
        else:
            signature_check.compliant = True
        
        checks.append(signature_check)
        
        return checks
    
    async def _validate_articles_specific(self, content: str) -> List[ComplianceCheck]:
        """Articles-specific validations"""
        checks = []
        
        # Check for board composition
        board_check = ComplianceCheck(
            section="Board Composition",
            required=True,
            present="director" in content.lower() and "board" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if board_check.present:
            # Check for minimum director requirement
            if "one director" in content.lower() or "1 director" in content.lower():
                board_check.compliant = True
            else:
                board_check.issues.append("Minimum director requirements not clearly specified")
                board_check.recommendations.append("Specify minimum number of directors")
        else:
            board_check.issues.append("Board composition not addressed")
            board_check.recommendations.append("Add board composition and director requirements")
        
        checks.append(board_check)
        
        return checks
    
    async def _validate_application_specific(self, content: str) -> List[ComplianceCheck]:
        """Application-specific validations"""  
        checks = []
        
        # Check for business activity codes
        activity_check = ComplianceCheck(
            section="Business Activities",
            required=True,
            present="activity" in content.lower() or "business" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if activity_check.present:
            # Look for activity codes (simplified check)
            if re.search(r'\d{4,5}', content):
                activity_check.compliant = True
            else:
                activity_check.issues.append("Business activity codes not specified")
                activity_check.recommendations.append("Include specific ADGM business activity codes")
        else:
            activity_check.issues.append("Business activities section missing")
            activity_check.recommendations.append("Add detailed business activities description")
        
        checks.append(activity_check)
        
        return checks
    
    async def _validate_resolution_specific(self, content: str) -> List[ComplianceCheck]:
        """Board resolution-specific validations"""
        checks = []
        
        # Check for meeting quorum
        quorum_check = ComplianceCheck(
            section="Meeting Quorum",
            required=True,
            present="quorum" in content.lower() or "present" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if quorum_check.present:
            quorum_check.compliant = True
        else:
            quorum_check.issues.append("Meeting quorum not confirmed")
            quorum_check.recommendations.append("Confirm meeting quorum was achieved")
        
        checks.append(quorum_check)
        
        return checks
    
    def calculate_compliance_score(self, compliance_checks: List[ComplianceCheck]) -> float:
        """Calculate overall compliance score"""
        if not compliance_checks:
            return 0.0
        
        total_checks = len(compliance_checks)
        compliant_checks = sum(1 for check in compliance_checks if check.compliant)
        
        return round((compliant_checks / total_checks) * 100, 2)
    
    def get_missing_documents_checklist(self, doc_type: DocumentType, uploaded_docs: List[str]) -> List[str]:
        """Get list of missing required documents for incorporation process"""
        
        incorporation_requirements = {
            DocumentType.APPLICATION: [
                "Company Registration Application",
                "Memorandum of Association", 
                "Articles of Association",
                "Board Resolution (if applicable)",
                "Passport copies of directors",
                "Proof of registered office"
            ]
        }
        
        required_docs = incorporation_requirements.get(doc_type, [])
        uploaded_doc_types = [doc.lower() for doc in uploaded_docs]
        
        missing_docs = []
        for required_doc in required_docs:
            if not any(req.lower() in uploaded for req in [required_doc] for uploaded in uploaded_doc_types):
                missing_docs.append(required_doc)
        
        return missing_docs
    
    # Enhanced knowledge base methods
    def _extract_requirements_from_text(self, text: str) -> List[str]:
        """Extract specific requirements from knowledge base text"""
        requirements = []
        
        # Look for requirement patterns
        requirement_patterns = [
            r'must\s+(?:include|contain|have|specify)\s+([^.]{20,100})',
            r'required?\s+(?:to|that)\s+([^.]{20,100})',
            r'shall\s+(?:include|contain|have|specify)\s+([^.]{20,100})',
            r'company\s+(?:must|shall)\s+([^.]{20,100})'
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                requirement = match.group(1).strip()
                if len(requirement) > 15:  # Filter out very short matches
                    requirements.append(requirement)
        
        # Also look for bullet points or numbered lists
        list_patterns = [
            r'[•\-\*]\s+([^.\n]{20,100})',
            r'\d+\.\s+([^.\n]{20,100})'
        ]
        
        for pattern in list_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                requirement = match.group(1).strip()
                if len(requirement) > 15:
                    requirements.append(requirement)
        
        return list(set(requirements))  # Remove duplicates
    
    def _extract_compliance_rules(self, text: str) -> List[str]:
        """Extract compliance rules from knowledge base text"""
        rules = []
        
        # Look for prohibition patterns
        prohibition_patterns = [
            r'(?:cannot|must not|shall not|prohibited)\s+([^.]{15,80})',
            r'not\s+(?:permitted|allowed)\s+to\s+([^.]{15,80})'
        ]
        
        for pattern in prohibition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                rule = match.group(1).strip()
                if len(rule) > 10:
                    rules.append(rule)
        
        # Look for mandatory compliance patterns
        compliance_patterns = [
            r'comply\s+with\s+([^.]{15,80})',
            r'accordance\s+with\s+([^.]{15,80})',
            r'subject\s+to\s+([^.]{15,80})'
        ]
        
        for pattern in compliance_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                rule = match.group(1).strip()
                if len(rule) > 10:
                    rules.append(rule)
        
        return list(set(rules))
    
    def _check_requirement_presence(self, content: str, requirement: str) -> bool:
        """Check if a requirement is addressed in the document"""
        content_lower = content.lower()
        requirement_lower = requirement.lower()
        
        # Extract key terms from requirement
        key_terms = self._extract_key_terms_from_requirement(requirement_lower)
        
        # Check if most key terms are present
        found_terms = sum(1 for term in key_terms if term in content_lower)
        
        # Requirement is considered present if 60% or more key terms are found
        return found_terms >= len(key_terms) * 0.6
    
    def _extract_key_terms_from_requirement(self, requirement: str) -> List[str]:
        """Extract key terms from a requirement"""
        # Remove common words and extract meaningful terms
        common_words = {
            'the', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'by', 'at', 'is', 'are', 'be', 
            'must', 'shall', 'should', 'include', 'contain', 'have', 'specify', 'company'
        }
        
        words = re.findall(r'\b[a-z]{3,}\b', requirement.lower())
        key_terms = [word for word in words if word not in common_words]
        
        return list(set(key_terms))[:8]  # Limit to 8 key terms
    
    def _validate_requirement_quality(self, content: str, requirement: str) -> bool:
        """Check if requirement is adequately addressed"""
        # Simple quality check based on context around key terms
        key_terms = self._extract_key_terms_from_requirement(requirement.lower())
        
        quality_score = 0
        for term in key_terms:
            # Find sentences containing the term
            sentences = re.findall(f'[^.]*{term}[^.]*\.', content.lower())
            
            # Award points for longer, more detailed sentences
            for sentence in sentences:
                if len(sentence) > 100:  # Detailed explanation
                    quality_score += 2
                elif len(sentence) > 50:   # Moderate detail
                    quality_score += 1
        
        # Requirement is well-addressed if quality score is reasonable
        return quality_score >= len(key_terms)
    
    def _check_compliance_violation(self, content: str, rule: str) -> str:
        """Check if content violates a compliance rule"""
        content_lower = content.lower()
        rule_lower = rule.lower()
        
        # Extract prohibited/required terms from rule
        if 'cannot' in rule_lower or 'must not' in rule_lower or 'prohibited' in rule_lower:
            # This is a prohibition rule
            prohibited_terms = self._extract_key_terms_from_requirement(rule_lower)
            
            for term in prohibited_terms:
                if term in content_lower:
                    return f"Document may violate prohibition: contains '{term}'"
        
        elif 'must' in rule_lower or 'shall' in rule_lower or 'comply' in rule_lower:
            # This is a requirement rule
            required_terms = self._extract_key_terms_from_requirement(rule_lower)
            missing_terms = [term for term in required_terms if term not in content_lower]
            
            if len(missing_terms) > len(required_terms) * 0.5:  # More than 50% missing
                return f"Document may not comply with requirement: missing {', '.join(missing_terms[:3])}"
        
        return ""  # No violation found
    
    def _compare_with_template_structure(self, content: str, template_content: str) -> List[str]:
        """Compare document structure with official template"""
        issues = []
        
        # Extract structural elements from template
        template_headings = re.findall(r'(?:^|\n)([A-Z][A-Z\s]{10,50})(?:\n|$)', template_content)
        content_upper = content.upper()
        
        missing_headings = []
        for heading in template_headings:
            heading = heading.strip()
            if len(heading) > 5 and heading not in content_upper:
                # Check for partial matches
                heading_words = heading.split()
                if len(heading_words) > 1:
                    # Check if at least half the words are present
                    found_words = sum(1 for word in heading_words if word in content_upper)
                    if found_words < len(heading_words) * 0.5:
                        missing_headings.append(heading)
        
        if missing_headings:
            issues.append(f"Missing template sections: {', '.join(missing_headings[:3])}")
        
        # Check for template-specific formatting requirements
        if 'signature' in template_content.lower() and 'signature' not in content.lower():
            issues.append("Missing signature section as shown in template")
        
        if 'date' in template_content.lower() and not re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', content):
            issues.append("Missing date formatting as shown in template")
        
        return issues
    
    async def get_contextual_recommendations(self, content: str, doc_type: DocumentType, issues: List[str]) -> List[str]:
        """Get contextual recommendations from knowledge base"""
        recommendations = []
        
        if not self.knowledge_initialized:
            return recommendations
        
        try:
            # Query for solutions to identified issues
            for issue in issues[:3]:  # Limit to top 3 issues
                solution_query = f"how to fix {issue} {doc_type.value if hasattr(doc_type, 'value') else str(doc_type)}"
                solution_results = self.knowledge_extractor.query_knowledge_base(
                    solution_query,
                    n_results=2
                )
                
                if solution_results.get('results'):
                    for result in solution_results['results']:
                        content_text = result.get('content', '')
                        # Extract actionable recommendations
                        actionable_recs = self._extract_actionable_recommendations(content_text)
                        recommendations.extend(actionable_recs[:2])  # Limit recommendations per issue
        
        except Exception as e:
            print(f"Error getting contextual recommendations: {str(e)}")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _extract_actionable_recommendations(self, text: str) -> List[str]:
        """Extract actionable recommendations from knowledge base text"""
        recommendations = []
        
        # Look for recommendation patterns
        rec_patterns = [
            r'(?:should|must|recommend|suggest)\s+([^.]{20,100})',
            r'(?:add|include|specify|ensure)\s+([^.]{20,100})',
            r'(?:to|for)\s+(?:comply|meet|satisfy)\s+([^.]{20,100})'
        ]
        
        for pattern in rec_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                rec = match.group(1).strip()
                if len(rec) > 15:
                    recommendations.append(rec)
        
        return recommendations[:3]  # Limit to 3 recommendations per text
    
    async def validate_document_against_checklist(self, content: str, doc_type: DocumentType) -> Dict:
        """Validate document against ADGM checklists from knowledge base"""
        if not self.knowledge_initialized:
            return {"error": "Knowledge base not initialized"}
        
        try:
            # Query for relevant checklists
            checklist_query = f"checklist {doc_type.value if hasattr(doc_type, 'value') else str(doc_type)} requirements"
            checklist_results = self.knowledge_extractor.query_knowledge_base(
                checklist_query,
                collection_names=['adgm_compliance'],
                n_results=3
            )
            
            checklist_items = []
            if checklist_results.get('results'):
                for result in checklist_results['results']:
                    items = self._extract_checklist_items(result.get('content', ''))
                    checklist_items.extend(items)
            
            # Check document against checklist items
            results = {
                'total_items': len(checklist_items),
                'completed_items': 0,
                'missing_items': [],
                'compliance_percentage': 0
            }
            
            for item in checklist_items:
                if self._check_requirement_presence(content, item):
                    results['completed_items'] += 1
                else:
                    results['missing_items'].append(item)
            
            if results['total_items'] > 0:
                results['compliance_percentage'] = round(
                    (results['completed_items'] / results['total_items']) * 100, 2
                )
            
            return results
        
        except Exception as e:
            return {"error": f"Checklist validation failed: {str(e)}"}
    
    def _extract_checklist_items(self, text: str) -> List[str]:
        """Extract checklist items from knowledge base text"""
        items = []
        
        # Look for checklist patterns
        checklist_patterns = [
            r'[✓✗☐☑]\s*([^.\n]{15,100})',  # Checkbox items
            r'(?:^|\n)\s*[-•*]\s+([^.\n]{15,100})',  # Bullet points
            r'(?:^|\n)\s*\d+\.\s+([^.\n]{15,100})',  # Numbered items
            r'(?:^|\n)\s*[a-z]\)\s+([^.\n]{15,100})'  # Lettered items
        ]
        
        for pattern in checklist_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                item = match.group(1).strip()
                if len(item) > 10 and item not in items:
                    items.append(item)
        
        return items[:20]  # Limit to 20 items per text
    
    def get_knowledge_base_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if self.knowledge_initialized:
            return self.knowledge_extractor.get_knowledge_stats()
        else:
            return {
                "status": "fallback_mode",
                "total_documents": self.adgm_collection.count() if self.adgm_collection else 0,
                "collections": {"basic_adgm_regulations": self.adgm_collection.count() if self.adgm_collection else 0}
            }