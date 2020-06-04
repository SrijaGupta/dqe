# Setup Instruction for Deployer CentOS VM/Machine

-  Install CentOSv7.5 (x86_64-Minimal-1804) VM (Memory: 4GB, 40GB HD, with access to VMM/Internet)

-  Run following commands to install pre-requites software packages to run the Contrail Install script 

```
sudo yum install -y epel-release
sudo yum install -y python-pip python-devel gcc gcc-c++ make openssl-devel libffi-devel rsync sshpass git net-tools jq
# sudo yum install -y rsync ntp git sshpass jq
# sudo yum install -y ansible 
pip install --upgrade setuptools
sudo pip install --upgrade  ansible markupsafe httplib2
sudo ansible --version

sudo pip install --upgrade Jinja2 netaddr jmespath jxmlease enum34 unique requests markupsafe httplib2 pika selenium passlib

sudo ansible-galaxy install Juniper.junos
pip install --no-cache jsnapy

```

