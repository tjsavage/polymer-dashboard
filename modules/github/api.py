import json
import datetime
import webapp2

from google.appengine.ext import ndb
from github import Github

from models import IssueSnapshot, GithubSnapshot
import tasks

class Index(webapp2.RequestHandler):
    def get(self):
        org = self.request.get("org")
        if not org or len(org) == 0:
            return self.response.write(json.dumps({
                    "type": "Error",
                    "body": "Bad org name"
                }))
        qry = GithubSnapshot.query(GithubSnapshot.github_org_name == org).order(-GithubSnapshot.requested_time)
        results = qry.fetch()

        result = {}
        requested_time = datetime.datetime.now()
        result["currentSnapshot"] = tasks.take_snapshot(org, requested_time, save=False).as_dict()
        result["snapshots"] = [r.as_dict() for r in results]

        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(json.dumps(result))

class Snapshots(webapp2.RequestHandler):
    def get(self):
        qry = GithubSnapshot.query().order(-GithubSnapshot.requested_time)
        results = qry.fetch()

        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(json.dumps([r.as_dict() for r in results]))

class TakeSnapshot(webapp2.RequestHandler):
    def get(self):
        org = self.request.get("org")
        if not org or len(org) == 0:
            return flask.jsonify({
                    "type": "Error",
                    "body": "Bad org name"
                })
        requested_time = datetime.datetime.now()

        result = tasks.take_snapshot(org, requested_time)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(json.dumps(result.as_dict()))