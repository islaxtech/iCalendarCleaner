import calendar_subscription
import event_filter
import calendar_generator
import update_calendar
from datetime import datetime, timedelta
import json
import os

START_DATE = datetime.now()
END_DATE = START_DATE + timedelta(days=30)
DIR = os.getcwd()

def load_config():
    with open(f'{DIR}/config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def update_filtered_calendar(config):
    print("Updating filtered calendar...")
    SOURCE_CALENDAR_URL = config['ROBIN_SOURCE_CALENDAR_URL']
    FILTERED_CALENDAR_PATH = config['ROBIN_FILTERED_CALENDAR_PATH']
    FILTER = config['FILTER']

    calendar = calendar_subscription.fetch_calendar(SOURCE_CALENDAR_URL)
    events = calendar.subcomponents
    exclude_names = FILTER

    events_filtered = event_filter.filter_events(events, exclude_names)
    filtered_events = event_filter.filter_events_by_date_range(events_filtered, START_DATE, END_DATE)

    calendar_generator.ensure_directory_exists(FILTERED_CALENDAR_PATH)
    calendar_generator.create_filtered_calendar(filtered_events, FILTERED_CALENDAR_PATH)
    update_calendar.update_google_calendar(config)
    print("Filtered calendar updated.")

def main():
    config = load_config()
    update_filtered_calendar(config)

if __name__ == '__main__':
    main()
