import os, sys
from pprint import pprint
sys.path.append('lib')

import webapp2

import modules
import settings

HOMEPAGE = open('home.html').read()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(HOMEPAGE)

app = webapp2.WSGIApplication([
    ('/', MainPage),

    ('/api/github/', modules.github_issues.api.Index),
    ('/api/github/snapshots/', modules.github_issues.api.Snapshots),
    ('/api/github/latest/', modules.github_issues.api.Latest),
    ('/tasks/github/take_snapshot/', modules.github_issues.tasks.SnapshotWorker),
    ('/tasks/github/delete/', modules.github_issues.tasks.DeleteAllWorker),

    ('/api/stackoverflow/', modules.stackoverflow.api.Index),
    ('/tasks/stackoverflow/take_snapshot/', modules.stackoverflow.tasks.SnapshotWorker)
])

if os.getenv('APPENGINE_CONF') == 'DEV':
    #development settings n
    app.config = settings.Development
    
elif os.getenv('APPENGINE_CONF') == 'TEST':
    app.config = settings.Testing

else:
    app.config = settings.Production


