import logging
import webapp2
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from modules.polymerdev.models import PolymerDevEmail

class PolymerDevMailHandler(InboundMailHandler):
    def receive(self, mail_message):
        polymerdevEmail = PolymerDevEmail.from_mail_message(mail_message)
        print polymerdevEmail.date
        polymerdevEmail.put()



app = webapp2.WSGIApplication([PolymerDevMailHandler.mapping()], debug=True)
