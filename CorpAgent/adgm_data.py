"""ADGM compliance data and rules."""

# Document checklists for different legal processes
ADGM_DOCUMENT_CHECKLISTS = {
    'Company Incorporation': [
        'Articles of Association',
        'Memorandum of Association',
        'Incorporation Application Form',
        'UBO Declaration Form',
        'Register of Members and Directors'
    ],
    'Licensing Application': [
        'License Application Form',
        'Business Plan',
        'Financial Projections',
        'Compliance Manual',
        'Key Personnel CVs',
        'Articles of Association',
        'Memorandum of Association'
    ],
    'Employment Contracts': [
        'Employment Contract',
        'Job Description',
        'Salary Certificate',
        'Benefits Summary'
    ],
    'Commercial Agreements': [
        'Service Agreement',
        'Terms and Conditions',
        'Liability and Insurance Clauses',
        'Dispute Resolution Clauses'
    ],
    'Compliance Review': [
        'Compliance Manual',
        'Risk Assessment',
        'Policies and Procedures',
        'Training Records'
    ]
}

# Rule-based compliance checks
ADGM_COMPLIANCE_RULES = {
    'Articles of Association': {
        'adgm_jurisdiction': {
            'check_type': 'missing_pattern',
            'pattern': r'adgm|abu\s+dhabi\s+global\s+market',
            'section': 'Jurisdiction Clause',
            'issue': 'Document does not specify ADGM jurisdiction',
            'severity': 'High',
            'suggestion': 'Add clause specifying ADGM as governing jurisdiction',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 6'
        },
        'federal_court_reference': {
            'check_type': 'forbidden_pattern',
            'pattern': r'uae\s+federal\s+court|federal\s+court\s+of\s+uae',
            'section': 'Jurisdiction Clause',
            'issue': 'References UAE Federal Courts instead of ADGM Courts',
            'severity': 'High',
            'suggestion': 'Replace with ADGM Courts reference',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 6'
        },
        'share_capital': {
            'check_type': 'missing_pattern',
            'pattern': r'share\s+capital|authorized\s+capital|issued\s+capital',
            'section': 'Share Capital',
            'issue': 'Share capital provisions not clearly defined',
            'severity': 'Medium',
            'suggestion': 'Include detailed share capital structure',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 12'
        },
        'registered_office': {
            'check_type': 'missing_pattern',
            'pattern': r'registered\s+office.*adgm',
            'section': 'Registered Office',
            'issue': 'Registered office address must be in ADGM',
            'severity': 'High',
            'suggestion': 'Specify ADGM registered office address',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 25'
        }
    },
    
    'Memorandum of Association': {
        'company_objects': {
            'check_type': 'missing_pattern',
            'pattern': r'objects?\s+of\s+the\s+company|business\s+activities',
            'section': 'Company Objects',
            'issue': 'Company objects not clearly defined',
            'severity': 'Medium',
            'suggestion': 'Include detailed description of business activities',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 8'
        },
        'adgm_jurisdiction': {
            'check_type': 'missing_pattern',
            'pattern': r'adgm|abu\s+dhabi\s+global\s+market',
            'section': 'Jurisdiction',
            'issue': 'ADGM jurisdiction not specified',
            'severity': 'High',
            'suggestion': 'Add ADGM jurisdiction clause',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 6'
        }
    },
    
    'Employment Contract': {
        'adgm_employment_law': {
            'check_type': 'missing_pattern',
            'pattern': r'adgm\s+employment\s+regulations?',
            'section': 'Governing Law',
            'issue': 'Contract does not reference ADGM Employment Regulations',
            'severity': 'High',
            'suggestion': 'Add reference to ADGM Employment Regulations 2019',
            'adgm_reference': 'ADGM Employment Regulations 2019'
        },
        'minimum_wage': {
            'check_type': 'missing_pattern',
            'pattern': r'salary|wage|compensation|remuneration',
            'section': 'Compensation',
            'issue': 'Salary/wage provisions not clearly specified',
            'severity': 'Medium',
            'suggestion': 'Include detailed compensation structure',
            'adgm_reference': 'ADGM Employment Regulations 2019, Section 5'
        },
        'termination_clause': {
            'check_type': 'missing_pattern',
            'pattern': r'termination|notice\s+period|resignation',
            'section': 'Termination',
            'issue': 'Termination procedures not clearly defined',
            'severity': 'Medium',
            'suggestion': 'Include detailed termination and notice provisions',
            'adgm_reference': 'ADGM Employment Regulations 2019, Section 20'
        }
    },
    
    'Board Resolution': {
        'resolution_authority': {
            'check_type': 'missing_pattern',
            'pattern': r'board\s+of\s+directors?|directors?\s+resolve',
            'section': 'Authority',
            'issue': 'Board authority not clearly established',
            'severity': 'Medium',
            'suggestion': 'Clearly state board authority for the resolution',
            'adgm_reference': 'ADGM Companies Regulations 2020, Article 18'
        },
        'quorum_requirements': {
            'check_type': 'missing_pattern',
            'pattern': r'quorum|minimum\s+number.*directors?',
            'section': 'Quorum',
            'issue': 'Quorum requirements not specified',
            'severity': 'Low',
            'suggestion': 'Include quorum requirements for board meetings',
            'adgm_reference': 'ADGM Companies Regulations 2020'
        }
    },
    
    'UBO Declaration': {
        'beneficial_ownership': {
            'check_type': 'missing_pattern',
            'pattern': r'ultimate\s+beneficial\s+owner|beneficial\s+ownership|ubo',
            'section': 'UBO Definition',
            'issue': 'Ultimate beneficial ownership not clearly defined',
            'severity': 'High',
            'suggestion': 'Include clear UBO definition and disclosure',
            'adgm_reference': 'ADGM AML Regulations'
        },
        'ownership_percentage': {
            'check_type': 'missing_pattern',
            'pattern': r'\d+%|percent|percentage.*ownership',
            'section': 'Ownership Details',
            'issue': 'Ownership percentages not clearly specified',
            'severity': 'Medium',
            'suggestion': 'Include exact ownership percentages for all UBOs',
            'adgm_reference': 'ADGM AML Regulations'
        }
    }
}

# ADGM regulation references
ADGM_REGULATIONS = {
    'Companies Regulations 2020': {
        'url': 'https://en.adgm.com/legal-framework/companies-regulations/',
        'key_articles': {
            'Article 6': 'Jurisdiction and governing law',
            'Article 8': 'Company objects and activities',
            'Article 12': 'Share capital requirements',
            'Article 18': 'Directors and board requirements',
            'Article 25': 'Registered office requirements'
        }
    },
    'Employment Regulations 2019': {
        'url': 'https://en.adgm.com/legal-framework/employment-regulations/',
        'key_sections': {
            'Section 5': 'Minimum wage and compensation',
            'Section 12': 'Working hours and overtime',
            'Section 20': 'Termination and notice periods'
        }
    },
    'Licensing Regulations 2021': {
        'url': 'https://en.adgm.com/legal-framework/licensing-regulations/',
        'key_chapters': {
            'Chapter 3': 'Capital adequacy requirements',
            'Chapter 5': 'Key personnel qualifications',
            'Chapter 8': 'Ongoing compliance obligations'
        }
    }
}

# Common ADGM compliance issues and their fixes
COMMON_COMPLIANCE_ISSUES = {
    'jurisdiction_errors': {
        'issue': 'Referencing wrong jurisdiction (UAE Federal vs ADGM)',
        'fix': 'Update all jurisdiction references to ADGM Courts and ADGM laws',
        'severity': 'High'
    },
    'missing_adgm_clauses': {
        'issue': 'Missing mandatory ADGM-specific clauses',
        'fix': 'Add required ADGM clauses per relevant regulations',
        'severity': 'High'
    },
    'incomplete_ubo_disclosure': {
        'issue': 'Incomplete ultimate beneficial ownership disclosure',
        'fix': 'Provide complete UBO information with ownership percentages',
        'severity': 'High'
    },
    'non_compliant_employment_terms': {
        'issue': 'Employment terms not compliant with ADGM Employment Regulations',
        'fix': 'Update terms to comply with ADGM Employment Regulations 2019',
        'severity': 'Medium'
    },
    'missing_signatures': {
        'issue': 'Missing required signatures or execution clauses',
        'fix': 'Add proper signature blocks and execution requirements',
        'severity': 'Medium'
    }
}
