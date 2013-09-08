#!/usr/bin/env python
from base import *
from server_model import *
import urlparse



def set_current_server(location):
    server = Server_Location(key=Server_Key,location='http://'+location.replace('http://','').strip())
    server.put()

def get_current_server():
    return Server_Key.get().location


if LOCAL:
    set_current_server('http://ec2-54-211-164-158.compute-1.amazonaws.com/')
    EC2_Server = get_current_server()
else:
    try:
        EC2_Server = get_current_server()
    except:
        EC2_Server = ""
        pass

class Home(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        self.generate('home.html')

class Search(BaseRequestHandler):
    def get(self):
        EC2_Server = get_current_server()
        req = urllib2.Request(EC2_Server+'/Search/'+urllib2.quote(self.request.get('q')))
        req.add_header('Cache-Control', 'max-age=0')
        # user = users.get_current_user()
        data = json.loads(urllib2.urlopen(req).read())
        self.generate_json(data)

class Server(BaseRequestHandler):
    def get(self):
        try:
            EC2_Server = get_current_server()
            req = urllib2.Request(EC2_Server)
            req.add_header('Cache-Control', 'max-age=0')
            data = json.loads(urllib2.urlopen(req).read())
            self.generate_json(data)
        except:
            self.generate_json({"status":"offline"})
            pass


class Admin(BaseRequestHandler):
    def post(self):
        user = users.get_current_user()
        location = self.request.get('server')
        if user and users.is_current_user_admin():
            set_current_server(location)
            self.redirect("/")
        else:
            self.response.out.write(location)
            self.redirect(users.CreateLoginURL("/"))
            return




if LOCAL:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.INFO)
Routes = [
    ('/',Home),
    ('/Search/',Search),
    ('/Admin/',Admin),
    ('/Server/',Server),

    ]
app = webapp2.WSGIApplication(Routes,debug = LOCAL)


