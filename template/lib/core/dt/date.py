from datetime import datetime, UTC
import pytz

# Application timezone - set this to your desired default
APP_TIMEZONE = pytz.timezone('America/Sao_Paulo')

class Date:
  def local():
    return datetime.now(APP_TIMEZONE).date()

  def utc():
    return datetime.now(UTC).date()
