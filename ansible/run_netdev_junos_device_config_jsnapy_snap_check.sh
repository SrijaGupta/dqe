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
# Description   : bash-script to run the ansible-playbook for device-disovery in
#                 Junos Space based on the stack-name and with  default paramaters.
#                 It is a convinient way to customize the input parameters.
#
#

DEBUG=
DEBUG="-vvvv"

ANSIBLE_PLAYBOOK=netdev_junos_device_config_jsnapy_snap_check.yml

DQE_NET_INVENTORY_FILE_PATH=${DQE_NET_INVENTORY_FILE_PATH:=inventory/cluster_inventory.inv}
DEVICE_GROUP_NAME=cluster_fabric_mx_devices


JSNAPY_TRANSACTION_ID=`date '+%m%d%H%M'`
JSNAPY_BASE_DIR_PATH="/var/tmp/jsnapy/${JSNAPY_TRANSACTION_ID}"
JSNAPY_SNAPSHOT_DIR_PATH=${JSNAPY_BASE_DIR_PATH}/snapshots 
mkdir -p ${JSNAPY_SNAPSHOT_DIR_PATH}

SVM_SSH_USER_NAME=root
SVM_SSH_PRIVKEY=${SVM_SSH_PRIVKEY:=~/.ssh/id_rsa}
SVM_SSH_PUBKEY=${SVM_SSH_PUBKEY:=~/.ssh/id_rsa.pub}

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

if [ ! -e $DQE_NET_INVENTORY_FILE_PATH ] ; then
    echo "ERROR: couln't find DQE_NET_INVENTORY_FILE_PATH file: $DQE_NET_INVENTORY_FILE_PATH"
    exit 1
fi

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${DEBUG} \
	-i ${DQE_NET_INVENTORY_FILE_PATH}  \
	-e transaction_id=${JSNAPY_TRANSACTION_ID} \
        -e jsnapy_base_dir_path=${JSNAPY_BASE_DIR_PATH} \
        -e jsnapy_snapshot_dir_path=${JSNAPY_SNAPSHOT_DIR_PATH} \
	-e juniper_user=${SVM_SSH_USER_NAME} \
	-e juniper_key=${SVM_SSH_PRIVKEY} \
	${ANSIBLE_PLAYBOOK} 
set +x

echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

echo "ANSIBLE_PLAYBOOK            : $ANSIBLE_PLAYBOOK"
echo "DQE_NET_INVENTORY_FILE_PATH : $DQE_NET_INVENTORY_FILE_PATH"
echo "JSNAPY_BASE_DIR_PATH        : $JSNAPY_BASE_DIR_PATH"
echo "JSNAPY_SNAPSHOT_DIR_PATH    : $JSNAPY_SNAPSHOT_DIR_PATH"

