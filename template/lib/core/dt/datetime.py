from datetime import datetime, UTC
import pytz

# Application timezone - set this to your desired default
APP_TIMEZONE = pytz.timezone('America/Sao_Paulo')

class DateTime:
  def local(include_tz: bool = False):
    if include_tz:
      return datetime.now(APP_TIMEZONE)
    else:
      return datetime.now(APP_TIMEZONE).replace(tzinfo=None)

  def utc(include_tz: bool = False):
    if include_tz:
      return datetime.now(UTC)
    else:
      return datetime.now(UTC).replace(tzinfo=None)
