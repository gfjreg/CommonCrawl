__author__ = 'aub3'
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

class FileQueue(object):
    """
    A queue of files stored on SQS.
    """
    SQS = SQSConnection()

    def __init__(self,name,files=None):
        """
        Requires list of files and queue name
        """
        if files == None:
            files = []
        self.name = name
        self.files = files
        self.queue = FileQueue.SQS.get_queue(name)
        if not self.queue:
            self.queue = FileQueue.SQS.create_queue(self.name)

    def add_files(self,count=None):
        """
        if count is none then add all files to queue, otherwise add count files to queue
        """
        message_buffer =[]
        if count is None:
            count = len(self.files)
        while count:
            count -= 1
            message_buffer.append(Message(body=self.files.pop()))
            if len(message_buffer) > 9:
                self.queue.write_batch(message_buffer)
                message_buffer = []
        if message_buffer: # write remaining
            self.queue.write_batch(message_buffer)

    def clear(self):
        """
        Clears the queue. This is a costly operation.
        """
        self.queue.clear()

    def __iter__(self):
        return self

    def next(self,visibility_timeout=None):
        """ iterate over the queue"""
        if self.queue:
            messages = self.queue.get_messages(1,visibility_timeout=visibility_timeout)
            if messages:
                for m in messages:
                    return m
        raise StopIteration

    def delete_message(self,m):
        self.queue.delete_message(m)

if __name__ == '__main__':
    import commoncrawl13
    crawl = commoncrawl13.CommonCrawl13()
    wat_queue = FileQueue('aksay_test_queue',crawl.wat)
    wat_queue.add_files(5)
    for m in wat_queue:
        print m.get_body()
        wat_queue.delete_message(m)
