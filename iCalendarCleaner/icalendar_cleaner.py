from iCalendarCleaner import event_filter
from iCalendarCleaner import calendar_generator
from iCalendarCleaner import update_calendar
from iCalendarCleaner import utils
import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class iCalendarCleaner:

    def __init__(self):
        self.config = self.load_config()
        self.filtered_calendar = self.config['ROBIN_FILTERED_CALENDAR_PATH']

    def load_config(self):
        config_path = os.path.join(BASE_DIR, 'config', 'config.json')
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config

    def get_events(self):
        SOURCE_CALENDAR_URL = self.config['ROBIN_SOURCE_CALENDAR_URL']
        calendar = calendar_generator.fetch_calendar(SOURCE_CALENDAR_URL)
        return calendar.subcomponents

    def get_date_range(self):
        today_local_midnight = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        today_utc_midnight = utils.to_utc(today_local_midnight)
        
        start_date = today_utc_midnight.isoformat().replace('+00:00', 'Z')
        end_date = (today_utc_midnight + datetime.timedelta(days=60)).isoformat().replace('+00:00', 'Z')

        return start_date, end_date

    def update_filtered_calendar(self):
        print("Updating filtered calendar...")

        events = self.get_events()
        start_date, end_date = self.get_date_range()

        filtered_events = event_filter.filter_events(self.config, events, start_date, end_date)

        calendar_generator.create_filtered_calendar(filtered_events, self.filtered_calendar)
        update_calendar.update_google_calendar(self.config, start_date, end_date)
        
        print("Filtered calendar updated.")