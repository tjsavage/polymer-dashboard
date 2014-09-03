import os
import unittest

from google.appengine.ext import testbed

from github import Github

from application import app

class GithubTestCase(unittest.TestCase):
    def setUp(self):
        print app
        # Flask apps testing. See: http://flask.pocoo.org/docs/testing/
        # app.config['TESTING'] = True
        # app.config['CSRF_ENABLED'] = False
        # self.app = app.test_client()

        # Setups app engine test bed. See: http://code.google.com/appengine/docs/python/tools/localunittesting.html#Introducing_the_Python_Testing_Utilities
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()

        # Set up github object
        self.g = Github(app.config.GITHUB_USERNAME, app.config.GITHUB_PASSWORD)

    def tearDown(self):
        self.testbed.deactivate()