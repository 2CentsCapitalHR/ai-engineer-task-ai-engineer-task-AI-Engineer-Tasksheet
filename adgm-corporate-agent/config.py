# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # OpenAI Configuration
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY not found in environment variables")

# # Alternative API Keys
# ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# # Application Settings
# DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
# MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
# ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'docx').split(',')

# # Vector Store Configuration
# VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'data/vector_store/')
# EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

# # RAG Configuration
# CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
# CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '50'))
# RETRIEVAL_TOP_K = int(os.getenv('RETRIEVAL_TOP_K', '5'))

# # LLM Settings
# LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
# MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
# TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))

# # ADGM Data Sources
# ADGM_URLS = [
#     "https://www.adgm.com/registration-authority/registration-and-incorporation",
#     "https://www.adgm.com/setting-up",
#     "https://www.adgm.com/legal-framework/guidance-and-policy-statements",

# ]

# # Validation
# def validate_config():
#     """Validate that required configuration is present"""
#     if not OPENAI_API_KEY:
#         raise ValueError("OpenAI API key is required")
    
#     if not os.path.exists('data'):
#         os.makedirs('data')
#         os.makedirs('data/vector_store')
    
#     print("✅ Configuration validated successfully")

# if __name__ == "__main__":
#     validate_config()

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Alternative API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Application Settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'docx').split(',')

# Vector Store Configuration
VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'data/vector_store/')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

# RAG Configuration
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '50'))
RETRIEVAL_TOP_K = int(os.getenv('RETRIEVAL_TOP_K', '5'))

# LLM Settings
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))

# ADGM Data Sources - Complete List from Data-Sources.pdf
ADGM_URLS = {
    # Company Formation & Governance
    "company_formation_main": "https://www.adgm.com/registration-authority/registration-and-incorporation",
    
    "company_setup_guide": "https://www.adgm.com/setting-up",
    
    # Policy & Guidance
    "legal_framework_guidance": "https://www.adgm.com/legal-framework/guidance-and-policy-statements",
    
    # Document Templates - Company Formation
    "resolution_multiple_shareholders": "https://assets.adgm.com/download/assets/adgm-ra-resolution-multiple-incorporate-shareholders-LTD-incorporation-v2.docx/186a12846c3911efa4e6c6223862cd87",
    
    # Checklists
    "checklist_branch_non_financial": "https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/branch-non-financial-services-20231228.pdf",
    
    "checklist_private_company_limited": "https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/private-company-limited-by-guarantee-non-financial-services-20231228.pdf",
    
    # Employment & HR Templates
    "employment_contract_2024": "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+Template+-+ER+2024+(Feb+2025).docx/ee14b252edbe11efa63b12b3a30e5e3a",
    
    "employment_contract_2019_short": "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+-+ER+2019+-+Short+Version+(May+2024).docx/33b57a92ecfe11ef97a536cc36767ef8",
    
    # Data Protection
    "data_protection_policy_template": "https://www.adgm.com/documents/office-of-data-protection/templates/adgm-dpr-2021-appropriate-policy-document.pdf",
    
    # Compliance & Filings
    "annual_accounts_filings": "https://www.adgm.com/operating-in-adgm/obligations-of-adgm-registered-entities/annual-filings/annual-accounts",
    
    # Letters & Permits
    "letters_permits_application": "https://www.adgm.com/operating-in-adgm/post-registration-services/letters-and-permits",
    
    # Regulatory Guidance
    "incorporation_package_thomson": "https://en.adgm.thomsonreuters.com/rulebook/7-company-incorporation-package",
    
    # Regulatory Templates
    "shareholder_resolution_amendment": "https://assets.adgm.com/download/assets/Templates_SHReso_AmendmentArticles-v1-20220107.docx/97120d7c5af911efae4b1e183375c0b2?forcedownload=1"
}

# Categorized URLs for easier processing
ADGM_URL_CATEGORIES = {
    "company_formation": [
        "https://www.adgm.com/registration-authority/registration-and-incorporation",
        "https://www.adgm.com/setting-up",
        "https://assets.adgm.com/download/assets/adgm-ra-resolution-multiple-incorporate-shareholders-LTD-incorporation-v2.docx/186a12846c3911efa4e6c6223862cd87"
    ],
    
    "checklists": [
        "https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/branch-non-financial-services-20231228.pdf",
        "https://www.adgm.com/documents/registration-authority/registration-and-incorporation/checklist/private-company-limited-by-guarantee-non-financial-services-20231228.pdf"
    ],
    
    "employment_hr": [
        "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+Template+-+ER+2024+(Feb+2025).docx/ee14b252edbe11efa63b12b3a30e5e3a",
        "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+-+ER+2019+-+Short+Version+(May+2024).docx/33b57a92ecfe11ef97a536cc36767ef8"
    ],
    
    "compliance_regulatory": [
        "https://www.adgm.com/legal-framework/guidance-and-policy-statements",
        "https://www.adgm.com/operating-in-adgm/obligations-of-adgm-registered-entities/annual-filings/annual-accounts",
        "https://www.adgm.com/operating-in-adgm/post-registration-services/letters-and-permits",
        "https://en.adgm.thomsonreuters.com/rulebook/7-company-incorporation-package"
    ],
    
    "data_protection": [
        "https://www.adgm.com/documents/office-of-data-protection/templates/adgm-dpr-2021-appropriate-policy-document.pdf"
    ],
    
    "templates": [
        "https://assets.adgm.com/download/assets/Templates_SHReso_AmendmentArticles-v1-20220107.docx/97120d7c5af911efae4b1e183375c0b2?forcedownload=1"
    ]
}

# Document Type Mapping
DOCUMENT_TYPE_SOURCES = {
    "articles_of_association": [
        "https://www.adgm.com/registration-authority/registration-and-incorporation",
        "https://www.adgm.com/setting-up"
    ],
    "memorandum_of_association": [
        "https://www.adgm.com/registration-authority/registration-and-incorporation",
        "https://www.adgm.com/setting-up"
    ],
    "board_resolution": [
        "https://assets.adgm.com/download/assets/adgm-ra-resolution-multiple-incorporate-shareholders-LTD-incorporation-v2.docx/186a12846c3911efa4e6c6223862cd87"
    ],
    "employment_contract": [
        "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+Template+-+ER+2024+(Feb+2025).docx/ee14b252edbe11efa63b12b3a30e5e3a",
        "https://assets.adgm.com/download/assets/ADGM+Standard+Employment+Contract+-+ER+2019+-+Short+Version+(May+2024).docx/33b57a92ecfe11ef97a536cc36767ef8"
    ]
}

# Validation
def validate_config():
    """Validate that required configuration is present"""
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is required")
    
    if not os.path.exists('data'):
        os.makedirs('data')
        os.makedirs('data/vector_store', exist_ok=True)
    
    print("✅ Configuration validated successfully")
    print(f"📋 Total ADGM URLs loaded: {len(ADGM_URLS)}")
    print(f"📁 URL Categories: {list(ADGM_URL_CATEGORIES.keys())}")

def get_urls_by_category(category):
    """Get URLs for a specific category"""
    return ADGM_URL_CATEGORIES.get(category, [])

def get_all_urls():
    """Get all ADGM URLs as a flat list"""
    return list(ADGM_URLS.values())

if __name__ == "__main__":
    validate_config()
    print("\n📋 Available URL Categories:")
    for category, urls in ADGM_URL_CATEGORIES.items():
        print(f"  • {category}: {len(urls)} URLs")
