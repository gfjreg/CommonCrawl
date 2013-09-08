#!/usr/bin/env sh
sudo yum update
sudo yum install python26-devel
sudo yum install libevent
sudo easy_install flask
sudo easy_install celery
wget http://nodejs.org/dist/v0.10.15/node-v0.10.15-linux-x64.tar.gz
tar xzf node-v0.10.15-linux-x64.tar.gz
rm node-v0.10.15-linux-x64.tar.gz
mv node-v0.10.15-linux-x64 /home/ec2-user/node
chmod a+x /home/ec2-user/node/bin/*
export PATH=$PATH:/home/ec2-user/node/bin
npm install requests
npm install express
npm install aws-sdk
wget http://iweb.dl.sourceforge.net/project/htop/htop/1.0.2/htop-1.0.2.tar.gz
tar xvfz htop-1.0.2.tar.gz
rm htop-1.0.2.tar.gz
cd htop-1.0.2
sudo yum install gcc glibc-devel
sudo yum install ncurses-static.x86_64
./configure
make
sudo make install
