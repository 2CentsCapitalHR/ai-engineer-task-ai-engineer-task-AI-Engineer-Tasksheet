#!/usr/bin/env python3
"""
ADGM Corporate Agent - CLI Client for Testing
"""

import requests
import json
import time
import argparse
from pathlib import Path
from typing import Optional

class ADGMClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def upload_document(self, file_path: str) -> Optional[str]:
        """Upload document for analysis"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return None
            
            print(f"📤 Uploading: {file_path.name}")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = self.session.post(f"{self.base_url}/api/documents/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    document_id = data['data']['document_id']
                    print(f"✅ Upload successful! Document ID: {document_id}")
                    return document_id
                else:
                    print(f"❌ Upload failed: {data['message']}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
        
        return None
    
    def get_status(self, document_id: str) -> dict:
        """Get document processing status"""
        try:
            response = self.session.get(f"{self.base_url}/api/documents/{document_id}/status")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Status check failed: HTTP {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Status check error: {str(e)}")
            return {}
    
    def wait_for_completion(self, document_id: str, timeout: int = 300) -> bool:
        """Wait for document processing to complete"""
        print(f"⏳ Waiting for analysis to complete...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_response = self.get_status(document_id)
            
            if status_response.get('success'):
                status = status_response['data']['status']
                print(f"📊 Status: {status}")
                
                if status == "completed":
                    print("✅ Analysis completed!")
                    return True
                elif status == "error":
                    print("❌ Analysis failed!")
                    return False
                
            time.sleep(5)  # Check every 5 seconds
        
        print("⏰ Timeout waiting for completion")
        return False
    
    def get_analysis(self, document_id: str) -> dict:
        """Get analysis results"""
        try:
            response = self.session.get(f"{self.base_url}/api/documents/{document_id}/analyze")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Analysis retrieval failed: HTTP {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Analysis retrieval error: {str(e)}")
            return {}
    
    def get_report(self, document_id: str) -> dict:
        """Get detailed report"""
        try:
            response = self.session.get(f"{self.base_url}/api/documents/{document_id}/report")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Report retrieval failed: HTTP {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Report retrieval error: {str(e)}")
            return {}
    
    def download_document(self, document_id: str, output_path: str = None) -> bool:
        """Download marked-up document"""
        try:
            response = self.session.get(f"{self.base_url}/api/documents/{document_id}/download")
            
            if response.status_code == 200:
                if not output_path:
                    output_path = f"reviewed_document_{document_id}.docx"
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"💾 Downloaded to: {output_path}")
                return True
            else:
                print(f"❌ Download failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Download error: {str(e)}")
            return False
    
    def system_status(self) -> dict:
        """Get system status"""
        try:
            response = self.session.get(f"{self.base_url}/api/system/status")
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"❌ System status error: {str(e)}")
            return {}
    
    def print_analysis_summary(self, analysis_data: dict):
        """Print formatted analysis summary"""
        if not analysis_data.get('success'):
            print("❌ No analysis data available")
            return
        
        data = analysis_data['data']
        
        print("\n" + "="*60)
        print("📋 DOCUMENT ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📄 Document ID: {data['document_id']}")
        print(f"📂 Document Type: {data['document_type']}")
        print(f"📊 Compliance Score: {data['compliance_score']}%")
        print(f"📈 Completeness Score: {data['completeness_score']}%")
        
        print(f"\n🚨 Issues Found:")
        flags = data.get('flags', [])
        critical = [f for f in flags if f['severity'] == 'critical']
        warnings = [f for f in flags if f['severity'] == 'warning']
        info = [f for f in flags if f['severity'] == 'info']
        
        print(f"   • Critical: {len(critical)}")
        print(f"   • Warnings: {len(warnings)}")
        print(f"   • Info: {len(info)}")
        
        if critical:
            print(f"\n🔴 Critical Issues:")
            for i, flag in enumerate(critical, 1):
                print(f"   {i}. {flag['title']}")
                print(f"      └─ {flag['description']}")
        
        if data.get('missing_sections'):
            print(f"\n📋 Missing Sections:")
            for section in data['missing_sections']:
                print(f"   • {section}")
        
        print(f"\n📝 Summary: {data['summary']}")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="ADGM Corporate Agent CLI Client")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--file", help="Document file to upload and analyze")
    parser.add_argument("--status", help="Check status of document ID")
    parser.add_argument("--analyze", help="Get analysis results for document ID")
    parser.add_argument("--report", help="Get detailed report for document ID")
    parser.add_argument("--download", help="Download reviewed document by ID")
    parser.add_argument("--system", action="store_true", help="Show system status")
    parser.add_argument("--output", help="Output file path for downloads")
    parser.add_argument("--kb-query", help="Query the knowledge base")
    parser.add_argument("--kb-stats", action="store_true", help="Show knowledge base statistics")
    parser.add_argument("--kb-refresh", action="store_true", help="Refresh knowledge base")
    
    args = parser.parse_args()
    
    client = ADGMClient(args.url)
    
    print("🏢 ADGM Corporate Agent CLI Client")
    print(f"🔗 Connected to: {args.url}")
    print("-" * 40)
    
    if args.system:
        print("📊 System Status:")
        status = client.system_status()
        if status.get('success'):
            data = status['data']
            print(f"   Status: {data['system_status']}")
            print(f"   Version: {data['version']}")
            print(f"   Documents: {data['documents']['total']} total, {data['documents']['completed']} completed")
            print(f"   Queue: {data['queue']['size']}/{data['queue']['max_size']}")
            print(f"   Storage: {data['storage']['free_space_mb']} MB free")
        return
    
    if args.file:
        # Full workflow: upload, wait, analyze, download
        document_id = client.upload_document(args.file)
        if document_id:
            if client.wait_for_completion(document_id):
                # Get and display analysis
                analysis = client.get_analysis(document_id)
                client.print_analysis_summary(analysis)
                
                # Download reviewed document
                output_file = args.output or f"reviewed_{Path(args.file).name}"
                client.download_document(document_id, output_file)
                
                # Save report
                report = client.get_report(document_id)
                if report.get('success'):
                    report_file = f"report_{document_id}.json"
                    with open(report_file, 'w') as f:
                        json.dump(report['data'], f, indent=2)
                    print(f"📄 Report saved to: {report_file}")
        return
    
    if args.status:
        status = client.get_status(args.status)
        if status.get('success'):
            data = status['data']
            print(f"📊 Document {args.status}:")
            print(f"   Status: {data['status']}")
            print(f"   Type: {data['document_type']}")
            print(f"   Created: {data['created_at']}")
            if data['completed_at']:
                print(f"   Completed: {data['completed_at']}")
        return
    
    if args.analyze:
        analysis = client.get_analysis(args.analyze)
        client.print_analysis_summary(analysis)
        return
    
    if args.report:
        report = client.get_report(args.report)
        if report.get('success'):
            print(json.dumps(report['data'], indent=2))
        return
    
    if args.download:
        client.download_document(args.download, args.output)
        return
    
    # Show help if no arguments
    parser.print_help()

if __name__ == "__main__":
    main()