# coding=utf-8


from oauth2client import client
from googleapiclient import sample_tools


"""
    Google Calendar:
    * https://developers.google.com/google-apps/calendar/quickstart/python
    * https://developers.google.com/api-client-library/python/
    * http://tools.ietf.org/html/rfc5545
"""


class CalendarEvent(object):
    def __init__(self):
        self.event_id = None
        self.color = None
        self.start_date = None
        self.end_date = None
        self.summary = None
        self.description = None
        self.updated = None
        self.recurrence = None

        self.all_day = None

    @staticmethod
    def from_json(event):
        calendar_event = CalendarEvent()

        calendar_event.event_id = event.get('id')
        calendar_event.color = event.get('colorId')

        start = event.get('start')
        start_date_time = start.get('dateTime')
        start_date = start.get('date')

        if start_date_time:
            calendar_event.start_date = start_date_time
        elif start_date:
            calendar_event.start_date = start_date

        end = event.get('end')
        end_date_time = end.get('dateTime')
        end_date = end.get('date')

        if end_date_time:
            calendar_event.end_date = end_date_time
        elif end_date:
            calendar_event.end_date = end_date

        if start_date_time and end_date_time:
            calendar_event.all_day = False
        else:
            calendar_event.all_day = True

        calendar_event.summary = event.get('summary').encode('utf-8').strip()
        description = event.get('description')
        if description:
            calendar_event.description = description.encode('utf-8').strip()
        calendar_event.updated = event.get('updated')

        calendar_event.recurrence = event.get('recurrence')

        return calendar_event


class GoogleCalendar(object):
    def __init__(self, argv):
        self.calendar_events = dict()
        self.ticktick_calendar_id = None
        self.ticktick_calendar_name = 'tucktuck'

        self.service, self.flags = sample_tools.init(
            argv, 'calendar', 'v3', __doc__, __file__,
            scope='https://www.googleapis.com/auth/calendar')

        try:
            self.get_ticktick_calendar_id()
        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize.')
            raise

    def create_ticktick_calendar(self, name):
        calendar = {
            'summary': name,
            'timeZone': 'Europe/Kiev'
        }

        created_calendar = self.service.calendars().insert(body=calendar).execute()
        return created_calendar['id']

    def get_ticktick_calendar_id(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(
                pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                name = calendar_list_entry['summary']
                if name == self.ticktick_calendar_name:
                    self.ticktick_calendar_id = calendar_list_entry['id']
                    break

            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        if not self.ticktick_calendar_id:
            self.ticktick_calendar_id = self.create_ticktick_calendar(self.ticktick_calendar_name)


    def fetch_ticktick_events(self):
        page_token = None
        while True:
            events = self.service.events().list(calendarId=self.ticktick_calendar_id, pageToken=page_token).execute()
            for event in events['items']:
                event = CalendarEvent.from_json(event)
                self.calendar_events[event.event_id] = event

            page_token = events.get('nextPageToken')
            if not page_token:
                break

    def create_event(self, calendar_event):
        body = event_to_json(calendar_event)

        event = self.service.events().insert(calendarId=self.ticktick_calendar_id, body=body).execute()
        calendar_event.event_id = event.get('id')

    def modify_event(self, calendar_event):
        body = event_to_json(calendar_event)

        self.service.events().update(calendarId=self.ticktick_calendar_id, eventId=calendar_event.event_id, body=body).execute()

    def remove_event(self, calendar_event):
        self.service.events().delete(calendarId=self.ticktick_calendar_id, eventId=calendar_event.event_id).execute()


def event_to_json(calendar_event, body={}):
    start = dict()
    end = dict()
    if calendar_event.all_day is True:
        start = {'date': calendar_event.start_date}
        end = {'date': calendar_event.end_date}
    else:
        start = {'dateTime': calendar_event.start_date}
        end = {'dateTime': calendar_event.end_date}

    start['timeZone'] = 'UTC'
    end['timeZone'] = 'UTC'

    body['summary'] = calendar_event.summary
    body['description'] = calendar_event.description
    body['start'] = start
    body['end'] = end
    body['colorId'] = calendar_event.color

    if calendar_event.recurrence:
        body['recurrence'] = calendar_event.recurrence

    return body
