from asyncio import run

from config.core.broker import celery
from app.utils.authentication import delete_expired_tokens

@celery.task
def clean_expired_tokens():
  run(delete_expired_tokens())
