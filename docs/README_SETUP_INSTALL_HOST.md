# Ansible Scripts Junos Config Generation, Deployment and Validation for Junso Devices

## Configure Install Host 

You run the downloaded Ansible scripts on the Install Host (or control host). 

### Configure Mac OSX based Install Host 

- Install `sshpass` 
- Install python 2.7.10+
- Install pip 10.0.1 and related python modules
    - Use the [requirements.txt](../requirements.txt) file for the module info
    ```
    pip install pip
    pip install --upgrade pika Jinja2 netaddr jmespath jxmlease selenium passlib python-openstackclient python-heatclient openstacksdk
    ansible-galaxy install Juniper.junos
    ```


### Configure Ubuntu based Install Host 
You would need machine (this could be your laptop or another VM) that would be used as install or control host for Ansible scripts.

If you are using Ubuntu-based install host, you can following the instruction below to setup the VM:

- Follow instruction here to install Ansible : http://docs.ansible.com/ansible/latest/intro_installation.html#latest-releases-via-apt-ubuntu

```

sudo apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev sshpass rsync git 
sudo apt-get install -y sshpass rsync
sudo pip install ansible markupsafe httplib2

sudo pip install --upgrade Jinja2 netaddr jmespath jxmlease enum34 unique requests markupsafe httplib2 pika selenium passlib
ansible-galaxy install Juniper.junos (Install Juniper.junos Ansible roles)
pip install --no-cache jsnapy

python --version
pip --version
ansible --version

```
For detailed instuction on setting up deployer host on Linux VM:
- For Ubuntu v16.04.02 : [ubuntu_setup_steps.md ](ubuntu_setup_steps.md) 
- For CentOS v7.5      : [centos_setup_steps.md ](centos_setup_steps.md) 


### Run ssh-keygen to install SSH key for password-less access:
- `ssh-keygen` 

Ansible scripts are tested with :

- Python 2.7.10
- pip 19.0.1 
- Ansible 2.6.2
- Jinja2 2.10

