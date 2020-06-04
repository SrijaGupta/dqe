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

ANSIBLE_PLAYBOOK=netdev_junos_config_gen_deploy.yml

PLAYBOOK_DIR_PATH=${BinDir}
CONFIG_FRAGMENT_TEMPLATE_BASE_DIR=${CONFIG_FRAGMENT_TEMPLATE_BASE_DIR:=${PLAYBOOK_DIR_PATH}/templates}

DQE_NET_INVENTORY_FILE=${DQE_NET_INVENTORY_FILE:=inventory/cluster_inventory.inv}
DEVICE_GROUP_NAME=${DEVICE_GROUP_NAME:=ACX2200}
# DEVICE_ROLE_NAME=`echo ${DEVICE_GROUP_NAME} | tr '[:upper:]' '[:lower:]' `

export COMMIT_ACTION=${COMMIT_ACTION:=}
export COMMIT_DEVICE_INV_HOSTNAMES=${COMMIT_DEVICE_INV_HOSTNAMES:=}    # Commaa seperated device-ip-list 


show_usage() {
    # local SCRIPT_NAME=$1
    echo "
    usage: $0
        [ -i|--inventory                 <DQE_NET_INVENTORY_FILE>            ]
        [ --device-group-name            <DEVICE_GROUP_NAME>                 ]
	[ --device-inv-hostnames         <COMMIT_DEVICE_INV_HOSTNAMES> (only for --commit opton)       ]
        [ --config-fragment-template-dir <CONFIG_FRAGMENT_TEMPLATE_BASE_DIR> ]
        [ --commit                                                           ]
        [ -h|--help  ]
        [ --debug|-v ]
"
}

# set -x
# echo "args: $*"
if [ $# == 1 ] ; then 
    case $1 in
        -*) ;;
        *) DEVICE_GROUP_NAME=$1;  shift ;
    esac
fi
while [ $# -gt 0 ]; do
    if [ $# -eq 0 ]; then
        break;
    fi
    # echo "$#: $1";
    case $1 in
        -i|--inventory) shift; DQE_NET_INVENTORY_FILE=$1;;
        --device-group-name) shift; DEVICE_GROUP_NAME=$1;;
        --device-inv-hostnames) shift; COMMIT_DEVICE_INV_HOSTNAMES=$1;;
        --config-fragment-template-dir) shift; CONFIG_FRAGMENT_TEMPLATE_BASE_DIR=$1;;
        --commit) COMMIT_ACTION=1;;
        --debug|-v) DEBUG=1; ANSIBLE_DEBUG="-v";;
        -h|--help) show_usage ; exit 0;;
        -*) echo "Unknown option: $1"; show_usage; exit 1;;
    esac
    shift ;
done
# set +x

# exit 0

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

if [ "$CONFIG_FRAGMENT_TEMPLATE_BASE_DIR" == ""  ] ; then
    echo "ERROR: Must set CONFIG_FRAGMENT_TEMPLATE_BASE_DIR env-var - cannot be empty string"
    exit 1
fi
if [ ! -e $CONFIG_FRAGMENT_TEMPLATE_BASE_DIR ] ; then
    echo "ERROR: couln't find CONFIG_FRAGMENT_TEMPLATE_BASE_DIR file: $CONFIG_FRAGMENT_TEMPLATE_BASE_DIR"
    exit 1
fi

if [ "$DQNET_DEVICE_DATA_DIR" == ""  ] ; then
    echo "ERROR: Must set DQNET_DEVICE_DATA_DIR env-var - cannot be empty string"
    exit 1
fi
if [ ! -e $DQNET_DEVICE_DATA_DIR ] ; then
    echo "ERROR: couldn't find DQNET_DEVICE_DATA_DIR file: $DQNET_DEVICE_DATA_DIR"
    exit 1
fi


if [ "$DQE_NET_INVENTORY_FILE" == ""  ] ; then
    echo "ERROR: Must provide '-i' arg or set DQE_NET_INVENTORY_FILE env-var - cannot be empty string"
    exit 1
fi
if [ ! -e $DQE_NET_INVENTORY_FILE ] ; then
    echo "ERROR: couln't find DQE_NET_INVENTORY_FILE file: $DQE_NET_INVENTORY_FILE"
    exit 1
fi
if [ "$DEVICE_GROUP_NAME" == ""  ] ; then
    echo "ERROR: Must provide '--device-group-name' arg or set DEVICE_GROUP_NAME env-var - cannot be empty "
    exit 1
fi

if [ "$COMMIT_ACTION" != ""  ] ; then
    if [ "$COMMIT_DEVICE_INV_HOSTNAMES" == ""  ] ; then
        echo "ERROR: Must provide '--device-inv-hostnames' or set COMMIT_DEVICE_INV_HOSTNAMES  env-var for commit oprtaion - comma seperated device ip-list. "
        exit 1
    fi
fi


echo "DQE_NET_INVENTORY_FILE: $DQE_NET_INVENTORY_FILE DEVICE_GROUP_NAME: $DEVICE_GROUP_NAME"
echo "COMMIT_ACTION: $COMMIT_ACTION COMMIT_DEVICE_INV_HOSTNAMES: $COMMIT_DEVICE_INV_HOSTNAMES"

# exit 0
ANSIBLE_PB_LIMIT_ARGS="--limit ${DEVICE_GROUP_NAME}"
COMMIT_ARGS="false"
if [ "$COMMIT_ACTION" != ""  ] ; then
    ANSIBLE_PB_LIMIT_ARGS=" --limit ${COMMIT_DEVICE_INV_HOSTNAMES} "
    COMMIT_ARGS="true"
fi
echo "ANSIBLE_PB_LIMIT_ARGS  : $ANSIBLE_PB_LIMIT_ARGS"
echo "COMMIT_ARGS  : $COMMIT_ARGS"


# exit 0



# # export ANSIBLE_DEBUG=True 
# export ANSIBLE_LOG_PATH=`echo ${ANSIBLE_PLAYBOOK%%.*} | tr '[:lower:]' '[:upper:]' | sed -e 's/^/logs\//' | sed -e 's/$/.log/' `
# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${ANSIBLE_DEBUG} \
	-i ${DQE_NET_INVENTORY_FILE} \
	${ANSIBLE_PB_LIMIT_ARGS} \
	-e "device_group_name=${DEVICE_GROUP_NAME}" \
	-e "{'dqenet_device_junos_commit':${COMMIT_ARGS}}" \
	${ANSIBLE_PLAYBOOK} 

	# -e "device_role_name=${DEVICE_ROLE_NAME}" \
        # -e ns_junosvm_custom_config_params_template=${JUNOSVM_CUSTOM_CONFIG_PARAMS_TEMPLATE} \
        # -e ns_junosvm_config_template=${NS_JUNOSVM_CONFIG_TEMPLATE} \
set +x

echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

# echo "ANSIBLE_LOG_PATH: $ANSIBLE_LOG_PATH"
echo "ANSIBLE_PLAYBOOK            : $ANSIBLE_PLAYBOOK"
echo "ANSIBLE_PB_COMMIT_ARGS      : $ANSIBLE_PB_COMMIT_ARGS"
echo "DQNET_DEVICE_DATA_DIR       : $DQNET_DEVICE_DATA_DIR"
echo "DQE_NET_INVENTORY_FILE      : $DQE_NET_INVENTORY_FILE"
echo "DEVICE_GROUP_NAME           : $DEVICE_GROUP_NAME"
echo "CONFIG_FRAGMENT_TEMPLATE_BASE_DIR           : $CONFIG_FRAGMENT_TEMPLATE_BASE_DIR"

