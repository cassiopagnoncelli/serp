from app.core.queue import celery

# Usage:
#
# from app.jobs.ping import ping
#
# result = ping.delay()
# print(f"Task ID: {result.id}") 

@celery.task
def ping():
  return "pong"
