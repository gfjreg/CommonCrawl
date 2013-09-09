__author__ = 'aub3'
import random
from google.appengine.ext import ndb
NUM_SHARDS = 4


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
    """Increment the value for a given sharded counter."""
    shard_string_index = str(random.randint(0, NUM_SHARDS - 1))
    counter = IndexCounter.get_by_id(shard_string_index)
    if counter is None:
        counter = IndexCounter(id=shard_string_index)
    counter.count += 1
    counter.put()



class FileCounter(ndb.Model):
    """Shards for the counter"""
    count = ndb.IntegerProperty(default=0)

def get_file_count():
    total = 0
    for counter in FileCounter.query():
        total += counter.count
    return total



@ndb.transactional
def increment_file_count(num):
    """Increment the value for a given sharded counter."""
    shard_string_index = str(random.randint(0, NUM_SHARDS - 1))
    counter = FileCounter.get_by_id(shard_string_index)
    if counter is None:
        counter = FileCounter(id=shard_string_index)
    counter.count += num
    counter.put()