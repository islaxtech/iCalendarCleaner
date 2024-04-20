from datetime import datetime

def filter_events(config, events, start_date, end_date):
    start_date = datetime.strptime(start_date.split("T")[0], '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date.split("T")[0], '%Y-%m-%d').date()

    filter = config['FILTER']
    filtered_events = []

    for event in events:
        if event.get('dtstart') is not None:
            event_start = event.decoded('dtstart')

            if isinstance(event_start, datetime):
                event_start = event_start.date()
            if start_date <= event_start <= end_date:
                summary = event.get('summary')
                if summary is not None:
                    if any(name in summary for name in filter):
                        continue
                    else:
                        filtered_events.append(event)

    return filtered_events