import cgi
from  google.appengine.api import users
import webapp2

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/sign" method="post">
      <div><textarea name="content" rows="3" cols="60" ></textarea></div>
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>
  </body>
</html>
"""

  

class MainPage(webapp2.RequestHandler):
  def GetUserOrRedirect(self, uri):
    user = users.get_current_user()
    if user:
      return user
    else:
      self.redirect(users.create_login_url(uri))

  def get(self):
    user = self.GetUserOrRedirect(self.request.uri)
    if user:
      self.response.write(MAIN_PAGE_HTML)

  def post(self):
    user = self.GetUserOrRedirect(self.request.uri)
    self.response.write("<html/><body> Hi %s you wrote: <pre>" % user.nickname())
    self.response.write(cgi.escape(self.request.get("content")))
    self.response.write("</pre></body></html>")

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', MainPage),
], debug=True)
