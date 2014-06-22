#!/usr/bin/env python
import os,logging,json,jinja2,config,filequeue,spotinstance
from cclib import commoncrawl
from flask import Flask,jsonify,request,render_template,url_for

logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'server/templates/')))
template_directory = os.path.join(os.path.dirname(__file__), 'server/templates/');

CRAWLS = {crawl_id:commoncrawl.CommonCrawl(crawl_id) for crawl_id in commoncrawl.CommonCrawl.crawl_id_list}

app = Flask(__name__,template_folder=template_directory,static_folder="server/static")
app.debug = True


@app.route('/crawl/<crawl_id>/<file_type>')
def crawl_details(crawl_id,file_type):
    return render_template('home.html',files=CRAWLS[crawl_id].get_files(file_type))

@app.route('/')
def home():
    json_data = {
        "config": {
            "key_filename":config.key_filename,
            "IAM_ROLE":config.IAM_ROLE,
            "IAM_PROFILE":config.IAM_PROFILE,
            "IAM_POLICY_NAME":config.IAM_POLICY_NAME,
            "IAM_POLICY":config.IAM_POLICY,
            "price":config.price,
            "instance_type":config.instance_type,
            "image_id":config.image_id,
            "key_name":config.key_name,
            "NUM_WORKERS":config.NUM_WORKERS,
            "VISIBILITY_TIMEOUT":config.VISIBILITY_TIMEOUT,
            "EC2_Tag":config.EC2_Tag,
            "JOB_QUEUE":config.JOB_QUEUE,
            "OUTPUT_S3_BUCKET":config.OUTPUT_S3_BUCKET,
            "CODE_BUCKET":config.CODE_BUCKET,
            "CODE_KEY":config.CODE_KEY,
            "FILE_TYPE":config.FILE_TYPE,
            "CRAWL_ID":config.CRAWL_ID,
            "SPOT_REQUEST_VALID":config.SPOT_REQUEST_VALID,
            "MAX_TIME_MINS":config.MAX_TIME_MINS,
            "USER_DATA":config.USER_DATA
        },
    }
    json_data["crawl"] = {crawl_id: {file_type:CRAWLS[crawl_id].get_file_list(file_type) for file_type in commoncrawl.CommonCrawl.file_types} for crawl_id in CRAWLS}
    return render_template('home.html',config=config,crawls=CRAWLS,json_data=json.dumps(json_data))

#key.get_contents_as_string(headers={'Range' : 'bytes=0-9'})

if __name__ == '__main__':
    app.run(port=8087)

