import pytest
from app.jobs.ping import ping

def test_ping_task(celery_test):
  result = ping()
  assert result == "pong"

def test_ping_task_async(celery_test):
  result = ping.delay()
  assert result.get() == "pong"
