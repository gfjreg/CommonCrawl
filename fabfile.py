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


def status():
    run('ls -l /home/ec2-user/')


def upload_ec2(IAM=False,home_dir='/home/ec2-user'):
    """
    Upload applications to EC2 instance and installs the library
    """
    try:
        sudo('rm -rf ~/*')
    except:
        pass
    put('AWS','~')
    put('libs','~')
    if not IAM: # not required if the remote machine uses IAM roles (preferred)
        put('/etc/boto.cfg','~')
    sudo('mv boto.cfg /etc/boto.cfg')
    with cd(home_dir+'/libs'): # using ~ causes an error with sudo since ~ turns into /root/
        sudo('python setup.py install')
    sudo('rm -rf '+home_dir+'/libs')


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

