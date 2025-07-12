"""
Test script for AI document processing functionality.

This script provides basic tests to verify the AI document processing
system is working correctly with mock data and real API calls.
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mock_invoice_image() -> str:
    """Create a mock invoice image for testing."""
    
    # Create a simple invoice image
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw invoice content
    y_pos = 50
    
    # Header
    draw.text((50, y_pos), "COMMERCIAL INVOICE", fill='black', font=font_large)
    y_pos += 60
    
    # Invoice details
    draw.text((50, y_pos), "Invoice Number: INV-2024-001", fill='black', font=font_medium)
    y_pos += 30
    draw.text((50, y_pos), f"Invoice Date: {datetime.now().strftime('%Y-%m-%d')}", fill='black', font=font_medium)
    y_pos += 50
    
    # Seller information
    draw.text((50, y_pos), "SELLER:", fill='black', font=font_medium)
    y_pos += 25
    draw.text((50, y_pos), "ABC Trading Company Pty Ltd", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "123 Business Street", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "Sydney NSW 2000, Australia", fill='black', font=font_small)
    y_pos += 50
    
    # Buyer information
    draw.text((50, y_pos), "BUYER:", fill='black', font=font_medium)
    y_pos += 25
    draw.text((50, y_pos), "XYZ Import Company", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "456 Import Avenue", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "Melbourne VIC 3000, Australia", fill='black', font=font_small)
    y_pos += 50
    
    # Items table header
    draw.text((50, y_pos), "DESCRIPTION", fill='black', font=font_medium)
    draw.text((300, y_pos), "QTY", fill='black', font=font_medium)
    draw.text((400, y_pos), "UNIT PRICE", fill='black', font=font_medium)
    draw.text((550, y_pos), "TOTAL", fill='black', font=font_medium)
    y_pos += 30
    
    # Draw line
    draw.line([(50, y_pos), (700, y_pos)], fill='black', width=1)
    y_pos += 20
    
    # Items
    items = [
        ("Electronic Components - Resistors", "1000", "0.05", "50.00"),
        ("Electronic Components - Capacitors", "500", "0.10", "50.00"),
        ("Circuit Boards", "100", "2.50", "250.00"),
    ]
    
    for desc, qty, price, total in items:
        draw.text((50, y_pos), desc, fill='black', font=font_small)
        draw.text((300, y_pos), qty, fill='black', font=font_small)
        draw.text((400, y_pos), f"AUD {price}", fill='black', font=font_small)
        draw.text((550, y_pos), f"AUD {total}", fill='black', font=font_small)
        y_pos += 25
    
    y_pos += 30
    
    # Totals
    draw.text((400, y_pos), "SUBTOTAL:", fill='black', font=font_medium)
    draw.text((550, y_pos), "AUD 350.00", fill='black', font=font_medium)
    y_pos += 25
    
    draw.text((400, y_pos), "GST (10%):", fill='black', font=font_medium)
    draw.text((550, y_pos), "AUD 35.00", fill='black', font=font_medium)
    y_pos += 25
    
    draw.text((400, y_pos), "TOTAL:", fill='black', font=font_large)
    draw.text((550, y_pos), "AUD 385.00", fill='black', font=font_large)
    y_pos += 50
    
    # Additional info
    draw.text((50, y_pos), "Country of Origin: China", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "HS Code: 8541.10.00", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "Payment Terms: Net 30 days", fill='black', font=font_small)
    y_pos += 20
    draw.text((50, y_pos), "Incoterms: CIF Melbourne", fill='black', font=font_small)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    image.save(temp_file.name, 'PNG')
    temp_file.close()
    
    return temp_file.name


async def test_document_upload_and_processing():
    """Test document upload and AI processing workflow."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Create mock invoice
            logger.info("Creating mock invoice image...")
            invoice_path = create_mock_invoice_image()
            
            # Upload document
            logger.info("Uploading document...")
            with open(invoice_path, 'rb') as f:
                upload_response = await client.post(
                    f"{base_url}/api/documents/upload",
                    files={"file": ("test_invoice.png", f, "image/png")},
                    data={
                        "title": "Test Commercial Invoice",
                        "description": "Mock invoice for AI processing test",
                        "document_type": "invoice",
                        "category": "import"
                    }
                )
            
            if upload_response.status_code != 200:
                logger.error(f"Document upload failed: {upload_response.status_code} - {upload_response.text}")
                return False
            
            document_data = upload_response.json()
            document_id = document_data["id"]
            logger.info(f"Document uploaded successfully with ID: {document_id}")
            
            # Process document with AI
            logger.info("Starting AI processing...")
            process_response = await client.post(
                f"{base_url}/api/ai/documents/process",
                json={"document_id": document_id}
            )
            
            if process_response.status_code != 200:
                logger.error(f"AI processing failed: {process_response.status_code} - {process_response.text}")
                return False
            
            processing_data = process_response.json()
            logger.info(f"AI processing started: {processing_data['processing_status']}")
            
            # Wait for processing to complete
            max_attempts = 30  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                await asyncio.sleep(10)  # Wait 10 seconds
                attempt += 1
                
                status_response = await client.get(
                    f"{base_url}/api/ai/documents/status/{document_id}",
                    params={"include_ocr_text": True}
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Status check failed: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                status = status_data["processing_status"]
                
                logger.info(f"Processing status (attempt {attempt}): {status}")
                
                if status == "completed":
                    logger.info("Processing completed successfully!")
                    
                    # Display results
                    print("\n" + "="*50)
                    print("AI PROCESSING RESULTS")
                    print("="*50)
                    
                    print(f"Document Type: {status_data.get('detected_document_type', 'Unknown')}")
                    print(f"Type Confidence: {status_data.get('document_type_confidence', 0):.2f}")
                    print(f"OCR Confidence: {status_data.get('ocr_confidence', 0):.2f}")
                    print(f"Extraction Confidence: {status_data.get('extraction_confidence', 'Unknown')}")
                    print(f"Requires Manual Review: {status_data.get('requires_manual_review', False)}")
                    
                    print(f"\nExtracted Fields ({len(status_data.get('extracted_fields', []))}):")
                    for field in status_data.get('extracted_fields', []):
                        confidence = field.get('confidence_score', 0)
                        print(f"  - {field['field_name']}: {field['field_value']} (confidence: {confidence:.2f})")
                    
                    ai_analysis = status_data.get('ai_analysis', {})
                    if ai_analysis:
                        print(f"\nSuggested HS Codes ({len(ai_analysis.get('suggested_hs_codes', []))}):")
                        for hs_code in ai_analysis.get('suggested_hs_codes', []):
                            print(f"  - {hs_code['code']}: {hs_code['description']} (confidence: {hs_code['confidence']:.2f})")
                        
                        print(f"\nCompliance Flags ({len(ai_analysis.get('compliance_flags', []))}):")
                        for flag in ai_analysis.get('compliance_flags', []):
                            print(f"  - {flag['flag']} ({flag['severity']}): {flag['description']}")
                        
                        risk_assessment = ai_analysis.get('risk_assessment', {})
                        if risk_assessment:
                            print(f"\nRisk Assessment:")
                            print(f"  - Overall Risk: {risk_assessment.get('overall_risk', 'Unknown')}")
                            print(f"  - Risk Score: {risk_assessment.get('risk_score', 0):.2f}")
                            print(f"  - Risk Factors: {', '.join(risk_assessment.get('risk_factors', []))}")
                    
                    print("="*50)
                    return True
                
                elif status == "failed":
                    logger.error(f"Processing failed: {status_data.get('error_message', 'Unknown error')}")
                    return False
                
                elif status in ["pending", "processing"]:
                    continue
                
                else:
                    logger.warning(f"Unknown status: {status}")
            
            logger.error("Processing timed out")
            return False
            
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            return False
        
        finally:
            # Cleanup
            try:
                os.unlink(invoice_path)
            except:
                pass


async def test_batch_processing():
    """Test batch processing functionality."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Create multiple mock documents
            document_ids = []
            
            for i in range(3):
                logger.info(f"Creating mock document {i+1}...")
                invoice_path = create_mock_invoice_image()
                
                with open(invoice_path, 'rb') as f:
                    upload_response = await client.post(
                        f"{base_url}/api/documents/upload",
                        files={"file": (f"test_invoice_{i+1}.png", f, "image/png")},
                        data={
                            "title": f"Test Invoice {i+1}",
                            "description": f"Mock invoice {i+1} for batch processing test",
                            "document_type": "invoice",
                            "category": "import"
                        }
                    )
                
                if upload_response.status_code == 200:
                    document_data = upload_response.json()
                    document_ids.append(document_data["id"])
                    logger.info(f"Document {i+1} uploaded with ID: {document_data['id']}")
                
                os.unlink(invoice_path)
            
            if not document_ids:
                logger.error("No documents uploaded for batch processing")
                return False
            
            # Start batch processing
            logger.info(f"Starting batch processing for {len(document_ids)} documents...")
            batch_response = await client.post(
                f"{base_url}/api/ai/documents/batch-process",
                json={
                    "document_ids": document_ids,
                    "force_reprocess": False
                }
            )
            
            if batch_response.status_code != 200:
                logger.error(f"Batch processing failed: {batch_response.status_code} - {batch_response.text}")
                return False
            
            batch_data = batch_response.json()
            batch_id = batch_data["batch_id"]
            logger.info(f"Batch processing started with ID: {batch_id}")
            
            # Monitor batch progress
            max_attempts = 60  # 10 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                await asyncio.sleep(10)
                attempt += 1
                
                status_response = await client.get(
                    f"{base_url}/api/ai/documents/batch-status/{batch_id}"
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Batch status check failed: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                status = status_data["processing_status"]
                
                logger.info(f"Batch status (attempt {attempt}): {status}")
                
                if status == "completed":
                    logger.info("Batch processing completed!")
                    
                    print("\n" + "="*50)
                    print("BATCH PROCESSING RESULTS")
                    print("="*50)
                    
                    print(f"Total Documents: {status_data['total_documents']}")
                    print(f"Processed Documents: {len(status_data.get('documents', []))}")
                    
                    for doc in status_data.get('documents', []):
                        print(f"\nDocument {doc['document_id']}:")
                        print(f"  Status: {doc['processing_status']}")
                        print(f"  Type: {doc.get('detected_document_type', 'Unknown')}")
                        print(f"  Fields: {len(doc.get('extracted_fields', []))}")
                        print(f"  Manual Review: {doc.get('requires_manual_review', False)}")
                    
                    print("="*50)
                    return True
                
                elif status == "failed":
                    logger.error("Batch processing failed")
                    return False
                
                elif status in ["pending", "processing"]:
                    continue
            
            logger.error("Batch processing timed out")
            return False
            
        except Exception as e:
            logger.error(f"Batch test failed with exception: {e}")
            return False


async def test_processing_stats():
    """Test processing statistics endpoint."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info("Getting processing statistics...")
            
            stats_response = await client.get(
                f"{base_url}/api/ai/documents/stats",
                params={"days": 30}
            )
            
            if stats_response.status_code != 200:
                logger.error(f"Stats request failed: {stats_response.status_code} - {stats_response.text}")
                return False
            
            stats_data = stats_response.json()
            
            print("\n" + "="*50)
            print("PROCESSING STATISTICS")
            print("="*50)
            
            print(f"Total Processed: {stats_data['total_processed']}")
            print(f"Successful: {stats_data['successful_processing']}")
            print(f"Failed: {stats_data['failed_processing']}")
            print(f"Pending: {stats_data['pending_processing']}")
            print(f"Success Rate: {stats_data.get('success_rate', 0):.2%}")
            print(f"Average Processing Time: {stats_data.get('average_processing_time', 0):.1f} seconds")
            
            print("\nDocument Type Breakdown:")
            for doc_type, count in stats_data.get('document_type_breakdown', {}).items():
                print(f"  - {doc_type}: {count}")
            
            print("="*50)
            return True
            
        except Exception as e:
            logger.error(f"Stats test failed with exception: {e}")
            return False


async def main():
    """Run all tests."""
    
    print("AI Document Processing Test Suite")
    print("="*50)
    
    # Check if API is available
    try:
        async with httpx.AsyncClient() as client:
            health_response = await client.get("http://localhost:8000/health")
            if health_response.status_code != 200:
                logger.error("API is not available. Please start the FastAPI server.")
                return
    except Exception as e:
        logger.error(f"Cannot connect to API: {e}")
        return
    
    tests = [
        ("Single Document Processing", test_document_upload_and_processing),
        ("Batch Processing", test_batch_processing),
        ("Processing Statistics", test_processing_stats),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
            results[test_name] = result
            
            if result:
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI document processing is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs and configuration.")


if __name__ == "__main__":
    asyncio.run(main())