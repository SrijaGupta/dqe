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

DQNET_DEVICE_DATA_DIR=${DQNET_DEVICE_DATA_DIR:=}
DEVICE_GROUP_NAME=${DEVICE_GROUP_NAME:=}


ATOOL_SERVER_IP_ADDRESS=${ATOOL_SERVER_IP_ADDRESS:=}
ATOOL_SERVER_USER_NAME=${ATOOL_SERVER_USER_NAME:=}
ATOOL_SERVER_USER_PASSWORD=${ATOOL_SERVER_USER_PASSWORD:=}

ATOOL_SERVER_CONFIG_TOP_DIR=${ATOOL_SERVER_CONFIG_TOP_DIR:=}

show_usage() {
    # local SCRIPT_NAME=$1
    echo "
    usage: $0
        [ --device-data-dir              <DQNET_DEVICE_DATA_DIR>       ]
        [ --device-group-name            <DEVICE_GROUP_NAME>           ]
        [ --atool-config-top-dir         <ATOOL_SERVER_CONFIG_TOP_DIR> ]
        [ --atool-server-ip-address      <ATOOL_SERVER_IP_ADDRESS>     ]
        [ --atool-server-user-name       <ATOOL_SERVER_USER_NAME>      ]
        [ --atool-server-user-password   <ATOOL_SERVER_USER_PASSWORD>  ]
        [ -h|--help  ]
        [ --debug|-v ]
"
}

# set -x
# echo "args: $*"
while [ $# -gt 0 ]; do
    if [ $# -eq 0 ]; then
        break;
    fi
    # echo "$#: $1";
    case $1 in
        --device-data-dir) shift; DQNET_DEVICE_DATA_DIR=$1;;
        --device-group-name) shift; DEVICE_GROUP_NAME=$1;;
        --atool-config-top-dir) shift; ATOOL_SERVER_CONFIG_TOP_DIR=$1;;
        --atool-server-ip-address) shift; ATOOL_SERVER_IP_ADDRESS=$1;;
        --atool-server-user-name) shift; ATOOL_SERVER_USER_NAME=$1;;
        --atool-server-user-password) shift; ATOOL_SERVER_USER_PASSWORD=$1;;
        -h|--help) show_usage ; exit 0;;
        -*) echo "Unknown option: $1"; show_usage; exit 1;;
    esac
    shift ;
done
# set +x

if [ "$DQNET_DEVICE_DATA_DIR" == ""  ] ; then
    echo "ERROR: Must provide '--device-data-dir' or set DQNET_DEVICE_DATA_DIR env-var - cannot be empty string"
    exit 1
fi
if [ ! -e $DQNET_DEVICE_DATA_DIR ] ; then
    echo "ERROR: couln't find DQNET_DEVICE_DATA_DIR file: $DQNET_DEVICE_DATA_DIR"
    exit 1
fi
if [ "$DEVICE_GROUP_NAME" == ""  ] ; then
    echo "ERROR: Must provide '--device-group-name' or set DEVICE_GROUP_NAME env-var - cannot be empty string"
    exit 1
fi

if [ "$ATOOL_SERVER_CONFIG_TOP_DIR" == ""  ] ; then
    echo "ERROR: Must provide '--atool-config-top-dir' or set ATOOL_SERVER_CONFIG_TOP_DIR env-var - cannot be empty string"
    exit 1
fi
# if [ ! -e $ATOOL_SERVER_CONFIG_TOP_DIR ] ; then
#     echo "ERROR: couln't find ATOOL_SERVER_CONFIG_TOP_DIR file: $ATOOL_SERVER_CONFIG_TOP_DIR"
#     exit 1
# fi

if [ "$ATOOL_SERVER_IP_ADDRESS" == ""  ] ; then
    echo "ERROR: Must provide '--atool-server-ip-address' or set ATOOL_SERVER_IP_ADDRESS env-var - cannot be empty string"
    exit 1
fi
if [ "$ATOOL_SERVER_USER_NAME" == ""  ] ; then
    echo "ERROR: Must provide '--atool-server-user-name' or set ATOOL_SERVER_USER_NAME env-var - cannot be empty string"
    exit 1
fi
if [ "$ATOOL_SERVER_USER_PASSWORD" == ""  ] ; then
    echo "ERROR: Must provide '--atool-server-user-password' or set ATOOL_SERVER_USER_PASSWORD env-var - cannot be empty string"
    exit 1
fi

# exit 0

ATOOL_SERVER_DEVICE_GROUP_BASE_CONFIG_DIR=${ATOOL_SERVER_CONFIG_TOP_DIR}/${DEVICE_GROUP_NAME}

DEVICE_GROUP_BASE_CONFIG_DIR=${DQNET_DEVICE_DATA_DIR}/junos_config_base/${DEVICE_GROUP_NAME}

SRC_BASE_CONFIG_FILE_PATH=${DEVICE_GROUP_BASE_CONFIG_DIR}/junos_config.conf
DEST_ATOOL_SERVER_BASE_CONFIG_FILE_PATH=${ATOOL_SERVER_DEVICE_GROUP_BASE_CONFIG_DIR}/junos_config.conf

if [ ! -e $DEVICE_GROUP_BASE_CONFIG_DIR ] ; then
    echo "ERROR: couln't find DEVICE_GROUP_BASE_CONFIG_DIR file: $DEVICE_GROUP_BASE_CONFIG_DIR"
    exit 1
fi
if [ ! -e $SRC_BASE_CONFIG_FILE_PATH ] ; then
    echo "ERROR: couln't find SRC_BASE_CONFIG_FILE_PATH file: $SRC_BASE_CONFIG_FILE_PATH"
    exit 1
fi

# exit 0

set -x
scp ${SRC_BASE_CONFIG_FILE_PATH} ${ATOOL_SERVER_USER_NAME}@${ATOOL_SERVER_IP_ADDRESS}:${DEST_ATOOL_SERVER_BASE_CONFIG_FILE_PATH}
set +x


exit 0

