__author__ = 'aub3'
from commoncrawl13 import CommonCrawl13
from sqsqueue import FileQueue





if __name__ == '__main__':
    # compare with aws s3 mv s3://aws-publicdatasets/common-crawl/blekko/raw/blekko-extracturls-20130324.gz blekkourls
    
    crawl = CommonCrawl13('data/crawl_index.gz')
    wat_files = FileQueue('wat_quick_analysis',crawl.wat)