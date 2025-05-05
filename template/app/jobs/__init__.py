"""
Jobs package that exports all jobs from submodules.
"""
from .ping import ping
from .mailer import mailer

__all__ = [
  "ping",
  "mailer"
]
