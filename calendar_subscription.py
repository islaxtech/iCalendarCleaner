import requests
from icalendar import Calendar

def fetch_calendar(url):
    response = requests.get(url)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)
    return calendar
