__author__ = 'aub3'
# Put AWS credentials in /etc/boto.cfg for use on local machine
key_filename = '/users/aub3/.ssh/cornellmacos.pem' # please replace this with path to your pem

# following IAM role is used when launching instance
IAM_ROLE = "ccSpot_role"
IAM_PROFILE = "ccSpot_profile"
IAM_POLICY_NAME = "ccSpt_policy"
IAM_POLICY ="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1399521628000",
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Sid": "Stmt1399521640000",
      "Effect": "Allow",
      "Action": [
        "sqs:*"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}"""


##########
#
# Instance Configuration
#
#########
price = 0.30 # 30 cents per hour slightly above the reserve price of the r3.8xlarge instance on the spot market
instance_type = 'r3.8xlarge'
image_id = 'ami-978d91fe' # default AMI for Amazon Linux HVM
key_name = 'cornellmacos' # replace with name of your configured key-pair
NUM_WORKERS = 40 # Number of worker processes per machine
VISIBILITY_TIMEOUT = 500 #TODO Seconds during which a worker process has time to process the message

##########
#
# Job Configuration
#
#########
EC2_Tag = "cc_wat_13_2"
JOB_QUEUE = 'wat_stats_2013_2' # SQS queue name
OUTPUT_S3_BUCKET = 'wat_stats_2013_2' # S3 bucket
CODE_BUCKET = "akshay_code" # bucket used to store code & configuration make sure this is different from output bucket
CODE_KEY = "wat_stats_2013_2" # key for storing code which will be downloaded by user-data script
FILE_TYPE = "wat" # Type of files you wish to process choose from {"wat","wet","text","warc"}
CRAWL_ID = "2013_2" # 2nd crawl in 2013




USER_DATA= """#!/usr/bin/env python
from boto.s3.connection import S3Connection
from boto.s3 import key
import os

os.system('yum update -y')
# install GCC, Make, Setuptools etc.
os.system('yum install -y gcc-c++')
os.system('yum install -y openssl-devel')
os.system('yum install -y make')
os.system('yum install -y python-devel')
os.system('yum install -y python-setuptools')
os.system('easy_install flask')

S3 = S3Connection()
code_bucket = S3.get_bucket("<CODE_BUCKET>") # Bucket where code is stored
code = key.Key(code_bucket)
code.key = "<CODE_KEY>" # Key for the code
code.get_contents_to_filename("/root/code.tar.gz")
os.system('cd /root/;tar -xzf code.tar.gz')
os.system('cd /root/code/libs;python setup.py install')
for worker in range(<NUM_WORKERS>):
    os.system('cd /root/;screen -d -m python code/worker.py; sleep 1')
""".replace("<CODE_BUCKET>",CODE_BUCKET).replace("<CODE_KEY>",CODE_KEY).replace("<NUM_WORKERS>",str(NUM_WORKERS))

