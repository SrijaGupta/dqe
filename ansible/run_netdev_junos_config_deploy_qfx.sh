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
BinDir=${0%/*}
export PATH=$BinDir:$PATH


ANSIBLE_DEBUG="-vvvvv"
ANSIBLE_DEBUG="-v"
ANSIBLE_DEBUG="-vvv"
PLAYBOOK_ARGS=

ANSIBLE_PLAYBOOK=netdev_junos_config_deploy_qfx.yml

# JUNOSVM_CUSTOM_CONFIG_PARAMS_TEMPLATE=junosvm_config_params_vz.j2 
# NS_JUNOSVM_CONFIG_TEMPLATE=custom-vz-junosvm-config-text.conf.j2

#
# Provides confgiuration and network interface related information of nodes in NS HA cluster
# 
DQE_NET_INVENTORY_FILE=${DQE_NET_INVENTORY_FILE:=inventory/cluster_inventory.inv}
# DEVICE_GROUP_NAME=cluster_fabric_qfx_devices
DEVICE_GROUP_NAME=${DEVICE_GROUP_NAME:=qfx}
INVENTORY_DEVICE_GROUP_NAME="cluster_fabric_${DEVICE_GROUP_NAME}_devices"

PLAYBOOK_DIR_PATH=${BinDir}
export CONFIG_FRAGMENT_TEMPLATE_BASE_DIR=${CONFIG_FRAGMENT_TEMPLATE_BASE_DIR:=${PLAYBOOK_DIR_PATH}/templates}

if [ ! -e $DQE_NET_INVENTORY_FILE ] ; then
    echo "ERROR: couln't find DQE_NET_INVENTORY_FILE file: $DQE_NET_INVENTORY_FILE"
    exit 1
fi
if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi
if [ ! -e $CONFIG_FRAGMENT_TEMPLATE_BASE_DIR ] ; then
    echo "ERROR: couln't find CONFIG_FRAGMENT_TEMPLATE_BASE_DIR file: $CONFIG_FRAGMENT_TEMPLATE_BASE_DIR"
    exit 1
fi

# # export ANSIBLE_DEBUG=True 
# export ANSIBLE_LOG_PATH=`echo ${ANSIBLE_PLAYBOOK%%.*} | tr '[:lower:]' '[:upper:]' | sed -e 's/^/logs\//' | sed -e 's/$/.log/' `
# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${ANSIBLE_DEBUG} \
	-i ${DQE_NET_INVENTORY_FILE} \
	-l ${INVENTORY_DEVICE_GROUP_NAME} \
	-e "device_group_name=${DEVICE_GROUP_NAME}" \
	${ANSIBLE_PLAYBOOK} 

        # -e ns_junosvm_custom_config_params_template=${JUNOSVM_CUSTOM_CONFIG_PARAMS_TEMPLATE} \
        # -e ns_junosvm_config_template=${NS_JUNOSVM_CONFIG_TEMPLATE} \
set +x

echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"
echo "ANSIBLE_PLAYBOOK                 : $ANSIBLE_PLAYBOOK"
echo "DQE_NET_INVENTORY_FILE      : $DQE_NET_INVENTORY_FILE"
echo "INVENTORY_DEVICE_GROUP_NAME : $INVENTORY_DEVICE_GROUP_NAME"
echo "DEVICE_GROUP_NAME           : $DEVICE_GROUP_NAME"

