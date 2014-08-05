import json

from google.appengine.ext import ndb
from github import Github, GithubException

from application import app
from models import IssueSnapshot, GithubSnapshot, IssuesResult

g = Github(app.config['GITHUB_USERNAME'], app.config['GITHUB_PASSWORD'])

def take_snapshot(github_org_name, requested_time, name = None, index = None, save = True):
    parent_snapshot = GithubSnapshot(requested_time = requested_time,
                                    github_org_name = github_org_name,
                                    snapshot_name = name,
                                    snapshot_index = index)

    if save:
        parent_snapshot_key = parent_snapshot.put()

    issues_result = take_issues_snapshot(github_org_name, parent_snapshot_key)

    parent_snapshot.issues_result = issues_result
    if save:
        parent_snapshot.put()

    return parent_snapshot

def take_issues_snapshot(github_org_name, parent_snapshot_key, save = True):
    num_open = 0
    num_open_unassigned = 0
    num_open_unlabeled = 0

    repos = g.get_organization(github_org_name).get_repos()
    for repo in repos:
        try:
            issues = repo.get_issues(state="open")

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
        except GithubException:
            pass

    return IssuesResult(
            num_open=num_open,
            num_open_unassigned=num_open_unassigned,
            num_open_unlabeled=num_open_unlabeled
        )

