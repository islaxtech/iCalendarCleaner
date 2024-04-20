from icalendar import Calendar
import requests
import os

def fetch_calendar(url):
    response = requests.get(url)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)
    return calendar

def generate_calendar(events, file_path='filtered_calendar.ics'):
    cal = Calendar()
    cal.add('prodid', '-//Filtered Calendar//mxm.dk//')
    cal.add('version', '2.0')

    for event in events:
        cal.add_component(event)

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())

    print(f"Filtered calendar generated and saved to {file_path}")

def create_filtered_calendar(events, file_path):
    ensure_directory_exists(file_path)
    cal = Calendar()
    for event in events:
        cal.add_component(event)

    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())
        print(f"Filtered calendar has been saved to {file_path}")

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
