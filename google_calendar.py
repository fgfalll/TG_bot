from datetime import datetime, timedelta
from gmail_auth import authenticate_google_services

gmail_service, calendar_service = authenticate_google_services()

def list_calendar_events():
    events_result = calendar_service.events().list(
        calendarId='primary', timeMin=datetime.utcnow().isoformat() + 'Z',
        maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return []

    calendar_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event['summary']
        calendar_events.append(f"{start} - {summary}")

    return calendar_events

def create_calendar_event(title, date, time, duration, description=''):
    start_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
    end_datetime = start_datetime + timedelta(minutes=duration)

    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'UTC'},
    }

    calendar_service.events().insert(calendarId='primary', body=event).execute()