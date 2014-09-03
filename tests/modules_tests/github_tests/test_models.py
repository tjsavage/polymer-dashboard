import os
import unittest
import datetime
from pprint import pprint

from google.appengine.ext import testbed

from github import Github

from application import app

from test_base import GithubTestCase

from modules.github_issues.models import GithubIssue, GithubSnapshot, IssuesResult

class GithubIssueTestCase(GithubTestCase):
    def test_serialization_from_github(self):
        issues = self.g.search_issues("problem")
        issue = issues[0]
        snapshot = GithubIssue.from_github_issue(issue)
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
        assert snapshot.html_url == issue.html_url

class GithubIssuesSnapshotTestCase(GithubTestCase):
    def test_snapshot_single_child(self):
        requested_time = datetime.datetime.now()

        parent = GithubSnapshot(
                requested_time = requested_time
            )

        parent_key = parent.put()

        issues = self.g.search_issues("problem")
        issue = issues[0]
        snapshot = GithubIssue.from_github_issue(issue)
        snapshot.parent_snapshot = parent_key

        snapshot_key = snapshot.put()

        parent_query = GithubSnapshot.query()
        returned_parent = parent_query.fetch(1)[0]

        assert returned_parent != None
        assert returned_parent.requested_time == requested_time

        issue_query = GithubIssue.query()
        returned_issue = issue_query.fetch(1)[0]

        assert returned_issue != None
        assert returned_issue.title == issue.title


class IssuesResultTestCase(GithubTestCase):
    def test_issues_result_merge(self):
        result1 = IssuesResult(
                num_open=2,
                num_open_unassigned=3,
                num_open_unlabeled=4,
                by_assignee={
                    "a": 1,
                    "b": 2
                },
                by_repo={
                    "x": 1,
                    "y": 2
                }
            )

        result2 = IssuesResult(
                num_open=2,
                num_open_unassigned=3,
                num_open_unlabeled=4,
                by_assignee={
                    "b": 2,
                    "c": 3
                },
                by_repo={
                    "y": 2,
                    "z": 3
                }
            )

        result1.merge(result2)

        assert result1.num_open == 4
        assert result1.num_open_unassigned == 6
        assert result1.num_open_unlabeled == 8
        assert result1.by_assignee["a"] == 1
        assert result1.by_assignee["b"] == 4
        assert result1.by_assignee["c"] == 3
        assert result1.by_repo["x"] == 1
        assert result1.by_repo["y"] == 4
        assert result1.by_repo["z"] == 3