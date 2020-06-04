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
# Description   : 
#
#

ANSIBLE_DEBUG="-vvv"
ANSIBLE_DEBUG=""
# ANSIBLE_DEBUG=${ANSIBLE_DEBUG:=}
ANSIBLE_DEBUG=${ANSIBLE_DEBUG:=-vvvvv}

ANSIBLE_PLAYBOOK=netdev_device_exec_cli_terminal_pb.yml

SERVER_GROUP_NAME=${SERVER_GROUP_NAME:=cluster_fabric_mx_devices}
SERVER_STATUS_CMD="${SERVER_STATUS_CMD:=login}"

DQE_NET_INVENTORY_FILE_PATH=${DQE_NET_INVENTORY_FILE_PATH:=inventory/cluster_inventory.inv}


if [ "$DQE_NET_INVENTORY_FILE_PATH" == "" ] ; then
    echo "ERROR: DQE_NET_INVENTORY_FILE_PATH env-var must be set "
    exit 1
fi
if [ ! -e $DQE_NET_INVENTORY_FILE_PATH ] ; then
    echo "ERROR: couln't find DQE_NET_INVENTORY_FILE_PATH file: $DQE_NET_INVENTORY_FILE_PATH"
    exit 1
fi

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

OS_TYPE=`uname`
if [ "$OS_TYPE" != "Darwin" ] ; then
    echo "ERROR: You can run this script only on MacOSX - need 'ttab' module from npm."
    exit 1
fi

NPM_TTAB_PATH=`which ttab`
if [ "$NPM_TTAB_PATH" == "" ] ; then
    echo "ERROR: 'ttab' binary is not in PATH - add the directory of 'ttab' to PATH env var or install 'npm install -g ttab'"
    echo "For more info on installing 'ttab', see https://stackoverflow.com/questions/7171725/open-new-terminal-tab-from-command-line-mac-os-x"
    exit 1
fi

ANSIBLE_ARGS="" 
if [ "$SERVER_GROUP_NAME" != "" ] ; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS -e server_group_name=$SERVER_GROUP_NAME"
fi
if [ "$SERVER_STATUS_CMD" != "" ] ; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS -e server_status_cmd=\"$SERVER_STATUS_CMD\""
fi

ANSIBLE_ARGS=""
ANSIBLE_ARGS_FILE="/var/tmp/ANSIBLE_ARGS_FILE_$$.yml"
touch ${ANSIBLE_ARGS_FILE}
if [ "$SERVER_GROUP_NAME" != "" ] ; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS -e server_group_name=$SERVER_GROUP_NAME"
    cat >> ${ANSIBLE_ARGS_FILE} << EOF
server_group_name: $SERVER_GROUP_NAME
EOF
fi
if [ "$SERVER_STATUS_CMD" != "" ] ; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS -e server_status_cmd=\"$SERVER_STATUS_CMD\""
    cat >> ${ANSIBLE_ARGS_FILE} << EOF
server_status_cmd: "$SERVER_STATUS_CMD"
EOF
fi


echo "ANSIBLE_ARGS: $ANSIBLE_ARGS"

# cat $ANSIBLE_ARGS_FILE
# exit 0

# export ANSIBLE_DEBUG=True 
# export ANSIBLE_LOG_PATH=`echo ${ANSIBLE_PLAYBOOK%%.*} | tr '[:lower:]' '[:upper:]' | sed -e 's/^/logs\//' | sed -e 's/$/.log/' `
# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${ANSIBLE_DEBUG}  \
        -i ${DQE_NET_INVENTORY_FILE_PATH} \
	-e @${ANSIBLE_ARGS_FILE} \
	${ANSIBLE_PLAYBOOK} 
set +x

    # server_group_name : 'cluster_servers_instances'
    # server_status_cmd: "{{ server_docker_status_cmd }}"
    # ${ANSIBLE_ARGS} \
    # -e "ansible_ssh_user=root"  \


echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

echo "ANSIBLE_PLAYBOOK          : $ANSIBLE_PLAYBOOK"
# echo "ANSIBLE_ARGS              : $ANSIBLE_ARGS"
echo "SERVER_GROUP_NAME         : $SERVER_GROUP_NAME"
echo "NS_INSTALL_CONFIG_DIR     : $NS_INSTALL_CONFIG_DIR"
echo "DQE_NET_INVENTORY_FILE_PATH       : $DQE_NET_INVENTORY_FILE_PATH"


