#!/usr/bin/env python
from base import *
from home import *



if LOCAL:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.INFO)

Routes = home_routes

app = webapp2.WSGIApplication(Routes,debug = LOCAL)


