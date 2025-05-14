import yaml
from pathlib import Path
from celery.schedules import crontab

def load_beat_schedule():
    cron_file = Path('config/cron.yml')
    with open(cron_file, 'r') as f:
        config = yaml.safe_load(f)
    
    beat_schedule = {}
    for task_name, task_config in config.items():
        schedule_str = task_config['schedule']
        # Parse full crontab expression (minute hour day_of_month month day_of_week)
        parts = schedule_str.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid crontab format for {task_name}. Must be 'minute hour day_of_month month day_of_week'")
            
        schedule = crontab(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month_of_year=parts[3],
            day_of_week=parts[4]
        )
        
        beat_schedule[task_name] = {
            'task': task_config['task'],
            'schedule': schedule
        }
    
    return beat_schedule
