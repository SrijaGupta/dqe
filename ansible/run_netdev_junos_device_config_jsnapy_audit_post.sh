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

export JSNAPY_ACTION=snap_post

# JSNAPY_TRANSACTION_ID_DEFAULT=`date '+%m%d%H%M'`
# export JSNAPY_TRANSACTION_ID=${JSNAPY_TRANSACTION_ID:=}
# if [ "$JSNAPY_TRANSACTION_ID" == ""  ] ; then
#     echo "ERROR: Must provide JSNAPY_TRANSACTION_ID - it must be set with pre-snapshot transation-id "
#     exit 1
# fi

run_netdev_junos_device_config_jsnapy_audit.sh $* # --jsnapy-action ${JSNAPY_ACTION} # --jsnapy-transaction-id ${JSNAPY_TRANSACTION_ID}
# run_netdev_junos_device_config_jsnapy_audit.sh $* --jsnapy-action ${JSNAPY_ACTION} # --jsnapy-transaction-id ${JSNAPY_TRANSACTION_ID}


