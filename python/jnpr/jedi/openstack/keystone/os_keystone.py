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
# Description   : A python script that shows 
#
# Last Modified : 17-October-2017
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

import time 

from netaddr import *
from urlparse import urlparse


import uuid
# import logging.config

import json

# Data processing libraries
from jinja2 import Template
import yaml

from keystoneauth1.identity import v2
from keystoneauth1 import session
from keystoneclient.v2_0 import Client as Keystone_Client

# from novaclient.client import Client as Nova_Client
# from heatclient.client import Client as Heat_Client

usage = "usage: os_stack.py \n\
    \n\
Examples:  \n\
    python os_stack.py --cmd stack-create --stack-name <stack-name> --stack-data-file-path <stack_data_file_path> \n\
    python os_stack.py --cmd stack-list \n\
    python os_stack.py --cmd stack-show --stack-name <stack-name> \n\
    python os_stack.py --cmd stack-delete --stack-name <stack-name> \n\
    python os_stack.py --cmd resource-list --stack-name <stack-name>  \n\
    python os_stack.py --cmd resource-show --stack-name <stack-name> --resource-name <resource-name> \n\
 "

class KeystoneMgr:


    def __init__(self, args):

        logging.debug("..........Start.")

        # cred = get_keystone_creds(config_node_ip, tenant_name)
        os_cred = args["os_cred"]
        logging.debug("os_cred:%s " % (json.dumps(os_cred,  indent=2)))

        # auth = v2.Password(**cred)
        auth = v2.Password(
                # connection_pool=True,
                username=os_cred["os_username"],
                password=os_cred["os_password"],
                tenant_name=os_cred["os_tenant_name"],
                auth_url=os_cred["os_auth_url"]
                )
        self.session = session.Session(auth=auth)
        self.keystone = Keystone_Client(session=self.session)

        tenant_list = self.keystone.tenants.list()
        logging.debug("auth_ref: %s token: %s" % (self.keystone.auth_ref, self.keystone.auth_token))
        logging.debug("..........10.")

        if False :
            self.keystone = Keystone_Client(
                username=os_cred["os_username"],
                password=os_cred["os_password"],
                tenant_name=os_cred["os_tenant_name"],
                auth_url=os_cred["os_auth_url"]
                )
            logging.debug("..........20.")
        # end-if

        logging.debug("..........End.")
    # end-def __init__

    def get_token(self):
        token = self.keystone.auth_token
        return token
    # end-def get_token

# end-class KeystoneMgr:

class KeystoneMgrCmdHandler:

    default_domain_name = "default-domain"
    default_tenant_name = "admin"

    default_config_file_name = "os_keystone.conf"
    default_log_file_path = ""

    def __init__(self,args_str=None):
        self.process_arguments()
        self.keystone_mgr = KeystoneMgr(self.args)
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

        # print "KeystoneMgrCmdHandler: config_file_path: %s " % config_file_path
        default_options = {
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
                "get-token",
                "test"
                ]
        parser = argparse.ArgumentParser(description="Python script to demo REST API ussage for CSO ")

        # parser.add_argument('-cmd', '--command', help="Apply the Action on the Resource", default="show-ns-lsps", choices=cmd_choices)
        parser.add_argument('-cmd', '--command', help="Apply the Action on the Resource", default=cmd_choices[0], choices=cmd_choices)
        parser.add_argument('-d', '--debug', action="store_true", help="Enable debugging")
        parser.add_argument('--test', action="store_true", help="Invoke unit-test method")
        # OS params
        parser.add_argument('--os-auth-url', help="Keystone Auth URL authentication (OS_AUTH_URL)", default=argparse.SUPPRESS)
        parser.add_argument('--os-username', help="Keystone user-name for authentication (OS_USERNAME)", default=argparse.SUPPRESS)
        parser.add_argument('--os-password', help="Keystone user-password for authentication (OS_PASSWORD)", default=argparse.SUPPRESS)
        parser.add_argument('--os-tenant-name', help="Keystone tenant-namefor authentication (OS_TENANT_NAME)", default=argparse.SUPPRESS)
        parser.add_argument('--os-auth-domain', help="Keystone tenant-namefor authentication (OS_AUTH_DOMAIN)", default="default")
        parser.add_argument('--os-version', help="OpenStack version: v2.0/v3", default=argparse.SUPPRESS)

        cli_args = vars(parser.parse_args())
        # print ("cli_args:\n%s\n" % (json.dumps(cli_args,  indent=2)))

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
                args[key] = self.cli_args[key]
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
        # else :
        # end-if

        log_level = args.get('log_level', None)
        # print "log_level: %s " % (log_level)
        logging_level = getattr(logging, log_level.upper(), None)
        if (logging_level == None): 
            logging_level = logging.ERROR
        # end-if
        # print "Log file path : %s (level: %s)" % (log_file_path, logging_level)

        if args.get('debug', None):
            logging_level = logging.DEBUG
        # else:
        #     logging_level = logging.CRITICAL
        # end-if
        # print "Log file path : %s (level: %s)" % (log_file_path, logging_level)

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
        logging.debug("args:\n%s\n" % (json.dumps(args,  indent=2)))
    
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
        # logging.debug("args:\n%s\n" % (json.dumps(self.args,  indent=2)))

        # sys.exit(0)
        # return self.args
    # end-def process_arguments

    def test(self, args):
        xxx = "yyy"
    # end-def test

    def apply_command(self):
        cmd = self.args["command"]
        logging.debug ("KeystoneMgrCmdHandler: cmd: %s " % (cmd))

        if (cmd == "test") :
            self.test(args)
        elif (cmd == "get-token") :
            token = self.keystone_mgr.get_token()
            print "token: %s " % token
        else :
            logging.error("Invalid command: %s", cmd)
        # end-if

    # end-def apply_command

# end-class KeystoneMgrCmdHandler:

def main(args_str=None):
    keystone_mgr_cmd_handler = KeystoneMgrCmdHandler(args_str)
    keystone_mgr_cmd_handler.apply_command()
# end-def main

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    sys.exit(main())

