from app.core.queue import app

@app.task
def ping():
  return "pong"
