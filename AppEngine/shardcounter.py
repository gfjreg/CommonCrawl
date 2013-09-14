__author__ = 'aub3'
import random
from google.appengine.ext import ndb
NUM_SHARDS = 1


class IndexCounter(ndb.Model):
    """Shards for the counter"""
    count = ndb.IntegerProperty(default=0)


def get_indexer_count():
    total = 0
    for counter in IndexCounter.query():
        total += counter.count
    return total



@ndb.transactional
def increment_indexer_count():
    counter = IndexCounter.get_by_id("0")
    if counter is None:
        counter = IndexCounter(id="0")
    counter.count += 1
    counter.put()
    return counter.count

