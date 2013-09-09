Trawl Search
------------
 A simple app for mining common crawl data

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
Create keys.py

    # Put following file in both AppEngine and AWS folders
    AWS_KEY = '<your AWS key>'
    AWS_SECRET = '<your AWS secret>'
    PASSCODE = 'Any short random passcode. make sure it is same in both files'

Setting up indexers on AWS-EC2

1.  Add keys.py to AWS folder
2.  Launch indexer.py in AWS folder
3.  You should launch multiple processes depending on the type of EC-2 machines

Setting up public interface on Google App Engine

1.  Update app.yaml with your app identifier
2.  Add keys.py to AppEngine folder
3.  Upload the code to app engine
4.  Using the Google account which is owns the app you can access the admin page to configure and monitor progress




References
-------
[Library used for reading sequencefiles in python](https://github.com/matteobertozzi/Hadoop/tree/master/python-hadoop)

