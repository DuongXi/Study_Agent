import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))
from auth.auth import *

class Calendar():
  def __init__(self, access_token=None, refresh_token=None):
    if access_token and refresh_token:
      self.creds = calendar_authenticate(access_token,refresh_token)

  # Lấy thời gian hiện tại
  def get_date_time(self):
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    return now

  # Tạo sự kiện
  def generate_event(self, summary, location, description, start, end):
    return {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
          "dateTime": start,
          "timeZone": "Asia/Ho_Chi_Minh"
        },
        "end": {
          "dateTime": end,
          "timeZone": "Asia/Ho_Chi_Minh"
        },
      }

  # Tạo sự kiện lặp lại
  def generate_recurring_event(self, summary, location, description, start, end, freq, count):
    return {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
          "dateTime": start,
          "timeZone": "Asia/Ho_Chi_Minh"
        },
        "end": {
          "dateTime": end,
          "timeZone": "Asia/Ho_Chi_Minh"
        },
        'recurrence': [
          f'RRULE:FREQ={freq};COUNT={count}'
        ],
      }

  # Tạo sự kiện
  def create_event(self, event):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      event = service.events().insert(calendarId="primary", body=event).execute()
      return event
    except HttpError as error:
      print(f"An error occurred: {error}")

  # Lấy sự kiện sắp tới
  def get_upcoming_events(self, time_min=None, time_max=None, max_results=20):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      if time_min is None:
        time_min = self.get_date_time()

      events_result = service.events().list(calendarId='primary',
                                            timeMin=time_min,
                                            timeMax=time_max,
                                            maxResults=max_results,
                                            singleEvents=True,
                                            orderBy="startTime").execute()
      events = events_result.get("items", [])
      events_list = []
      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        events_list.append({"id": event["id"], "start": start, "summary": event["summary"]})
      return events_list
    except HttpError as error:
      print(f"An error occurred: {error}")
 
  # Lấy sự kiện lặp lại
  def get_recurring_event(self):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      events_result = (
        service.events()
        .list(
            calendarId="primary",
        )
        .execute()
      )
      events = events_result.get("items", [])
      events_list = []
      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        events_list.append({"id": event["id"], "start": start, "summary": event["summary"]})
      return events_list
    except HttpError as error:
      print(f"An error occurred: {error}")

  # Xóa sự kiện lặp lại
  def delete_recurring_event(self, recurring_event_id):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      instances = service.events().instances(calendarId='primary', eventId=recurring_event_id).execute()
      instance = instances['items'][0]
      instance['status'] = 'cancelled'
      service.events().update(calendarId='primary', eventId=instance['id'], body=instance).execute()
      return {"message": "Sự kiện đã được xóa"}
    except HttpError as error:
      print(f"An error occurred: {error}")

  # Xóa sự kiện
  def delete_event(self, event_id):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      service.events().delete(calendarId="primary", eventId=event_id).execute()
      return {"message": "Sự kiện đã được xóa"}
    except HttpError as error:
      print(f"An error occurred: {error}")

  # Cập nhật sự kiện
  def update_event(self, event_id, event):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      event = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
      return {"message": "Sự kiện đã được cập nhật"}
    except HttpError as error:
      print(f"An error occurred: {error}")

if __name__ == "__main__":
  cal = Calendar()
  cal.get_recurring_event()