import pytest
from app.jobs.ping import ping
from celery import Celery
from config.initializers.broker import celery

@pytest.fixture(autouse=True)
def setup_celery():
  # configure Celery to use memory backend for testing
  celery.conf.update(
    result_backend='cache+memory://',
    task_always_eager=True # execute synchronously
  )
  yield
  celery.conf.update(
    result_backend=None,
    task_always_eager=False
  )

def test_ping_task():
  result = ping()
  assert result == "pong"

def test_ping_task_async():
  result = ping.delay()
  assert result.get() == "pong"
