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

ANSIBLE_DEBUG="-vvv"
ANSIBLE_DEBUG=
ANSIBLE_DEBUG="-vvvvv"

ANSIBLE_PLAYBOOK=netdev_service_open_gui_pb.yml

# SERVER_GROUP_NAME=${SERVER_GROUP_NAME:=}
# SERVER_STATUS_CMD=${SERVER_STATUS_CMD:=}

DQE_NET_INVENTORY_FILE=${DQE_NET_INVENTORY_FILE:=inventory/cluster_inventory.inv}


if [ "$DQE_NET_INVENTORY_FILE" == "" ] ; then
    echo "ERROR: DQE_NET_INVENTORY_FILE env-var must be set "
    exit 1
fi
if [ ! -e $DQE_NET_INVENTORY_FILE ] ; then
    echo "ERROR: couln't find DQE_NET_INVENTORY_FILE file: $DQE_NET_INVENTORY_FILE"
    exit 1
fi

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

CHROME_DRIVER_PATH=`which chromedriver`
if [ "$CHROME_DRIVER_PATH" == "" ] ; then
    echo "ERROR: 'chromedriver' binary is not in PATH - add the directory of 'chromedriver' to PATH env var"
    echo "For more info on installing 'chromedriver', see https://sites.google.com/a/chromium.org/chromedriver/getting-started"
    exit 1
fi

ANSIBLE_ARGS="" 
if [ "$SERVER_GROUP_NAME" != "" ] ; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS -e server_group_name=$SERVER_GROUP_NAME"
fi
if [ "$SERVER_STATUS_CMD" != "" ] ; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS -e server_status_cmd=\"$SERVER_STATUS_CMD\""
fi

echo "ANSIBLE_ARGS: $ANSIBLE_ARGS"

# export ANSIBLE_DEBUG=True 
# export ANSIBLE_LOG_PATH=`echo ${ANSIBLE_PLAYBOOK%%.*} | tr '[:lower:]' '[:upper:]' | sed -e 's/^/logs\//' | sed -e 's/$/.log/' `
# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${ANSIBLE_DEBUG}  \
	-e '{"ns_gui_open_in_browser" : true }' \
        -i ${DQE_NET_INVENTORY_FILE} \
	-e "ansible_ssh_user=root"  \
	${ANSIBLE_ARGS} \
	${ANSIBLE_PLAYBOOK} 
set +x

    # server_group_name : 'cluster_servers_instances'
    # server_status_cmd: "{{ server_docker_status_cmd }}"


echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

echo "ANSIBLE_PLAYBOOK          : $ANSIBLE_PLAYBOOK"
echo "ANSIBLE_ARGS              : $ANSIBLE_ARGS"
echo "CFM_INSTALL_CONFIG_DIR    : $CFM_INSTALL_CONFIG_DIR"
echo "DQE_NET_INVENTORY_FILE       : $DQE_NET_INVENTORY_FILE"


