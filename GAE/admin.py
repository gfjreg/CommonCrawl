__author__ = 'aub3'
#!/usr/bin/env python
from base import *
from models import *


class Admin(BaseRequestHandler):
    def get(self):
        status = get_status()
        self.generate('admin.html',status)
        return

    def post(self):
        status = get_status()
        self.generate('admin.html',status)
        return

class UpdateQueue(BaseRequestHandler):
    def get(self):
        num = 25
        if add_files_queue(num,project_name=None):
            self.generate_json({'num':num})
        else:
            self.generate_json({'num':False})


class IndexerDelete(BaseRequestHandler):
    def get(self,pid):
        status = {}
        if delete_indexer(pid):
            status['status_success'] = 'Deleted indexer '+pid
        else:
            status['status_error'] = 'Could not find indexer '+pid
        status.update(get_status())
        self.generate('admin.html',status)
        return


if LOCAL:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.INFO)

Routes = [
    ('/',Admin),
    ('/Admin/',Admin),
    ('/Admin/Queue/',UpdateQueue),
    ('/Admin/Delete/(.*)',IndexerDelete),
    ]
app = webapp2.WSGIApplication(Routes,debug = LOCAL)


