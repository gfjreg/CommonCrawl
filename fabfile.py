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



def status():
    run('ls -l /home/ec2-user/')


def upload():
    """
    Upload applications and library to EC2 instance
    """
    run('rm -r /home/ec2-user/AWS')
    put('AWS','/home/ec2-user/')
    run('rm -r /home/ec2-user/libs')
    put('libs','/home/ec2-user/')

def test_local():
    with lcd('libs/cclib'):
        local('chmod a+x commoncrawl13.py')
        local('./commoncrawl13.py')

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