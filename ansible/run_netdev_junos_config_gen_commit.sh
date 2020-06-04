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

export COMMIT_ACTION=1

# export COMMIT_DEVICE_INV_HOSTNAMES=vmx101,vmx102,vmx103,vmx104
# export COMMIT_DEVICE_INV_HOSTNAMES=${COMMIT_DEVICE_INV_HOSTNAMES}

# ARGS_HAS_INV_HOSTNAMES=`echo "$*" | grep 'device-inv-hostnames'`
# echo "ARGS_HAS_INV_HOSTNAMES: $ARGS_HAS_INV_HOSTNAMES"



CMD_ARGS="--commit"
# set -x
run_netdev_junos_config_gen_deploy.sh $* --commit
# run_netdev_junos_config_gen_deploy.sh $* --commit --device-inv-hostnames "${COMMIT_DEVICE_INV_HOSTNAMES}"
# set +x


