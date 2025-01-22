from datetime import datetime
import pytz # type: ignore

def get_current_time_custom():
    """Returns the current time in UTC-5:30."""
    custom_timezone = pytz.FixedOffset(-330)  # UTC-5:30
    current_utc_time = datetime.utcnow()
    return pytz.utc.localize(current_utc_time).astimezone(custom_timezone)
