import os, sys
sys.path.append('lib')

import webapp2

from modules import github
import settings

HOMEPAGE = open('home.html').read()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(HOMEPAGE)

app = webapp2.WSGIApplication([
    ('/', MainPage),

    ('/api/github/', github.api.Index),
    ('/api/github/snapshots/', github.api.Snapshots),
    ('/api/github/latest/', github.api.Latest),
    ('/tasks/github/take_snapshot/', github.tasks.SnapshotWorker)
])

if os.getenv('APPENGINE_CONF') == 'DEV':
    #development settings n
    app.config = settings.Development
    
elif os.getenv('APPENGINE_CONF') == 'TEST':
    app.config = settings.Testing

else:
    app.config = settings.Production


