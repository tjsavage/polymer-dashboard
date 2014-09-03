import os
import unittest
import datetime

from google.appengine.ext import testbed

from github import Github

from application import app

from test_base import GithubTestCase

from modules.github_issues.models import GithubIssue, GithubSnapshot
from modules.github_issues.tasks import take_snapshot

class TakeSnapshotTestCase(GithubTestCase):
    def test_take_snapshot(self):
        requested_time = datetime.datetime.now()

        take_snapshot("tjsavage-test-organization", requested_time)

        snapshot_query = GithubSnapshot.query(GithubSnapshot.requested_time == requested_time)
        snapshot_result = snapshot_query.fetch()[0]

        assert snapshot_result != None

        issues_query = GithubIssue.query()
        issues_results = issues_query.fetch()

        assert issues_results != None
        assert len(issues_results) > 0
        assert len(issues_results[0].title) > 0

        assert snapshot_result.issues_result.num_open == 4
        assert snapshot_result.issues_result.num_open_unlabeled == 2
        assert snapshot_result.issues_result.num_open_unassigned == 3
        assert snapshot_result.issues_result.by_assignee["tjsavage"] == 1


