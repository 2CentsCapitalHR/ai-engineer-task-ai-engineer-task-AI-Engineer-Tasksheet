#!/usr/bin/env python3
"""Fix all DocumentIssue creations to include line_number parameter."""

import re
import os

def fix_document_issues(file_path):
    """Fix DocumentIssue creations in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match DocumentIssue creation without line_number
    pattern = r'DocumentIssue\(((?:[^)]|(?:\([^)]*\)))*)\)'
    
    def replace_func(match):
        inner_content = match.group(1)
        # Check if line_number is already present
        if 'line_number' in inner_content:
            return match.group(0)  # Already has line_number
        
        # Add line_number=None before the closing parenthesis
        return f'DocumentIssue({inner_content},\n                    line_number=None)'
    
    # Replace all occurrences
    new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    # Write back only if content changed
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {file_path}")
        return True
    return False

def main():
    """Fix all DocumentIssue creations in the project."""
    files_to_fix = [
        'src/core/compliance_checker.py',
        'src/rag/rag_system.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_document_issues(file_path):
                print(f"✓ Fixed DocumentIssue creations in {file_path}")
            else:
                print(f"- No changes needed in {file_path}")
        else:
            print(f"✗ File not found: {file_path}")

if __name__ == "__main__":
    main()
