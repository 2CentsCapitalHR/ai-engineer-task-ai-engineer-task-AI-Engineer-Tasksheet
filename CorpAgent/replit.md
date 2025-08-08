# Overview

The ADGM Corporate Agent is an AI-powered legal document review and compliance assistant specifically designed for the Abu Dhabi Global Market (ADGM) jurisdiction. The system analyzes legal documents uploaded by users, identifies compliance issues, and provides structured feedback to ensure adherence to ADGM regulations. It combines rule-based validation with AI-powered analysis using Retrieval-Augmented Generation (RAG) to deliver comprehensive document reviews for various corporate processes including company incorporation, licensing, employment contracts, and commercial agreements.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses Streamlit as the web interface framework, providing a simple and intuitive UI for document upload and review. The main interface (`app.py`) orchestrates the interaction between different system components and presents results through a web-based dashboard with sidebar configuration options.

## Core Document Processing Pipeline
The system follows a multi-stage document analysis approach:

1. **Document Ingestion**: Accepts `.docx` files through the Streamlit interface
2. **Type Detection**: Uses pattern matching to automatically identify document types (Articles of Association, Employment Contracts, etc.)
3. **Content Extraction**: Parses document structure, paragraphs, tables, and formatting
4. **Dual Analysis**: Combines rule-based compliance checking with AI-powered RAG analysis
5. **Output Generation**: Produces marked-up documents with comments and structured compliance reports

## Compliance Engine Architecture
The compliance checking system (`ComplianceChecker`) implements a dual-validation approach:

- **Rule-Based Validation**: Predefined patterns and checks for specific ADGM requirements stored in `adgm_data.py`
- **AI-Enhanced Analysis**: Uses OpenAI GPT-4o through the RAG system for contextual understanding and complex compliance assessment
- **Process Validation**: Checks document completeness against predefined checklists for different legal processes

## RAG System Design
The Retrieval-Augmented Generation system (`RAGSystem`) serves as the AI backbone:

- **Knowledge Base**: Contains structured ADGM legal requirements, red flags, and compliance criteria
- **LLM Integration**: Uses OpenAI GPT-4o model for document analysis and natural language processing
- **Contextual Analysis**: Provides intelligent insights beyond pattern matching for nuanced legal interpretation

## Document Markup and Output System
The `DocumentProcessor` handles:

- **Content Parsing**: Extracts text, structure, and metadata from Word documents
- **Markup Generation**: Adds comments and highlights to identify compliance issues
- **Format Preservation**: Maintains original document formatting while adding review annotations
- **Export Functionality**: Generates downloadable reviewed documents with embedded feedback

## Data Management
Document checklists and compliance rules are stored in structured Python dictionaries within `adgm_data.py`, allowing for easy maintenance and updates to ADGM requirements without code changes.

# External Dependencies

## AI Services
- **OpenAI API**: Primary LLM service using GPT-4o model for document analysis and natural language understanding
- **OpenAI Client Library**: Python SDK for API integration

## Document Processing
- **python-docx**: Library for reading, parsing, and modifying Microsoft Word documents
- **Streamlit**: Web application framework for the user interface

## Utility Libraries
- **Standard Python Libraries**: Regular expressions (re), JSON processing, datetime handling, and I/O operations for core functionality

## Configuration
- **Environment Variables**: OpenAI API key management through environment variables with fallback to user input
- **Caching**: Streamlit resource caching for system initialization to improve performance

The system is designed to be self-contained with minimal external dependencies, focusing on document processing and AI-powered analysis capabilities specific to ADGM legal compliance requirements.