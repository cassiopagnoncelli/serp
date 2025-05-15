import sys
import threading

# Status icons
PENDING = "⏳"
SUCCESS = "✅"
ERROR = "❌"
LOADING = "🔄"

class ServiceStatus:
  def __init__(self):
    self.status_lock = threading.Lock()
    self.db_status = PENDING
    self.redis_status = PENDING
    self.storage_status = PENDING
    self.last_line = ""
    
  def update_db(self, status):
    with self.status_lock:
      self.db_status = status
      self._update_display()
      
  def update_redis(self, status):
    with self.status_lock:
      self.redis_status = status
      self._update_display()
  
  def update_storage(self, status):
    with self.status_lock:
      self.storage_status = status
      self._update_display()
  
  def _update_display(self):
    # Clear the last status line
    if self.last_line:
      sys.stdout.write("\r" + " " * len(self.last_line) + "\r")
      
    # Create new status line
    status_line = f"Database: {self.db_status}  Redis: {self.redis_status}  Storage: {self.storage_status}"
    sys.stdout.write(status_line)
    sys.stdout.flush()
    self.last_line = status_line
  
  def finalize(self):
    # Complete the line with a newline
    if self.last_line:
      print()
