# Setup Instruction for Deployer Ubuntu VM/Machine

-  Install Ubuntu v16.04.02(xenial-x86_64) VM (Memory: 4GB, 40GB HD, with access to VMM/Internet)

-  While installing Ubuntu OS, make sure to create an user with same uid as your Juniper user-id 

-  After installation login with juniper user-id to the CentOS v7.5 VM 

-  Run following commands to install pre-requites software packages to run the Contrail Install script 

```

sudo apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev sshpass rsync git jq
# sudo apt-get install -y sshpass rsync
sudo pip install --upgrade ansible markupsafe httplib2

sudo pip install --upgrade Jinja2 netaddr jmespath jxmlease enum34 unique requests markupsafe httplib2 pika selenium passlib
sudo ansible-galaxy install Juniper.junos (Install Juniper.junos Ansible roles)

python --version
pip --version
ansible --version


```

