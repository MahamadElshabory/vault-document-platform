from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "vault",
    broker=settings.redis_url,
    include=["app.tasks.document_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    broker_connection_retry_on_startup=True
)