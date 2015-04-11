import fix_path
import json
import datetime
from dateutil.parser import parse as dateutil_parse
from pytz import timezone

from google.appengine.ext import ndb

# Taken from http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
dthandler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

class PolymerDevResponse(ndb.Model):
    timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
    sender = ndb.StringProperty()
    body = ndb.TextProperty()

    def as_dict(self):
        result = {}
        result['timestamp'] = dthandler(self.timestamp)
        result['sender'] = self.sender
        result['body'] = self.body

        return result

class PolymerDevEmail(ndb.Model):
    """Example Model"""
    raw_timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
    date = ndb.DateTimeProperty()
    sender = ndb.StringProperty()
    subject = ndb.StringProperty()
    body = ndb.TextProperty()
    responses = ndb.StructuredProperty(PolymerDevResponse, repeated=True)
    message_id = ndb.StringProperty()

    @classmethod
    def from_mail_message(cls, mail_message):
        bodies = mail_message.bodies('text/plain')
        all_bodies_text = ""
        for text in bodies:
            all_bodies_text += text[1].decode()

        return cls(
            date = dateutil_parse(mail_message.date).replace(tzinfo=None),
            sender = mail_message.sender,
            subject = mail_message.subject,
            body = all_bodies_text
        )

    def as_dict(self):
        result = {}
        result['raw_timestamp'] = dthandler(self.raw_timestamp)
        result['date'] = dthandler(self.date)
        result['sender'] = self.sender
        result['subject'] = self.subject
        result['body'] = self.body
        result['responses'] = [r.as_dict() for r in self.responses]

        return result

class PolymerDevSnapshot(ndb.Model):
    raw_timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
    requested_time = ndb.DateTimeProperty()
    num_emails = ndb.IntegerProperty()
    num_unresponded_emails = ndb.IntegerProperty()

    def as_dict(self):
        result = {}
        result['raw_timestamp'] = dthandler(self.raw_timestamp)
        result['requested_time'] = dthandler(self.requested_time)
        result['num_emails'] = self.num_emails
        result['num_unresponded_emails'] = self.num_unresponded_emails

        return result