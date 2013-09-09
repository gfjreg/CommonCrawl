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

References
-------
[Library used for reading sequencefiles in python](https://github.com/matteobertozzi/Hadoop/tree/master/python-hadoop)

