#!/usr/bin/env python
__author__ = 'aub3'
import pickle,gzip,os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from StringIO import StringIO


class CommonCrawl13(object):

    def __init__(self,filename=os.path.dirname(__file__)+'/data/crawl_index.gz',aws_key=None,aws_secret=None):
        """
        You can either provide a pickle with list of files or iterate over the segments.
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
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.CONN = None
        self.bucket = None

    def download(self):
        """
        Downloads list of files iterating through all segments
        """
        prefix = 'common-crawl/crawl-data/CC-MAIN-2013-20/segments/'
        if self.aws_key and self.aws_secret:
            self.CONN = S3Connection(self.aws_key,self.aws_secret)
        else:
            self.CONN = S3Connection()
        self.bucket = self.CONN.get_bucket('aws-publicdatasets',validate=False)
        self.files = [key.name.encode('utf-8') for key in self.bucket.list(prefix)]

    def store(self,filename=os.path.dirname(__file__)+'/data/crawl_index.gz'):
        """
        Stores list of files in a local pickle file.
        """
        fh = gzip.open(filename,'w')
        pickle.dump(self.files,fh)
        fh.close()

    def get_file(self,key,compressed_string=False):
        """
        Downloads file from AWS S3 and returns a GzipFile object.
        Optionally if compressed_string == True then it can return the compressed data as a string.
        """
        if not self.CONN:
            if self.aws_key and self.aws_secret:
                self.CONN = S3Connection(self.aws_key,self.aws_secret)
            else:
                self.CONN = S3Connection()
        if not self.bucket:
            self.bucket = self.CONN.get_bucket('aws-publicdatasets',validate=False)
        item = Key(self.bucket)
        item.key = key
        if compressed_string:
            return item.get_contents_as_string()
        else:
            return gzip.GzipFile(fileobj=StringIO(item.get_contents_as_string()))



if __name__ == '__main__':
    # Few simple tests
    crawl = CommonCrawl13()
    print "wat",len(crawl.wat),crawl.wat[:10]
    print "wet",len(crawl.wet),crawl.wet[:10]
    print "warc",len(crawl.warc),crawl.warc[:10]
    print "text",len(crawl.text),crawl.text[:10]
    infile = crawl.get_file(crawl.wat[26741])
    count  = 0
    for line in infile:
        count += 1
        if count>(100000-5000) and line[0] == '{':
            print line
        if count>100000:
            break
    #crawl.store()
