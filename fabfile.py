__author__ = 'aub3'
from fabric.api import env,local,run,sudo,put,cd,lcd
from hosts import hosts
from config import key_filename, OUTPUT_S3_BUCKET, JOB_QUEUE

import boto.ec2,time,os

CONN = boto.ec2.connect_to_region("us-east-1")

env.hosts = hosts
env.user = 'ec2-user'
env.key_filename = key_filename


def setup_queue():
    """
    Sets up the queue, creates bucket
    """
    import logging
    from boto.s3.connection import S3Connection
    from cclib.commoncrawl13 import CommonCrawl13
    from cclib.queue import FileQueue
    logging.basicConfig(filename='logs/setup_queue.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    S3 = S3Connection()
    logging.info("Creating bucket "+OUTPUT_S3_BUCKET)
    S3.create_bucket(OUTPUT_S3_BUCKET)
    logging.info("bucket created")
    crawl = CommonCrawl13()
    file_list = crawl.text # Text files
    text_queue = FileQueue(JOB_QUEUE,file_list)
    logging.debug("Adding "+str(len(file_list))+" files to queue "+JOB_QUEUE)
    text_queue.add_files()
    logging.debug("Finished adding files")
    print "Finished adding files"


def setup_instance():
    """
    updates, installs necessary packages on an EC2 instance
    """
    sudo('yum update -y')
    # install GCC, Make, Setuptools etc.
    sudo('yum install -y gcc-c++')
    sudo('yum install -y openssl-devel')
    sudo('yum install -y make')
    sudo('yum install -y python-devel')
    sudo('yum install -y python-setuptools')
    sudo('easy_install flask') # not used


def list_ec2_instances():
    """
    Lists current EC2 instances
    """
    reservations = CONN.get_all_reservations()
    for reservation in reservations:
        print reservation.id,reservation.region
        instances = reservation.instances
        for instance in instances:
            print "Instance ype",instance.instance_type
            print "Image ID",instance.image_id
            print "IP address",instance.ip_address
            print "Public dns",instance.public_dns_name
            print "\n"



def test_update_lib():
    """
    Update & install common crawl library locally
    """
    with lcd('libs'):
        try:
            local('rm -r build')
        except:
            pass
        local('python setup.py install')
        local('rm -r build')

def setup_job():
    """
    Sets up the queue
    """
    local('python setup_queue.py')

def run_workers(N=32,IAM=False,home_dir='/home/ec2-user'):
    """
    1. Uploads boto configuration and applications to EC2 instance
    2. Installs the common crawl library
    3. Starts N process running AWS/worker.py
    """
    local('mv config.py AWS/config.py')
    try:
        sudo('rm -rf '+home_dir+'/*')
    except:
        pass
    put('AWS','~')
    put('libs','~')
    with cd('AWS'):
        try:
            run('rm -r logs')
            run('mkdir logs')
        except:
            pass
    if not IAM: # not required if the remote machine uses IAM roles (preferred)
        put('/etc/boto.cfg','~')
    sudo('mv boto.cfg /etc/boto.cfg')
    with cd(home_dir+'/libs'): # using ~ causes an error with sudo since ~ turns into /root/
        sudo('python setup.py install')
    sudo('rm -rf '+home_dir+'/libs')
    with cd(home_dir+'/AWS'):
        for _ in range(N):
            run('screen -d -m python worker.py; sleep 1')


def Update_GAE():
    """
    Updates and uploads Google App Engine   (Optional)
    """
    pass