import fix_path
import json
import datetime

from google.appengine.ext import ndb

# Taken from http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
dthandler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

class StackOverflowSnapshot(ndb.Model):
    """Example Model"""
    raw_timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
    requested_time = ndb.DateTimeProperty(required=True)
    num_questions_by_tag = ndb.JsonProperty()
    num_tagged_questions = ndb.IntegerProperty()
    num_answered = ndb.IntegerProperty()
    num_unanswered = ndb.IntegerProperty()
    total_question_views = ndb.IntegerProperty()
    status = ndb.StringProperty()
    status_string = ndb.StringProperty()

    def as_dict(self):
        result = {}
        result['requested_time'] = dthandler(self.requested_time)
        result['num_tagged_questions'] = self.num_tagged_questions
        result['num_questions_by_tag'] = self.num_questions_by_tag
        result['num_answered'] = self.num_answered
        result['num_unanswered'] = self.num_unanswered
        result['total_question_views'] = self.total_question_views
        result['status'] = self.status
        result['status_string'] = self.status_string

        return result

class StackOverflowQuestion(ndb.Model):
    first_seen = ndb.DateTimeProperty(required=True, auto_now_add=True)
    tags = ndb.StringProperty(repeated=True)
    is_answered = ndb.BooleanProperty()
    view_count = ndb.IntegerProperty()
    answer_count = ndb.IntegerProperty()
    url = ndb.StringProperty()
    title = ndb.StringProperty()
    creation_date = ndb.DateTimeProperty()
    question_id = ndb.IntegerProperty()

    def as_dict(self):
        result = {}
        result['first_seen'] = dthandler(self.first_seen)
        result['tags'] = [t for t in self.tags]
        result['is_answered'] = self.is_answered
        result['view_count'] = self.view_count
        result['answer_count'] = self.answer_count
        result['url'] = self.url
        result['title'] = self.title
        result['creation_date'] = dthandler(self.creation_date)
        result['question_id'] = self.question_id

        return result

    def update_to_stackexchange_question(self, stackexchange_question):
        updated = False
        if stackexchange_question.tags != self.tags:
            self.tags = stackexchange_question.tags
            updated = True
        if stackexchange_question.json['is_answered'] != self.is_answered:
            self.is_answered = stackexchange_question.json['is_answered']
            updated = True
        if stackexchange_question.view_count != self.view_count:
            self.view_count = stackexchange_question.view_count
            updated = True
        if stackexchange_question.json['answer_count'] != self.answer_count:
            self.answer_count = stackexchange_question.json['answer_count']
            updated = True
        if stackexchange_question.url != self.url:
            self.url = stackexchange_question.url
            updated = True
        if stackexchange_question.title != self.title:
            self.title = stackexchange_question.title
            updated = True
        if stackexchange_question.creation_date != self.creation_date:
            self.creation_date = stackexchange_question.creation_date
            updated = True
        if stackexchange_question.json['question_id'] != self.question_id:
            self.question_id = stackexchange_question.json['question_id']
            updated = True
        return updated

    @classmethod
    def from_stackexchange_question(cls, stackexchange_question):
        result = cls(
            tags = [t for t in stackexchange_question.tags],
            is_answered = stackexchange_question.json['is_answered'],
            view_count = stackexchange_question.view_count,
            answer_count = stackexchange_question.json['answer_count'],
            url = stackexchange_question.url,
            title = stackexchange_question.title,
            creation_date = stackexchange_question.creation_date,
            question_id = stackexchange_question.json['question_id']
            )

        return result