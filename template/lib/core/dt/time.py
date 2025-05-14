from datetime import datetime, UTC
import pytz

# Application timezone - set this to your desired default
APP_TIMEZONE = pytz.timezone('America/Sao_Paulo')

class Time:
  def local():
    return datetime.now(APP_TIMEZONE).time()

  def utc():
    return datetime.now(UTC).time()
