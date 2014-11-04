import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

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
CONTENT = """
Dear %s %s,

We're getting married! 

Please grace our wedding with your presence, on 28th Nov 2014,
at : <venue details>

Please click on the link below to view your personalized invitation:
http://bharathandranjitha.appspot.com?uuid=%s

Hope to see you there!

Thanks,
Bharath and Ranjitha
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

class MainPage(webapp2.RequestHandler):
  def GetRightTemplate(self, user_agent_string):
    """Get the right template depending on the user agent"""
    if 'Mobile' in user_agent_string or 'Nexus' in user_agent_string:
      return JINJA_ENVIRONMENT.get_template('mob_index.html')

    return JINJA_ENVIRONMENT.get_template('index.html')
      

  def get(self):
    myuuid = self.request.get("uuid")
    template_values = {
          'guest' : None,
    }

    if myuuid:
      query = Invitee.query(Invitee.uuid == myuuid)
      invitees = query.fetch()
      if len(invitees) == 1:
        template_values['guest'] = invitees[0]

    template = self.GetRightTemplate(self.request.headers.get('user_agent'))
    self.response.write(template.render(template_values))


class RSVP(webapp2.RequestHandler):
  def post(self):
    myuuid = self.request.get("uuid")
    rsvp = self.request.get("rsvp")

    query = Invitee.query(Invitee.uuid == myuuid)
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



class AdminPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      if user.email() not in ADMINS:
          self.response.write('You are not admin')
          return

      self.DoGet()

  def post(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      if user.email() not in ADMINS:
          self.response.write('You are not admin')
          return

      self.DoPost()

  def DoGet(self):
    # Override this function
    return

  def DoPost(self):
    # Override this function
    return

class GuestManager(AdminPage):
  def DoGet(self):
    query = Invitee.query()
    invitees = query.fetch()
    
    template_values = {
        'invitees': invitees,
    }

    template = JINJA_ENVIRONMENT.get_template('add.html')
    self.response.write(template.render(template_values))

  def DoPost(self):
    first = self.request.get("first")
    last = self.request.get("last")
    email = self.request.get("email")
    myuuid = str(uuid.uuid4())
      
    print 'UUID', myuuid
    invitee = Invitee(first_name=first,
                      last_name=last,
                      email=email,
                      rsvp="0",
                      uuid=myuuid)
    query = Invitee.query(Invitee.email == invitee.email)
    invitees = query.fetch()
  
    if len(invitees):
      print 'EXISTS ALREADY'
    else:
      invitee.put()
    self.redirect('/admin')

class Emailer(AdminPage):
  def DoGet(self):
    template_values = {}
    template = JINJA_ENVIRONMENT.get_template('email.html')
    self.response.write(template.render(template_values))

  def DoPost(self):
    email_to_fetch = self.request.get("email")

    invitees = None
    if email_to_fetch == "all":
      query = Invitee.query()
      invitees = query.fetch()
    else:
      query = Invitee.query(Invitee.email == email_to_fetch)
      invitees = query.fetch()
 
    for invitee in invitees:
      if not mail.is_email_valid(invitee.email):
        self.response.write('Invalid email: ' + invitee.email)
        return
      else:
        sender_address = ('Ranjitha Gurunath Kulkarni <ranjithagk@gmail.com>')
        receiver_address = invitee.email
        subject = "Wedding invitation"
        content = CONTENT % (invitee.first_name, invitee.last_name, invitee.uuid) 
        mail.send_mail(sender_address, receiver_address, subject, content)
        self.response.write("Success : " + invitee.email)
    
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin', GuestManager),
    ('/rsvp', RSVP),
    ('/email', Emailer),
], debug=True)
