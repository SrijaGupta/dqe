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


ANSIBLE_PLAYBOOK=netdev_ansible_module_demo_vnfstack.yml

VNF_PROV_TXN_ID=`date '+%m%d%H%M'`
VNF_MGT_VN_NAME=${VNF_MGT_VN_NAME:=bms-public-vn}
# SVM_IMAGE_NAME=${SVM_IMAGE_NAME:=vSRX-151X49-D110-BASE-FW}
SVM_IMAGE_NAME=${SVM_IMAGE_NAME:=cirros-0.4.0}

VNF_TENANT_NAME=${VNF_TENANT_NAME:=${OS_TENANT_NAME}}
unset OS_TENANT_NAME
# echo "OS_TENANT_NAME: $OS_TENANT_NAME"

SVM_SSH_USER_NAME=${SVM_SSH_USER_NAME:=admin}
# SVM_SSH_PRIVKEY=../etc/os_keys/id_rsa_csimlab_spaceadmin
SVM_SSH_PRIVKEY=${SVM_SSH_PRIVKEY:=~/.ssh/id_rsa}
# SVM_SSH_PUBKEY=../etc/os_keys/id_rsa_csimlab_spaceadmin.pub
SVM_SSH_PUBKEY=${SVM_SSH_PUBKEY:=~/.ssh/id_rsa.pub}

if [ "${OS_AUTH_URL}" == "" ] ; then
    echo "ERROR: Must provide a OS_AUTH_URL - source openstack-rc file before running thus script"
    exit 1
fi

if [ ! -e $ANSIBLE_PLAYBOOK ] ; then
    echo "ERROR: couln't find ANSIBLE_PLAYBOOK file: $ANSIBLE_PLAYBOOK"
    exit 1
fi

export VNF_STACK_NAME=${VNF_STACK_NAME:=}
if [ $# -gt 0 ] ; then
    export VNF_STACK_NAME=$1
fi


echo "VNF_STACK_NAME: $VNF_STACK_NAME"
if [ "${VNF_STACK_NAME}" == "" ] ; then 
    echo "ERROR: Must provide a stack-name."
    exit 1
fi

START_TIME=`date`
echo "START_TIME: $START_TIME"
echo ""

set -x
ansible-playbook  -vvvvv \
	-e transaction_id=${VNF_PROV_TXN_ID} \
	-e juniper_user=${SVM_SSH_USER_NAME} \
	-e juniper_key=${SVM_SSH_PRIVKEY} \
	-e juniper_rsa_key=${SVM_SSH_PRIVKEY} \
	-e vnf_svm_image_name=${SVM_IMAGE_NAME} \
	-e vnf_mgmt_vn_name=${VNF_MGT_VN_NAME} \
	-e vnf_stack_name=${VNF_STACK_NAME} \
	-e os_tenant_name=${VNF_TENANT_NAME} \
	${ANSIBLE_PLAYBOOK} 

set +x

echo " "
END_TIME=`date`
echo "START_TIME: $START_TIME"
echo "END_TIME:   $END_TIME"

echo "STACK_NAME: $STACK_NAME"
