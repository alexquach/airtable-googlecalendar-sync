from google.oauth2 import service_account
from googleapiclient.discovery import build

from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = './service-account-credentials.json'

TIMEZONE = 'UTC'

class calendar:
    def __init__(self, calendar_id):
        self.calendar_id = calendar_id
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        self.service = build('calendar', 'v3', credentials=self.credentials)

    def create_event(self, title, start, duration=1, timezone=TIMEZONE):
        event = {
            'summary': title,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': (start + timedelta(hours=duration)).isoformat(),
                'timeZone': timezone,
            }
        }

        event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
