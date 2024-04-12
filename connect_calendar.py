import pytz
import os.path
import datetime
from icalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes define the level of access you need
SCOPES = ['https://www.googleapis.com/auth/calendar']

def load_ics(filename):
    with open(filename, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    return cal

import datetime
import pytz

def to_utc(dt):
    utc = pytz.UTC
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=utc)
    elif dt.tzinfo is not None: 
        return dt.astimezone(utc)
    else:  
        return utc.localize(dt)
    return dt


def authenticate_google_calendar():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def fetch_google_calendar_events(service, calendar_id):
    now = datetime.datetime.now(datetime.timezone.utc)
    seven_days_later = now + datetime.timedelta(days=7)
    time_min = now.isoformat()
    time_max = seven_days_later.isoformat()
    
    time_min = time_min.replace('+00:00', 'Z')
    time_max = time_max.replace('+00:00', 'Z')

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return {event['summary']: event for event in events_result.get('items', [])}
    except HttpError as error:
        print('An error occurred:', error)
        return {}

def update_google_calendar(service, cal, calendar_id):
    google_events = fetch_google_calendar_events(service, calendar_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    seven_days_later = now + datetime.timedelta(days=7)
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = str(component.get('summary'))
            start_dt = to_utc(component.get('dtstart').dt)
            end_dt = to_utc(component.get('dtend').dt)

            if now <= start_dt < seven_days_later:
                google_event = {
                    'summary': summary,
                    'start': {'dateTime': start_dt.isoformat()},
                    'end': {'dateTime': end_dt.isoformat()},
                }
                if summary in google_events:
                    event_id = google_events[summary]['id']
                    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=google_event).execute()
                    print('Event updated: %s' % (updated_event.get('htmlLink')))
                else:
                    inserted_event = service.events().insert(calendarId=calendar_id, body=google_event).execute()
                    print('Event created: %s' % (inserted_event.get('htmlLink')))

def main():

    try:
        ics_calendar = load_ics('robin_work_filtered.ics')
        google_service = authenticate_google_calendar()
        calendar_id = 'a3f05a7fa5681e7d3d0280b976de9b580e55a557fde7d3b996810fc190d2ebcf@group.calendar.google.com'
        update_google_calendar(google_service, ics_calendar, calendar_id)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
