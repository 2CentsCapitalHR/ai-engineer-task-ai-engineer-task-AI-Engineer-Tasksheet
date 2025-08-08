#!/usr/bin/env python3
"""
Setup script for ADGM Corporate Agent Pro
AI-Powered Legal Document Review & Compliance Assistant
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="adgm-corporate-agent",
    version="1.0.0",
    author="ADGM Corporate Agent Team",
    author_email="support@adgm-agent.com",
    description="AI-Powered Legal Document Review & Compliance Assistant for Abu Dhabi Global Market",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/adgm-corporate-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "adgm-agent=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
    },
    keywords="legal compliance adgm document analysis ai machine learning",
    project_urls={
        "Bug Reports": "https://github.com/your-username/adgm-corporate-agent/issues",
        "Source": "https://github.com/your-username/adgm-corporate-agent",
        "Documentation": "https://docs.adgm-agent.com",
        "Demo": "https://youtu.be/YU6zeUOyqEI",
    },
)
