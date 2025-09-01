from celery import Celery

from dostavka.settings import RABBITMQ_URL

celery_app = Celery(
    "package_tasks",
    broker=RABBITMQ_URL,
    backend="rpc://",
    include=["dostavka.celery.tasks"]
)

celery_app.conf.task_default_queue = "packages"
celery_app.conf.task_routes = {
    "dostavka.celery.tasks.calculate_and_save": {"queue": "packages"}
}
