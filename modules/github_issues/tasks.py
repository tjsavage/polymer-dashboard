import fix_path
import json
import sys
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from github import Github, GithubException

from settings import Config
from models import GithubIssue, GithubSnapshot, IssuesResult

g = Github(Config.GITHUB_USERNAME, Config.GITHUB_PASSWORD)

class SnapshotWorker(webapp2.RequestHandler):
    def get(self):
        github_org_name = self.request.get("org")
        name = self.request.get("name")
        index = int(self.request.get("index")) if self.request.get("index") else None
        requested_time = datetime.datetime.now()

        deferred.defer(take_snapshot, github_org_name, requested_time)
        return self.response.write("Taking snapshot...")

class DeleteAllWorker(webapp2.RequestHandler):
    def get(self):

        ndb.delete_multi(GithubIssue.query().fetch(keys_only=True))
        ndb.delete_multi(GithubSnapshot.query().fetch(keys_only=True))
        return self.response.write("Deleted!")

def take_snapshot(github_org_name, requested_time):
    snapshot = GithubSnapshot(requested_time = requested_time,
                                    github_org_name = github_org_name)

    snapshot.issues_result = IssuesResult.empty_result()

    github_api_repos = g.get_organization(github_org_name).get_repos()
    for github_api_repo in github_api_repos:
        repo_issues_result = sync_repo_issues_to_datastore(github_api_repo)
        snapshot.issues_result.merge(repo_issues_result)
        print "Synced %s" % github_api_repo.name

    snapshot.put()

    return snapshot

def sync_repo_issues_to_datastore(github_api_repo):
    repository_name = github_api_repo.name

    repo_api_issues = github_api_repo.get_issues(state='all')
    repo_datastore_issues = GithubIssue.query(GithubIssue.repository == github_api_repo.name).fetch()

    repo_datastore_issues_by_github_id = {issue.github_id: issue for issue in repo_datastore_issues}

    datastore_issues_to_put = []

    issues_result = IssuesResult.empty_result()
    for repo_api_issue in repo_api_issues:
        if repo_api_issue.id in repo_datastore_issues_by_github_id:
            datastore_issue = repo_datastore_issues_by_github_id[repo_api_issue.id]
            updated = datastore_issue.update_to_github_issue(repo_api_issue, repository_name=repository_name)
            #if updated:
            #    datastore_issue.put()
        else:
            datastore_issue = GithubIssue.from_github_issue(repo_api_issue, repository_name=repository_name)
            #datastore_issue.put()
        print "\t%s" % datastore_issue.title
        datastore_issues_to_put.append(datastore_issue)

        if datastore_issue.state == 'open':
            issues_result.num_open += 1
            if datastore_issue.assignee == None:
                issues_result.num_open_unassigned += 1
            if datastore_issue.labels == None or len(repo_api_issue.labels) == 0:
                issues_result.num_open_unlabeled += 1

            if datastore_issue.assignee in issues_result.by_assignee:
                issues_result.by_assignee[datastore_issue.assignee] += 1
            else:
                issues_result.by_assignee[datastore_issue.assignee] = 1

    ndb.put_multi(datastore_issues_to_put)

    issues_result.by_repo[github_api_repo.name] = issues_result.num_open

    return issues_result


