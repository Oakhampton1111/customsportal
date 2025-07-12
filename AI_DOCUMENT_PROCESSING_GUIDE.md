# AI Document Processing System - Implementation Guide

## Overview

This document provides a comprehensive guide to the AI-powered document processing system implemented for the Customs Broker Portal. The system uses Claude 3.5 Sonnet for intelligent document analysis, OCR for text extraction, and automated field extraction for various customs document types.

## Features Implemented

### 🤖 AI-Powered Analysis
- **Claude 3.5 Sonnet Integration**: Advanced AI model for document understanding and analysis
- **Document Type Detection**: Automatic classification of document types (invoices, packing lists, bills of lading, etc.)
- **Intelligent Field Extraction**: Structured data extraction from unstructured documents
- **Confidence Scoring**: Quality assessment for all extracted data
- **Compliance Analysis**: Automated compliance checking and risk assessment
- **HS Code Suggestions**: AI-powered tariff classification recommendations

### 📄 Document Processing Pipeline
- **OCR Text Extraction**: Support for PDF and image files with preprocessing
- **Multi-format Support**: PDF, JPEG, PNG, TIFF document processing
- **Batch Processing**: Handle multiple documents simultaneously
- **Background Processing**: Celery-based async processing for large documents
- **Progress Tracking**: Real-time status updates for processing operations

### 🔍 Quality Assurance
- **Manual Review Workflows**: Flag documents requiring human verification
- **Field Correction System**: Allow manual corrections with audit trails
- **Processing Templates**: Configurable extraction templates for different document types
- **Validation Rules**: Automated data validation and format checking

### 📊 Analytics & Reporting
- **Processing Statistics**: Success rates, processing times, document type breakdowns
- **Performance Metrics**: Confidence scores, manual review rates, error analysis
- **Audit Trails**: Complete history of processing activities and corrections

## System Architecture

### Core Components

1. **AI Document Processor** (`backend/ai/document_processor.py`)
   - Main processing engine with Claude integration
   - OCR preprocessing and text extraction
   - Document type detection and field extraction

2. **Database Models** (`backend/models/ai_document_processing.py`)
   - `AIDocumentProcessing`: Main processing records
   - `ExtractedField`: Individual field extraction results
   - `ProcessingTemplate`: Configurable extraction templates

3. **API Routes** (`backend/routes/ai_document_processing.py`)
   - RESTful endpoints for document processing
   - Batch processing and status tracking
   - Field correction and review workflows

4. **Background Tasks** (`backend/tasks/ai_document_processing.py`)
   - Celery tasks for async processing
   - Batch operations and maintenance tasks
   - Periodic cleanup and reporting

5. **Pydantic Schemas** (`backend/schemas/ai_document_processing.py`)
   - Request/response validation
   - Type safety and documentation

## API Endpoints

### Document Processing
```
POST /api/ai/documents/process
- Process single document with AI analysis
- Returns processing status and extracted data

POST /api/ai/documents/batch-process  
- Process multiple documents in batch
- Returns batch ID for status tracking

GET /api/ai/documents/status/{document_id}
- Get processing status and results
- Includes extracted fields and AI analysis

POST /api/ai/documents/reprocess/{document_id}
- Force reprocessing of existing document
- Useful for improved models or corrections
```

### Batch Operations
```
GET /api/ai/documents/batch-status/{batch_id}
- Get status of batch processing operation
- Includes individual document results

GET /api/ai/documents/pending
- Get documents requiring manual review
- Supports pagination and filtering
```

### Quality Assurance
```
POST /api/ai/documents/fields/correct
- Correct extracted field values
- Creates audit trail for corrections

POST /api/ai/documents/{document_id}/mark-reviewed
- Mark document as manually reviewed
- Updates review status and timestamp
```

### Analytics
```
GET /api/ai/documents/stats
- Get processing statistics and metrics
- Configurable time periods and breakdowns
```

## Document Types Supported

### Commercial Invoices
- Invoice number, date, parties
- Line items with descriptions, quantities, prices
- Total amounts and currency
- Payment terms and Incoterms
- Country of origin information

### Packing Lists
- Packing list number and date
- Shipper and consignee details
- Package counts, weights, dimensions
- Item descriptions and quantities

### Bills of Lading
- B/L number, vessel, voyage details
- Ports of loading and discharge
- Container and seal numbers
- Freight terms and notify parties

### Certificates of Origin
- Certificate number and issuing authority
- Exporter and consignee information
- Country of origin declarations
- Product descriptions and HS codes

### Additional Types
- Airway bills
- Customs declarations
- Insurance certificates
- Purchase orders
- Proforma invoices

## Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=your_claude_api_key_here

# Optional (with defaults)
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

### Processing Templates
Templates define extraction rules for each document type:
- Required and optional fields
- Field types and validation rules
- Extraction prompts for AI guidance
- Success rate tracking

### Celery Configuration
Background processing with Redis broker:
- Separate queues for different task types
- Configurable timeouts and retry policies
- Monitoring and error handling

## Installation & Setup

### 1. Install Dependencies
```bash
# Core dependencies already in requirements.txt
pip install -r backend/requirements.txt

# Additional system dependencies for OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr poppler-utils

# macOS:
brew install tesseract poppler

# Windows:
# Download and install Tesseract from GitHub releases
# Download and install Poppler from conda-forge
```

### 2. Database Migration
```bash
cd backend
python migrations/add_ai_document_processing.py
```

### 3. Start Services
```bash
# Start Redis (required for Celery)
redis-server

# Start Celery worker
cd backend
celery -A celery_app worker --loglevel=info

# Start FastAPI application
python main.py
```

### 4. Test the System
```bash
# Upload a test document through the existing document API
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_invoice.pdf"

# Process the document with AI
curl -X POST "http://localhost:8000/api/ai/documents/process" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1}'

# Check processing status
curl "http://localhost:8000/api/ai/documents/status/1"
```

## Usage Examples

### Single Document Processing
```python
import httpx

# Process a document
response = httpx.post(
    "http://localhost:8000/api/ai/documents/process",
    json={"document_id": 123}
)
processing_result = response.json()

# Check status
status_response = httpx.get(
    f"http://localhost:8000/api/ai/documents/status/{processing_result['document_id']}"
)
status = status_response.json()

print(f"Status: {status['processing_status']}")
print(f"Document Type: {status['detected_document_type']}")
print(f"Extracted Fields: {len(status['extracted_fields'])}")
```

### Batch Processing
```python
# Start batch processing
batch_response = httpx.post(
    "http://localhost:8000/api/ai/documents/batch-process",
    json={
        "document_ids": [123, 124, 125],
        "force_reprocess": False
    }
)
batch_info = batch_response.json()

# Monitor progress
import time
while True:
    status_response = httpx.get(
        f"http://localhost:8000/api/ai/documents/batch-status/{batch_info['batch_id']}"
    )
    status = status_response.json()
    
    if status['processing_status'] == 'completed':
        print(f"Batch completed: {len(status['documents'])} documents processed")
        break
    
    time.sleep(5)
```

### Field Correction
```python
# Correct an extracted field
correction_response = httpx.post(
    "http://localhost:8000/api/ai/documents/fields/correct",
    json={
        "field_id": 456,
        "corrected_value": "INV-2024-001-CORRECTED",
        "correction_notes": "Fixed typo in invoice number"
    }
)
```

## Performance Considerations

### Processing Times
- Simple documents (1-2 pages): 30-60 seconds
- Complex documents (5+ pages): 2-5 minutes
- Batch processing: Parallel execution with configurable concurrency

### Scaling
- Horizontal scaling with multiple Celery workers
- Redis clustering for high-throughput scenarios
- Database connection pooling and optimization

### Cost Optimization
- Claude API usage monitoring and rate limiting
- Caching of processing results
- Intelligent reprocessing decisions

## Monitoring & Maintenance

### Health Checks
- Processing queue monitoring
- API response time tracking
- Error rate analysis
- Resource utilization metrics

### Maintenance Tasks
- Periodic cleanup of old processing records
- Failed document reprocessing
- Performance report generation
- Template optimization based on success rates

### Logging
- Structured logging with correlation IDs
- Processing pipeline tracing
- Error tracking and alerting
- Audit trail maintenance

## Security Considerations

### Data Protection
- Document content encryption at rest
- Secure API key management
- Access control and authentication
- Audit logging for compliance

### Privacy
- Configurable data retention policies
- Secure deletion of processed content
- GDPR compliance considerations
- Customer data isolation

## Troubleshooting

### Common Issues

1. **OCR Quality Problems**
   - Check image resolution and quality
   - Verify Tesseract installation
   - Review preprocessing settings

2. **Claude API Errors**
   - Verify API key configuration
   - Check rate limiting and quotas
   - Monitor API response times

3. **Processing Timeouts**
   - Adjust Celery task timeouts
   - Optimize document preprocessing
   - Consider document size limits

4. **Database Performance**
   - Monitor query performance
   - Optimize indexes for common queries
   - Consider connection pooling

### Debug Mode
Enable detailed logging for troubleshooting:
```python
import logging
logging.getLogger("ai.document_processor").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- Multi-language document support
- Custom field extraction training
- Integration with external validation services
- Advanced analytics and reporting dashboards
- Mobile document capture integration

### Model Improvements
- Fine-tuning for specific document types
- Custom classification models
- Confidence score calibration
- Active learning from corrections

## Support & Documentation

### API Documentation
- Interactive API docs at `/docs` (development)
- OpenAPI specification available
- Postman collection for testing

### Code Documentation
- Comprehensive docstrings
- Type hints throughout
- Example usage in docstrings

### Community
- GitHub issues for bug reports
- Feature requests and discussions
- Contributing guidelines

---

This AI document processing system provides a robust foundation for intelligent document analysis in the customs brokerage industry, with the flexibility to adapt to specific business requirements and scale with growing document volumes.