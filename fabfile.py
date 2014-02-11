__author__ = 'aub3'
from fabric.api import env,local,run,sudo,put,cd,lcd
from hosts import hosts
env.hosts = hosts
env.user = 'ec2-user'
env.key_filename = '/users/aub3/.ssh/cornellmacos.pem'

def setup_instance():
    """
    updates, installs necessary packages and node.js
    """
    sudo('yum update -y')
    # install GCC, Make, Setuptools etc.
    sudo('yum install -y gcc-c++')
    sudo('yum install -y openssl-devel')
    sudo('yum install -y make')
    sudo('yum install -y python-setuptools')
    # install node.js
    sudo('wget http://nodejs.org/dist/node-latest.tar.gz')
    sudo('tar -zxvf node-latest.tar.gz')
    sudo('rm -rf node-latest.tar.gz')
    with cd('node-*'):
        sudo('./configure --prefix=/usr')
        sudo('make')
        sudo('make install')


def test_update_lib():
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
    with lcd('AWS'):
        local('python example_setup.py')

def run_workers(N=2,IAM=False,home_dir='/home/ec2-user'):
    """
    0. Setup queue and create S3 bucket
    1. Uploads boto configuration and applications to EC2 instance
    2. Installs the common crawl library
    3. Starts N process running AWS/example_worker.py
    """
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
            run('screen -d -m python example_worker.py; sleep 1')



def setup_spot_instance():
    """
    Upload spot.sh and set it to run on startup.
    """
    put('spot.sh','')
    sudo('mv spot.sh /etc/rc.local')

def update_app_engine():
    """
    Update/Upload app engine
    """
    local("appcfg.py update GAE")

