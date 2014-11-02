import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import cgi
import jinja2
import json
import webapp2
import uuid

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/add" method="post">
      <div>First Name: <input type="text" name="first"><br></div>
      <div>Last Name: <input type="text" name="last"><br><div>
      <div>Email: <input type="text" name="email"><br></div>
      <div><input type="submit" value="Add"></div>
      <div><input type="submit" value="Remove"></div>
    </form>
  </body>
</html>
"""

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

ADMINS = ['bharathravi1@gmail.com', 'ranjithagk@gmail.com', 'test@example.com']

class Invitee(ndb.Model):
  """A single invitee"""
  first_name = ndb.StringProperty(indexed=True)
  last_name = ndb.StringProperty(indexed=True)
  email = ndb.StringProperty(indexed=True)
  rsvp = ndb.StringProperty(indexed=True)
  uuid = ndb.StringProperty(indexed=True)

class LoginPage(webapp2.RequestHandler):
  def GetUserOrRedirect(self, uri):
    user = users.get_current_user()
    if user:
      return user
    else:
      self.redirect(users.create_login_url(uri))

class MainPage(webapp2.RequestHandler):
  def get(self):
    uuid = self.request.get("uuid")
    template_values = {
          'guest' : None,
    }

    if uuid:
      query = Invitee.query(Invitee.uuid == uuid)
      invitees = query.fetch()
      if len(invitees) == 1:
        template_values['guest'] = invitees[0]

    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))


class RSVP(LoginPage):
  def post(self):
    uuid = self.request.get("uuid")
    rsvp = self.request.get("rsvp")

    query = Invitee.query(Invitee.uuid == uuid)
    invitees = query.fetch()

    array = {"retval": "1"}
    if len(invitees) != 1:
      array["retval"] = "0"
    else:
      invitees[0].rsvp = rsvp
      invitees[0].put()

    print rsvp, array["retval"]
    print json.dumps(array)

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(array))


class GuestManager(LoginPage):
  def get(self):
    user = self.GetUserOrRedirect(self.request.uri)
    if user.email() not in ADMINS:
        self.response.write('You are not admin')
        return

    query = Invitee.query()
    invitees = query.fetch()
     
    template_values = {
        'invitees': invitees,
    }

    template = JINJA_ENVIRONMENT.get_template('add.html')
    self.response.write(template.render(template_values))

  def post(self):
    user = self.GetUserOrRedirect(self.request.uri)
    first = self.request.get("first")
    last = self.request.get("last")
    email = self.request.get("email")
    uuid = uuid.uuid4()
    
    invitee = Invitee(first_name=first,
                      last_name=last,
                      email=email,
                      rsvp="0",
                      uuid=uuid)
    query = Invitee.query(Invitee.email == invitee.email)
    invitees = query.fetch()

    if len(invitees):
      print 'EXISTS ALREADY'
    else:
      invitee.put()
    self.redirect('/admin')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin', GuestManager),
    ('/rsvp', RSVP),
], debug=True)
