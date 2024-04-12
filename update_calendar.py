import pytz
import os.path
import datetime
import json
from icalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def load_ics(filename):
    with open(filename, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    return cal

import datetime
import pytz

def to_utc(dt):
    utc = pytz.UTC
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=None)
    if dt.tzinfo is None:
        dt = utc.localize(dt)
    else:
        dt = dt.astimezone(utc) 
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
    today_local_midnight = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
    today_utc_midnight = to_utc(today_local_midnight)

    time_min = today_utc_midnight.isoformat().replace('+00:00', 'Z')
    thirty_days_later = (today_utc_midnight + datetime.timedelta(days=30)).isoformat().replace('+00:00', 'Z')

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=thirty_days_later,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events_dict = {}
        for event in events_result.get('items', []):
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            event_start_dt = datetime.datetime.fromisoformat(event_start.replace('Z', '+00:00'))
            event_start_utc = to_utc(event_start_dt)
            event_key = (event['summary'], event_start_utc.isoformat())
            events_dict[event_key] = event
        return events_dict
    except HttpError as error:
        print('An error occurred:', error)
        return {}

def update_google_calendar():
    config = load_config()

    try:
        cal = load_ics('robin_work_filtered.ics')
        service = authenticate_google_calendar()
        calendar_id = config['ROBIN_GOOGLE_CAL']

        google_events = fetch_google_calendar_events(service, calendar_id)
        
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary'))
                start_dt = to_utc(component.get('dtstart').dt)
                end_dt = to_utc(component.get('dtend').dt)

                event_key = (summary, start_dt.isoformat())

                google_event = {
                    'summary': summary,
                    'start': {'dateTime': start_dt.isoformat()},
                    'end': {'dateTime': end_dt.isoformat()},
                }
                if event_key in google_events:
                    event_id = google_events[event_key]['id']
                    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=google_event).execute()
                    print('Event updated: %s' % (updated_event.get('htmlLink')))
                else:
                    inserted_event = service.events().insert(calendarId=calendar_id, body=google_event).execute()
                    print('Event created: %s' % (inserted_event.get('htmlmlLink')))
        
    except HttpError as error:
        print(f"An error occurred: {error}")
