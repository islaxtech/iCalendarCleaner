from icalendar import Event
from datetime import datetime

def filter_events(events, exclude_names):
    filtered_events = []
    for event in events:
        summary = event.get('summary')
        # Exclude events by name
        if summary is not None:
            if any(name in summary for name in exclude_names):
                continue
            else:
                filtered_events.append(event)
    return filtered_events

import datetime

def filter_events_by_date_range(events, start_date, end_date):
    if isinstance(start_date, datetime.datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime.datetime):
        end_date = end_date.date()

    filtered_events = []
    for event in events:
        event_start = event.decoded('dtstart')

        if isinstance(event_start, datetime.datetime):
            event_start = event_start.date()

        if start_date <= event_start <= end_date:
            filtered_events.append(event)
    return filtered_events


