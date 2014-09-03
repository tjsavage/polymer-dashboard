import fix_path
import json
import sys
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext import deferred
import stackexchange

from settings import Config
from models import StackOverflowSnapshot, StackOverflowQuestion

so = stackexchange.Site(stackexchange.StackOverflow, Config.STACKEXCHANGE_KEY)

class SnapshotWorker(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        requested_time = datetime.datetime.now()

        deferred.defer(take_snapshot, requested_time)
        return self.response.write("Taking snapshot...")

def take_snapshot(requested_time):
    snapshot = StackOverflowSnapshot(requested_time=requested_time)
    snapshot.num_tagged_questions = 0
    snapshot.num_questions_by_tag = {}
    snapshot.num_answered = 0
    snapshot.num_unanswered = 0
    snapshot.total_question_views = 0

    datastore_questions = StackOverflowQuestion.query().fetch()
    datastore_questions_by_so_id = {question.question_id: question for question in datastore_questions}

    questions = so.questions(tagged='polymer')
    for stackexchange_question in questions:
        if stackexchange_question.json['question_id'] in datastore_questions_by_so_id:
            datastore_question = datastore_questions_by_so_id[stackexchange_question.json['question_id']]
            updated = datastore_question.update_to_stackexchange_question(stackexchange_question)
            if updated:
                datastore_question.put()
        else:
            datastore_question = StackOverflowQuestion.from_stackexchange_question(stackexchange_question)
            datastore_question.put()

        snapshot.num_tagged_questions += 1
        for tag in datastore_question.tags:
            if tag in snapshot.num_questions_by_tag:
                snapshot.num_questions_by_tag[tag] += 1
            else:
                snapshot.num_questions_by_tag[tag] = 1
        if datastore_question.is_answered:
            snapshot.num_answered += 1
        else:
            snapshot.num_unanswered += 1
        snapshot.total_question_views += datastore_question.view_count

    snapshot.put()

    return snapshot


