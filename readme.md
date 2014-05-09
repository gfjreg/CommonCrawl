Common Crawl Dev
------------
A simple app for mining common crawl data

Author
-------
Akshay Uday Bhat (www.akshaybhat.com)

Description:
---------
This repo contains code for accessing commoncrawl 2013 crawl & code for launching spot instances for analyzing the crawl data.
The code follows most of the best practices to ensure :

1. An SQS queue is used to track progress of the job.
2. Output is stored in an S3 Bucket with



Dependancies
--------------
Boto
Fabric

Documentation
------------
libs/setup.py
libs/cclib/commoncrawl13.py
libs/cclib/queue.py

config.py
fabfile.py
spotinstance.py
worker.py

Tasks
------------








AWS credentials
----------------
AWS credentials should be stored in /etc/boto.cfg, the credentials are not transferred
