__author__ = 'aub3'
from fabric.api import env,local,run,sudo,put,cd,lcd
from config import *
from spotinstance import *
import filequeue
import logging
logging.basicConfig(filename='fab.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


env.hosts = [line.strip() for line in file("hosts").readlines()]
env.user = 'ec2-user'
env.key_filename = key_filename

def setup_iam():
    """
    Sets up IAM policy, roles and instance profile
    """
    from boto.iam.connection import IAMConnection
    IAM = IAMConnection()
    profile = IAM.create_instance_profile(IAM_PROFILE)
    role = IAM.create_role(IAM_ROLE)
    IAM.add_role_to_instance_profile(IAM_PROFILE, IAM_ROLE)
    IAM.put_role_policy(IAM_ROLE, IAM_POLICY_NAME, IAM_POLICY)

def setup_job():
    """
    Sets up the queue adds all files (text or warc or wat or wet), creates bucket to store output
    """
    #IAM
    try:
        setup_iam()
    except:
        print "Error while setting up IAM PROFILE, most likely due to existing profile"
        logging.exception("Error while setting up IAM PROFILE, most likely due to existing profile")
        pass
    #S3 bucket
    from boto.s3.connection import S3Connection
    from cclib.commoncrawl import CommonCrawl
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    import filequeue
    S3 = S3Connection()
    logging.info("Creating bucket "+OUTPUT_S3_BUCKET)
    S3.create_bucket(OUTPUT_S3_BUCKET)
    logging.info("bucket created")
    # SQS
    crawl = CommonCrawl(CRAWL_ID)
    file_list = crawl.get_file_list(FILE_TYPE) # Text files
    file_queue = filequeue.FileQueue(JOB_QUEUE,VISIBILITY_TIMEOUT,file_list)
    logging.debug("Adding "+str(len(file_list))+" "+FILE_TYPE+" files to queue "+JOB_QUEUE)
    file_queue.add_files()
    logging.debug("Finished adding files")
    print "Finished adding files"


def setup_instance(home_dir='/home/ec2-user'):
    """
    Updates, installs necessary packages on an EC2 instance.
    Upload library, boto configuration, worker code.
    Make sure that any changes made here are also reflected in USER_DATA script in config
    """
    sudo('yum update -y')
    sudo('yum install -y gcc-c++')
    sudo('yum install -y openssl-devel')
    sudo('yum install -y make')
    sudo('yum install -y python-devel')
    sudo('yum install -y python-setuptools')
    sudo('easy_install flask')
    try:
        sudo('rm -rf '+home_dir+'/*')
    except:
        pass
    put('libs','~')
    put('config.py','~/config.py')
    put('queue.py','~/queue.py')
    put('worker.py','~/worker.py')
    with cd(home_dir+'/libs'): # using ~ causes an error with sudo since ~ turns into /root/
        sudo('python setup.py install')
    sudo('rm -rf '+home_dir+'/libs')


def push_code():
    """
    Bundles worker code, library & configuration in to a zipped files and store it on S3.
    Finally updates
    """
    from boto.s3.connection import S3Connection
    from boto.s3 import key
    try:
        local("rm -r code")
    except:
        pass
    local("mkdir code")
    local("cp config.py code/config.py")
    local("cp queue.py code/queue.py")
    local("cp -r libs code/libs")
    local("cp worker.py code/worker.py")
    local("tar -zcvf code.tar.gz code")
    S3 = S3Connection()
    code_bucket = S3.create_bucket(CODE_BUCKET)
    code = key.Key(code_bucket)
    code.key = CODE_KEY
    code.set_contents_from_filename("code.tar.gz")
    local("rm code.tar.gz")
    local("rm -r code")
    logging.info("code pushed to bucket "+CODE_BUCKET+" key "+CODE_KEY)


def ls_instances():
    """
    Lists current EC2 instances with current Job tag, and stores their public_dns_name to hosts.
    """
    with open('hosts','w') as fh:
        for instance in SpotInstance.get_spot_instances(EC2_Tag):
            print instance.status()
            if instance.public_dns_name:
                fh.write(instance.public_dns_name+'\n')
    print "Information about current spot instance has been added to hosts.py"


def request_spot_instance():
    """
    Lists current EC2 instances
    """
    spot = SpotInstance(EC2_Tag)
    spot.request_instance(price,instance_type,image_id,key_name,USER_DATA,IAM_PROFILE)


def terminate_instances():
    """
    Terminates all spot instances, clear hosts file
    """
    for s in SpotInstance.get_spot_instances(EC2_Tag):
        print "terminating", s.status()
        if s.instance_object and s.instance_object.state_code != 48:
            s.terminate()
        print "terminated"
    with file("hosts","w") as f:
        f.write("")

def update_lib():
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

def run_workers(N=NUM_WORKERS,IAM=False,home_dir='/home/ec2-user'):
    """
    Starts N process running AWS/worker.py
    """
    with cd(home_dir):
        for _ in range(N):
            run('screen -d -m python worker.py; sleep 1')


def rm_bucket(bucket_name):
    """
    Deletes the specified bucket
    bucket_name : str
    """
    from boto.s3.connection import S3Connection
    S3 = S3Connection()
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    bucket = S3.get_bucket(bucket_name)
    bucketListResultSet = bucket.list()
    result = bucket.delete_keys([key.name for key in bucketListResultSet])
    S3.delete_bucket(bucket_name)

def ls_bucket(bucket_name=OUTPUT_S3_BUCKET):
    """
    Selects one key from the bucket store locally and runs less command
    """
    from boto.s3.connection import S3Connection
    from boto.s3 import key
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    import random
    S3 = S3Connection()
    bucket = S3.get_bucket(bucket_name)
    keys = [example_key for example_key in bucket.list()]
    if keys:
        example = key.Key(bucket)
        example.key = random.sample(keys,1)[0]
        example.get_contents_to_filename("temp.json")
    print "Number of keys in the output bucket ",len(keys)
    print "a randomly selected key is written to temp.json"

def kill_python_processes():
    """
    Kills all python processes on remote hosts
    """
    sudo("killall python")

def test_worker():
    """
    Runs worker.py in test mode after updating the local version of the common crawl library
    """
    update_lib()
    try:
        local("rm worker.log")
    except:
        pass
    local("python worker.py test")