from iCalendarCleaner import utils

from icalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_ics(filename):
    with open(filename, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    return cal

def authenticate_google_calendar():
    token = os.path.join(BASE_DIR, 'credentials', 'token.json')
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("Refresh token is invalid or expired. Need to re-authenticate.")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(token, "w") as token:
                token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def fetch_google_calendar_events(service, calendar_id, start_date, end_date):
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
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

def update_google_calendar(config, start_date, end_date):

    try:
        cal = load_ics('robin_work_filtered.ics')
        service = authenticate_google_calendar()
        calendar_id = config['ROBIN_GOOGLE_CAL']

        google_events = fetch_google_calendar_events(service, calendar_id, start_date, end_date)
        
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary'))
                start_dt = utils.to_utc(component.get('dtstart').dt)
                end_dt = utils.to_utc(component.get('dtend').dt)
                description = component.get('description', '')
                uid = component.get('UID').lower().replace("-","")
                last_updated = datetime.datetime.now()

                google_event = {
                    'summary': summary,
                    'description': f'{description}\n\n{uid}\n\nLast updated: {last_updated}',
                    'start': {'dateTime': start_dt.isoformat()},
                    'end': {'dateTime': end_dt.isoformat()},
                    'id' : uid
                }
                if uid in google_events:
                    try: 
                        updated_event = service.events().update(calendarId=calendar_id, eventId=uid, body=google_event).execute()
                        print(f"Event {summary} updated: {updated_event.get('htmlLink')}")
                    except HttpError as error:
                        print(f"An error occurred updating an event: {error}")
                else:
                    try:
                        inserted_event = service.events().insert(calendarId=calendar_id, body=google_event).execute()
                        print(f"Event {summary} created: {inserted_event.get('htmlLink')}")
                    except HttpError as error:
                        if error.resp.status == 409:
                            print("Event already exists.")
                        else:
                            print(f"An error occurred inserting an event: {error}")
        os.remove('robin_work_filtered.ics')
        
    except Exception as error:
        print(f"An error occurred: {error}")
