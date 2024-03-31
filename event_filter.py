from icalendar import Event
from datetime import datetime

def filter_events(events, exclude_names):
    """
    Filters events based on keywords and excludes events with specific names.

    Parameters:
        events (list): A list of icalendar Event objects.
        keywords (list of str): Keywords to filter the events by.
        exclude_names (list of str): Event names to exclude from the results.

    Returns:
        list: A list of events that match the criteria.
    """
    filtered_events = []
    for event in events:
        summary = event.get('summary')
        # Exclude events by name
        if any(name in summary for name in exclude_names):
            continue
        else:
            filtered_events.append(event)
    return filtered_events

# def filter_events_by_date_range(events, start_date, end_date):
#     """
#     Filters events to only include those within the specified date range.

#     Parameters:
#         events (list): A list of icalendar Event objects.
#         start_date (datetime): The start date of the range.
#         end_date (datetime): The end date of the range.

#     Returns:
#         list: A list of events that fall within the specified date range.
#     """
#     filtered_events = []
#     for event in events:
#         event_start = event.decoded('dtstart')
#         if start_date <= event_start <= end_date:
#             filtered_events.append(event)
#     return filtered_events
