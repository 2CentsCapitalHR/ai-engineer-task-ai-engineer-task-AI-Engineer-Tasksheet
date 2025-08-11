# llm_checker.py

import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_legal_issues(text, doc_type):
    """
    Uses an AI model to check an ADGM document for compliance issues.
    Returns: list of dictionaries containing issues found.
    """
    prompt = f"""
    You are an expert in Abu Dhabi Global Market (ADGM) company regulations.
    Review the following document: {doc_type}
    Detect compliance issues, cite the exact ADGM law/regulation, 
    and provide a suggested fix.

    Format output exactly as JSON list like:
    [
        {{
            "section": "Clause 2.1",
            "issue": "Jurisdiction clause does not specify ADGM",
            "severity": "High",
            "suggestion": "Update jurisdiction to ADGM Courts."
        }}
    ]

    Document text:
    {text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change this to another available GPT model
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error while calling AI: {e}")
        return []
