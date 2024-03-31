from icalendar import Calendar, Event
import os

def generate_calendar(events, file_path='filtered_calendar.ics'):
    """
    Generates an iCalendar file from the provided list of events.

    Parameters:
        events (list): A list of icalendar Event objects to be included in the calendar.
        file_path (str): The path where the generated calendar should be saved.
    """
    # Create a new calendar
    cal = Calendar()
    cal.add('prodid', '-//Filtered Calendar//mxm.dk//')
    cal.add('version', '2.0')

    # Add each event to the calendar
    for event in events:
        cal.add_component(event)

    # Write the calendar to the specified file
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())

    print(f"Filtered calendar generated and saved to {file_path}")

from icalendar import Calendar, Event
import os

def create_filtered_calendar(events, file_path):
    """
    Creates a new iCalendar file from the provided list of events.

    Parameters:
        events (list): A list of icalendar Event objects to include in the new calendar.
        file_path (str): The path where the new iCalendar file should be saved.

    Returns:
        None
    """
    # Create a new Calendar
    cal = Calendar()

    # Add events to the calendar
    for event in events:
        cal.add_component(event)

    # Write the calendar to file
    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())
        print(f"Filtered calendar has been saved to {file_path}")

def ensure_directory_exists(file_path):
    """
    Ensures that the directory for the file path exists, creating it if necessary.

    Parameters:
        file_path (str): The file path for which to ensure directory existence.

    Returns:
        None
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
