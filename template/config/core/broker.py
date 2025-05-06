from celery import Celery
from celery.schedules import crontab
from config.core.settings import get_settings

settings = get_settings()

celery = Celery(
  settings.fetch("APP_NAME"),
  include=['app.jobs'],
  broker = settings.fetch("BROKER_URL"),
  result_backend = settings.fetch("BROKER_RESULT_BACKEND"),
)

# Import periodic tasks
celery.conf.beat_schedule = {
    'ping-every-minute': {
        'task': 'app.jobs.ping.ping',  # Use full task path
        'schedule': crontab(minute='*'),  # Run every minute
    },
}
