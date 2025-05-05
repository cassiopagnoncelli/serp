from config.core.broker import celery
from lib.core.mailer import Mailer
from pydantic import EmailStr
from typing import Dict, Any
from config.core.mailer import mailer_config
from asyncio import run

# Usage:
#
# from app.jobs.mailer import mailer
#
# result = mailer.delay(email, subject, template, variables)
# print(f"Task ID: {result.id}") 

@celery.task
def mailer(email: EmailStr, subject: str, template: str, variables: Dict[str, Any] = {}):
  mailer = Mailer(config = mailer_config, verbose = True)
  run(mailer.send_email(email, subject, template, variables))
