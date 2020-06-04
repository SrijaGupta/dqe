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

# ANSIBLE_PLAYBOOK=netdev_junos_device_config_jsnapy_audit_inv.yml
ANSIBLE_PLAYBOOK=netdev_junos_device_config_jsnapy_audit.yml

DQE_NET_INVENTORY_FILE_PATH=${DQE_NET_INVENTORY_FILE_PATH:=inventory/cluster_inventory.inv}
DEVICE_GROUP_NAME=${DEVICE_GROUP_NAME:=}

JSNAPY_OUTPUT_DIR=${JSNAPY_OUTPUT_DIR:=/var/tmp/jsnapy}
JSNAPY_ACTION=${JSNAPY_ACTION:=snap_pre}
# JSNAPY_TRANSACTION_ID_DEFAULT=`date '+%m%d%H%M'`
# JSNAPY_TRANSACTION_ID=${JSNAPY_TRANSACTION_ID:=${JSNAPY_TRANSACTION_ID_DEFAULT}}
JSNAPY_TRANSACTION_ID=${JSNAPY_TRANSACTION_ID:=}

JSNAPY_TEST_FILE_NAME=${JSNAPY_TEST_FILE_NAME:=}


SVM_SSH_USER_NAME=${SVM_SSH_USER_NAME:=root}
SVM_SSH_PRIVKEY=${SVM_SSH_PRIVKEY:=~/.ssh/id_rsa}
SVM_SSH_PUBKEY=${SVM_SSH_PUBKEY:=~/.ssh/id_rsa.pub}

show_usage() {
    # local SCRIPT_NAME=$1
    echo "
    usage: $0
        [ -i|--inventory                 <DQE_NET_INVENTORY_FILE>            ]
        [ --device-group-name            <DEVICE_GROUP_NAME>                 ]
        [ --jsnapy-output-dir            <JSNAPY_OUTPUT_DIR> ]
        [ --jsnapy-action                <snap_pre|snap_post>                 ]
	[ --jsnapy-transaction-id        <JSNAPY_TRANSACTION_ID> (for post action, must match transaction-id used in pre) ]
	[ --jsnapy-test-file             <JSNAPY_TEST_FILE_NAME> (must be present under JSNAPY_HOMAE_DIR/testfiles ]
        [ -h|--help  ]
        [ --debug|-v ]
"
}

set -x
echo "args: $*"
if [ $# == 1 ] ; then 
    case $1 in
        -*) ;;
        *) DEVICE_GROUP_NAME=$1;  shift ;
    esac
fi
echo "DEVICE_GROUP_NAME: $DEVICE_GROUP_NAME"
while [ $# -gt 0 ]; do
    if [ $# -eq 0 ]; then
        break;
    fi
    # echo "$#: $1";
    case $1 in
        -i|--inventory) shift; DQE_NET_INVENTORY_FILE_PATH=$1;;
        --device-group-name) shift; DEVICE_GROUP_NAME=$1;;
        --jsnapy-action) shift; JSNAPY_ACTION=$1;;
        --jsnapy-transaction-id) shift; JSNAPY_TRANSACTION_ID=$1;;
        --jsnapy-output-dir) shift; JSNAPY_OUTPUT_DIR=$1;;
	--jsnapy-test-file) shift; JSNAPY_TEST_FILE_NAME=$1;;
        --debug|-v) DEBUG=1; ANSIBLE_DEBUG="-v";;
        -h|--help) show_usage ; exit 0;;
        -*) echo "Unknown option: $1"; show_usage; exit 1;;
    esac
    shift ;
done
set +x

# exit 0

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

if [ "$DQE_NET_INVENTORY_FILE_PATH" == ""  ] ; then
    echo "ERROR: Must provide '-i' arg or set DQE_NET_INVENTORY_FILE env-var - cannot be empty string"
    exit 1
fi
if [ ! -e $DQE_NET_INVENTORY_FILE_PATH ] ; then
    echo "ERROR: couln't find DQE_NET_INVENTORY_FILE file: $DQE_NET_INVENTORY_FILE_PATH"
    exit 1
fi
if [ "$DEVICE_GROUP_NAME" == ""  ] ; then
    echo "ERROR: Must provide '--device-group-name' arg or set DEVICE_GROUP_NAME env-var - cannot be empty "
    exit 1
fi

if [ "$JSNAPY_TRANSACTION_ID" == ""  ] ; then
    echo "ERROR: Must provide '--jsnapy-transaction-id' or set JSNAPY_TRANSACTION_ID env-var - for post run use the id from pre rrun  "
    exit 1
fi
if [ "$JSNAPY_OUTPUT_DIR" == ""  ] ; then
    echo "ERROR: Must provide '--jsnapy-output-dir' arg or set JSNAPY_OUTPUT_DIR env-var - cannot be empty string"
    exit 1
fi
# if [ ! -e $JSNAPY_OUTPUT_DIR ] ; then
#     echo "ERROR: couln't find JSNAPY_OUTPUT_DIR file: $JSNAPY_OUTPUT_DIR"
#     exit 1
# fi
if [ "$JSNAPY_TEST_FILE_NAME" == ""  ] ; then
    echo "ERROR: Must provide '--jsnapy-test-file' or set JSNAPY_TEST_FILE_NAME env-var - for post run use the id from pre rrun  "
    exit 1
fi

JSNAPY_BASE_DIR_PATH="${JSNAPY_OUTPUT_DIR}/${JSNAPY_TRANSACTION_ID}"
JSNAPY_SNAPSHOT_DIR_PATH=${JSNAPY_BASE_DIR_PATH}/snapshots 
JSNAPY_LOG_DIR_PATH=${JSNAPY_BASE_DIR_PATH}/logs 
mkdir -p ${JSNAPY_SNAPSHOT_DIR_PATH}
mkdir -p ${JSNAPY_LOG_DIR_PATH}


echo "JSNAPY_ACTION               : $JSNAPY_ACTION"
echo "JSNAPY_TRANSACTION_ID       : $JSNAPY_TRANSACTION_ID"

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook ${DEBUG} \
	-i ${DQE_NET_INVENTORY_FILE_PATH}  \
	-l localhost,${DEVICE_GROUP_NAME} \
        -e device_group_name=${DEVICE_GROUP_NAME} \
        -e jsnapy_base_dir_path=${JSNAPY_BASE_DIR_PATH} \
        -e jsnapy_snapshot_dir_path=${JSNAPY_SNAPSHOT_DIR_PATH} \
	-e jsnapy_action=${JSNAPY_ACTION} \
	-e transaction_id=${JSNAPY_TRANSACTION_ID} \
	-e jsnapy_config_audit_test_file=${JSNAPY_TEST_FILE_NAME} \
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
echo "DEVICE_GROUP_NAME           : $DEVICE_GROUP_NAME"
echo "JSNAPY_ACTION               : $JSNAPY_ACTION"
echo "JSNAPY_TRANSACTION_ID       : $JSNAPY_TRANSACTION_ID"
echo "JSNAPY_TEST_FILE_NAME       : $JSNAPY_TEST_FILE_NAME"
echo "JSNAPY_BASE_DIR_PATH        : $JSNAPY_BASE_DIR_PATH"
echo "JSNAPY_SNAPSHOT_DIR_PATH    : $JSNAPY_SNAPSHOT_DIR_PATH"

