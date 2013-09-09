Trawl Search (A simple app for mining common crawl data)
---------------------------------------------------------


Author
-------
Akshay Uday Bhat (www.akshaybhat.com)


Architecture
-------------
The architecture of Trawl Search is composed of

Public interface (Google App Engine)
http://www.datamininghobby.com

AWS-EC2 Indexers:
    For downloading data from AWS-S3 and processing data

AWS-SQS:
    For managing common crawl files across multiple machines

Setting up
-----------

AWS:
1. Setting up indexer.py

2. add keys.py to AWS folder

    AWS/keys.py
    AWS_KEY = '<your AWS key>'
    AWS_SECRET = '<your AWS secret>'
    PASSCODE = 'Any short random passcode. make sure it is same in both files'


App Engine:

1. update app.yaml with your app identifier

2. add keys.py to AppEngine folder

    AppEngine/keys.py
    AWS_KEY = '<your AWS key>'
    AWS_SECRET = '<your AWS secret>'
    PASSCODE = 'Any short random passcode. make sure it is same in both files'


References
-------
[Library used for reading sequencefiles in python](https://github.com/matteobertozzi/Hadoop/tree/master/python-hadoop)

