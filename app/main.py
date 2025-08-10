import os
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from app.models import (
    DocumentAnalysis, ProcessingStatus, DocumentType, FlagSeverity, DocumentFlag,
    APIResponse, ProcessingRequest, AnalysisReport, ADGMValidationRequest, ComplianceCheck
)
from app.services.document_parser import DocumentParser
from app.services.gemini_analyzer import GeminiAnalyzer
from app.services.adgm_validator import ADGMValidator  # Updated to use merged validator
from app.utils.file_handler import FileHandler
from app.utils.report_generator import ReportGenerator
from config import settings

# Global storage for document analyses (in production, use proper database)
document_store: Dict[str, DocumentAnalysis] = {}
processing_queue: asyncio.Queue = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global processing_queue
    
    # Startup
    processing_queue = asyncio.Queue(maxsize=settings.MAX_CONCURRENT_ANALYSES)
    
    # Initialize enhanced ADGM validator with knowledge base
    print("🚀 Initializing ADGM Knowledge Base...")
    knowledge_success = await adgm_validator.initialize_knowledge_base()
    
    if knowledge_success:
        print("✅ ADGM Knowledge Base initialized successfully")
        stats = adgm_validator.get_knowledge_base_stats()
        print(f"📊 Knowledge Base Stats: {stats}")
    else:
        print("⚠️ ADGM Knowledge Base initialization failed - using fallback mode")
    
    # Start background processor
    processor_task = asyncio.create_task(process_documents_background())
    
    print("ADGM Corporate Agent started successfully")
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    print(f"Output directory: {settings.OUTPUT_DIR}")
    
    yield
    
    # Shutdown
    processor_task.cancel()
    try:
        await processor_task
    except asyncio.CancelledError:
        pass
    
    print("ADGM Corporate Agent shut down")

# Initialize FastAPI app
app = FastAPI(
    title="ADGM Corporate Agent",
    description="AI-powered legal assistant for ADGM document compliance with comprehensive knowledge base",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize services
document_parser = DocumentParser()
gemini_analyzer = GeminiAnalyzer()
adgm_validator = ADGMValidator()  # Updated to use merged validator
file_handler = FileHandler()
report_generator = ReportGenerator()

# Background document processor
async def process_documents_background():
    """Background task to process documents in queue"""
    while True:
        try:
            # Get document from queue
            document_id = await processing_queue.get()
            
            if document_id in document_store:
                analysis = document_store[document_id]
                
                try:
                    # Update status
                    analysis.status = ProcessingStatus.ANALYZING
                    
                    # Process document
                    await process_document_analysis(document_id)
                    
                    # Mark as completed
                    analysis.status = ProcessingStatus.COMPLETED
                    analysis.completed_at = datetime.now()
                    
                except Exception as e:
                    # Mark as error
                    analysis.status = ProcessingStatus.ERROR
                    analysis.analysis_summary = f"Processing failed: {str(e)}"
                    print(f"Error processing document {document_id}: {str(e)}")
                
                # Mark task as done
                processing_queue.task_done()
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Background processor error: {str(e)}")
            await asyncio.sleep(1)

async def process_document_analysis(document_id: str):
    """Process individual document analysis with enhanced knowledge base"""
    analysis = document_store[document_id]
    
    # Parse document
    file_path = getattr(analysis, 'file_path', '')
    parsed_doc = await document_parser.parse_document(file_path)
    
    # Update document type if detected
    if parsed_doc['document_type'] != DocumentType.UNKNOWN:
        analysis.document_type = parsed_doc['document_type']
    
    # Run Gemini analysis
    gemini_results = await gemini_analyzer.analyze_document(
        parsed_doc['content']['text'],
        analysis.document_type
    )
    
    # Process red flags
    if 'red_flags' in gemini_results and gemini_results['red_flags'].get('flags'):
        for flag_data in gemini_results['red_flags']['flags']:
            flag = DocumentFlag(
                severity=FlagSeverity(flag_data.get('severity', 'info')),
                title=flag_data.get('title', ''),
                description=flag_data.get('description', ''),
                location=flag_data.get('location', ''),
                suggested_fix=flag_data.get('suggested_fix'),
                adgm_reference=flag_data.get('adgm_reference')
            )
            analysis.flags.append(flag)
    
    # Run enhanced ADGM validation (now includes knowledge base integration)
    compliance_checks = await adgm_validator.validate_document_compliance(
        parsed_doc['content']['text'],
        analysis.document_type,
        parsed_doc['structure']
    )
    analysis.compliance_checks = compliance_checks
    
    # Calculate scores
    analysis.compliance_score = adgm_validator.calculate_compliance_score(compliance_checks)
    
    # Calculate completeness score
    if 'completeness' in gemini_results:
        completeness_data = gemini_results['completeness']
        analysis.completeness_score = completeness_data.get('completeness_score', 0.0) * 100
        analysis.missing_sections = completeness_data.get('missing_sections', [])
    
    # Get contextual recommendations from knowledge base
    issues = [flag.title for flag in analysis.flags]
    contextual_recommendations = await adgm_validator.get_contextual_recommendations(
        parsed_doc['content']['text'], 
        analysis.document_type, 
        issues
    )
    
    # Run checklist validation if knowledge base is available
    checklist_results = await adgm_validator.validate_document_against_checklist(
        parsed_doc['content']['text'],
        analysis.document_type
    )
    
    # Generate enhanced analysis summary
    kb_status = "enhanced" if adgm_validator.knowledge_initialized else "basic"
    checklist_info = f", Checklist: {checklist_results.get('compliance_percentage', 0)}%" if checklist_results.get('compliance_percentage') else ""
    
    analysis.analysis_summary = f"Analysis completed ({kb_status} mode). Compliance: {analysis.compliance_score}%, Completeness: {analysis.completeness_score}%{checklist_info}. Found {len(analysis.flags)} issues."
    
    # Store additional results
    setattr(analysis, 'contextual_recommendations', contextual_recommendations)
    setattr(analysis, 'checklist_results', checklist_results)
    
    # Generate marked-up document
    if analysis.flags:
        output_path = await file_handler.create_output_file(
            document_id, 
            os.path.basename(file_path)
        )
        await document_parser.add_comments_to_document(
            file_path, 
            analysis.flags, 
            output_path
        )
        setattr(analysis, 'output_file_path', output_path)

# API Endpoints

@app.get("/", response_model=APIResponse)
async def root():
    """API root endpoint"""
    kb_stats = adgm_validator.get_knowledge_base_stats()
    
    return APIResponse(
        success=True,
        message="ADGM Corporate Agent API is running",
        data={
            "version": "1.0.0",
            "status": "operational",
            "supported_formats": settings.ALLOWED_FILE_TYPES,
            "knowledge_base": kb_stats
        }
    )

@app.post("/api/documents/upload", response_model=APIResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload document for analysis"""
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_content = await file.read()
        validation = file_handler.validate_file(file.filename, len(file_content))
        
        if not all(validation.values()):
            issues = [k for k, v in validation.items() if not v]
            raise HTTPException(
                status_code=400, 
                detail=f"File validation failed: {', '.join(issues)}"
            )
        
        # Save file
        file_path = await file_handler.save_uploaded_file(file_content, file.filename)
        
        # Create document analysis record
        document_id = file_handler.generate_document_id()
        analysis = DocumentAnalysis(
            document_id=document_id,
            document_type=DocumentType.UNKNOWN,
            status=ProcessingStatus.UPLOADED
        )
        
        # Store file path (in production, store in database)
        setattr(analysis, 'file_path', file_path)
        setattr(analysis, 'original_filename', file.filename)
        
        document_store[document_id] = analysis
        
        # Add to processing queue
        await processing_queue.put(document_id)
        
        return APIResponse(
            success=True,
            message="Document uploaded successfully",
            data={
                "document_id": document_id,
                "filename": file.filename,
                "status": analysis.status,
                "estimated_processing_time": "2-5 minutes",
                "knowledge_base_mode": "enhanced" if adgm_validator.knowledge_initialized else "basic"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/documents/{document_id}/status", response_model=APIResponse)
async def get_document_status(document_id: str):
    """Get document processing status"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = document_store[document_id]
    
    return APIResponse(
        success=True,
        message="Document status retrieved",
        data={
            "document_id": document_id,
            "status": analysis.status,
            "document_type": analysis.document_type,
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at,
            "progress_summary": analysis.analysis_summary
        }
    )

@app.get("/api/documents/{document_id}/analyze", response_model=APIResponse)
async def get_analysis_results(document_id: str):
    """Get enhanced document analysis results"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = document_store[document_id]
    
    if analysis.status != ProcessingStatus.COMPLETED:
        return APIResponse(
            success=False,
            message=f"Analysis not completed yet. Current status: {analysis.status}",
            data={"status": analysis.status}
        )
    
    # Get additional results
    contextual_recommendations = getattr(analysis, 'contextual_recommendations', [])
    checklist_results = getattr(analysis, 'checklist_results', {})
    
    return APIResponse(
        success=True,
        message="Analysis results retrieved",
        data={
            "document_id": document_id,
            "document_type": analysis.document_type,
            "compliance_score": analysis.compliance_score,
            "completeness_score": analysis.completeness_score,
            "flags": [
                {
                    "severity": flag.severity,
                    "title": flag.title,
                    "description": flag.description,
                    "location": flag.location,
                    "suggested_fix": flag.suggested_fix
                }
                for flag in analysis.flags
            ],
            "compliance_checks": [
                {
                    "section": check.section,
                    "required": check.required,
                    "present": check.present,
                    "compliant": check.compliant,
                    "issues": check.issues,
                    "recommendations": check.recommendations
                }
                for check in analysis.compliance_checks
            ],
            "missing_sections": analysis.missing_sections,
            "contextual_recommendations": contextual_recommendations,
            "checklist_validation": checklist_results,
            "summary": analysis.analysis_summary,
            "knowledge_base_mode": "enhanced" if adgm_validator.knowledge_initialized else "basic"
        }
    )

@app.get("/api/documents/{document_id}/report", response_model=APIResponse)
async def get_detailed_report(document_id: str):
    """Get comprehensive JSON report with knowledge base insights"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = document_store[document_id]
    
    if analysis.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    # Generate comprehensive report
    original_filename = getattr(analysis, 'original_filename', 'Unknown Document')
    report_data = await report_generator.generate_json_report(analysis, original_filename)
    
    # Add knowledge base specific data
    report_data['knowledge_base_insights'] = {
        'mode': 'enhanced' if adgm_validator.knowledge_initialized else 'basic',
        'contextual_recommendations': getattr(analysis, 'contextual_recommendations', []),
        'checklist_validation': getattr(analysis, 'checklist_results', {}),
        'stats': adgm_validator.get_knowledge_base_stats()
    }
    
    return APIResponse(
        success=True,
        message="Comprehensive report generated",
        data=report_data
    )

@app.get("/api/documents/{document_id}/download")
async def download_marked_document(document_id: str):
    """Download marked-up document"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = document_store[document_id]
    
    if analysis.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    output_file_path = getattr(analysis, 'output_file_path', None)
    
    if not output_file_path or not file_handler.file_exists(output_file_path):
        raise HTTPException(status_code=404, detail="Marked-up document not available")
    
    original_filename = getattr(analysis, 'original_filename', 'document.docx')
    download_filename = f"reviewed_{original_filename}"
    
    return FileResponse(
        output_file_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=download_filename
    )

@app.post("/api/adgm/validate", response_model=APIResponse)
async def validate_content(request: ADGMValidationRequest):
    """Validate content directly against ADGM requirements with knowledge base"""
    
    try:
        # Run enhanced ADGM validation with knowledge base
        compliance_checks = await adgm_validator.validate_document_compliance(
            request.document_content,
            request.document_type,
            {}  # No structure for direct validation
        )
        
        # Calculate compliance score
        compliance_score = adgm_validator.calculate_compliance_score(compliance_checks)
        
        # Get contextual recommendations
        contextual_recommendations = await adgm_validator.get_contextual_recommendations(
            request.document_content,
            request.document_type,
            [check.section for check in compliance_checks if not check.compliant]
        )
        
        # Run checklist validation
        checklist_results = await adgm_validator.validate_document_against_checklist(
            request.document_content,
            request.document_type
        )
        
        return APIResponse(
            success=True,
            message="Enhanced content validation completed",
            data={
                "compliance_score": compliance_score,
                "compliance_checks": [
                    {
                        "section": check.section,
                        "required": check.required,
                        "present": check.present,
                        "compliant": check.compliant,
                        "issues": check.issues,
                        "recommendations": check.recommendations
                    }
                    for check in compliance_checks
                ],
                "contextual_recommendations": contextual_recommendations,
                "checklist_validation": checklist_results,
                "knowledge_base_mode": "enhanced" if adgm_validator.knowledge_initialized else "basic"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/api/documents", response_model=APIResponse)
async def list_documents():
    """List all processed documents"""
    
    documents = []
    for doc_id, analysis in document_store.items():
        documents.append({
            "document_id": doc_id,
            "filename": getattr(analysis, 'original_filename', 'Unknown'),
            "document_type": analysis.document_type,
            "status": analysis.status,
            "compliance_score": analysis.compliance_score,
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at
        })
    
    return APIResponse(
        success=True,
        message=f"Retrieved {len(documents)} documents",
        data={"documents": documents}
    )

@app.delete("/api/documents/{document_id}", response_model=APIResponse)
async def delete_document(document_id: str):
    """Delete document and associated files"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = document_store[document_id]
    
    # Delete associated files
    file_path = getattr(analysis, 'file_path', '')
    output_path = getattr(analysis, 'output_file_path', '')
    
    if file_path:
        file_handler.delete_file(file_path)
    if output_path:
        file_handler.delete_file(output_path)
    
    # Remove from store
    del document_store[document_id]
    
    return APIResponse(
        success=True,
        message="Document deleted successfully"
    )

@app.get("/api/system/status", response_model=APIResponse)
async def system_status():
    """Get system status and statistics with knowledge base info"""
    
    # Calculate statistics
    total_docs = len(document_store)
    completed_docs = sum(1 for a in document_store.values() if a.status == ProcessingStatus.COMPLETED)
    processing_docs = sum(1 for a in document_store.values() if a.status == ProcessingStatus.ANALYZING)
    
    # Get disk space
    disk_info = file_handler.get_available_space()
    
    # Get knowledge base stats
    kb_stats = adgm_validator.get_knowledge_base_stats()
    
    return APIResponse(
        success=True,
        message="System status retrieved",
        data={
            "system_status": "operational",
            "version": "1.0.0",
            "documents": {
                "total": total_docs,
                "completed": completed_docs,
                "processing": processing_docs
            },
            "queue": {
                "size": processing_queue.qsize(),
                "max_size": settings.MAX_CONCURRENT_ANALYSES
            },
            "storage": {
                "free_space_mb": disk_info.get("free_space_mb", 0),
                "total_space_mb": disk_info.get("total_space_mb", 0)
            },
            "gemini_api": {
                "configured": bool(settings.GEMINI_API_KEY),
                "model": settings.GEMINI_MODEL
            },
            "knowledge_base": kb_stats
        }
    )

# New endpoints for knowledge base management

@app.get("/api/knowledge-base/stats", response_model=APIResponse)
async def get_knowledge_base_stats():
    """Get detailed knowledge base statistics"""
    
    stats = adgm_validator.get_knowledge_base_stats()
    
    return APIResponse(
        success=True,
        message="Knowledge base statistics retrieved",
        data=stats
    )

@app.post("/api/knowledge-base/query", response_model=APIResponse)
async def query_knowledge_base(query: str, collection_names: Optional[List[str]] = None, n_results: int = 5):
    """Query the ADGM knowledge base directly"""
    
    if not adgm_validator.knowledge_initialized:
        raise HTTPException(status_code=503, detail="Knowledge base not available")
    
    try:
        results = adgm_validator.knowledge_extractor.query_knowledge_base(
            query=query,
            collection_names=collection_names,
            n_results=n_results
        )
        
        return APIResponse(
            success=True,
            message="Knowledge base query completed",
            data=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/api/knowledge-base/refresh", response_model=APIResponse)
async def refresh_knowledge_base():
    """Refresh the knowledge base (re-scrape and update)"""
    
    try:
        print("🔄 Refreshing ADGM Knowledge Base...")
        success = await adgm_validator.initialize_knowledge_base()
        
        if success:
            stats = adgm_validator.get_knowledge_base_stats()
            return APIResponse(
                success=True,
                message="Knowledge base refreshed successfully",
                data={
                    "refresh_status": "completed",
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            return APIResponse(
                success=False,
                message="Knowledge base refresh failed",
                data={"refresh_status": "failed"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@app.get("/api/adgm/checklist/{document_type}", response_model=APIResponse)
async def get_document_checklist(document_type: str):
    """Get ADGM checklist for specific document type"""
    
    if not adgm_validator.knowledge_initialized:
        raise HTTPException(status_code=503, detail="Knowledge base not available")
    
    try:
        # Convert string to DocumentType enum
        try:
            doc_type = DocumentType(document_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
        
        # Get checklist from knowledge base
        checklist_query = f"checklist {document_type} requirements mandatory"
        checklist_results = adgm_validator.knowledge_extractor.query_knowledge_base(
            checklist_query,
            collection_names=['adgm_compliance'],
            n_results=3
        )
        
        checklist_items = []
        if checklist_results.get('results'):
            for result in checklist_results['results']:
                items = adgm_validator._extract_checklist_items(result.get('content', ''))
                checklist_items.extend(items)
        
        return APIResponse(
            success=True,
            message=f"Checklist retrieved for {document_type}",
            data={
                "document_type": document_type,
                "checklist_items": list(set(checklist_items)),  # Remove duplicates
                "total_items": len(set(checklist_items))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checklist retrieval failed: {str(e)}")

@app.get("/api/adgm/templates/{document_type}", response_model=APIResponse)
async def get_document_templates(document_type: str):
    """Get available ADGM templates for specific document type"""
    
    if not adgm_validator.knowledge_initialized:
        raise HTTPException(status_code=503, detail="Knowledge base not available")
    
    try:
        # Query for templates
        template_query = f"{document_type} template official ADGM"
        template_results = adgm_validator.knowledge_extractor.query_knowledge_base(
            template_query,
            collection_names=['adgm_templates'],
            n_results=5
        )
        
        templates = []
        if template_results.get('results'):
            for result in template_results['results']:
                metadata = result.get('metadata', {})
                templates.append({
                    'description': metadata.get('description', 'Unknown Template'),
                    'source_url': metadata.get('source_url', ''),
                    'doc_type': metadata.get('doc_type', ''),
                    'category': metadata.get('category', ''),
                    'content_preview': result.get('content', '')[:200] + '...'
                })
        
        return APIResponse(
            success=True,
            message=f"Templates retrieved for {document_type}",
            data={
                "document_type": document_type,
                "templates": templates,
                "total_templates": len(templates)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template retrieval failed: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with knowledge base status"""
    
    kb_status = "enhanced" if adgm_validator.knowledge_initialized else "basic"
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "knowledge_base": kb_status,
        "services": {
            "document_parser": "operational",
            "gemini_analyzer": "operational",
            "adgm_validator": "operational",
            "knowledge_base": kb_status
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=APIResponse(
            success=False,
            message="Resource not found",
            error="The requested resource was not found"
        ).dict()
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            message="Internal server error",
            error="An unexpected error occurred"
        ).dict()
    )

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
import os
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.models import (
    DocumentAnalysis, ProcessingStatus, DocumentType, FlagSeverity,
    APIResponse, ProcessingRequest, AnalysisReport, ADGMValidationRequest
)
from app.services.document_parser import DocumentParser
from app.services.gemini_analyzer import GeminiAnalyzer
from app.services.adgm_validator import EnhancedADGMValidator  # Updated import
from app.utils.file_handler import FileHandler
from app.utils.report_generator import ReportGenerator
from config import settings

# Global storage for document analyses (in production, use proper database)
document_store: Dict[str, DocumentAnalysis] = {}
processing_queue: asyncio.Queue = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global processing_queue
    
    # Startup
    processing_queue = asyncio.Queue(maxsize=settings.MAX_CONCURRENT_ANALYSES)
    
    # Initialize enhanced ADGM validator with knowledge base
    print("🚀 Initializing ADGM Knowledge Base...")
    knowledge_success = await adgm_validator.initialize_knowledge_base()
    
    if knowledge_success:
        print("✅ ADGM Knowledge Base initialized successfully")
    else:
        print("⚠️ ADGM Knowledge Base initialization failed - using fallback mode")
    
    # Start background processor
    processor_task = asyncio.create_task(process_documents_background())
    
    print("ADGM Corporate Agent started successfully")
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    print(f"Output directory: {settings.OUTPUT_DIR}")
    
    yield
    
    # Shutdown
    processor_task.cancel()
    try:
        await processor_task
    except asyncio.CancelledError:
        pass
    
    print("ADGM Corporate Agent shut down")

# Initialize FastAPI app
app = FastAPI(
    title="ADGM Corporate Agent",
    description="AI-powered legal assistant for ADGM document compliance with comprehensive knowledge base",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize services
document_parser = DocumentParser()
gemini_analyzer = GeminiAnalyzer()
adgm_validator = EnhancedADGMValidator()  # Updated to use enhanced validator
file_handler = FileHandler()
report_generator = ReportGenerator()

# Background document processor
async def process_documents_background():
    """Background task to process documents in queue"""
    while True:
        try:
            # Get document from queue
            document_id = await processing_queue.get()
            
            if document_id in document_store:
                analysis = document_store[document_id]
                
                try:
                    # Update status
                    analysis.status = ProcessingStatus.ANALYZING
                    
                    # Process document
                    await process_document_analysis(document_id)
                    
                    # Mark as completed
                    analysis.status = ProcessingStatus.COMPLETED
                    analysis.completed_at = datetime.now()
                    
                except Exception as e:
                    # Mark as error
                    analysis.status = ProcessingStatus.ERROR
                    analysis.analysis_summary = f"Processing failed: {str(e)}"
                    print(f"Error processing document {document_id}: {str(e)}")
                
                # Mark task as done
                processing_queue.task_done()
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Background processor error: {str(e)}")