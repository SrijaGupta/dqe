1. git clone template fragment repository 

2. git clone Ansible playbook repository 

3. Edit `CONFIG_FRAGMENT_TEMPLATE_REPO_DIR` env-var in `setenv_ansible.sh` file

4. Source `setenv_ansible.sh` and valiadate the `CONFIG_FRAGMENT_TEMPLATE_BASE_DIR` exists


6. Run the script 
    - `` export CONFIG_FRAGMENT_TEMPLATE_REPO_DIR=`pwd` ``
    - ` . setenv_ansible.sh `
    - ` export DEVICE_GOUP_NAME=ACX2200 `
    - Edit `run_netdev_junos_config_deploy_generic.sh` to configure the inventory variable for ansible script 
    - `run_netdev_junos_config_deploy_generic.sh` to deplpoy config  to ACX2200 devices
    - or 
    - Edit `run_netdev_junos_config_deploy_acx2200.sh` to configure the inventory variable for ansible script 
    - `run_netdev_junos_config_deploy_acx2200.sh` to deplpoy config  to ACX2200 devices




