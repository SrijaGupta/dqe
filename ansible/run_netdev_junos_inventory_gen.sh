#!/bin/bash
#
###################################################################################
#
# Copyright 2020 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is 
# located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the 
# parties, software distributed under the License is distri buted on an 
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
# or implied.
#
##################################################################################
#
# Author        : Subrata Mazumdar, Juniper Networks Professional Services
# Contact       : subratam@juniper.net
# Company       : Juniper Networks
#
#
# Description   : bash-script to run the ansible-playbook for backing up the NS nodes.
#                 It is a convinient way to customize the input parameters.
#
#

ANSIBLE_DEBUG="-vvvvv"
ANSIBLE_DEBUG="-v"
ANSIBLE_DEBUG="-vvv"
PLAYBOOK_ARGS=

ANSIBLE_PLAYBOOK=netdev_junos_inventory_gen.yml

# export NETDEV_JUNOS_DEVICE_UDATE_SSH_KNOWN_HOSTS=${NETDEV_JUNOS_DEVICE_UDATE_SSH_KNOWN_HOSTS:=}
export NETDEV_JUNOS_DEVICE_UDATE_SSH_KNOWN_HOSTS=${NETDEV_JUNOS_DEVICE_UDATE_SSH_KNOWN_HOSTS:=1}

# TODO: Mandatory Input params :NETDEV_DEVICE_IP_LIST and NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH 

# NETDEV_DEVICE_IP_LIST=${NETDEV_DEVICE_IP_LIST:=10.93.19.26}
# NETDEV_DEVICE_IP_LIST=${NETDEV_DEVICE_IP_LIST:=10.93.19.26,10.93.19.25,10.93.19.248,10.93.19.33}
NETDEV_DEVICE_IP_LIST=${NETDEV_DEVICE_IP_LIST:=}
NETDEV_DEVICE_IP_LIST=`echo $NETDEV_DEVICE_IP_LIST | sed -e 's/,/ /g'`
echo "NETDEV_DEVICE_IP_LIST: $NETDEV_DEVICE_IP_LIST"

NETDEV_DEVICE_CLI_USERNAME=${NETDEV_DEVICE_CLI_USERNAME:=root}
NETDEV_DEVICE_CLI_PASSWORD=${NETDEV_DEVICE_CLI_PASSWORD:=Embe1mpls}
NETDEV_DEVICE_LOGIN_USERNAME=${NETDEV_DEVICE_LOGIN_USERNAME:=${NETDEV_DEVICE_CLI_USERNAME}}

NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH=${NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH:=${HOME}/.ssh/id_rsa}
NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH=${NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH:=${HOME}/.ssh/id_rsa.pub}
# NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH=${NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH:=~/.ssh/id_rsa.pub}

# Default Input params
NETDEV_FABRIC_NAME=${FABRIC_NAME:=Fab1}
NETDEV_FABRIC_CONFIG_DIR=${FABRIC_CONFIG_DIR:=/var/tmp/${FABRIC_NAME}}
NETDEV_DEVICE_INVENTORY_DIR=${NETDEV_DEVICE_INVENTORY_DIR:=${NETDEV_FABRIC_CONFIG_DIR}/inventory}

NETDEV_DEVICE_INVENTORY_TEMPLATE_FILE_PATH=${NETDEV_DEVICE_INVENTORY_TEMPLATE_FILE_PATH:=/var/tmp/fabric_inventory_template.inv.j2}
NETDEV_DEVICE_INVENTORY_FILE_PATH=${NETDEV_DEVICE_INVENTORY_FILE_PATH:=/var/tmp/fabric_inventory_temp_$$.inv}


if [ "$NETDEV_DEVICE_IP_LIST" == "" ] ; then
    echo "ERROR: FABRIC_DEVICE_LIST_FILE_PATH env-var must be set "
    exit 1
fi

if [ ! -e $NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH ] ; then
    echo "ERROR: couln't find NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH file: $NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH"
    exit 1
fi
if [ ! -e $NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH ] ; then
    echo "ERROR: couln't find NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH file: $NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH"
    exit 1
fi

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

echo "NETDEV_DEVICE_INVENTORY_FILE_PATH: $NETDEV_DEVICE_INVENTORY_FILE_PATH"
if [ -e $NETDEV_DEVICE_INVENTORY_FILE_PATH ] ; then
    rm -f $NETDEV_DEVICE_INVENTORY_FILE_PATH 
fi

touch ${NETDEV_DEVICE_INVENTORY_FILE_PATH}
for NETDEV_DEVICE_IP in ${NETDEV_DEVICE_IP_LIST} ; do 
    DEVICE_NAME=${NETDEV_DEVICE_IP}
    DEVICE_IP=${NETDEV_DEVICE_IP}
    cat >> $NETDEV_DEVICE_INVENTORY_FILE_PATH << EOF
${DEVICE_NAME}  ansible_host=${DEVICE_IP} ansible_user=${xxx}  ansible_ssh_private_key_file=${NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH}  ansible_pass=${NETDEV_DEVICE_CLI_PASSWORD}
EOF
done
cat >> $NETDEV_DEVICE_INVENTORY_FILE_PATH << EOF
[cluster_fabric_devices]
EOF
for NETDEV_DEVICE_IP in ${NETDEV_DEVICE_IP_LIST} ; do 
    DEVICE_NAME=${NETDEV_DEVICE_IP}
cat >> $NETDEV_DEVICE_INVENTORY_FILE_PATH << EOF
${DEVICE_NAME}
EOF
done
cat >> $NETDEV_DEVICE_INVENTORY_FILE_PATH << EOF
[cluster_fabric_devices:vars]
login_shell=' '
EOF

echo "NETDEV_DEVICE_INVENTORY_FILE_PATH: $NETDEV_DEVICE_INVENTORY_FILE_PATH"
cat ${NETDEV_DEVICE_INVENTORY_FILE_PATH}

cat > $NETDEV_DEVICE_INVENTORY_TEMPLATE_FILE_PATH << EOF
{% for dev in  fab_devices                                             %}
{{ "%-20s" | format(dev.hostname) }} ansible_host={{ "%-15s" | format(dev.ip) }} ansible_user={{ "%-16s" | format(dev.ssh_user_name | default('root', true)) }}  ansible_ssh_private_key_file={{ "%-40s" | format(dev.ssh_private_key_file) }} #  ansible_ssh_pass={{ "%-16s" | format(dev.ssh_user_password) }}
{% endfor                                                              %}

[cluster_fabric_devices]
{% for dev in  fab_devices                                             %}
{{ dev.hostname}} model={{dev.model}} serial_number={{dev.serial_number}} version={{dev.version}} login_user_name={{ dev.ssh_user_name }}
{% endfor                                                              %}

[cluster_fabric_devices:vars]
login_shell=' '

EOF

# exit 0

# # export ANSIBLE_DEBUG=True 
# export ANSIBLE_LOG_PATH=`echo ${ANSIBLE_PLAYBOOK%%.*} | tr '[:lower:]' '[:upper:]' | sed -e 's/^/logs\//' | sed -e 's/$/.log/' `
# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${ANSIBLE_DEBUG} \
	-i ${NETDEV_DEVICE_INVENTORY_FILE_PATH} \
	-e "fabric_inventory_template_file_path=${NETDEV_DEVICE_INVENTORY_TEMPLATE_FILE_PATH}" \
	-e "fabric_device_ip_list=${NETDEV_DEVICE_IP_LIST}" \
	-e "cli_user_auth_keys_file_path=${NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH}" \
	-e "fabric_dev_login_username=${NETDEV_DEVICE_LOGIN_USERNAME}" \
	-e "fabric_dev_cli_username=${NETDEV_DEVICE_CLI_USERNAME}" \
	-e "fabric_dev_cli_password=${NETDEV_DEVICE_CLI_PASSWORD}" \
	${ANSIBLE_PLAYBOOK} 

set +x

rm -f ${NETDEV_DEVICE_INVENTORY_FILE_PATH}

echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"
echo "ANSIBLE_PLAYBOOK                    : $ANSIBLE_PLAYBOOK"
echo "NETDEV_FABRIC_NAME                         : $NETDEV_FABRIC_NAME"
echo "NETDEV_FABRIC_CONFIG_DIR                   : $NETDEV_FABRIC_CONFIG_DIR"

echo "NETDEV_DEVICE_IP_LIST               : $NETDEV_DEVICE_IP_LIST"
echo "NETDEV_DEVICE_INVENTORY_TEMPLATE_FILE_PATH          : $NETDEV_DEVICE_INVENTORY_TEMPLATE_FILE_PATH"
echo "NETDEV_DEVICE_INVENTORY_FILE_PATH          : $NETDEV_DEVICE_INVENTORY_FILE_PATH"
echo "NETDEV_DEVICE_LOGIN_USERNAME           : $NETDEV_DEVICE_LOGIN_USERNAME"
echo "NETDEV_DEVICE_CLI_USERNAME             : $NETDEV_DEVICE_CLI_USERNAME"
echo "NETDEV_DEVICE_CLI_PASSWORD             : $NETDEV_DEVICE_CLI_PASSWORD"
echo "NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH    : $NETDEV_DEVICE_CLI_USER_AUTH_PRIV_KEY_FILE_PATH"
echo "NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH    : $NETDEV_DEVICE_CLI_USER_AUTH_PUB_KEYS_FILE_PATH"

exit 0


