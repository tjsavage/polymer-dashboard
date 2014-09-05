import fix_path
import json
import datetime
import webapp2

from google.appengine.ext import ndb
import stackexchange

from models import StackOverflowQuestion, StackOverflowSnapshot
import tasks

class Index(webapp2.RequestHandler):
    def get(self):
        snapshots = StackOverflowSnapshot.query().order(StackOverflowSnapshot.requested_time).fetch()

        result = {}
        result['snapshots'] = [s.as_dict() for s in snapshots]

        self.response.headers['Content-Type'] = 'text/json'
        return self.response.write(json.dumps(result))


class SnapshotStatus(webapp2.RequestHandler):
    def get(self):
        qry = StackOverflowSnapshot.query().order(-StackOverflowSnapshot.requested_time)
        snapshot = qry.get();

        return self.response.write(json.dumps(snapshot.as_dict()))