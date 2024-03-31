import requests
from icalendar import Calendar

def fetch_calendar(url):
    """
    Fetches the iCalendar data from the given URL.
    
    Parameters:
        url (str): The URL of the iCalendar feed.
        
    Returns:
        Calendar: An icalendar Calendar object containing the fetched events.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    calendar = Calendar.from_ical(response.content)
    return calendar
