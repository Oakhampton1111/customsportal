"""
Celery configuration for background task processing.

This module configures Celery for handling background tasks such as
AI document processing, batch operations, and other long-running tasks.
"""

import os
from celery import Celery
from kombu import Queue

# Create Celery instance
celery_app = Celery("customs_broker_portal")

# Configuration
celery_app.conf.update(
    # Broker settings
    broker_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "ai_document_processing.*": {"queue": "ai_processing"},
        "document_processing.*": {"queue": "document_processing"},
        "batch_processing.*": {"queue": "batch_processing"},
    },
    
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default"),
        Queue("ai_processing", routing_key="ai_processing"),
        Queue("document_processing", routing_key="document_processing"),
        Queue("batch_processing", routing_key="batch_processing"),
    ),
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_annotations={
        "*": {
            "rate_limit": "10/s",
            "time_limit": 600,
            "soft_time_limit": 300,
        },
        "ai_document_processing.process_document": {
            "rate_limit": "5/s",
            "time_limit": 1200,  # 20 minutes for AI processing
            "soft_time_limit": 900,  # 15 minutes soft limit
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "tasks.ai_document_processing",
    "tasks.document_processing",
    "tasks.batch_processing",
])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f"Request: {self.request!r}")
    return "Celery is working!"


if __name__ == "__main__":
    celery_app.start()