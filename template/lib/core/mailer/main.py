import os
from typing import Dict, Any
from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from jinja2 import Environment, FileSystemLoader
from fastapi_mail.connection import ConnectionConfig
import sendgrid
from sendgrid.helpers.mail import *

template_env = Environment(loader = FileSystemLoader('/Users/cassio/tmp/bla/app/emails'))

class Mailer:
  def __init__(self, config: Dict[str, Any], verbose: bool = False):
    self.driver = config["driver"]
    if self.driver == "fastapi_mail":
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
    elif self.driver == "sendgrid":
      self.sg = sendgrid.SendGridAPIClient(api_key = config["api_key"])
    else:
      raise ValueError(f"Unsupported driver: {config['driver']}")
    self.verbose = verbose

  def _log(self, message: str):
    if self.verbose:
      print(message)
  
  def send_email(self, email: EmailStr, subject: str, template: str, variables: Dict[str, Any] = {}):
    if self.driver == "fastapi_mail":
      return self.send_email_mailer(email, subject, template, variables)
    elif self.driver == "sendgrid":
      return self.send_email_sendgrid(email, subject, template, variables)
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def send_email_mailer(self, email: EmailStr, subject: str, template: str, variables: Dict[str, Any] = {}):
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
  
  def send_email_sendgrid(self, email: EmailStr, subject: str, template: str, variables: Dict[str, Any] = {}):
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
    from_email = sendgrid.Email("test@example.com")
    to_email = sendgrid.To(email)
    subject = subject
    content = sendgrid.Content("text/html", html_content)
    mail = sendgrid.Mail(from_email, to_email, subject, content)

    # Send the message
    self._log(f"Sending message")
    response = self.sg.client.mail.send.post(request_body = mail.get())
    self._log(f"Response:")
    self._log(response.status_code)
    self._log(response.body)
    self._log(response.headers)
    return response
