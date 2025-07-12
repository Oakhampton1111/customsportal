"""
Celery tasks for AI document processing.

This module contains background tasks for AI-powered document processing,
including individual document processing and batch operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from celery_app import celery_app
from ai.document_processor import get_document_processor, DocumentProcessingError
from models.ai_document_processing import AIDocumentProcessing, ProcessingStatus
from database import get_database_url


logger = logging.getLogger(__name__)

# Create async database engine for tasks
engine = create_async_engine(get_database_url(), echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class DatabaseTask(Task):
    """Base task class that provides database session management."""
    
    def __init__(self):
        self._db_session = None
    
    async def get_db_session(self) -> AsyncSession:
        """Get async database session."""
        if self._db_session is None:
            self._db_session = AsyncSessionLocal()
        return self._db_session
    
    async def close_db_session(self):
        """Close database session."""
        if self._db_session:
            await self._db_session.close()
            self._db_session = None


def run_async_task(coro):
    """Helper function to run async coroutines in Celery tasks."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="ai_document_processing.process_document",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    soft_time_limit=900,  # 15 minutes
    time_limit=1200,      # 20 minutes
)
def process_document_task(self, document_id: int, force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Celery task for processing a single document with AI analysis.
    
    Args:
        document_id: ID of the document to process
        force_reprocess: Whether to reprocess if already processed
        
    Returns:
        Dictionary with processing results
    """
    async def _process_document():
        db = await self.get_db_session()
        try:
            processor = get_document_processor()
            processing = await processor.process_document(db, document_id, force_reprocess)
            
            return {
                "success": True,
                "processing_id": processing.id,
                "document_id": document_id,
                "status": processing.processing_status.value,
                "detected_type": processing.detected_document_type.value if processing.detected_document_type else None,
                "extraction_confidence": processing.extraction_confidence.value if processing.extraction_confidence else None,
                "requires_manual_review": processing.requires_manual_review,
                "processing_duration": float(processing.processing_duration_seconds) if processing.processing_duration_seconds else None,
                "completed_at": processing.processing_completed_at.isoformat() if processing.processing_completed_at else None
            }
            
        except DocumentProcessingError as e:
            logger.error(f"Document processing failed for document {document_id}: {e}")
            return {
                "success": False,
                "document_id": document_id,
                "error": str(e),
                "error_type": "DocumentProcessingError"
            }
        except Exception as e:
            logger.error(f"Unexpected error processing document {document_id}: {e}")
            return {
                "success": False,
                "document_id": document_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        finally:
            await self.close_db_session()
    
    try:
        return run_async_task(_process_document())
    except Exception as e:
        logger.error(f"Task execution failed for document {document_id}: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="ai_document_processing.batch_process_documents",
    soft_time_limit=3600,  # 1 hour
    time_limit=7200,       # 2 hours
)
def batch_process_documents_task(
    self, 
    batch_id: str, 
    document_ids: List[int], 
    force_reprocess: bool = False
) -> Dict[str, Any]:
    """
    Celery task for batch processing multiple documents.
    
    Args:
        batch_id: Unique identifier for the batch
        document_ids: List of document IDs to process
        force_reprocess: Whether to reprocess already processed documents
        
    Returns:
        Dictionary with batch processing results
    """
    async def _batch_process():
        db = await self.get_db_session()
        try:
            processor = get_document_processor()
            
            results = {
                "batch_id": batch_id,
                "total_documents": len(document_ids),
                "successful": 0,
                "failed": 0,
                "results": [],
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": None
            }
            
            for i, doc_id in enumerate(document_ids):
                try:
                    # Update progress
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "current": i + 1,
                            "total": len(document_ids),
                            "status": f"Processing document {doc_id}"
                        }
                    )
                    
                    processing = await processor.process_document(db, doc_id, force_reprocess)
                    
                    results["results"].append({
                        "document_id": doc_id,
                        "success": True,
                        "processing_id": processing.id,
                        "status": processing.processing_status.value,
                        "detected_type": processing.detected_document_type.value if processing.detected_document_type else None,
                        "requires_manual_review": processing.requires_manual_review
                    })
                    results["successful"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process document {doc_id} in batch {batch_id}: {e}")
                    results["results"].append({
                        "document_id": doc_id,
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                    results["failed"] += 1
            
            results["completed_at"] = datetime.utcnow().isoformat()
            
            logger.info(
                f"Batch processing {batch_id} completed: "
                f"{results['successful']} successful, {results['failed']} failed"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing {batch_id} failed: {e}")
            return {
                "batch_id": batch_id,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        finally:
            await self.close_db_session()
    
    return run_async_task(_batch_process())


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="ai_document_processing.reprocess_failed_documents",
    soft_time_limit=1800,  # 30 minutes
    time_limit=3600,       # 1 hour
)
def reprocess_failed_documents_task(self, days_back: int = 7) -> Dict[str, Any]:
    """
    Celery task for reprocessing failed documents.
    
    Args:
        days_back: Number of days to look back for failed documents
        
    Returns:
        Dictionary with reprocessing results
    """
    async def _reprocess_failed():
        from sqlalchemy import select, and_
        from datetime import timedelta
        
        db = await self.get_db_session()
        try:
            # Find failed documents from the last N days
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            result = await db.execute(
                select(AIDocumentProcessing.document_id)
                .where(
                    and_(
                        AIDocumentProcessing.processing_status == ProcessingStatus.FAILED,
                        AIDocumentProcessing.created_at >= cutoff_date
                    )
                )
                .distinct()
            )
            
            failed_document_ids = [row[0] for row in result.fetchall()]
            
            if not failed_document_ids:
                return {
                    "success": True,
                    "message": f"No failed documents found in the last {days_back} days",
                    "reprocessed": 0,
                    "failed": 0
                }
            
            processor = get_document_processor()
            reprocessed = 0
            failed = 0
            
            for doc_id in failed_document_ids:
                try:
                    await processor.process_document(db, doc_id, force_reprocess=True)
                    reprocessed += 1
                except Exception as e:
                    logger.error(f"Failed to reprocess document {doc_id}: {e}")
                    failed += 1
            
            return {
                "success": True,
                "total_found": len(failed_document_ids),
                "reprocessed": reprocessed,
                "failed": failed,
                "days_back": days_back
            }
            
        except Exception as e:
            logger.error(f"Failed to reprocess failed documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        finally:
            await self.close_db_session()
    
    return run_async_task(_reprocess_failed())


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="ai_document_processing.cleanup_old_processing_records",
    soft_time_limit=600,   # 10 minutes
    time_limit=1200,       # 20 minutes
)
def cleanup_old_processing_records_task(self, days_to_keep: int = 90) -> Dict[str, Any]:
    """
    Celery task for cleaning up old processing records.
    
    Args:
        days_to_keep: Number of days of records to keep
        
    Returns:
        Dictionary with cleanup results
    """
    async def _cleanup_records():
        from sqlalchemy import delete, and_
        from datetime import timedelta
        
        db = await self.get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old completed processing records
            result = await db.execute(
                delete(AIDocumentProcessing)
                .where(
                    and_(
                        AIDocumentProcessing.processing_status == ProcessingStatus.COMPLETED,
                        AIDocumentProcessing.created_at < cutoff_date,
                        AIDocumentProcessing.requires_manual_review == False
                    )
                )
            )
            
            deleted_count = result.rowcount
            await db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old processing records")
            
            return {
                "success": True,
                "deleted_records": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "days_kept": days_to_keep
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old processing records: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        finally:
            await self.close_db_session()
    
    return run_async_task(_cleanup_records())


@celery_app.task(
    bind=True,
    name="ai_document_processing.generate_processing_report",
    soft_time_limit=300,   # 5 minutes
    time_limit=600,        # 10 minutes
)
def generate_processing_report_task(self, days_back: int = 30) -> Dict[str, Any]:
    """
    Celery task for generating processing performance reports.
    
    Args:
        days_back: Number of days to include in the report
        
    Returns:
        Dictionary with report data
    """
    async def _generate_report():
        from sqlalchemy import select, func, and_
        from datetime import timedelta
        
        db = AsyncSessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get processing statistics
            stats_query = select(
                func.count(AIDocumentProcessing.id).label("total"),
                func.sum(
                    func.case(
                        (AIDocumentProcessing.processing_status == ProcessingStatus.COMPLETED, 1),
                        else_=0
                    )
                ).label("completed"),
                func.sum(
                    func.case(
                        (AIDocumentProcessing.processing_status == ProcessingStatus.FAILED, 1),
                        else_=0
                    )
                ).label("failed"),
                func.avg(AIDocumentProcessing.processing_duration_seconds).label("avg_duration"),
                func.sum(
                    func.case(
                        (AIDocumentProcessing.requires_manual_review == True, 1),
                        else_=0
                    )
                ).label("manual_review_required")
            ).where(AIDocumentProcessing.created_at >= cutoff_date)
            
            stats_result = await db.execute(stats_query)
            stats = stats_result.first()
            
            # Get document type breakdown
            type_query = select(
                AIDocumentProcessing.detected_document_type,
                func.count(AIDocumentProcessing.id)
            ).where(
                and_(
                    AIDocumentProcessing.created_at >= cutoff_date,
                    AIDocumentProcessing.detected_document_type.isnot(None)
                )
            ).group_by(AIDocumentProcessing.detected_document_type)
            
            type_result = await db.execute(type_query)
            type_breakdown = {
                doc_type.value if doc_type else "unknown": count
                for doc_type, count in type_result.fetchall()
            }
            
            report = {
                "report_period": {
                    "days_back": days_back,
                    "start_date": cutoff_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat()
                },
                "processing_statistics": {
                    "total_documents": stats.total or 0,
                    "completed": stats.completed or 0,
                    "failed": stats.failed or 0,
                    "success_rate": (stats.completed / stats.total) if stats.total else 0,
                    "average_processing_time_seconds": float(stats.avg_duration) if stats.avg_duration else 0,
                    "manual_review_required": stats.manual_review_required or 0
                },
                "document_type_breakdown": type_breakdown,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Failed to generate processing report: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        finally:
            await db.close()
    
    return run_async_task(_generate_report())


# Periodic tasks (to be configured with Celery Beat)
@celery_app.task(name="ai_document_processing.periodic_cleanup")
def periodic_cleanup_task():
    """Periodic task for cleaning up old records."""
    return cleanup_old_processing_records_task.delay(days_to_keep=90)


@celery_app.task(name="ai_document_processing.periodic_reprocess_failed")
def periodic_reprocess_failed_task():
    """Periodic task for reprocessing failed documents."""
    return reprocess_failed_documents_task.delay(days_back=1)


@celery_app.task(name="ai_document_processing.periodic_report")
def periodic_report_task():
    """Periodic task for generating processing reports."""
    return generate_processing_report_task.delay(days_back=7)