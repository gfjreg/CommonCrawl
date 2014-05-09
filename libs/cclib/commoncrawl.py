#!/usr/bin/env python
__author__ = 'aub3'
import pickle,gzip,os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from StringIO import StringIO


class CommonCrawl(object):
    file_types = ["wat","wet","warc","text"]
    crawl_prefix = {
        '2013_1':'common-crawl/crawl-data/CC-MAIN-2013-20/segments/',
        '2013_2':'common-crawl/crawl-data/CC-MAIN-2013-48/segments/',
        '2014_1':'common-crawl/crawl-data/CC-MAIN-2014-10/segments/',
    }
    crawl_id_list = ['2013_1','2013_2','2014_1']

    def __init__(self,crawl_id,aws_key=None,aws_secret=None,generate=False):
        """
        You can either provide a pickle with list of files or iterate over the segments.
        """
        self.crawl_id = crawl_id
        filename = os.path.dirname(__file__)+'/data/crawl_index_'+self.crawl_id+'.gz'
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        if generate:
            self.download()
        else:
            fh = gzip.open(filename)
            self.files = pickle.load(fh)
            fh.close()
        self.warc = [key for key in self.files if '/warc/' in key]
        self.text = [key for key in self.files if '/text/' in key]
        self.wet = [key for key in self.files if '/wet/' in key]
        self.wat = [key for key in self.files if '/wat/' in key]
        self.CONN = None
        self.bucket = None

    def get_file_list(self,file_type):
        if file_type == 'warc':
            return self.warc
        elif file_type == 'text':
            return self.text
        elif file_type == 'wet':
            return self.wet
        elif file_type == 'wat':
            return self.wat
        else:
            raise ValueError,"unknown file type"



    def download(self):
        """
        Downloads list of files iterating through all segments
        """
        if self.aws_key and self.aws_secret:
            self.CONN = S3Connection()
        else:
            self.CONN = S3Connection()
        self.bucket = self.CONN.get_bucket('aws-publicdatasets',validate=False)
        self.files = [key.name.encode('utf-8') for key in self.bucket.list(CommonCrawl.crawl_prefix[crawl_id])]

    def store(self):
        """
        Stores list of files in a local pickle file.
        """
        filename = os.path.dirname(__file__)+'/data/crawl_index_'+self.crawl_id+'.gz'
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
    # Generating data
    for crawl_id in CommonCrawl.crawl_id_list:
        print crawl_id
        crawl = CommonCrawl(crawl_id,generate=True)
        for file_type in CommonCrawl.file_types:
            print file_type,len(crawl.get_file_list(file_type)),crawl.get_file_list(file_type)[:10]
        print crawl_id,"finished"
        crawl.store()
