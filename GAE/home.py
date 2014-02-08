__author__ = 'aub3'
from base import *
from models import *

class Home(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        self.generate('home.html',get_status())

home_routes = [('/',Home),]
