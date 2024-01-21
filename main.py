from requests_oauthlib import OAuth1
import requests
from datetime import date
import config
from notifypy import Notify

API_BASE_URL = "https://api.schoology.com/v1/users/"

class SchoologyAPI:
    def __init__(self):
        self.auth = OAuth1(config.key, config.secret, "", "")
        self.sections = []
        self.grades = []
        self.events = []

    def make_api_request(self, endpoint, params=None):
        url = f"{API_BASE_URL}{config.user_id}/{endpoint}"
        response = requests.get(url, auth=self.auth, params=params)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response.json()

    def get_sections(self):
        sections = self.make_api_request("sections")["section"]
        self.sections = [[section["course_title"], section["id"]] for section in sections]
    
    def get_events(self):
        self.get_sections()
        today = date.today().isoformat()
        events = self.make_api_request("events", {"start_date": today}).get("event", [])
        temp = []

        for event in events:
            try:
                temp.append(
                    {
                        "name": event["title"],
                        "description": event["description"],
                        "course_id": event["section_id"],
                        "assignment_id": event["assignment_id"],
                        "date": event["start"],
                        "all_day": event["all_day"],
                    }
                )
            except KeyError:
                continue

        self.events = temp

class Notifier:
    def __init__(self, api):
        self.api = api
        self.api.get_events()
        self.notify()

    def notify(self):
        for i, event in enumerate(self.api.events):
            notification = Notify(
                default_notification_application_name="Schoology",
                default_notification_icon="Python/Schoology Notiier/schoology.png",
                default_notification_urgency="critical"
            )
            notification.title = f'{event["name"]}'
            notification.message = f'Date: {event["date"][slice(10)]}'
            notification.send()

if __name__ == "__main__":
    api = SchoologyAPI()
    notifier = Notifier(api)