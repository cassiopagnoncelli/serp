from app.core.background_jobs import app

@app.task
def ping():
    return "pong"
