from celery import Celery
from config.core.settings import get_settings

settings = get_settings()

celery = Celery(
  'my_app_queue',
  include=['app.jobs'],
  broker = settings.fetch("BROKER_BACKEND"),
)
