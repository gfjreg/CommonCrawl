#!/usr/bin/env python
import os,logging,json,jinja2,config,filequeue,spotinstance
from cclib import commoncrawl
from flask import Flask,jsonify,request,render_template,url_for

logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'server/templates/')))
template_directory = os.path.join(os.path.dirname(__file__), 'server/templates/');

CRAWLS = {'crawl_id':commoncrawl.CommonCrawl(crawl_id) for crawl_id in commoncrawl.CommonCrawl.crawl_id_list}

app = Flask(__name__,template_folder=template_directory,static_folder="server/static")
app.debug = True


#@app.route('/<bucket>/<int:index>')
#def details(directory,code):
#    pass

@app.route('/')
def home():
    return render_template('home.html',config=config,crawls=CRAWLS)

if __name__ == '__main__':
    app.run(port=8087)

