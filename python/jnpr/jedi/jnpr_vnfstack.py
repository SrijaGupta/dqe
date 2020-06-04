#!/usr/bin/env python
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
# Description   : A python script that gathers VNF stack related data.
#                   create-stack, list-stack, show-stack, wait-for-stack, delete-stack,
#                   show-stack-server-uuid-list, show-stack-server-data-list, show-stack-server-name-list, show-stack-server-mgmt-ip-list,
#                   show-stack-server-name-mgmtip-list,
#                   get-vnf-name,
#                 Usage:
#                   python jnpr/jedi/jedi_vnfstack.py --debug -cmd show-stack-server-name-list --stack-name STACK_201711020835_ZRDM3FRWL97OAM --server-mgmt-vn-name MGT 
#                   python jnpr/jedi/jedi_vnfstack.py --debug -cmd show-stack-server-name-mgmtip-list --stack-name STACK_201711020835_ZRDM3FRWL97OAM --server-mgmt-vn-name MGT 
#                                      
#                         

#
# Last Modified : 03-February-2018
#


import os
import sys
import traceback
import re
import os.path
import shutil
import requests
from pprint import pprint, pformat

import logging
import copy
import argparse
import ConfigParser
from lxml import objectify

import time 

from netaddr import *
from urlparse import urlparse


import uuid
# import logging.config

import json

# Data processing libraries
from jinja2 import Template
import yaml

from jnpr.jedi.openstack.keystone.os_keystone import KeystoneMgr
from jnpr.jedi.openstack.nova.os_server import NovaServerMgr
from jnpr.jedi.openstack.heat.os_stack import HeatStackMgr

usage = "usage: jedi_vnfstack.py \n\
    \n\
Examples:  \n\
 "

class JnprVNFStack:
    def __init__(self, args):
        self.args = args

        self.keystone_mgr = KeystoneMgr(self.args)
        self.nova_server_mgr = NovaServerMgr(self.keystone_mgr)
        self.heat_stack_mgr = HeatStackMgr(self.keystone_mgr)

        # servers = self.nova_server_mgr.find()
    # end-def __init__

    def get_token(self):
        token = self.heat_stack_mgr.get_token()
        return token
    # end-def get_token
    def list_stacks(self):
        return self.heat_stack_mgr.list_stacks()
    # end-def list_stacks
    def show_stack(self, stack_name):
        return self.heat_stack_mgr.show_stack(stack_name)
    # end-def show_stack
    def wait_till_stack_completion(self, stack_name, poll_period=30, max_wait_time=60):
        return self.heat_stack_mgr.wait_till_stack_completion(stack_name, poll_period, max_wait_time)
    # end-def wait_till_stack_completion

    def get_stack_server_uuid_list(self, stack_name, image_uuid=None, nested_depth=3, wait_for_stack_complete=False):
        return self.heat_stack_mgr.get_stack_server_uuid_list(stack_name, image_uuid, nested_depth, wait_for_stack_complete)
    # end-def get_stack_server_uuid_list
    def get_stack_server_name_list(self, stack_name, image_uuid=None, nested_depth=3, wait_for_stack_complete=False) :
        return self.heat_stack_mgr.get_stack_server_name_list(stack_name, image_uuid, nested_depth, wait_for_stack_complete)
    # end-def get_stack_server_name_list
    def get_stack_server_data_list(self, stack_name, image_uuid=None, nested_depth=3, wait_for_stack_complete=False) :
        return self.heat_stack_mgr.get_stack_server_data_list(stack_name, image_uuid, nested_depth, wait_for_stack_complete)
    # end-def get_stack_server_data_list

    def get_si_info(self, server_name_or_uuid):
        return self.nova_server_mgr.get_si_info(server_name_or_uuid)
    # end-def get_si_info

    def get_si_vnf_name_by_vm(self, server_name_or_uuid):
        vnf_name = None
        si_info = self.get_si_info(server_name_or_uuid)
        if (si_info["metadata"] and si_info["metadata"]["vnf_name"]) :
            vnf_name = si_info["metadata"]["vnf_name"]
        # end-if 
        return vnf_name
    # end-def get_si_vnf_name_by_vm
    def get_si_vnf_type_by_vm(self, server_name_or_uuid):
        vnf_type = None
        si_info = self.get_si_info(server_name_or_uuid)
        if (si_info["metadata"] and si_info["metadata"]["vnf_type"]) :
            vnf_type = si_info["metadata"]["vnf_type"]
        # end-if 
        return vnf_type
    # end-def get_si_vnf_type_by_vm
    def get_si_vnf_name_by_stack(self, stack_name, image_uuid, nested_depth=3, wait_for_stack_complete=False):
        vnf_name = None
        stack_server_name_list = self.get_stack_server_name_list(stack_name, image_uuid, nested_depth, wait_for_stack_complete) 
        if (stack_server_name_list == None  or (len(stack_server_name_list) == 0)) :
            err_msg = "Couldn't find any VM associated with stack: %s and image_uuid: %s" % (stack_name, image_uuid)
            logging.error(err_msg)
            raise RuntimeError(err_msg)
        # end-if 

        si_info = self.get_si_info(stack_server_name_list[0])
        if (si_info["metadata"] and si_info["metadata"]["vnf_name"]) :
            vnf_name = si_info["metadata"]["vnf_name"]
        # end-if 
        return vnf_name
    # end-def get_server_vnf_name

    def get_si_mgmt_ip(self, server_name_or_uuid, server_mgmt_vn_name):
        vm_mgmt_ip = self.nova_server_mgr.get_si_mgmt_ip(server_name_or_uuid, server_mgmt_vn_name)
        return vm_mgmt_ip
    # end-def get_si_mgmt_ip
    def get_si_mgmt_ip_name_dict(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_mgmt_ip_name_dict = self.nova_server_mgr.get_si_mgmt_ip_name_dict(server_name_or_uuid_list, server_mgmt_vn_name)
        return server_mgmt_ip_name_dict
    # end-def get_si_mgmt_ip_name_dict
    def get_si_mgmt_ip_list(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_mgmt_ip_list = self.nova_server_mgr.get_si_mgmt_ip_list(server_name_or_uuid_list, server_mgmt_vn_name)
        logging.debug("server_mgmt_ip_list: %s " % (server_mgmt_ip_list))
        return server_mgmt_ip_list
    # end-def get_si_mgmt_ip_list
    def get_stack_si_mgmt_ip_list(self, stack_name, server_mgmt_vn_name, image_name=None, nested_depth=3, wait_for_stack_complete=False):
        server_name_list = self.heat_stack_mgr.get_stack_server_name_list(stack_name, image_name, nested_depth, wait_for_stack_complete)
        server_mgmt_ip_list = self.nova_server_mgr.get_si_mgmt_ip_list(server_name_list, server_mgmt_vn_name)
        return server_mgmt_ip_list
    # end-def get_stack_si_mgmt_ip_list

    def get_si_name_mgmtip_dict_list(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_name_mgmtip_dict_list = self.nova_server_mgr.get_si_name_mgmtip_dict_list(server_name_or_uuid_list, server_mgmt_vn_name)
        return server_name_mgmtip_dict_list
    # end-def get_si_name_mgmtip_dict
    def get_stack_si_name_mgmtip_dict_list(self, stack_name, server_mgmt_vn_name, image_name=None, nested_depth=3, wait_for_stack_complete=False):
        logging.debug("stack_name: %s server_mgmt_vn_name: %s image_name: %s nested_depth: %d wait_for_stack_complete: %s" % (stack_name, server_mgmt_vn_name, image_name, nested_depth, wait_for_stack_complete))
        server_name_list = self.heat_stack_mgr.get_stack_server_name_list(stack_name, image_name, nested_depth, wait_for_stack_complete)
        server_name_mgmtip_dict_list = self.nova_server_mgr.get_si_name_mgmtip_dict_list(server_name_list, server_mgmt_vn_name)
        return server_name_mgmtip_dict_list
    # end-def get_stack_si_name_mgmtip_dict_list
    def get_stack_si_name_portlist_dict(self, stack_name, image_name=None, nested_depth=3, wait_for_stack_complete=False):
        server_name_list = self.heat_stack_mgr.get_stack_server_name_list(stack_name, image_name, nested_depth, wait_for_stack_complete)
        server_name_portlist_dict = self.nova_server_mgr.get_si_name_portlist_dict(server_name_list)
        return server_name_portlist_dict
    # end-def get_stack_si_name_portlist_dict
    def get_stack_si_name_portlist_list(self, stack_name, image_name=None, nested_depth=3, wait_for_stack_complete=False):
        server_name_list = self.heat_stack_mgr.get_stack_server_name_list(stack_name, image_name, nested_depth, wait_for_stack_complete)
        server_name_portlist_list = self.nova_server_mgr.get_si_name_portlist_list(server_name_list)
        return server_name_portlist_list
    # end-def get_stack_si_name_portlist_list

    def ping_host_ip(self, host_ip_addr, ping_params=None) :
        logging.debug("host_ip_addr: %s " % (host_ip_addr))
        if (ping_params) :
            ping_cmd = "ping -n -o -c %d %s " % (ping_params["count"], host_ip_addr)
        else :
            ping_cmd = "ping -n -o -c 1 %s " % host_ip_addr
        # end-if ping_params
        logging.debug("ping_cmd: %s " % (ping_cmd))
        response = os.system(ping_cmd)
        return response
    # ennd-def ping_host_ip

    def is_host_reachable(self, host_ip_addr, ping_params=None) :
        response = self.ping_host_ip(host_ip_addr, ping_params) 
        host_reachable = False
        if response == 0: 
            return True
        # end-if response
        logging.debug("host_ip_addr: %s host_reachable: %s " % (host_ip_addr, host_reachable))
        return host_reachable
    # end-def is_host_reachable

    def are_hosts_reachable(self, host_ip_addr_list, ping_params=None) :
        hosts_reachability = {}
        all_hosts_reachable = True
        for host_ip_addr in host_ip_addr_list :
            host_reachable = self.is_host_reachable(host_ip_addr, ping_params)
            hosts_reachability[host_ip_addr] = host_reachable
            if (not host_reachable) :
                all_hosts_reachable = False
            # end-if 
        # end-for 
        hosts_reachability["all"] = all_hosts_reachable
        logging.debug("hosts_reachability: %s" % (json.dumps(hosts_reachability, indent=2)))
        return hosts_reachability
    # end-def are_hosts_reachable

    def wait_for_all_hosts_reachable(self, host_ip_addr_list, ping_params=None, poll_period=30, max_wait_time=60) :
        hosts_reachability = {}

        # TODO: Make this multi-threaded 
        for host_ip_addr in host_ip_addr_list :
            elapsed_time = 0
            while True :
                host_reachable = self.is_host_reachable(host_ip_addr, ping_params)
                hosts_reachability[host_ip_addr] = host_reachable
                if (host_reachable) :
                    break
                # end-if 
                logging.debug("host %s is not reachable by ping - Waiting for %d sec - elapsed_time: %d sec" % (host_ip_addr, poll_period, elapsed_time))
                time.sleep(poll_period)
                elapsed_time += poll_period
                if (elapsed_time > (max_wait_time) ) :
                    error_msg = "Failed to succesfully ping %s in %d seconds" % (host_ip_addr, max_wait_time)
                    logging.error(error_msg)
                    raise RuntimeError(error_msg)
                # end-if elapsed_time
            # end-while
        # end-for 
        logging.debug("hosts_reachability: %s" % (json.dumps(hosts_reachability, indent=2)))
        return hosts_reachability
    # end-def wait_for_all_hosts_reachable

    def is_os_server_reachable(self, server_name_or_uuid, server_mgmt_vn_name) :
        vm_mgmt_ip = self.get_si_mgmt_ip(server_name_or_uuid, server_mgmt_vn_name)
        host_reachable = self.is_host_reachable(vm_mgmt_ip)
        return host_reachable
    # end-def is_os_server_reachable

    def are_os_servers_reachable(self, os_server_name_or_uuid_list, server_mgmt_vn_name) :
        os_servers_reachability = {}
        all_hosts_reachable = True
        for os_server_name_or_uuid in os_server_name_or_uuid_list :
            # TODO: make sure that servers are active before each ping
            host_reachable = self.is_os_server_reachable(os_server_name_or_uuid, server_mgmt_vn_name)
            os_servers_reachability[os_server_name_or_uuid] = host_reachable
            if (not host_reachable) :
                all_hosts_reachable = False
            # end-if 
        # end-for 
        os_servers_reachability["all"] = all_hosts_reachable
        logging.debug("os_servers_reachability: %s" % (json.dumps(os_servers_reachability, indent=2)))
        return os_servers_reachability
    # end-def are_os_servers_reachable

    def test(self, args):
        pass
    # end-def test

    def apply_command(self, args):
        cmd = args["command"]
        logging.debug ("JnprVNFStackCmdHandler: cmd: %s " % (cmd))

        result = {
                "command" : cmd,
                "data" : { 
                    "params" : {},
                    "output" : {}
                    },
                "changed" : False,
                "status" : "Success",
                "message" : "Success",
                "error_message" : ""
                }
        try:
            if (cmd == "test") :
                self.test(args)
            elif (cmd == "get-os-token") :
                token = self.get_token()
                result["data"]["output"] = { "token" : token}
            elif (cmd == "list-stack") :
                self.list_stacks()
            elif (cmd == "wait-for-stack-complete") :
                stack_name = args["stack_name"]
                token = self.wait_till_stack_completion(stack_name)
            elif (cmd == "show-stack") :
                stack_name = args["stack_name"]
                token = self.show_stack(stack_name)
            elif (cmd == "show-stack-server-mgmt-ip-list") :
                stack_name = args["stack_name"]
                server_mgmt_vn_name = args["server_mgmt_vn_name"]
                wait_for_stack_complete = args["wait_for_stack"]
    
                server_image_uuid_name = None
                try:
                    server_image_uuid_name = self.args["server_image_uuid"]
                except Exception as ex: 
                    pass
                # end-try 
                try:
                    server_image_uuid_name = self.args["server_image_name"]
                except Exception as ex: 
                    pass
                # end-try 
                if (server_image_uuid_name == None) :
                    err_msg = "server_image_uuid or server_image_name  must be provided.." 
                    logging.error(err_msg)
                    raise  RuntimeError(err_msg)
                # end-if server_image_uuid_name

                nested_depth = 4
                try :
                    nested_depth = args["nested_depth"]
                except Exception as ex:
                    pass
                # end-try
                server_mgmt_ip_list = self.get_stack_si_mgmt_ip_list(stack_name, server_mgmt_vn_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
                # print "server_mgmt_ip_list (%d): %s " % (len(server_mgmt_ip_list), json.dumps(sserver_mgmt_ip_list,  indent=2))
                result["data"]["params"] = {
                        "stack_name" : stack_name,
                        "server_mgmt_vn_name" : server_mgmt_vn_name,
                        "server_image_uuid_name" : server_image_uuid_name,
                        "wait_for_stack_complete" : wait_for_stack_complete
                        }
                result["data"]["output"] = server_mgmt_ip_list
            elif (cmd == "show-stack-server-uuid-list") :
                stack_name = args["stack_name"]
                wait_for_stack_complete = args["wait_for_stack"]
    
                server_image_uuid_name = None
                try:
                    server_image_uuid_name = self.args["server_image_uuid"]
                except Exception as ex: 
                    pass
                # end-try 
                try:
                    server_image_uuid_name = self.args["server_image_name"]
                except Exception as ex: 
                    pass
                # end-try 
                if (server_image_uuid_name == None) :
                    err_msg = "server_image_uuid or server_image_name  must be provided.." 
                    logging.error(err_msg)
                    raise  RuntimeError(err_msg)
                # end-if server_image_uuid_name
                nested_depth = 4
                try :
                    nested_depth = args["nested_depth"]
                except Exception as ex:
                    pass
                # end-try

                server_uuid_list = self.get_stack_server_uuid_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
                # print "server_uuid_list (%d): %s " % (len(server_uuid_list), json.dumps(server_uuid_list,  indent=2))
                result["data"]["params"] = {
                        "stack_name" : stack_name,
                        "server_image_uuid_name" : server_image_uuid_name,
                        "wait_for_stack_complete" : wait_for_stack_complete
                        }
                result["data"]["output"] = server_uuid_list
            elif (cmd == "show-stack-server-name-list") :
                stack_name = args["stack_name"]
                wait_for_stack_complete = args["wait_for_stack"]

                nested_depth = 4
                try :
                    nested_depth = args["nested_depth"]
                except Exception as ex:
                    pass
                # end-try
    
                server_image_uuid_name = None
                try:
                    server_image_uuid_name = self.args["server_image_uuid"]
                except Exception as ex: 
                    pass
                # end-try 
                try:
                    server_image_uuid_name = self.args["server_image_name"]
                except Exception as ex: 
                    pass
                # end-try 
                if (server_image_uuid_name == None) :
                    err_msg = "server_image_uuid or server_image_name  must be provided.." 
                    logging.error(err_msg)
                    raise  RuntimeError(err_msg)
                # end-if server_image_uuid_name

                server_name_list = self.get_stack_server_name_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
                print "server_name_list (%d): %s " % (len(server_name_list), json.dumps(server_name_list,  indent=2))
                result["data"]["params"] = {
                        "stack_name" : stack_name,
                        "server_image_uuid_name" : server_image_uuid_name,
                        "wait_for_stack_complete" : wait_for_stack_complete
                        }
                result["data"]["output"] = server_name_list
            elif (cmd == "show-stack-server-data-list") :
                stack_name = args["stack_name"]
                wait_for_stack_complete = args["wait_for_stack"]

                server_image_uuid_name = None
                try:
                    server_image_uuid_name = self.args["server_image_uuid"]
                except Exception as ex: 
                    pass
                # end-try 
                try:
                    server_image_uuid_name = self.args["server_image_name"]
                except Exception as ex: 
                    pass
                # end-try 
                if (server_image_uuid_name == None) :
                    err_msg = "server_image_uuid or server_image_name  must be provided.." 
                    logging.error(err_msg)
                    raise  RuntimeError(err_msg)
                # end-if server_image_uuid_name

                nested_depth = 4
                try :
                    nested_depth = args["nested_depth"]
                except Exception as ex:
                    pass
                # end-try

                server_data_list = self.get_stack_server_data_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
                # print "server_data_list (%d): %s " % (len(server_data_list), json.dumps(server_data_list,  indent=2))
                result["data"]["params"] = {
                        "stack_name" : stack_name,
                        "server_image_uuid_name" : server_image_uuid_name,
                        "wait_for_stack_complete" : wait_for_stack_complete
                        }
                result["data"]["output"] = server_data_list
            elif (cmd == "show-stack-server-name-mgmtip-list") :
                stack_name = args["stack_name"]
                server_mgmt_vn_name = args["server_mgmt_vn_name"]
                wait_for_stack_complete = args["wait_for_stack"]

                nested_depth = 4
                try :
                    nested_depth = args["nested_depth"]
                except Exception as ex:
                    pass
                # end-try
    
                server_image_uuid_name = None
                try:
                    server_image_uuid_name = self.args["server_image_uuid"]
                except Exception as ex: 
                    pass
                # end-try 
                try:
                    server_image_uuid_name = self.args["server_image_name"]
                except Exception as ex: 
                    pass
                # end-try 
                # if (server_image_uuid_name == None) :
                #     err_msg = "server_image_uuid or server_image_name  must be provided.." 
                #     logging.error(err_msg)
                #     raise  RuntimeError(err_msg)
                # # end-if server_image_uuid_name

                server_name_mgmtip_dict_list = self.get_stack_si_name_mgmtip_dict_list(stack_name, server_mgmt_vn_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
                # print "server_name_list (%d): %s " % (len(server_name_mgmtip_dict_list), json.dumps(server_name_mgmtip_dict_list,  indent=2))
                result["data"]["params"] = {
                        "stack_name" : stack_name,
                        "server_mgmt_vn_name" : server_mgmt_vn_name,
                        "server_image_uuid_name" : server_image_uuid_name,
                        "wait_for_stack_complete" : wait_for_stack_complete
                        }
                result["data"]["output"] = server_name_mgmtip_dict_list
            elif (cmd == "show-stack-server-name-port-list") :
                stack_name = args["stack_name"]
                # server_mgmt_vn_name = args["server_mgmt_vn_name"]
                wait_for_stack_complete = args["wait_for_stack"]

                nested_depth = 4
                try :
                    nested_depth = args["nested_depth"]
                except Exception as ex:
                    pass
                # end-try
    
                server_image_uuid_name = None
                try:
                    server_image_uuid_name = self.args["server_image_uuid"]
                except Exception as ex: 
                    pass
                # end-try 
                try:
                    server_image_uuid_name = self.args["server_image_name"]
                except Exception as ex: 
                    pass
                # end-try 
                if (server_image_uuid_name == None) :
                    err_msg = "server_image_uuid or server_image_name  must be provided.." 
                    logging.error(err_msg)
                    raise  RuntimeError(err_msg)
                # end-if server_image_uuid_name

                # server_name_portlist_dict = self.get_stack_si_name_portlist_dict(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
                server_name_portlist_list = self.get_stack_si_name_portlist_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)

                result["data"]["params"] = {
                        "stack_name" : stack_name,
                        "server_image_uuid_name" : server_image_uuid_name,
                        "wait_for_stack_complete" : wait_for_stack_complete
                        }
                # result["data"]["output"] = server_name_portlist_dict
                # result["data"]["output"] = server_name_portlist_list
                result["data"]["output"] = server_name_portlist_list
            elif (cmd == 'get-vnf-name'):
                si_vnf_name = None
                stack_name = args.get('stack_name', None)

                os_server_name_or_uuid_list = None
                if (args.get('os_server_uuid') != None) :
                    os_server_name_or_uuid_list = args.get('os_server_uuid', [])
                # end-if 
                if (args.get('os_server_name') != None) :
                    os_server_name_or_uuid_list = args.get('os_server_name', [])
                # end-if 

                if ((stack_name != None) and (stack_name != "")) :
                    server_image_uuid_name = None
                    try:
                        server_image_uuid_name = self.args["server_image_uuid"]
                    except Exception as ex: 
                        pass
                    # end-try 
                    try:
                        server_image_uuid_name = self.args["server_image_name"]
                    except Exception as ex: 
                        pass
                    # end-try 
                    if (server_image_uuid_name == None) :
                        err_msg = "server_image_uuid or server_image_name  must be provided.." 
                        logging.error(err_msg)
                        raise  RuntimeError(err_msg)
                    # end-if server_image_uuid_name

                    nested_depth = 4
                    try :
                        nested_depth = args["nested_depth"]
                    except Exception as ex:
                        pass
                    # end-try
                    # os_server_name_or_uuid_list = self.get_stack_server_name_list(stack_name, server_image_uuid, nested_depth)
                    # logging.debug("os_server_name_or_uuid_list: %s " % (json.dumps(os_server_name_or_uuid_list, indent=2)))
                    si_vnf_name = self.get_si_vnf_name_by_stack(stack_name, server_image_uuid_name, nested_depth)
                else : 
                    if (os_server_name_or_uuid_list and (len(os_server_name_or_uuid_list) > 0)) :
                        si_vnf_name = self.get_si_vnf_name_by_vm(os_server_name_or_uuid_list[0])
                    # end-if os_server_name_or_uuid_list
                # end-if stack_name 
                logging.debug("si_vnf_name: %s " % (si_vnf_name))

                result["data"]["output"] = { "vnf_name" : si_vnf_name }
                result["changed"] = False
            elif (cmd == 'get-vnf-type'):
                si_vnf_name = None
                server_image_uuid = None
                stack_name = args.get('stack_name', None)

                os_server_name_or_uuid_list = None
                if (args.get('os_server_uuid') != None) :
                    os_server_name_or_uuid_list = args.get('os_server_uuid', [])
                # end-if 
                if (args.get('os_server_name') != None) :
                    os_server_name_or_uuid_list = args.get('os_server_name', [])
                # end-if 

                if ((stack_name != None) and (stack_name != "")) :
                    server_image_uuid_name = None
                    try:
                        server_image_uuid_name = self.args["server_image_uuid"]
                    except Exception as ex: 
                        pass
                    # end-try 
                    try:
                        server_image_uuid_name = self.args["server_image_name"]
                    except Exception as ex: 
                        pass
                    # end-try 
                    if (server_image_uuid_name == None) :
                        err_msg = "server_image_uuid or server_image_name  must be provided.." 
                        logging.error(err_msg)
                        raise  RuntimeError(err_msg)
                    # end-if server_image_uuid_name

                    nested_depth = 4
                    try :
                        nested_depth = args["nested_depth"]
                    except Exception as ex:
                        pass
                    # end-try
                    os_server_name_or_uuid_list = self.get_stack_server_name_list(stack_name, server_image_uuid, nested_depth)
                    logging.debug("os_server_name_or_uuid_list: %s " % (json.dumps(os_server_name_or_uuid_list, indent=2)))
                # end-if stack_name 

                if (os_server_name_or_uuid_list and (len(os_server_name_or_uuid_list) > 0)) :
                    si_vnf_type = self.get_si_vnf_type_by_vm(os_server_name_or_uuid_list[0])
                # end-if os_server_name_or_uuid_list
                logging.debug("si_vnf_type: %s " % (si_vnf_type))

                result["data"]["output"] = { "vnf_type" : si_vnf_type }
                result["changed"] = False
            else:
                err_msg = "Unknow os-server admin cmd: '%s' " % cmd
                result["message"] = ""
                result["status"] = "Error"
                result["error_message"] = err_msg
                logging.error(err_msg)
        except Exception as ex:
            err_msg = "Failed to handle  cmd: '%s' - reason: %s - %s" % (cmd, str(ex), sys.exc_info()[0])
            result["status"] = "Error"
            result["error_message"] = err_msg
            result["message"] = ""
            logging.error(err_msg)
            traceback.print_exc()
            raise ex 
        finally:
            pass
        # end-try 
        return result

    # end-def apply_command

# end-class JnprVNFStack:

class JnprVNFStackCmdHandler:

    default_config_file_name = "jedi_vnfstack.conf"
    default_log_file_path = ""


    default_domain_name = "default-domain"
    default_tenant_name = "admin"

    def __init__(self,args_str=None):
        self.process_arguments()

        self.jedi_vnfstack = JnprVNFStack(self.args)


    # end-def __init__

    def get_keystone_v3_creds_by_envvar(self):
        # logging.debug(":..........Start.")

        OS_AUTH_URL = os.environ['OS_AUTH_URL']
        OS_USERNAME =  os.environ['OS_USERNAME']
        OS_PASSWORD = os.environ['OS_PASSWORD']
        OS_TENANT_NAME = os.environ['OS_TENANT_NAME']
        OS_PROJECT_DOMAIN_ID = os.environ['OS_PROJECT_DOMAIN_ID']
        OS_USER_DOMAIN_ID = os.environ['OS_USER_DOMAIN_ID']
        OS_VERSION = "3"

        # OS_HRZN_IPADDR is OS/Horzion GUI IP Adress
        os_auth_url_items = urlparse(OS_AUTH_URL)
        OS_HRZN_IPADDR=os_auth_url_items.hostname

        d = {}
        d['os_auth_url'] = OS_AUTH_URL
        d['os_username'] = OS_USERNAME
        d['os_password'] = OS_PASSWORD
        d['os_project_name'] = OS_TENANT_NAME
        d['os_project_domain_id'] = OS_PROJECT_DOMAIN_ID
        d['os_user_domain_id'] = OS_USER_DOMAIN_ID
        d['os_version'] = OS_VERSION

        # logging.debug(":..........End.")
        return d
    # end-def get_keystone_v3_creds_by_envvar


    def get_keystone_v2_creds_by_envvar(self):
        # logging.debug(":..........Start.")

        OS_AUTH_URL = os.environ['OS_AUTH_URL']
        OS_USERNAME =  os.environ['OS_USERNAME']
        OS_PASSWORD = os.environ['OS_PASSWORD']
        OS_TENANT_NAME = os.environ['OS_TENANT_NAME']
        OS_VERSION = "2"

        # OS_HRZN_IPADDR is OS/Horzion GUI IP Adress
        os_auth_url_items = urlparse(OS_AUTH_URL)
        OS_HRZN_IPADDR=os_auth_url_items.hostname

        d = {}
        d['os_auth_url'] = OS_AUTH_URL
        d['os_username'] = OS_USERNAME
        d['os_password'] = OS_PASSWORD
        d['os_tenant_name'] = OS_TENANT_NAME
        d['os_version'] = OS_VERSION

        # logging.debug(":..........End.")
        return d
    # end-def get_keystone_v2_creds_by_envvar

    def get_default_keystonev2_creds(self, config_node_ip, tenant_name):
        d = {}
        d['os_auth_url'] = 'http://' + config_node_ip + ':5000/v2.0'
        d['os_tenant_name'] = tenant_name
        d['os_username'] = 'admin'
        d['os_password'] = 'contrail123'
        return d
    # end-def get_default_keystonev2_creds

    def process_config_file(self, config_file_path):
        config_options = {}

        # print "JnprVNFStackCmdHandler: config_file_path: %s " % config_file_path
        default_options = {
                # TODO: Remove server_image_uuid after test
                # "server_image_name" : "vSRX_build50-image",
                # "server_image_uuid" : "96d924ac-d609-4029-9e89-04f8607da173",
                "skip_ping" : False,
                "nested_depth" : 3,
                "log_level" : "warning"
                }
        self.config_parser = ConfigParser.ConfigParser(default_options)
        self.config_parser.read(config_file_path)

        # if (not self.config_parser.has_section("default")): 
        #     self.config_parser.add_section("default")
        # # end-if

        config_options = self.config_parser.defaults()

        return config_options
    # end-def process_config_file

    def process_arguments(self):

        cmd_choices = [
                "get-os-token",
                "create-stack", "list-stack", "show-stack", "wait-for-stack", "delete-stack",
                "show-stack-server-uuid-list", "show-stack-server-data-list", "show-stack-server-name-list", "show-stack-server-mgmt-ip-list",
                "show-stack-server-name-mgmtip-list",
                "show-stack-server-name-port-list",
                "get-vnf-type",
                "get-vnf-name",
                "get-vnf-image-name",
                "test"
                ]
        parser = argparse.ArgumentParser(description="Python script to demo REST API ussage for CSO ")

        # parser.add_argument('-cmd', '--command', help="Apply the Action on the Resource", default="show-ns-lsps", choices=cmd_choices)
        # parser.add_argument("--verbosity", help="increase output verbosity")
        parser.add_argument('-cmd', '--command', help="Apply the Action on the Resource", default=cmd_choices[0], choices=cmd_choices)
        parser.add_argument('-d', '--debug', action="store_true", help="Enable debugging")
        # parser.add_argument('--test', action="store_true", help="Invoke unit-test method")
        # OS params
        parser.add_argument('--os-auth-url', help="Keystone Auth URL authentication (OS_AUTH_URL)", default=argparse.SUPPRESS)
        parser.add_argument('--os-username', help="Keystone user-name for authentication (OS_USERNAME)", default=argparse.SUPPRESS)
        parser.add_argument('--os-password', help="Keystone user-password for authentication (OS_PASSWORD)", default=argparse.SUPPRESS)
        parser.add_argument('--os-tenant-name', help="Keystone tenant-namefor authentication (OS_TENANT_NAME)", default=argparse.SUPPRESS)
        parser.add_argument('--os-auth-domain', help="Keystone tenant-namefor authentication (OS_AUTH_DOMAIN)", default="default")
        parser.add_argument('--os-version', help="OpenStack version: v2.0/v3", default=argparse.SUPPRESS)

        # Stack create params
        parser.add_argument('--stack-name', help="Regular expression to match stack names or to be used for stack creation", default=argparse.SUPPRESS)
        parser.add_argument('-e','--environment', help="Heat environment file path", default=argparse.SUPPRESS)
        parser.add_argument('-t','--template-file', help="Heat template file path. Parameter values from file used to create the stack.", default=argparse.SUPPRESS)
        parser.add_argument('--stack-paramaters', action="append", help="Parameter values used to create the stack. This can be specified multiple times", default=argparse.SUPPRESS)
        parser.add_argument('--wait-for-stack', action="store_true", help="Wait until stack goes to CREATE_COMPLETE or CREATE_FAILED", default=True)
        # Stack params
        parser.add_argument('--stack-filter', action="append", help="Filter properties to apply on returned stacks; (repeat to filter on multiple properties)", default=argparse.SUPPRESS)

        # Stack resource params
        parser.add_argument('--stack-resource-filter', action="append", help="Filter parameters to apply on returned resources based on their name, status, type, action, id and physical_resource_id", default=argparse.SUPPRESS)
        parser.add_argument('-n','--nested-depth', help="Depth of nested stacks from which to display resources", default=argparse.SUPPRESS)
        parser.add_argument('--stack-resource-type', help="Filter stack resources by type", default=argparse.SUPPRESS)
        parser.add_argument('--stack-resource-name', help="stack resources name", default=argparse.SUPPRESS)

        parser.add_argument('--server-mgmt-vn-name', help="OS Server Mgmt VN name - ip-address of Server interface on this VN to be used for discovery in Space", default=argparse.SUPPRESS)
        parser.add_argument('--server-image-uuid', help="stack server resources image uuid to be used for filtering server resources", default=argparse.SUPPRESS)
        parser.add_argument('--server-image-name', help="stack server resources image name to be used for filtering server resources", default=argparse.SUPPRESS)
        parser.add_argument('--os-server-name', action='append', help="OS server name", default=argparse.SUPPRESS)
        parser.add_argument('--os-server-uuid', action='append', help="OS server UUID", default=argparse.SUPPRESS)
        parser.add_argument('--skip-ping', action="store_true", help="If true, skip ping of os-server for connectivity check ", default=False)


        cli_args = vars(parser.parse_args())
        print ("cli_args:\n%s\n" % (json.dumps(cli_args,  indent=2)))

        # cache these two elements for future use
        self.parser = parser
        self.cli_args = cli_args

        # Load the config file if given in cli-arg, if not use the program default if it exists
        config_file_path = self.cli_args.get('config_file_path', None)
        if (config_file_path != None) :
            #  check if the config file exist - if not quit
            config_file_exists = os.path.exists(config_file_path) 
            if (not config_file_exists) :
                err_msg = "ERROR: given config file : '{}' does not exists - aborting.".format(config_file_path)
                print (err_msg)
                # raise Exception(err_msg)
                sys.exit(1)
            # end-if
        else :
            config_file_path = self.default_config_file_name
        # end-if
        config_options = self.process_config_file(config_file_path)
        # print ("config_options:\n%s\n" % (json.dumps(config_options,  indent=2)))
        args = copy.deepcopy(config_options)

        os_cred = self.get_keystone_v2_creds_by_envvar()

        # Override config options with CLI args
        for key in cli_args.keys() :
            if key in os_cred.keys() :
                if (self.cli_args[key] != None) :
                    os_cred[key] = self.cli_args[key]
                # end-if 
            else :
                if (self.cli_args[key] != None) :
                    args[key] = self.cli_args[key]
                # end-if 
            # end-if
        # end-for
        # print ("os_cred: %s\n" % (json.dumps(os_cred,  indent=2)))

        bool_props = ["debug"]
        for key in args.keys() :
            if key in bool_props :
                if (str(args[key]).upper() == "TRUE") :
                    args[key] = True
                else :
                    args[key] = False
                # end-if
            # end-if
        # end-for
        # print ("args: %s\n" % (json.dumps(args,  indent=2)))


        # Configure logging
        log_file_path = args.get('log_file', None)
        if (log_file_path == None) :
            log_file_path = self.default_log_file_path
        # end-if

        if args.get('debug', None):
            args["log_level"] = "DEBUG"
        # end-if

        log_level = args.get('log_level', None)
        # print "log_level: %s " % (log_level)
        logging_level = getattr(logging, log_level.upper(), None)
        if (logging_level == None): 
            logging_level = logging.ERROR
            args["log_level"] = "ERROR"
        # end-if
        # print "Log file path : %s (level: %s)" % (log_file_path, logging_level)

        logging_level = getattr(logging, log_level.upper(), None)
        if (log_file_path == "") :
            print "Logging on Stdout (level: %d (debug: %d))" % (logging_level, logging.DEBUG)
            logging.basicConfig(stream=sys.stdout, level=logging_level, 
                format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S")
        else :
            print "Logging on file: %s (level: %d)" % (log_file_path, logging_level)
            logging.basicConfig(filename=log_file_path, level=logging_level, filemode='w',
                format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S")
        # end-if
        # logging.debug("args:\n%s\n" % (json.dumps(args,  indent=2)))
    
        # Validate Params
        if not os_cred.get('os_auth_url'):
            print("\nSpecify the os_auth_url or in OS_AUTH_URL environment variable\n")
            parser.print_help()
            sys.exit(0)
        # end-if
        if not os_cred.get('os_username'):
            print("\nSpecify user argument at command or in OS_USERNAME environment variable\n")
            parser.print_help()
            sys.exit(0)
        # end-if
        if not os_cred.get('os_password'):
            print("\nSpecify password argument at command or in OS_PASSWORD environment variable\n")
            parser.print_help()
            sys.exit(0)
        # end-if
        args["os_cred"] = os_cred

        self.args = args
        logging.debug("args:\n%s\n" % (json.dumps(self.args,  indent=2)))

        # if True :
        #     sys.exit(0)
        # return self.args
    # end-def process_arguments

    def test(self, args):
        xxx = "yyy"
    # end-def test

    def apply_command(self):
        result = self.jedi_vnfstack.apply_command(self.args)
        print "result : %s " % (json.dumps(result,  indent=2))
    # end-def apply_command`



# end-class JnprVNFStackCmdHandler:


def main(args_str=None):
    jnpr_vnfstack_cmd_handler = JnprVNFStackCmdHandler(args_str)
    jnpr_vnfstack_cmd_handler.apply_command()
# end-def main

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    sys.exit(main())

