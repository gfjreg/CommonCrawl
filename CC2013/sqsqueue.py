__author__ = 'aub3'
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from settings import AWS_KEY,AWS_SECRET

class FileQueue(object):
    """
    A queue of files stored on SQS.
    """
    SQS = SQSConnection(AWS_KEY,AWS_SECRET)

    def __init__(self,name,files):
        """
        Requires list of files and queue name
        """
        self.name = name
        self.files = files
        self.queue = FileQueue.SQS.create_queue(self.name)

    def add_files(self,count=None):
        """
        if count is none then add all files to queue, otherwise add count files to queue
        """
        if count is None:
            count = len(self.files)
        while count:
            self.queue.write(Message(body=self.files.pop()))
            count -= 1

    def clear(self):
        """
        Clears the queue. This is a costly operation.
        """



if __name__ == '__main__':
    import commoncrawl13
    crawl = commoncrawl13.CommonCrawl13('data/crawl_index.gz')
    wat_queue = FileQueue('aksay_test_queue',crawl.wat)
    wat_queue.add_files(5)


