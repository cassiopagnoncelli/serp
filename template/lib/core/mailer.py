from typing import Dict, Any
from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from jinja2 import Environment, FileSystemLoader
from fastapi_mail.connection import ConnectionConfig

template_env = Environment(loader = FileSystemLoader('/Users/cassio/tmp/bla/app/emails'))

class Mailer:
  def __init__(self, config: Dict[str, Any], verbose: bool = False):
    if config["driver"] == "fastapi_mail":
      self.config = ConnectionConfig(
        MAIL_USERNAME = config["username"],
        MAIL_PASSWORD = config["password"],
        MAIL_FROM = config["from"],
        MAIL_PORT = config["port"],
        MAIL_SERVER = config["server"],
        MAIL_FROM_NAME = config["from_name"],
        MAIL_STARTTLS = True,
        MAIL_SSL_TLS = False
      )
    else:
      raise ValueError(f"Unsupported driver: {config['driver']}")
    self.verbose = verbose

  def _log(self, message: str):
    if self.verbose:
      print(message)

  def send_email(self, email: EmailStr, subject: str, template: str, variables: Dict[str, Any] = {}):
    # Log the email being sent
    self._log(f"Sending email to {email} with subject {subject} and template {template}")

    # Render the template
    self._log(f"Rendering template {template} with variables {variables}")
    template = template_env.get_template(template)
    
    # Render the template
    self._log(f"Rendering template {template} with variables {variables}")
    html_content = template.render(**variables)
    self._log(f"HTML content:")
    self._log(html_content)

    # Create the message
    self._log(f"Creating message")
    message = MessageSchema(
      subject = subject,
      recipients = [email],
      body = html_content,
      subtype = MessageType.html
    )
    
    # Send the message
    self._log(f"Sending message")
    fm = FastMail(self.config)
    return fm.send_message(message)
