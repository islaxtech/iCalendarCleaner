from icalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import datetime
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
                logging.warning("Refresh token is invalid or expired. Need to re-authenticate.")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(token, "w") as token:
                token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def synchronize_events(service, calendar_id, cal, start_date, end_date):
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        event_info = parse_event(component)
        event_id = event_info.get('id', None)
        try:
            if event_id and check_event_exists(service, calendar_id, event_id):
                update_event(service, calendar_id, event_info)
            else:
                insert_event(service, calendar_id, event_info)
        except HttpError as error:
            handle_http_error(error, event_info['summary'])

def update_google_calendar(config, start_date, end_date):
    try:
        cal = load_ics('robin_work_filtered.ics')
        service = authenticate_google_calendar()
        calendar_id = config['ROBIN_GOOGLE_CAL']
        
        synchronize_events(service, calendar_id, cal, start_date, end_date)

        os.remove('robin_work_filtered.ics')
    except Exception as error:
        logging.error(f"An error occurred during the update process: {error}")

def check_event_exists(service, calendar_id, event_id):
    try:
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        return event is not None
    except HttpError as error:
        if error.resp.status == 404:
            return False
        else:
            raise

def parse_event(component):
    return {
        'summary': str(component.get('summary')),
        'description': str(component.get('description', '')) + f"\n\nLast updated: {datetime.datetime.now()}",
        'start': {'dateTime': component.get('dtstart').dt.isoformat()},
        'end': {'dateTime': component.get('dtend').dt.isoformat()},
        'id': component.get('UID').lower().replace("-", "")
    }

def update_event(service, calendar_id, event_info):
    updated_event = service.events().update(
        calendarId=calendar_id, eventId=event_info['id'], body=event_info
    ).execute()
    logging.info(f"Event {event_info['summary']} updated: {updated_event.get('htmlLink')}")

def insert_event(service, calendar_id, event_info):
    inserted_event = service.events().insert(
        calendarId=calendar_id, body=event_info
    ).execute()
    logging.info(f"Event {event_info['summary']} created: {inserted_event.get('htmlLink')}")

def handle_http_error(error, summary):
    if error.resp.status == 409:
        logging.warning(f"Event {summary} already exists.")
    else:
        logging.error(f"An error occurred for {summary}: {error}")