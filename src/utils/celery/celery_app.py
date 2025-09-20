from celery import Celery

from src.config.settings import RABBITMQ_URL

celery_app = Celery(
    "package_tasks",
    broker=RABBITMQ_URL,
    backend="rpc://",
    include=["src.utils.celery.tasks"]
)
