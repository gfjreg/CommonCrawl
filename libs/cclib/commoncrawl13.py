#!/usr/bin/env python
__author__ = 'aub3'
import pickle,gzip,os
from boto.s3.connection import S3Connection
from keys import AWS_KEY,AWS_SECRET

class CommonCrawl13(object):
    def __init__(self,filename=os.path.dirname(__file__)+'/data/crawl_index.gz'):
        """
        if a pickled file is provided then it is loaded.
        Otherwise the list of keys is downloaded and stored in
        """
        if filename:
            fh = gzip.open(filename)
            self.files = pickle.load(fh)
            fh.close()
        else:
            self.download()
        self.warc = [key for key in self.files if '/warc/' in key]
        self.text = [key for key in self.files if '/text/' in key]
        self.wet = [key for key in self.files if '/wet/' in key]
        self.wat = [key for key in self.files if '/wat/' in key]

    def download(self):
        """
        Downloads list of files
        """
        prefix = 'common-crawl/crawl-data/CC-MAIN-2013-20/segments/'
        CONN = S3Connection(AWS_KEY,AWS_SECRET)
        bucketname = 'aws-publicdatasets'
        bucket = CONN.get_bucket(bucketname)
        self.files = [key.name.encode('utf-8') for key in bucket.list(prefix)]

    def store(self,filename=os.path.dirname(__file__)+'/data/crawl_index.gz'):
        """
        Stores list of files in a local pickle file.
        """
        fh = gzip.open(filename,'w')
        pickle.dump(self.files,fh)
        fh.close()

if __name__ == '__main__':
    crawl = CommonCrawl13()
    print "wat",len(crawl.wat),crawl.wat[:10]
    print "wet",len(crawl.wet),crawl.wet[:10]
    print "warc",len(crawl.warc),crawl.warc[:10]
    print "text",len(crawl.text),crawl.text[:10]
    #crawl.store()