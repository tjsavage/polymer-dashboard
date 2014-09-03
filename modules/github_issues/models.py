"""
modules/github/models.py

App Engine datastore models

"""

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

class IssuesResult(ndb.Model):
    num_open = ndb.IntegerProperty()
    num_open_unassigned = ndb.IntegerProperty()
    num_open_unlabeled = ndb.IntegerProperty()
    by_assignee = ndb.JsonProperty()
    by_repo = ndb.JsonProperty()

    def as_dict(self):
        result = {}
        result["num_open"] = self.num_open
        result["num_open_unassigned"] = self.num_open_unassigned
        result["num_open_unlabeled"] = self.num_open_unlabeled
        result["by_assignee"] = self.by_assignee
        result["by_repo"] = self.by_repo

        return result

    def merge(self, other_issues_result):
        self.num_open += other_issues_result.num_open
        self.num_open_unassigned += other_issues_result.num_open_unassigned
        self.num_open_unlabeled += other_issues_result.num_open_unlabeled

        self.by_assignee = { k: self.by_assignee.get(k, 0) + other_issues_result.by_assignee.get(k, 0) 
            for k in set(self.by_assignee) | set(other_issues_result.by_assignee)}

        self.by_repo = { k: self.by_repo.get(k, 0) + other_issues_result.by_repo.get(k, 0) 
            for k in set(self.by_repo) | set(other_issues_result.by_repo)}

    @classmethod
    def empty_result(cls):
        return IssuesResult(
            num_open = 0,
            num_open_unassigned = 0,
            num_open_unlabeled = 0,
            by_assignee = {},
            by_repo ={}
        )

class GithubSnapshot(ndb.Model):
    """Example Model"""
    raw_timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
    requested_time = ndb.DateTimeProperty(required=True)
    github_org_name = ndb.StringProperty()
    issues_result = ndb.StructuredProperty(IssuesResult)

    def as_dict(self):
        result = {}
        result["raw_timestamp"] = dthandler(self.raw_timestamp)
        result["requested_time"] = dthandler(self.requested_time)
        result["github_org_name"] = self.github_org_name
        result["issues_result"] = self.issues_result.as_dict()

        return result


class GithubIssue(ndb.Model):
    """Mirrors a particular github issue"""
    first_seen = ndb.DateTimeProperty(required=True, auto_now_add=True)
    assignee = ndb.StringProperty()
    body = ndb.TextProperty()
    closed_at = ndb.DateTimeProperty()
    created_at = ndb.DateTimeProperty()
    updated_at = ndb.DateTimeProperty()
    github_id = ndb.IntegerProperty()
    labels = ndb.StringProperty(repeated=True)
    number = ndb.IntegerProperty()
    num_comments = ndb.IntegerProperty()
    repository = ndb.StringProperty()
    state = ndb.StringProperty()
    title = ndb.StringProperty()
    html_url = ndb.StringProperty()
    pull_request_html_url = ndb.StringProperty()

    def as_dict(self):
        result = {}
        result["first_seen"] = dthandler(self.first_seen)
        result["assignee"] = self.assignee
        result["body"] = self.body
        result["closed_at"] = dthandler(self.closed_at)
        result["created_at"] = dthandler(self.created_at)
        result["updated_at"] = dthandler(self.updated_at)
        result["github_id"] = self.github_id
        result["labels"] = [l for l in self.labels]
        result["number"] = self.number
        result["num_comments"] = self.num_comments
        result["repository"] = self.repository
        result["state"] = self.state
        result["title"] = self.title
        result["html_url"] = self.html_url
        result["pull_request_html_url"] = self.pull_request_html_url

        return result

    def update_to_github_issue(self, github_issue, repository_name = None):
        updated = False
        if self.assignee != (github_issue.assignee.login if github_issue.assignee else None):
            self.assignee = github_issue.assignee.login if github_issue.assignee else None
            updated = True
        if self.body != github_issue.body:
            self.body = github_issue.body
            updated = True
        if self.closed_at != github_issue.closed_at:
            self.closed_at = github_issue.closed_at
            updated = True
        if self.created_at != github_issue.created_at:
            self.created_at != github_issue.created_at
            updated = True
        if self.github_id != github_issue.id:
            self.github_id = github_issue.id
            updated = True
        if self.labels != [l.name for l in github_issue.labels]:
            self.labels = [l.name for l in github_issue.labels]
            updated = True
        if self.number != github_issue.number:
            self.number = github_issue.number
            updated = True
        if self.num_comments != github_issue.comments:
            self.num_comments = github_issue.comments
            updated = True
        if self.repository != (repository_name if repository_name else github_issue.repository.name):
            self.repository = (repository_name if repository_name else github_issue.repository.name)
            updated = True
        if self.state != github_issue.state:
            self.state = github_issue.state
            updated = True
        if self.title != github_issue.title:
            self.title = github_issue.title
            updated = True
        if self.html_url != github_issue.html_url:
            self.html_url = github_issue.html_url
            updated = True
        if self.pull_request_html_url != github_issue.pull_request.html_url if github_issue.pull_request else None:
            self.pull_request_html_url = github_issue.pull_request.html_url if github_issue.pull_request else None
            updated = True
        return updated

    @classmethod
    def from_github_issue(cls, github_issue, repository_name = None):
        issue = cls(
            assignee = github_issue.assignee.login if github_issue.assignee else None,
            body = github_issue.body,
            closed_at = github_issue.closed_at,
            created_at = github_issue.created_at,
            github_id = github_issue.id,
            labels = [l.name for l in github_issue.labels],
            number = github_issue.number,
            num_comments = github_issue.comments,
            repository = repository_name if repository_name else github_issue.repository.name,
            state = github_issue.state,
            title = github_issue.title,
            html_url = github_issue.html_url,
            pull_request_html_url = github_issue.pull_request.html_url if github_issue.pull_request else None
        )
        return issue