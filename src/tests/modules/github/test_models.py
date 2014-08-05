import os
import unittest
import datetime

from google.appengine.ext import testbed

from github import Github

from application import app

from test_base import GithubTestCase

from application.modules.github.models import IssueSnapshot, GithubSnapshot

class IssueSnapshotTestCase(GithubTestCase):
    def test_serialization_from_github(self):
        issues = self.g.search_issues("problem")
        issue = issues[0]
        snapshot = IssueSnapshot.from_github_issue(issue)
        assert snapshot != None
        assert snapshot.assignee == (issue.assignee.login if issue.assignee else None)
        assert snapshot.body == issue.body
        assert snapshot.closed_at == issue.closed_at
        assert snapshot.created_at == issue.created_at
        assert snapshot.github_id == issue.id
        assert len(snapshot.labels) == len(issue.labels)
        assert snapshot.number == issue.number
        assert snapshot.num_comments == issue.comments
        assert snapshot.repository == issue.repository.name
        assert snapshot.state == issue.state
        assert snapshot.title == issue.title
        assert snapshot.url == issue.url

class GithubIssuesSnapshotTestCase(GithubTestCase):
    def test_snapshot_single_child(self):
        requested_time = datetime.datetime.now()

        parent = GithubSnapshot(
                requested_time = requested_time
            )

        parent_key = parent.put()

        issues = self.g.search_issues("problem")
        issue = issues[0]
        snapshot = IssueSnapshot.from_github_issue(issue)
        snapshot.parent_snapshot = parent_key

        snapshot_key = snapshot.put()

        parent_query = GithubSnapshot.query()
        returned_parent = parent_query.fetch(1)[0]

        assert returned_parent != None
        assert returned_parent.requested_time == requested_time

        issue_query = IssueSnapshot.query(IssueSnapshot.parent_snapshot == returned_parent.key)
        returned_issue = issue_query.fetch(1)[0]

        assert returned_issue != None
        assert returned_issue.title == issue.title


