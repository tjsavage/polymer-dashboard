import fix_path
import json
import sys
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from github import Github, GithubException

from settings import Config
from models import IssueSnapshot, GithubSnapshot, IssuesResult

g = Github(Config.GITHUB_USERNAME, Config.GITHUB_PASSWORD)

class SnapshotWorker(webapp2.RequestHandler):
    def get(self):
        github_org_name = self.request.get("org")
        name = self.request.get("name")
        index = int(self.request.get("index")) if self.request.get("index") else None
        requested_time = datetime.datetime.now()

        deferred.defer(take_snapshot, github_org_name, requested_time, name, index)
        return self.response.write("Taking snapshot...")

def take_snapshot(github_org_name, requested_time, name = None, index = None, save = True):
    parent_snapshot = GithubSnapshot(requested_time = requested_time,
                                    github_org_name = github_org_name,
                                    snapshot_name = name,
                                    snapshot_index = index)

    parent_snapshot.issues_result = IssuesResult(
        num_open=0,
        num_open_unassigned=0,
        num_open_unlabeled=0
        )
    if save:
        parent_snapshot_key = parent_snapshot.put()
    else:
        parent_snapshot_key = None

    take_issues_snapshot(github_org_name, parent_snapshot_key)

    return parent_snapshot

def take_issues_snapshot(github_org_name, parent_snapshot_key, save = True):
    repos = g.get_organization(github_org_name).get_repos()
    for repo in repos:
        deferred.defer(take_repo_issues_snapshot, repo, parent_snapshot_key, save)

def take_repo_issues_snapshot(github_repo, parent_snapshot_key, save = True):
    num_open = 0
    num_open_unassigned = 0
    num_open_unlabeled = 0
    try:
        issues = github_repo.get_issues(state="open")
        if parent_snapshot_key:
            parent_snapshot = parent_snapshot_key.get()
            if not parent_snapshot.issues_result.by_assignee:
                parent_snapshot.issues_result.by_assignee = {}
                parent_snapshot.put()
            if not parent_snapshot.issues_result.by_repo:
                parent_snapshot.issues_result.by_repo = {}
                parent_snapshot.put()

        for issue in issues:
            issue_snapshot = IssueSnapshot.from_github_issue(issue)
            issue_snapshot.parent_snapshot = parent_snapshot_key
            if save:
                issue_snapshot.put()

            if issue_snapshot.state == 'open':
                num_open += 1
            if issue_snapshot.state == 'open' and issue_snapshot.assignee == None:
                num_open_unassigned +=1
            if issue_snapshot.state == 'open' and (issue_snapshot.labels == None or len(issue_snapshot.labels)) == 0:
                num_open_unlabeled +=1

            if issue_snapshot.assignee and issue_snapshot.assignee in parent_snapshot.issues_result.by_assignee:
                parent_snapshot.issues_result.by_assignee[issue_snapshot.assignee] += 1
            elif issue_snapshot.assignee:
                parent_snapshot.issues_result.by_assignee[issue_snapshot.assignee] = 1

        if parent_snapshot_key:
            parent_snapshot = parent_snapshot_key.get()
            parent_snapshot.issues_result.num_open += num_open
            parent_snapshot.issues_result.num_open_unassigned += num_open_unassigned
            parent_snapshot.issues_result.num_open_unlabeled += num_open_unlabeled

            parent_snapshot.issues_result.by_repo[github_repo.name] = num_open

            parent_snapshot.put()
    except GithubException:
        pass
