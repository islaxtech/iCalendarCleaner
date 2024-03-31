import calendar_subscription
import event_filter
import calendar_generator
from datetime import datetime, timedelta
import json
# from apscheduler.schedulers.blocking import BlockingScheduler

# Configuration
START_DATE = datetime.now()
END_DATE = START_DATE + timedelta(days=30)

def load_config():
    """
    Loads configuration settings from config.json.
    
    Returns:
        dict: A dictionary with configuration settings.
    """
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def update_filtered_calendar(SOURCE_CALENDAR_URL, FILTERED_CALENDAR_PATH, FILTER):
    """
    Fetches the source calendar, filters events, and generates a new filtered calendar.
    """
    print("Updating filtered calendar...")
    # Fetch the source calendar
    calendar = calendar_subscription.fetch_calendar(SOURCE_CALENDAR_URL)

    # Extract events from the calendar
    events = calendar.subcomponents

    # Define names to exclude
    exclude_names = FILTER

    # Filter events based on keywords, excluding specific names, and by date range
    events_filtered = event_filter.filter_events(events, exclude_names)
    # filtered_events = event_filter.filter_events_by_date_range(events_filtered, START_DATE, END_DATE)

    # Generate a new filtered calendar
    calendar_generator.ensure_directory_exists(FILTERED_CALENDAR_PATH)
    calendar_generator.create_filtered_calendar(events_filtered, FILTERED_CALENDAR_PATH)
    print("Filtered calendar updated.")


def main():
    """
    Main function to orchestrate the updating of the filtered calendar at regular intervals.
    """
    config = load_config()
    # scheduler = BlockingScheduler()
    # scheduler.add_job(update_filtered_calendar, 'interval', hours=1)  # Update every hour
    # print("Scheduler started. The filtered calendar will be updated every hour.")
    # scheduler.start()
    # update_filtered_calendar(ROBIN_SOURCE_CALENDAR_URL, ROBIN_FILTERED_CALENDAR_PATH)
    update_filtered_calendar(config['GT_SOURCE_CALENDAR_URL'], config['GT_FILTERED_CALENDAR_PATH'], config['FILTER'])

if __name__ == '__main__':
    main()
