from pydantic import EmailStr
from typing import Dict, Any
from asyncio import run

from config.core.mailer import mailer_config
from lib.core.mailer.main import Mailer
from config.core.broker import celery

# Usage:
#
# from app.jobs.mailer import mailer
#
# result = mailer.delay(
#   email = "to@example.com",
#   subject = "Test email",
#   template = "welcome.html.en.v1.jinja2",
#   variables = { "user_name": "Name Surname" }
# )
# print(f"Task ID: {result.id}") 

@celery.task
def mailer(email: EmailStr, subject: str, template: str, variables: Dict[str, Any] = {}):
  mailer = Mailer(config = mailer_config, verbose = True)
  run(mailer.send_email(email, subject, template, variables))
