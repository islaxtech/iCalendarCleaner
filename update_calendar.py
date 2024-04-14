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
DIR = os.getcwd()

def load_ics(filename):
    with open(filename, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    return cal

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
    token = f'{DIR}/token.json'
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(token, "w") as token:
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
            events_dict[event['id']] = event
        return events_dict
    except HttpError as error:
        print('An error occurred:', error)
        return {}

def update_google_calendar(config):

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
                description = component.get('description', '')
                uid = component.get('UID').lower().replace("-","")

                google_event = {
                    'summary': summary,
                    'description': description,
                    'start': {'dateTime': start_dt.isoformat()},
                    'end': {'dateTime': end_dt.isoformat()},
                    'id' : uid
                }
                if uid in google_events:
                    updated_event = service.events().update(calendarId=calendar_id, eventId=uid, body=google_event).execute()
                    print('Event updated: %s' % (updated_event.get('htmlLink')))
                else:
                    inserted_event = service.events().insert(calendarId=calendar_id, body=google_event).execute()
                    print('Event created: %s' % (inserted_event.get('htmlmlLink')))
        
    except HttpError as error:
        print(f"An error occurred: {error}")
