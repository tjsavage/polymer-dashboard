"""
modules/github/models.py

App Engine datastore models

"""

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

class IssuesResult(ndb.Model):
    num_open = ndb.IntegerProperty()
    num_open_unassigned = ndb.IntegerProperty()
    num_open_unlabeled = ndb.IntegerProperty()

    def as_dict(self):
        result = {}
        result["num_open"] = self.num_open
        result["num_open_unassigned"] = self.num_open_unassigned
        result["num_open_unlabeled"] = self.num_open_unlabeled

        return result

class GithubSnapshot(ndb.Model):
    """Example Model"""
    raw_timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
    requested_time = ndb.DateTimeProperty(required=True)
    snapshot_name = ndb.StringProperty()
    github_org_name = ndb.StringProperty()
    snapshot_index = ndb.IntegerProperty()
    issues_result = ndb.StructuredProperty(IssuesResult)

    def as_dict(self):
        result = {}
        result["raw_timestamp"] = dthandler(self.raw_timestamp)
        result["requested_time"] = dthandler(self.requested_time)
        result["snapshot_name"] = self.snapshot_name
        result["github_org_name"] = self.github_org_name
        result["snapshot_index"] = self.snapshot_index
        result["issues_result"] = self.issues_result.as_dict()

        return result

class IssueSnapshot(ndb.Model):
    """Snapshot of a particular github issue"""
    assignee = ndb.StringProperty()
    body = ndb.TextProperty()
    closed_at = ndb.DateTimeProperty()
    created_at = ndb.DateTimeProperty()
    github_id = ndb.IntegerProperty()
    labels = ndb.StringProperty(repeated=True)
    number = ndb.IntegerProperty()
    num_comments = ndb.IntegerProperty()
    parent_snapshot = ndb.KeyProperty(kind=GithubSnapshot)
    repository = ndb.StringProperty()
    state = ndb.StringProperty()
    title = ndb.StringProperty()
    url = ndb.StringProperty()

    def as_dict(self):
        result = {}
        result["assignee"] = self.assignee
        result["body"] = self.body
        result["closed_at"] = dthandler(self.closed_at)
        result["created_at"] = dthandler(self.created_at)
        result["github_id"] = self.github_id
        result["labels"] = [l for l in self.labels]
        result["number"] = self.number
        result["num_comments"] = self.num_comments
        result["parent_snapshot"] = self.parent_snapshot
        result["repository"] = self.repository
        result["state"] = self.state
        result["title"] = self.title
        result["url"] = self.url

        return result

    @classmethod
    def from_github_issue(cls, github_issue):
        issue_snapshot = cls(
                assignee = github_issue.assignee.login if github_issue.assignee else None,
                body = github_issue.body,
                closed_at = github_issue.closed_at,
                created_at = github_issue.created_at,
                github_id = github_issue.id,
                labels = [l.name for l in github_issue.labels],
                number = github_issue.number,
                num_comments = github_issue.comments,
                repository = github_issue.repository.name,
                state = github_issue.state,
                title = github_issue.title,
                url = github_issue.url
            )
        return issue_snapshot