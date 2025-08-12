CATEGORY_KEYWORDS = {
    "Company Formation & Governance": [
        "articles of association", "memorandum of association",
        "board resolution", "ubo", "register of members", "incorporation application"
    ],
    "Company Formation (Resolution for Incorporation)": [
        "resolution for incorporation", "multiple shareholders", "limited company", "ltd incorporation"
    ],
    "Company Formation & Compliance (SPV, LLC, Other Forms)": [
        "special purpose vehicle", "spv", "limited liability company", "llc incorporation"
    ],
    "Policy & Guidance": [
        "policy statement", "guidance", "template policy", "adgm policy"
    ],
    "ADGM Company Set-up — Checklist (Branch)": [
        "branch registration", "non-financial services branch", "branch incorporation checklist"
    ],
    "ADGM Company Set-up — Checklist (Private Company Limited)": [
        "private company limited", "guarantee", "non-financial services", "company setup checklist"
    ],
    "Employment & HR (2024 Template)": [
        "employment contract", "employer", "employee", "salary", "leave entitlement", "probation"
    ],
    "Employment & HR (2019 Short Version)": [
        "employment contract", "short version", "employer", "employee"
    ],
    "Data Protection": [
        "appropriate policy document", "data protection", "personal data", "data privacy"
    ],
    "Compliance & Filings (Annual Accounts)": [
        "annual accounts", "financial statements", "compliance filing", "filing requirements"
    ],
    "Letters & Permits": [
        "application for official letter", "permit application", "official letters", "permits"
    ],
    "Regulatory Guidance (Incorporation Package)": [
        "incorporation package", "filings", "incorporation guidance", "regulatory guidance"
    ],
    "Regulatory Template (Shareholder Resolution — Amendment of Articles)": [
        "shareholder resolution", "amendment of articles", "template shareholder resolution"
    ]
}


def detect_category(text):
    """Detects category based on keyword matches in document text."""
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in text.lower():
                scores[cat] += 1
    # Return category with highest score
    return max(scores, key=scores.get)
