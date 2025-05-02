from celery import Celery
import app.jobs

app = Celery(
    'my_app_queue',
    broker='pyamqp://guest@localhost//',  # RabbitMQ default
    backend='rpc://'
)

app.autodiscover_tasks()
