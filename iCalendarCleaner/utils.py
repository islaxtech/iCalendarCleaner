import pytz
import datetime

def to_utc(dt):
    utc = pytz.UTC
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=None)
    if dt.tzinfo is None:
        dt = utc.localize(dt)
    else:
        dt = dt.astimezone(utc) 
    return dt