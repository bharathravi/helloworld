from google.appengine.api import users
from google.appengine.ext import ndb

import cgi
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

class Invitee(ndb.Model):
  """A single invitee"""
  first_name = ndb.StringProperty(indexed=True)
  last_name = ndb.StringProperty(indexed=True)
  email = ndb.StringProperty(indexed=True)


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
      self.response.write(MAIN_PAGE_HTML)

  def post(self):
    user = self.GetUserOrRedirect(self.request.uri)
    first = self.request.get("first")
    last = self.request.get("last")
    email = self.request.get("email")

    invitee = Invitee(first_name=first,
                      last_name=last,
                      email=email)

    invitee.put()
    self.redirect('/')

class GuestList(LoginPage):
  def get(self):
    user = self.GetUserOrRedirect(self.request.uri)
    query = Invitee.query()
    invitees = query.fetch()
    for x in invitees:
      self.response.write(x.first_name)

class GuestTest(LoginPage):
  def get(self):
    user = self.GetUserOrRedirect(self.request.uri)
    if user:
      query = Invitee.query(Invitee.email == user.email())
      invitees = query.fetch()

      if not len(invitees) == 1:
        self.response.write("Not found :(")
      else:
        self.response.write("Welcome back " + invitees[0].first_name)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', MainPage),
    ('/list', GuestList),
    ('/test', GuestTest),
], debug=True)
