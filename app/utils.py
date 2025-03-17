from datetime import datetime
import pytz # type: ignore

def get_current_time_custom():
    """Returns the current time in UK timezone."""
    uk_timezone = pytz.timezone('Europe/London')
    return datetime.now(pytz.utc).astimezone(uk_timezone)

