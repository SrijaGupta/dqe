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
# Description   : A python script that shows nova client CRUD API usage for servers (VM)
#                 based on the code example here : https://docs.openstack.org/python-novaclient/latest/reference/api/index.html
#                 Also in https://github.com/openstack/python-novaclient/blob/master/novaclient/shell.py
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


from netaddr import *
from urlparse import urlparse


import uuid
import logging.config

import json

# Data processing libraries
from jinja2 import Template
import yaml

from keystoneauth1.identity import v2
from keystoneauth1 import session
from keystoneclient.v2_0 import Client as Keystone_Client

from novaclient.client import Client as Nova_Client
from glanceclient.client import Client as Glance_Client

from jnpr.jedi.openstack.keystone.os_keystone import KeystoneMgr

debug = False
debug = True

usage = "usage: os_server.py \n\
    \n\
Examples:  \n\
    python os_server.py --cmd create --name <name> --image <image-name>  \n\
    python os_server.py --cmd list \n\
    python os_server.py --cmd show --name <name> \n\
    python os_server.py --cmd delete --name <name> \n\
 "

class NovaServerMgr:

    def __init__(self, keystone_mngr):
        logging.debug("..........Start.")

        self.keystone_mngr = keystone_mngr

        self.session = keystone_mngr.session
        self.keystone = keystone_mngr.keystone

        self.nova = Nova_Client("2.0", session=self.session)
        self.glance = Glance_Client("2", session=self.session)

        logging.debug("..........End.")
    # end-def __init__


    def get_token(self):
        token = self.keystone.auth_token
        return token
    # end-def get_token

    def get_image(self, image_uuid):
        logging.debug("image_uuid: %s" % (image_uuid))
        if (image_uuid == None):
            msg = "ERROR: image_uuid is required."
            raise RuntimeError(msg);
        # end-if image_uuid

        image = self.glance.images.get(image_uuid)
        logging.debug("image: %s" % (image))
        return image
    # end-def get_image

    def get_image_by_name(self, image_name):
        logging.debug("image_name: %s" % (image_name))
        if (image_name == None):
            msg = "ERROR: image_name is required."
            raise RuntimeError(msg);
        # end-if image_name


        image_list = []
        search_opts = {
                "name" : ("%s" % image_name)
                }
        # image_generator_list = self.glance.images.list()
        image_generator_list = self.glance.images.list(filters=search_opts)
        for image in image_generator_list:
            # print image
            image_list.append(image)
        # end-for image
        logging.debug("image_list: %s" % (image_list))

        image = None
        if (len(image_list) == 0) :
            # check if image_name is uuid
            try :
                image = self.get_image(image_name)
                image_list.append(image)
            except Exception as ex:
                pass
            # end-try
        # end-if 

        if (len(image_list) != 1) :
            err_msg = "Error: Unable to resolve name:%s to unique uuid - received %s" % (image_name, image_list)
            logging.error(err_msg)
            raise RuntimeError(err_msg);
        # end-if 

        image = image_list[0]
        return image
    # end-def get_image_by_name
    def get_image_uuid_by_name(self, image_name):
        image = self.get_image_by_name(image_name)
        return image.id
    # end-def get_image_uuid_by_name

    def create(self, **kwargs):
        name = kwargs["name"]
        vm_ram = kwargs["vm_ram"]
        fl = nova.flavors.find(ram=vm_ram)
        server = self.nova.servers.create(name, flavor=fl)
        return server
    # end-def create


    def find(self, **kwargs):
        search_opts = {}
        if (kwargs.get("ip", None) != None) :
            search_opts["ip"] = kwargs.get("ip")
        # end-if 
        if (kwargs.get("image", None) != None) :
            image_name = kwargs.get("image")
            # search_opts["image"] = kwargs.get("image")
            image_uuid = self.get_image_uuid_by_name(image_name)
            if (image_uuid == None) :
                err_msg = "Error: Unable to resolve name:%s to unique uuid - received %s" % (image_name, image_list)
                logging.error(err_msg)
                raise RuntimeError(err_msg);
            # end-if
            search_opts["image"] = image_uuid
        # end-if 
        if (kwargs.get("name", None) != None) :
            # search_opts["name"] = ("^%s$" %  kwargs.get("name"))
            search_opts["name"] = ("^%s$" %  kwargs.get("name"))
        # end-if 
        list_opts = {
                # "detailed" : False,
                "search_opts" : search_opts,
                }
        logging.debug("list_opts: %s" % (json.dumps(list_opts, indent=2)))

        server_list = self.nova.servers.list(**list_opts)
        logging.debug("server_list: %s" % (server_list))
        return server_list
    # end-def find

    def get(self, vm_uuid):
        logging.debug("vm_uuid: %s" % (vm_uuid))
        if (vm_uuid == None):
            msg = "ERROR: vm_uuid is required."
            raise RuntimeError(msg);
        # end-if vm_uuid

        server = self.nova.servers.get(vm_uuid)
        logging.debug("server: %s" % (server))
        return server
    # end-def get

    def get_by_name(self, name):
        search_opts = {
                "name" : ("^%s$" % name)
                }
        server_list = self.find(**search_opts)
        logging.debug("server_list: %s" % (server_list))
        if (len(server_list) != 1) :
            err_msg = "Error: Unable to resolve name:%s to unique uuid - received %s" % (name, server_list)
            raise RuntimeError(err_msg);
        # end-if 
        server = server_list[0]
        return server
    # end-def get

    def delete(self, vm_uuid):
        logging.debug("vm_uuid: %s" % (vm_uuid))
        server = self.get(vm_uuid)
        server.delete()
    # end-def delete
    def delete_by_name(self, name):
        logging.debug("name: %s" % (name))
        server = self.get_by_name(name)
        server.delete()
    # end-def delete

    def dump_server(self, server):
        if (server == None):
            return
        # end-if server
        server_dict = server.to_dict()
        print "server_dict:%s " % (json.dumps(server_dict, indent=2))
    # end-def dump_server

    def show_server(self, name):
        # server = self.get_by_name(name)
        server = None
        try :
            server = self.get(name)
        except Exception as ex :
            logging.error("Failed to get VM by id: %s - reason: %s" % (name, str(ex)))
            server = self.get_by_name(name)
        # end-try 
        if (server == None) :
            err_msg = "ERROR: Failed to get VM by name/id: %s" % (name)
            logging.error(err_msg)
        # end-if
        self.dump_server(server)
    # end-def show_server

    def get_si_info(self, uuid_or_name):
        server = None
        try :
            server = self.get(uuid_or_name)
        except Exception as ex :
            logging.debug("Failed to get VM by id: %s - reason: %s - ignoring" % (uuid_or_name, str(ex)))
            server = self.get_by_name(uuid_or_name)
        # end-try 
        if (server == None) :
            err_msg = "ERROR: Failed to get VM by id: %s" % (uuid_or_name)
            logging.error(err_msg)
            raise RuntimeError(err_msg);
        # end-if
        server_dict = server.to_dict()

        vm_interface_list = server.interface_list() 
        # logging.debug("uuid_or_name: %s interfaces: %s\n" % (uuid_or_name, json.dumps(vm_interface_list, indent=2)))
        logging.debug("uuid_or_name: %s interfaces: %s\n" % (uuid_or_name, vm_interface_list))
        vm_if_dict_list = []
        for vm_if in vm_interface_list :
            vm_if_dict = vm_if.to_dict()
            logging.debug("vm_if_dict: %s\n" % (json.dumps(vm_if_dict, indent=2)))
            vm_if_dict_list.append(vm_if_dict)
        # end-for 

        vm_ips = self.nova.servers.ips(server)
        logging.debug("uuid_or_name: %s ips : %s\n" % (uuid_or_name, json.dumps(vm_ips, indent=2)))

        vm_metadata = {}
        if (server_dict["metadata"]) :
            vm_metadata = server_dict["metadata"]
        # end-if 

        vn_ip_map = {}
        si_info = {
                "id"        : server_dict["id"],
                "name"      : server_dict["name"],
                "image_id"  : server_dict["image"]["id"],
                "av_zone"   : server_dict["OS-EXT-AZ:availability_zone"],
                "status"    : server_dict["status"],
                "interface_list" : vm_if_dict_list, 
                "metadata" : vm_metadata, 
                "vn_ip_map" : vm_ips
                }
        # self.dump_server(server)
        logging.debug("uuid_or_name: %s si_info: %s\n" % (uuid_or_name, json.dumps(si_info, indent=2)))
        return si_info
    # end-def get_si_info

    def get_si_mgmt_ip(self, server_name_or_uuid, server_mgmt_vn_name):
        logging.debug("server_name_or_uuid: %s server_mgmt_vn_name: %s " % (server_name_or_uuid, server_mgmt_vn_name))
        vm_si_info = self.get_si_info(server_name_or_uuid)
        logging.debug("vm_si_info: %s" % (json.dumps(vm_si_info, indent=2)))

        vm_mgmt_ip = None
        try :
            # TODO: We assume only one subnet per VN, if not we pick the first one
            # vm_mgmt_ip = vm_si_info["vn_ip_map"][server_mgmt_vn_name][0]["addr"]
            vn_ip_map = vm_si_info["vn_ip_map"]
            vm_mgmt_ip = vn_ip_map[server_mgmt_vn_name][0]["addr"]
        except Exception as ex :
            vm_si_info_str = json.dumps(vm_si_info, indent=2)
            error_msg = "Couldn;t resolve ip-address of server : '%s' for VN: '%s' - reason: '%s(%s)' - vm_si_info_str: %s" % (server_name_or_uuid, server_mgmt_vn_name, str(ex), sys.exc_info()[0], vm_si_info_str)
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        # end-try 
        logging.debug("vm_mgmt_ip: %s " % (vm_mgmt_ip))
        if (vm_mgmt_ip == None) :
            error_msg = "Couldn;t resolve ip-address of server : %s for VN: %s " % (server_name_or_uuid, server_mgmt_vn_name)
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        # end-if vm_mgmt_ip
        return vm_mgmt_ip
    # end-def get_si_mgmt_ip

    def get_si_subnet_ip(self, server_name_or_uuid, subnet_uuid):
        logging.debug("server_name_or_uuid: %s server_mgmt_vn_name: %s " % (server_name_or_uuid, server_mgmt_vn_name))
        vm_si_info = self.get_si_info(server_name_or_uuid)
        logging.debug("vm_si_info: %s" % (json.dumps(vm_si_info, indent=2)))

        vm_subnet_ip = None
        try :
            for port in vm_si_info.interface_list :
                for fixed_ip in port.fixed_ips :
                    if (fixed_ip.subnet_id == subnet_uuid) :
                        return fixed_ip
                    # end-if 
                # end-for fixed_ip
            # end-for port 
        except Exception as ex :
            vm_si_info_str = json.dumps(vm_si_info, indent=2)
            error_msg = "Couldn;t resolve ip-address of server : '%s' for subnet_uuid: '%s' - reason: '%s(%s)' - vm_si_info_str: %s" % (server_name_or_uuid, subnet_uuid, str(ex), sys.exc_info()[0], vm_si_info_str)
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        # end-try 
        logging.debug("vm_mgmt_ip: %s " % (vm_mgmt_ip))
        if (vm_subnet_ip == None) :
            error_msg = "Couldn't resolve ip-address of server : %s for subnet-uuid: %s " % (server_name_or_uuid, subnet_uuid)
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        # end-if vm_subnet_ip
        return vm_subnet_ip
    # end-def get_si_subnet_ip

    def Xget_si_mgmt_ip_list(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_mgmt_ip_list = []
        server_mgmt_ip_name_dict = {}
        for server_name_or_uuid in server_name_or_uuid_list : 
            server_mgmt_ip = self.get_si_mgmt_ip(server_name_or_uuid, server_mgmt_vn_name)
            if (server_mgmt_ip == None) :
                err_msg = "Couldn't find the mgmt-ip for server : %s" % (server_name_or_uuid)
                logging.error(err_msg)
                raise RuntimeError(err_msg)
            # end-if server_mgmt_ip
            logging.debug("server_name_or_uuid: %s server_mgmt_ip: %s " % (server_name_or_uuid, server_mgmt_ip))
            server_mgmt_ip_list.append(server_mgmt_ip)
            server_mgmt_ip_name_dict[server_mgmt_ip] = server_uuid
        # end-for 
        logging.debug("server_mgmt_ip_list: %s " % (server_mgmt_ip_list))
        return server_mgmt_ip_list
    # end-def get_si_mgmt_ip_list

    def get_si_mgmt_ip_name_dict(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_mgmt_ip_name_dict = {}
        for server_name_or_uuid in server_name_or_uuid_list : 
            server_mgmt_ip = self.get_si_mgmt_ip(server_name_or_uuid, server_mgmt_vn_name)
            if (server_mgmt_ip == None) :
                err_msg = "Couldn't find the mgmt-ip for server : %s" % (server_name_or_uuid)
                logging.error(err_msg)
                raise RuntimeError(err_msg)
            # end-if server_mgmt_ip
            logging.debug("server_name_or_uuid: %s server_mgmt_ip: %s " % (server_name_or_uuid, server_mgmt_ip))
            server_mgmt_ip_name_dict[server_mgmt_ip] = server_name_or_uuid
        # end-for 
        logging.debug("server_mgmt_ip_name_dict: %s " % (server_mgmt_ip_name_dict))
        return server_mgmt_ip_name_dict
    # end-def get_si_mgmt_ip_name_dict
    def get_si_mgmt_ip_list(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_mgmt_ip_name_dict = self.get_si_mgmt_ip_name_dict(server_name_or_uuid_list, server_mgmt_vn_name)
        logging.debug("si_mgmt_ip_list: %s " % (server_mgmt_ip_name_dict.keys()))
        return server_mgmt_ip_name_dict.keys()
    # ed-def get_si_mgmt_ip_list

    def get_si_name_mgmtip_dict_list(self, server_name_or_uuid_list, server_mgmt_vn_name):
        server_name_mgmtip_dict_list = []
        for server_name_or_uuid in server_name_or_uuid_list : 
            server_name_mgmtip_dict = {}
            server_mgmt_ip = self.get_si_mgmt_ip(server_name_or_uuid, server_mgmt_vn_name)
            if (server_mgmt_ip == None) :
                err_msg = "Couldn't find the mgmt-ip for server : %s" % (server_name_or_uuid)
                logging.error(err_msg)
                raise RuntimeError(err_msg)
            # end-if server_mgmt_ip
            logging.debug("server_name_or_uuid: %s server_mgmt_ip: %s " % (server_name_or_uuid, server_mgmt_ip))

            server_name_mgmtip_dict["name"] = server_name_or_uuid
            server_name_mgmtip_dict["vn_name"] = server_mgmt_vn_name
            server_name_mgmtip_dict["ip_address"] = server_mgmt_ip
            server_name_mgmtip_dict_list.append(server_name_mgmtip_dict)
        # end-for 
        logging.debug("server_name_mgmtip_dict_list: %s " % (server_name_mgmtip_dict_list))
        return server_name_mgmtip_dict_list
    # end-def get_si_name_mgmtip_dict_list

    def get_si_name_portlist_dict(self, server_name_or_uuid_list):
        server_name_portlist_dict = {}
        for server_name_or_uuid in server_name_or_uuid_list : 
            server_name_mgmtip_dict = {}
            si_info = self.get_si_info(server_name_or_uuid)
            if (si_info == None) :
                err_msg = "Couldn't find the mgmt-ip for server : %s" % (server_name_or_uuid)
                logging.error(err_msg)
                raise RuntimeError(err_msg)
            # end-if server_mgmt_ip
            logging.debug("server_name_or_uuid: %s si_info: %s\n" % (server_name_or_uuid, json.dumps(si_info, indent=2)))
            server_name_portlist_dict[server_name_or_uuid] = si_info["interface_list"]
        # end-for 
        logging.debug("server_name_portlist_dict: %s " % (json.dumps(server_name_portlist_dict, indent=2) ))
        return server_name_portlist_dict
    # end-def get_si_name_portlist_dict

    def get_si_name_portlist_list(self, server_name_or_uuid_list):
        server_name_portlist_list = []
        for server_name_or_uuid in server_name_or_uuid_list : 
            si_info = self.get_si_info(server_name_or_uuid)
            if (si_info == None) :
                err_msg = "Couldn't find the mgmt-ip for server : %s" % (server_name_or_uuid)
                logging.error(err_msg)
                raise RuntimeError(err_msg)
            # end-if server_mgmt_ip
            logging.debug("server_name_or_uuid: %s si_info: %s\n" % (server_name_or_uuid, json.dumps(si_info, indent=2)))
            name_portlist_dict = {}
            name_portlist_dict["name"] = server_name_or_uuid
            name_portlist_dict["interface_list"] = si_info["interface_list"]
            # name_portlist_dict["vn_ip_map"] = si_info["vn_ip_map"]
            server_name_portlist_list.append(name_portlist_dict)
            # server_name_portlist_list.append(si_info)
        # end-for 
        logging.debug("server_name_portlist_list: %s " % (json.dumps(server_name_portlist_list, indent=2) ))
        return server_name_portlist_list
    # end-def get_si_name_portlist_list

    def ping_host_ip(host_ip_addr) :
        response = os.system("ping -n 1 " + hostname)
        return response
    # ennd-def ping_host_ip


    def find_servers(self, **kwargs):
        servers = self.find(**kwargs)
        server_list = [] 
        for server in servers: 
            server_list.append(server.to_dict())
        # end-for server
        logging.debug("server_list: %s" % (server_list))
        return server_list
    # end-def find_servers

    def find_servers_by_vnf_image_name(self, **kwargs):
        vnf_name = kwargs["vnf_name"]
        server_list = self.find_servers(**kwargs)

        logging.debug("vnf_name: %s" % (vnf_name))

        vnf_server_list = []
        for server in server_list : 
            if (server.get("metadata") == None):
                logging.error("Found no meta-data for %s" % server["name"])
                continue
            # end-if server
            server_vnf_name = server["metadata"]["vnf_name"]
            if (server["metadata"]["vnf_name"] == vnf_name) :
                vnf_server_list.append(server)
            # end-if vm_metadata
        # end-for server
        logging.debug("vnf_server_list: %s" % (vnf_server_list))
        return vnf_server_list
    # end-def find_servers_by_vnf_image_name

    def list_servers(self, **kwargs):
        server_list = self.find_servers(**kwargs)
        print "server_list:%s " % (json.dumps(server_list, indent=2))
    # end-def list_servers
    def list_servers_by_vnf_image_name(self, **kwargs):
        vnf_server_list = self.find_servers_by_vnf_image_name(**kwargs)
        print "vnf_server_list:%s " % (json.dumps(vnf_server_list, indent=2))
    # end-def list_servers

# end-class NovaServerMgr:

class NovaServerMgrCmdHandler:

    default_domain_name = "default-domain"
    default_tenant_name = "admin"

    default_config_file_name = "os_server.conf"
    default_log_file_path = ""

    def __init__(self,args_str=None):
        self.process_arguments()

        self.keystone_mgr = KeystoneMgr(self.args)
        self.nova_server_mgr = NovaServerMgr(self.keystone_mgr)
    # end-def __init__

    def get_keystone_v3_creds_by_envvar(self):
        logging.debug(":..........Start.")

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

        logging.debug(":..........End.")
        return d
    # end-def get_keystone_v3_creds_by_envvar


    def get_keystone_v2_creds_by_envvar(self):
        logging.debug(":..........Start.")

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

        logging.debug(":..........End.")
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

        # print "NovaServerMgrCmdHandler: config_file_path: %s " % config_file_path
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
                "show-image", "show-image-by-name", "show-image-uuid-by-name",
                "list", "show",
                "find-by-image-name", "find-by-vnf-image-name",
                "create", "delete",
                "gen-si-info",
                "test"
                ]
        parser = argparse.ArgumentParser(description="Python script to demo REST API ussage for CSO ")

        # parser.add_argument('-cmd', '--command', help="Apply the Action on the Resource", default="show-ns-lsps", choices=cmd_choices)
        parser.add_argument('-cmd', '--command', help="Apply the Action on the Resource", default=cmd_choices[0], choices=cmd_choices)
        parser.add_argument('-d', '--debug', action="store_true", help="Enable debugging")
        parser.add_argument('--test', action="store_true", help="Invoke unit-test method")


        # OS Params
        parser.add_argument('--os-auth-url', help="Keystone Auth URL authentication (OS_AUTH_URL)", default=argparse.SUPPRESS)
        parser.add_argument('--os-username', help="Keystone user-name for authentication (OS_USERNAME)", default=argparse.SUPPRESS)
        parser.add_argument('--os-password', help="Keystone user-password for authentication (OS_PASSWORD)", default=argparse.SUPPRESS)
        parser.add_argument('--os-tenant-name', help="Keystone tenant-namefor authentication (OS_TENANT_NAME)", default=argparse.SUPPRESS)
        parser.add_argument('--os-auth-domain', help="Keystone tenant-namefor authentication (OS_AUTH_DOMAIN)", default="default")
        parser.add_argument('--os-version', help="OpenStack version: v2.0/v3", default=argparse.SUPPRESS)

        # Server create params
        parser.add_argument('--name', help="Regular expression to match names or to be used for creation", default=argparse.SUPPRESS)
        parser.add_argument('--image', help="Search by image (name or ID)", default=argparse.SUPPRESS)
        parser.add_argument('--vnf-name', help="VNF name embedded in metadata of server", default=argparse.SUPPRESS)
        parser.add_argument('--vm-ram', help="RAM to be used to find flavor", default=argparse.SUPPRESS)
        parser.add_argument('--vm-flavor', help="Flavor to be used to create server", default=argparse.SUPPRESS)
        # Server params
        parser.add_argument('--ip', help="Regular expression to match IP addresses", default=argparse.SUPPRESS)
        parser.add_argument('--host', help="Search by hostname", default=argparse.SUPPRESS)
        parser.add_argument('--server', help="Server (name or ID)", default=argparse.SUPPRESS)

        cli_args = vars(parser.parse_args())
        # print ("cli_args:\n%s\n" % (json.dumps(cli_args, indent=2)))

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
        # print ("config_options:\n%s\n" % (json.dumps(config_options, indent=2)))
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
        # print ("os_cred: %s\n" % (json.dumps(os_cred, indent=2)))

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
        # print ("args: %s\n" % (json.dumps(args, indent=2)))


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
            print "Logging on Stdout (level: %d)" % logging_level
            logging.basicConfig(stream=sys.stdout, level=logging_level, filemode='w',
                format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S")
        else :
            print "Logging on file: %s (level: %d)" % (log_file_path, logging_level)
            logging.basicConfig(filename=log_file_path, level=logging_level, filemode='w',
                format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S")
        # end-if
        logging.debug("args:\n%s\n" % (json.dumps(args, indent=2)))
    
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
        # logging.debug("args:\n%s\n" % (json.dumps(self.args, indent=2)))

        # sys.exit(0)
        # return self.args
    # end-def process_arguments

    def server_create(self, args):
        server= None
        return
    # end-def server_create
    def server_list(self, args):
        server_list = []
        return
    # end-def server_list

    def test(self, args):
        xxx = "yyy"
    # end-def test

    def apply_command(self):
        cmd = self.args["command"]
        logging.debug ("NovaServerMgrCmdHandler: cmd: %s " % (cmd))

        if (cmd == "test") :
            self.test(args)
        elif (cmd == "get-token") :
            token = self.nova_server_mgr.get_token()
            print "token: %s " % token
        elif (cmd == "create") :
            self.nova_server_mgr.create(self.args)
        elif (cmd == "list") :
            self.nova_server_mgr.list_servers(**self.args)
        elif (cmd == "find") :
            self.nova_server_mgr.list_servers(**self.args)
        elif (cmd == "find-by-image-name") :
            image_name = self.args["image"]
            self.nova_server_mgr.list_servers(**self.args)
        elif (cmd == "find-by-vnf-image-name") :
            image_name = self.args["image"]
            vnf_name = self.args["vnf_name"]
            self.nova_server_mgr.list_servers_by_vnf_image_name(**self.args)
        elif (cmd == "show") :
            name = self.args["name"]
            self.nova_server_mgr.show_server(name)
        elif (cmd == "delete") :
            name = self.args["name"]
            self.nova_server_mgr.delete_server(name)
        elif (cmd == "gen-si-info") :
            name = self.args["name"]
            vm_si_info = self.nova_server_mgr.get_si_info(name)
            print "%s" % (json.dumps(vm_si_info, indent=2))
        elif (cmd == "show-image") :
            name = self.args["image"]
            image = self.nova_server_mgr.get_image(name)
            print "image:%s " % (json.dumps(image, indent=2))
        elif (cmd == "show-image-by-name") :
            name = self.args["image"]
            image = self.nova_server_mgr.get_image_by_name(name)
            print "image:%s " % (json.dumps(image, indent=2))
        elif (cmd == "show-image-uuid-by-name") :
            image_name = self.args["image"]
            image_uuid = self.nova_server_mgr.get_image_uuid_by_name(image_name)
            print "image_name: %s image_uuid:%s " % (image_name, image_uuid)
        else :
            logging.error("Invalid command: %s", cmd)
        # end-if

    # end-def apply_command

# end-class NovaServerMgrCmdHandler:

def main(args_str=None):
    nova_server_mgr_cmd_handler = NovaServerMgrCmdHandler(args_str)
    nova_server_mgr_cmd_handler.apply_command()
# end-def main

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    sys.exit(main())

