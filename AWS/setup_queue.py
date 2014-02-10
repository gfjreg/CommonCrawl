__author__ = 'aub3'
from cclib.commoncrawl13 import CommonCrawl13
from cclib.queue import FileQueue





if __name__ == '__main__':
    crawl = CommonCrawl13()
    wat_queue = FileQueue('akshay_wat_analysis',crawl.wat)
    wat_queue.add_files(5)
    for m in wat_queue:
        print m.get_body()
        wat_queue.delete_message(m)
