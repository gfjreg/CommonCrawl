__author__ = 'aub3'
import os,time


if __name__ == '__main__':
    for _ in range(50):
        os.system('python example_metadata.py &')
        time.sleep(3)
        print "process launched"