from celery import Celery
from config.core.settings import get_settings

# App settings.
settings = get_settings()

celery = Celery(
  settings.fetch("APP_NAME"),
  include=['app.jobs'],
  broker = settings.fetch("BROKER_URL"),
  result_backend = settings.fetch("BROKER_RESULT_BACKEND"),
)
