__author__ = 'aub3'
import platform,os


DEBUG = True

if platform.system() == 'Darwin': # local environment detected by
    STORE_PATH = '/Users/aub3/Data/trawl/' # used for local testing
    try:
        os.mkdir(STORE_PATH)
    except:
        pass
    LOCAL = True
else:
    STORE_PATH = '/dev/shm/' # instance store (SSD)
    LOCAL = False


def chunk_list(inlist,size=10):
    " Modified from the remote_copy function from Common Crawl index package"
    n = len(inlist) / float(size)
    for i in xrange(int(n)):
        yield inlist[int(round(size * i)): int(round(size * (i + 1)))]

try:
    from keys import AWS_KEY,AWS_SECRET
except:
        print "Keys not set, please enter AWS key and secret to continue"
        import os
        fh = open('keys.py','w')
        key = raw_input('enter AWS key')
        secret = raw_input('enter AWS Secret')
        fh.write("AWS_KEY = '%s'; AWS_SECRET = '%s'"%(key,secret))
        fh.close()
        print "information stored in keys.py"
        print "testing if keys can be imported"
        try:
            from keys import AWS_KEY,AWS_SECRET
        except:
            print "failed to import keys.py"
            raise ImportError

