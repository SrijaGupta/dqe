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

export JSNAPY_ACTION=snap_pre

JSNAPY_TRANSACTION_ID_DEFAULT=`date '+%m%d%H%M'`
ARGS_HAS_TRANSACTION_ID=`echo "$*" | grep 'jsnapy-transaction-id'`
# echo "ARGS_HAS_TRANSACTION_ID: $ARGS_HAS_TRANSACTION_ID"

CMD_ARGS="--jsnapy-action snap_pre"
if [ "${ARGS_HAS_TRANSACTION_ID}" == "" ] ; then
    export JSNAPY_TRANSACTION_ID=${JSNAPY_TRANSACTION_ID:=${JSNAPY_TRANSACTION_ID_DEFAULT}}
    CMD_ARGS="${CMD_ARGS} --jsnapy-transaction-id  ${JSNAPY_TRANSACTION_ID}"
fi
# echo "CMD_ARGS: $CMD_ARGS"

# exit 0
# set -x
run_netdev_junos_device_config_jsnapy_audit.sh $* ${CMD_ARGS} # --jsnapy-action snap_pre # --jsnapy-transaction-id ${JSNAPY_TRANSACTION_ID}
# set +x

