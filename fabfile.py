__author__ = 'aub3'
from fabric.api import env,local,run,sudo,put,cd,lcd
from hosts import hosts
from config import key_filename, OUTPUT_S3_BUCKET, JOB_QUEUE,EC2_Tag
from spotinstance import *


env.hosts = hosts
env.user = 'ec2-user'
env.key_filename = key_filename


def setup_queue():
    """
    Sets up the queue adds all files (text or warc or wat or wet) , creates bucket to store output
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


def setup_instance(IAM=False,home_dir='/home/ec2-user'):
    """
    updates, installs necessary packages on an EC2 instance
    upload library, boto configuration, worker code
    """
    sudo('yum update -y')
    # install GCC, Make, Setuptools etc.
    sudo('yum install -y gcc-c++')
    sudo('yum install -y openssl-devel')
    sudo('yum install -y make')
    sudo('yum install -y python-devel')
    sudo('yum install -y python-setuptools')
    sudo('easy_install flask') # not used
    local('cp config.py AWS/config.py')
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
    local('rm AWS/config.py')


def list_spot_instances():
    """
    Lists current EC2 instances
    """
    for s in SpotInstance.get_spot_instances():
        print s.status()


def request_spot_instance():
    """
    Lists current EC2 instances
    """
    from config import price,instance_type,image_id,key_name
    spot = SpotInstance(EC2_Tag)
    spot.request_instance(price,instance_type,image_id,key_name)
    spot.check_allocation()
    spot.add_tag()
    with open('hosts.py','w') as fh:
        fh.write('hosts = '+repr([spot.public_dns_name])+'\ninstance_id="'+spot.instance_id+'"\n')
    print "Information about current spot instance written to hosts.py"
    print "Use 'fab setup_instance' and 'fab run_workers'"


def terminate_all_spot():
    """
    Terminates all spot instances
    """
    for s in SpotInstance.get_spot_instances():
        print "terminating"
        print s.status()
        s.terminate()
        print "terminated"

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

def run_workers(N=32,IAM=False,home_dir='/home/ec2-user'):
    """
    1. Uploads boto configuration and applications to EC2 instance
    2. Installs the common crawl library
    3. Starts N process running AWS/worker.py
    """
    with cd(home_dir+'/AWS'):
        for _ in range(N):
            run('screen -d -m python worker.py; sleep 1')


def create_ami():
    """
    Start an on-Demand EC2 instance, update code, set up start script, create an AMI, terminate the instance.
    """
    pass

def deploy_GAE():
    """
    Updates and uploads Google App Engine   (Optional)
    """
    pass

def start_local_server():
    """
    A Local flask server provides information about current job   (Optional)
    """
    pass