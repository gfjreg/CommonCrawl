__author__ = 'aub3'
from base import *

class Home(BaseRequestHandler):
    def get(self):
        self.generate('home.html')

home_routes = [('/',Home),]
