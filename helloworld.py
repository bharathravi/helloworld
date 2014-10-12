import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import cgi
import jinja2
import json
import webapp2

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/add" method="post">
      <div>First Name: <input type="text" name="first"><br></div>
      <div>Last Name: <input type="text" name="last"><br><div>
      <div>Email: <input type="text" name="email"><br></div>
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>
  </body>
</html>
"""

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Invitee(ndb.Model):
  """A single invitee"""
  first_name = ndb.StringProperty(indexed=True)
  last_name = ndb.StringProperty(indexed=True)
  email = ndb.StringProperty(indexed=True)
  rsvp = ndb.StringProperty(indexed=True)

class LoginPage(webapp2.RequestHandler):
  def GetUserOrRedirect(self, uri):
    user = users.get_current_user()
    if user:
      return user
    else:
      self.redirect(users.create_login_url(uri))

class MainPage(LoginPage):
  def get(self):
    user = self.GetUserOrRedirect(self.request.uri)
    if user:
      query = Invitee.query(Invitee.email == user.email())
      invitees = query.fetch()

      template_values = {
            'guest' : None,
            'logout_url' : users.create_logout_url(self.request.uri)
      }
      if len(invitees) == 1:
        template_values['guest'] = invitees[0]

      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render(template_values))

class GuestManager(LoginPage):
  def get(self):
    user = self.GetUserOrRedirect(self.request.uri)
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

    invitee = Invitee(first_name=first,
                      last_name=last,
                      email=email,
                      rsvp="0")
    query = Invitee.query(Invitee.email == invitee.email)
    invitees = query.fetch()

    if len(invitees):
      print 'EXISTS ALREADY'
    else:
      invitee.put()
    self.redirect('/admin')

class RSVP(LoginPage):
  def post(self):
    print "asa"
    user = self.GetUserOrRedirect(self.request.uri)
    rsvp = self.request.get("rsvp")

    query = Invitee.query(Invitee.email == user.email())
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


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin', GuestManager),
    ('/rsvp', RSVP),
], debug=True)
