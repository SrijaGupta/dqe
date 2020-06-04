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
from heatclient.client import Client as Heat_Client
from glanceclient.client import Client as Glance_Client

from jnpr.jedi.openstack.keystone.os_keystone import KeystoneMgr

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

class HeatStackMgr:

    def __init__(self, keystone_mngr):
        self.keystone_mngr = keystone_mngr

        self.session = keystone_mngr.session
        self.keystone = keystone_mngr.keystone

        self.heat = Heat_Client('1', session=self.session)

        self.glance = Glance_Client("2", session=self.session)

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
            err_msg = "Error: Unable to resolve name:%s to unique uuid - received %s(%d) images." % (image_name, image_list, len(image_list))
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

    def create(self, kwargs):
        stack = None

        f = open(kwargs['template'])
        template_data = f.read()

        e = open(kwargs['environment'])
        env_data = e.read()

        param_data = kwargs.get('parameters', [])
    
        stack_name = kwargs['name']
        tx = {
            "files": {},
            "disable_rollback": "true",
            "stack_name": stack_name,
            "template": template_data,
            "parameters": param_data,
            "environment": env_data
        }
        # logging.debug("stack_params: %s" % (json.dumps(tx,  indent=2)))
    
        stack = self.heat.stacks.create(**tx)
        if (kwargs["wait"]) :
            stack = self.wait_till_stack_completion(stack_name)
        # end-if
        return stack
    # end-def create

    def find(self, **kwargs):
        search_opts = {}


        if (kwargs.get("nested", None) != None) :
            search_opts["nested"] = True
        # end-if 

        stack_filters = {}
        if (kwargs.get("stack_name", None) != None) :
            stack_filters["stack_name"] = kwargs.get("stack_name")
        # end-if
        if (kwargs.get("property", None) != None) :
            property_list = kwargs.get("property")
            for prop in property_list : 
                (n, v) = p.split(('='), 1)
                stack_filters[n, v]
            # end-for prop
        # end-if 
        logging.debug("stack_filters: %s" % (json.dumps(stack_filters,  indent=2)))
        if (len(stack_filters.keys()) > 0 ) :
            search_opts["filters"] = stack_filters
        # end-if
        logging.debug("search_opts: %s" % (json.dumps(search_opts,  indent=2)))

        stack_list = self.heat.stacks.list(**search_opts)
        stack_list = list(stack_list)
        return stack_list
    # end-def find

    def get(self, uuid):
        logging.debug("uuid: %s" % (uuid))
        if (uuid == None):
            msg = "ERROR: uuid is required."
            raise RuntimeError(msg);
        # end-if uuid

        stack = self.heat.stacks.get(uuid)
        logging.debug("stack: %s" % (stack))
        return stack
    # end-def get

    def get_by_name(self, name):
        stack = self.heat.stacks.get(name)
        if True :
            return stack
        search_opts = {
                # "stack_name" : ("^%s$" % name)
                "stack_name" : name
                }
        stack_list = self.find(**search_opts)
        logging.debug("stack_list: %s" % (stack_list))

        if (len(stack_list) != 1) :
            err_msg = "Error: Unable to resolve name: %s to unique uuid - received %s" % (name, stack_list)
            logging.error(err_msg)
            raise RuntimeError(err_msg);
        # end-if 
        stack = stack_list[0]
        return stack
    # end-def get

    def delete(self, uuid):
        logging.debug("uuid: %s" % (uuid))
        stack = self.get(uuid)
        stack.delete()
    # end-def delete
    def delete_by_name(self, name):
        logging.debug("name: %s" % (name))
        stack = self.heat.stacks.get(name)
        stack = self.get_by_name(name)
        stack.delete(stack["uuid"])
    # end-def delete

    def wait_till_stack_completion(self, stack_name, poll_period=30, max_wait_time=60):
        elapsed_time = 0
        stack = None
        while True :
            stack = self.heat.stacks.get(stack_name, resolve_outputs=False)
            stack_status = stack.stack_status
            stack_name = stack.stack_name
            stack_uuid = stack.id
            logging.debug("stack_name: %s stack_uuid: %s" % (stack_name, stack_uuid))

            status_msg = "\n Stack %s %s \n" % (stack_name, stack_status)
            logging.info(status_msg)
            if ((stack.stack_status == "CREATE_COMPLETE") or (stack.stack_status == "CREATE_FAILED")) :
                break

            logging.debug("Waiting for %s sec." % poll_period)
            time.sleep(poll_period)
            elapsed_time += poll_period
            if (elapsed_time > (max_wait_time) ) :
                error_msg = "Stack %s failed to complete in %s seconds" % (stack_name, max_wait_time)
                logging.error(error_msg)
                raise RuntimeError(error_msg)
            # end-if elapsed_time
        # end-while 
        return stack
    # end-def wait_till_stack_completion

    def dump_stack(self, stack):
        if (stack == None):
            return
        # end-if stack
        stack_dict = stack.to_dict()
        print "stack: %s " % (json.dumps(stack_dict,  indent=2))
    # end-def dump_stack

    def show_stack(self, name):
        # stack = self.get_by_name(name)
        stack = None
        try :
            stack = self.get(name)
        except Exception as ex :
            logging.debug("Failed to get resource by id: %s - reason: %s - ignoring" % (name, str(ex)))
            stack = self.get_by_name(name)
        # end-try 
        if (stack == None) :
            err_msg = "ERROR: Failed to get VM by name/id: %s" % (name)
            logging.error(err_msg)
        # end-if
        self.dump_stack(stack)
    # end-def show_stack

    def list_stacks(self, **kwargs):
        stacks = self.find(**kwargs)
        stack_list = [] 
        for stack in stacks: 
            stack_list.append(stack.to_dict())
        # end-for stack
        print "stack_list: %s " % (json.dumps(stack_list,  indent=2))
    # end-def list_stacks

    #########################  STACK-RESOURCE ##########################

    def get_resource_parent_stack_uuid(self, stack_resource):
        stack_uuid = None
        for link in stack_resource.links :
            if (link['rel'] != "stack") :
                continue
            # nested_url = link.href
            stack_name = link['href'].split('/')[-2]
            stack_uuid = link['href'].split('/')[-1]
            logging.debug( "stack_name: %s stack_uuid: %s " % (stack_name, stack_uuid))
            break
        # end-for link
        return stack_uuid
    # end-def get_resource_parent_stack_uuid

    def get_nested_stacks(self, stack_resource):
        if (stack_resource == None):
            return

        nested_stacks = []
        for link in stack_resource.links :
            if (link['rel'] != "nested") :
                continue
            # nested_url = link.href
            stack_name = link['href'].split('/')[-2]
            stack_uuid = link['href'].split('/')[-1]
            logging.debug( "stack_name: %s stack_uuid: %s " % (stack_name, stack_uuid))
            nested_stack = self.get_stack(stack_uuid)
            nested_stacks.append(nested_stack)
        # end-for link
        return nested_stacks
    # end-def get_nested_stacks

    def find_stack_resources(self, stack_name, **kwargs):
        logging.debug("stack_name: %s kwargs: %s" % (stack_name, json.dumps(kwargs,  indent=2) ))

        if (stack_name == None):
            msg = "Invalid Arg: stack_name is missing."
            raise RuntimeError(msg);
            # return
        # end-if

        # stack = self.get_by_name(stack_name)
        stack = self.heat.stacks.get(stack_name)

        stack_resources = self.heat.resources.list(stack_name, **kwargs)
        return stack_resources
    # end-def find_stack_resources

    def get_stack_resource(self, stack_name, resource_name):
        logging.debug("stack_name: %s resource_name: %s" % (stack_name, resource_name))

        if (stack_name == None):
            msg = "Invalid Arg: stack_name is missing."
            raise RuntimeError(msg);
        # end-if stack_name

        if (resource_name == None):
            msg = "ERROR: resource name is required."
            raise RuntimeError(msg);
        # end-if resource_name

        # stack = self.get_by_name(stack_name)
        # stack = self.heat.stacks.get(stack_name)

        fields = {
                'resource_name': resource_name,
                'stack_id': stack_name
                }
        stack_resource = self.heat.resources.get(**fields)
        logging.debug("stack_resource: %s" % (stack_resource))

        return stack_resource
    # end-def get_stack_resource


    def find_stack_server_resources(self, stack_name, nested_depth=0):
        fileds = { 
                'nested_depth' : nested_depth,
                # 'status' : "CREATE_COMPLETE",
                "type" : "OS::Nova::Server"
                }
        stack_server_resources = self.find_stack_resources(stack_name, **fileds)
        return stack_server_resources
    # end-def find_stack_server_resources

    def find_stack_server_resources_by_filter(self, stack_name, **kwargs):

        logging.debug("stack_name: %s kwargs: %s " % (stack_name, json.dumps(kwargs,  indent=2) ))
        # stack = self.get_by_name(stack_name)

        # Allowed filter attributes
        server_filter_attrs = ["image", "name", "address", "status"]

        filter_image_uuid_name = None
        try :
            filter_image_uuid_name = kwargs["image"]
            filter_image_uuid = self.get_image_uuid_by_name(filter_image_uuid_name)
            if (filter_image_uuid == None):
                err_msg = "ERROR: unable to find image with uuid/name: %s", filter_value
                logging.error(err_msg)
                raise RuntimeError(msg);
            # end-if image_uuid
            logging.debug("filter_image_uuid_name: %s filter_image_uuid: %s " % (filter_image_uuid_name, filter_image_uuid))
            kwargs["image"] = filter_image_uuid
        except Exception as ex: 
            filter_image_uuid_name = None
            pass 
        # end-try 

        nested_depth = 3
        try :
            nested_depth = kwargs['nested_depth']
        except Exception as ex: 
            pass 
        # end-try 
        logging.debug("filter_image_uuid_name: %s nested_depth: %s " % (filter_image_uuid_name, nested_depth))

        stack_server_resources = self.find_stack_server_resources(stack_name, nested_depth)

        filtered_server_resources = []
        for stack_resource in stack_server_resources :
            parent_stack_uuid = self.get_resource_parent_stack_uuid(stack_resource)
            logging.debug("parent_stack_uuid: %s stack_resource.resource_name: %s" % (parent_stack_uuid, stack_resource.resource_name))

            server_resource = self.get_stack_resource(parent_stack_uuid, stack_resource.resource_name)
            server_resource_dict = server_resource.to_dict()
            logging.debug("server_resource_dict: %s " % (json.dumps(server_resource_dict,  indent=2) ))

            filter_matched = True
            for filter_attr in server_filter_attrs :
                # logging.debug("filter_attr: %s " % (filter_attr))
                filter_value = None
                try :
                    filter_value = kwargs[filter_attr]
                except Exception as ex: 
                    continue 
                # end-try 
                logging.debug("filter_attr: %s filter_value: %s" % (filter_attr, filter_value))
                if (filter_value == None) :
                    continue
                # end-if

                res_attr_value = None
                try :
                    res_attr_value = server_resource_dict["attributes"][filter_attr] 
                except Exception as ex: 
                    pass
                # end-try 
                if (res_attr_value == None) :
                    filter_matched = False
                    break
                # end-if 

                if (filter_attr == "image") :
                    if (res_attr_value == None) :
                        continue
                    # end-if res_attr_value

                    res_image_id = None
                    try: 
                        res_image_id = res_attr_value["id"]
                    except Exception as ex: 
                        pass
                    # end-try 
                    logging.debug("filter_image_uuid %s res_image_id: %s" % (filter_value, res_image_id))
                    if (res_image_id != None) and ((res_image_id != filter_value)) :
                        filter_matched = False
                        break
                    # end-if 
                else :
                    if (res_attr_value == None) :
                        continue
                    # end-if res_attr_value
                    if (res_attr_value != filter_value) :
                        filter_matched = False
                        break
                    # end-if 
                # end-if filter_attr
            # end-for
            if (filter_matched) :
                filtered_server_resources.append(server_resource)
            # end-if
        # end-for 
        return filtered_server_resources
    # end-def find_stack_server_resources_by_filter

    def find_stack_server_resources_by_image(self, stack_name, image_uuid_name, nested_depth=2):

        logging.debug("stack_name: %s image_uuid_name: %s nested_depth: %d" % (stack_name, image_uuid_name, nested_depth))

        image_uuid = self.get_image_uuid_by_name(image_uuid_name)
        if (image_uuid == None):
            err_msg = "ERROR: unable to find image with uuid/name: %s", image_uuid_name
            logging.error(err_msg)
            raise RuntimeError(msg);
        # end-if image_uuid
        logging.debug("image_uuid_name: %s image_uuid: %s " % (image_uuid_name, image_uuid))


        server_filters = {
                "nested_depth" : nested_depth,
                "image" : image_uuid
                }
        filtered_server_resources = self.find_stack_server_resources_by_filter(stack_name, **server_filters)
        return filtered_server_resources
    # end-def find_stack_server_resources_by_image

    def get_server_uuid_by_stack_resource(self, stack_server_resource):
        server_resource_dict = stack_server_resource.to_dict()
        logging.debug("server_resource_dict: %s " % (json.dumps(server_resource_dict,  indent=2) ))
        server_uuid = server_resource_dict["attributes"]["id"] 
        return server_uuid
    # end-def get_server_uuid_by_stack_resource

    def get_server_uuid_by_stack_resources(self, stack_server_resources):
        server_uuid_list = []
        for stack_server_resource in stack_server_resources :
            # server_uuid = self.get_server_uuid_by_stack_resource(stack_server_resource)
            server_uuid = stack_server_resource.attributes["id"]
            server_uuid_list.append(server_uuid)
        return server_uuid_list
    # end-def get_server_uuid_by_stack_resources

    def get_stack_server_uuid_list(self, stack_name, image_uuid_name=None, nested_depth=2, wait_for_stack_complete=False):
        if (wait_for_stack_complete) :
            stack = self.wait_till_stack_completion(stack_name)
        # end-if wait_for_stack_complete`
        server_filters = {}
        server_filters["nested_depth"] =  nested_depth
        if (image_uuid_name != None) :
            image_uuid = self.get_image_uuid_by_name(image_uuid_name)
            if (image_uuid == None):
                err_msg = "ERROR: unable to find image with uuid/name: %s", image_uuid_name
                logging.error(err_msg)
                raise RuntimeError(msg);
            # end-if image_uuid
            logging.debug("image_uuid_name: %s image_uuid: %s " % (image_uuid_name, image_uuid))
            server_filters["image"] = image_uuid
        # end-if

        filtered_server_resources = self.find_stack_server_resources_by_filter(stack_name, **server_filters)
        server_uuid_list = self.get_server_uuid_by_stack_resources(filtered_server_resources)
        return server_uuid_list
    # end-def get_stack_server_uuid_List

    def get_server_name_by_stack_resources(self, stack_server_resources):
        server_name_list = []
        for stack_server_resource in stack_server_resources :
            # server_name = self.get_server_name_by_stack_resource(stack_server_resource)
            server_name = stack_server_resource.attributes["name"]
            server_name_list.append(server_name)
        return server_name_list
    # end-def get_server_name_by_stack_resources

    def get_stack_server_name_list(self, stack_name, image_uuid_name=None, nested_depth=2, wait_for_stack_complete=False) :
        logging.debug("stack_name: %s image_uuid_name: %s nested_depth: %d wait_for_stack_complete: %s" % (stack_name, image_uuid_name, nested_depth, wait_for_stack_complete))

        if (wait_for_stack_complete) :
            stack = self.wait_till_stack_completion(stack_name)
        # end-if wait_for_stack_complete`

        server_filters = {}
        server_filters["nested_depth"] =  nested_depth
        if (image_uuid_name != None) :
            image_uuid = self.get_image_uuid_by_name(image_uuid_name)
            if (image_uuid == None):
                err_msg = "ERROR: unable to find image with uuid/name: %s", image_uuid_name
                logging.error(err_msg)
                raise RuntimeError(msg);
            # end-if image_uuid
            logging.debug("image_uuid_name: %s image_uuid: %s " % (image_uuid_name, image_uuid))
            server_filters["image"] = image_uuid
        # end-if
        filtered_server_resources = self.find_stack_server_resources_by_filter(stack_name, **server_filters)

        server_name_list = self.get_server_name_by_stack_resources(filtered_server_resources)
        logging.debug( "server_name_list (%d): %s " % (len(server_name_list), json.dumps(server_name_list,  indent=2)))
        return server_name_list
    # end-def get_stack_server_name_List


    def get_server_data_by_stack_resources(self, stack_server_resources):
        server_data_list = []
        for stack_server_resource in stack_server_resources :
            # server_uuid = self.get_server_uuid_by_stack_resource(stack_server_resource)
            server_attributes = copy.deepcopy(stack_server_resource.attributes)

            server_data = {}
            server_data["attributes"] = server_attributes
            server_data["id"] = server_attributes["id"]
            server_data["name"] = server_attributes["name"]

            vn_interface_list = {}
            for vn_name in server_attributes["addresses"].keys() :
                vn_ifaces_data = server_attributes["addresses"][vn_name] 
                # TODO: Need a logic for picking up the ip-address
                vn_iface_data = vn_ifaces_data[0]
                vn_iface_ipaddr = vn_iface_data["addr"]
                vn_interface_list[vn_name] = vn_iface_ipaddr
            # end-for 
            server_data["interface_list"] = vn_interface_list
            server_data_list.append(server_data)
        # end-for 
        return server_data_list
    # end-def get_server_data_by_stack_resources
    def get_stack_server_data_list(self, stack_name, image_uuid_name=None, nested_depth=2, wait_for_stack_complete=False):
        if (wait_for_stack_complete) :
            self.wait_till_stack_completion(stack_name)
        # end-if

        server_filters = {}
        server_filters["nested_depth"] =  nested_depth
        if (image_uuid_name != None) :
            image_uuid = self.get_image_uuid_by_name(image_uuid_name)
            if (image_uuid == None):
                err_msg = "ERROR: unable to find image with uuid/name: %s", image_name
                logging.error(err_msg)
                raise RuntimeError(msg);
            # end-if image_uuid
            logging.debug("image_uuid_name: %s image_uuid: %s " % (image_uuid_name, image_uuid))
            server_filters["image"] = image_uuid
        # end-if
        logging.debug( "server_filters: %s " % (json.dumps(server_filters,  indent=2)))

        filtered_server_resources = self.find_stack_server_resources_by_filter(stack_name, **server_filters)
        logging.debug( "filtered_server_resources (%d): " % (len(filtered_server_resources)))

        server_data_list = self.get_server_data_by_stack_resources(filtered_server_resources)
        return server_data_list
    # end-def get_stack_server_data_List

    def dump_stack_resource(self, stack_resource):
        if (stack_resource == None):
            return
        # end-if stack
        stack_resource_dict = stack_resource.to_dict()
        print "stack_resource_dict: %s " % (json.dumps(stack_resource_dict,  indent=2))
    # end-def dump_stack_resource

    def show_stack_resource(self, stack_name, resource_name):
        # stack = self.get_by_name(stack_name)
        stack_resource = self.get_stack_resource(stack_name, resource_name)
        self.dump_stack_resource(stack_resource)
    # end-def show_stack

    def list_stack_resources(self, stack_name, **kwargs):
        stack_resources = self.find_stack_resources(stack_name, **kwargs)
        stack_resource_list = []
        for stack_resource in stack_resources: 
            stack_resource_list.append(stack_resource.to_dict())
        # end-for stack_resource
        print "stack_resource_list: %s " % (json.dumps(stack_resource_list,  indent=2))
    # end-def list_stack_resources

    #########################  STACK-RESOURCE ##########################

# end-class HeatStackMgr:

class HeatStackMgrCmdHandler:

    default_domain_name = "default-domain"
    default_tenant_name = "admin"

    default_config_file_name = "os_stack.conf"
    default_log_file_path = ""

    def __init__(self,args_str=None):
        self.process_arguments()

        self.keystone_mgr = KeystoneMgr(self.args)
        self.heat_stack_mgr = HeatStackMgr(self.keystone_mgr)
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

        # print "HeatStackMgrCmdHandler: config_file_path: %s " % config_file_path
        default_options = {
                "server_image_uuid" : "96d924ac-d609-4029-9e89-04f8607da173",
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
                "create", "list", "show", "delete", "wait",
                "resource-list", "resource-show",
                "si-server-resource-list", "si-server-uuid-list", "si-server-data-list", "si-server-name-list",
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

        # Stack create params
        parser.add_argument('--name', help="Regular expression to match stack names or name to be used for stack creation", default=argparse.SUPPRESS)
        parser.add_argument('-e','--environment', help="Path to the environment file", default=argparse.SUPPRESS)
        parser.add_argument('-t','--template', help="Path to the template file.", default=argparse.SUPPRESS)
        parser.add_argument('--paramaters', action="append", help="Parameter values used to create the stack. This can be specified multiple times", default=argparse.SUPPRESS)
        parser.add_argument('--wait', action="store_true", help="Wait until stack goes to CREATE_COMPLETE or CREATE_FAILED")
        # Stack params
        parser.add_argument('--stack-filter', action="append", help="Filter properties to apply on returned stacks; (repeat to filter on multiple properties)", default=argparse.SUPPRESS)

        # Stack resource params
        parser.add_argument('--resource-filter', action="append", help="Filter parameters to apply on returned resources based on their name, status, type, action, id and physical_resource_id", default=argparse.SUPPRESS)
        parser.add_argument('-n','--nested-depth', help="Depth of nested stacks from which to display resources")
        parser.add_argument('--resource-type', help="Filter stack resources by type", default=argparse.SUPPRESS)
        parser.add_argument('--resource-name', help="stack resources name", default=argparse.SUPPRESS)
        parser.add_argument('--server-image-uuid', help="stack server resources image uuid to be used for filtering server resources", default=argparse.SUPPRESS)
        parser.add_argument('--server-image-name', help="stack server resources image name to be used for filtering server resources", default=argparse.SUPPRESS)

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
        logging.debug ("HeatStackMgrCmdHandler: cmd: %s " % (cmd))

        if (cmd == "test") :
            self.test(args)
        elif (cmd == "get-token") :
            token = self.heat_stack_mgr.get_token()
            print "token: %s " % token
        elif (cmd == "create") :
            self.heat_stack_mgr.create(self.args)
        elif (cmd == "list") :
            self.heat_stack_mgr.list_stacks(**self.args)
        elif (cmd == "show") :
            name = self.args["name"]
            self.heat_stack_mgr.show_stack(name)
        elif (cmd == "delete") :
            name = self.args["name"]
            self.heat_stack_mgr.delete_stack(name)
        elif (cmd == "resource-list") :
            stack_name = self.args["name"]
            resource_filter = {}
            if (self.args.get("nested_depth", None) != None) :
                resource_filter["nested_depth"] = self.args.get("nested_depth")
            # end-if 
            if (self.args.get("resource_name", None) != None) :
                resource_filter["name"] = self.args.get("resource_name")
            # end-if 
            if (self.args.get("resource_type", None) != None) :
                resource_filter["type"] = self.args.get("resource_type")
            # end-if 
            if (self.args.get("resource_filter", None) != None) :
                res_filters = self.args.get("resource_filter")
                for res_filter in res_filters :
                    logging.debug("res_filter: %s " % res_filter)
                    (n, v) = res_filter.split(('='), 1)
                    resource_filter[n] = v
                # end-for 
            # end-if 
            logging.debug("resource_filter: %s" % (json.dumps(resource_filter,  indent=2)))
            self.heat_stack_mgr.list_stack_resources(stack_name, **resource_filter)
        elif (cmd == "wait") :
            stack_name = self.args["name"]
            stack = self.heat_stack_mgr.wait_till_stack_completion(stack_name)
        elif (cmd == "resource-show") :
            stack_name = self.args["name"]
            resource_name = self.args["resource_name"]
            self.heat_stack_mgr.show_stack_resource(stack_name, resource_name)
        elif (cmd == "si-server-resource-list") :
            stack_name = self.args["name"]
            server_image_uuid = None
            if (self.args.get("server_image_uuid", None) != None) :
                server_image_uuid = self.args["server_image_uuid"]
            elif (self.args.get("server_image_name", None) != None) :
                server_image_name = self.args["server_image_name"]
            # end-if
            nested_depth = 3
            if (self.args.get("nested_depth", None) != None) :
                nested_depth = int(self.args.get("nested_depth"))
            # end-if
            server_resources = self.heat_stack_mgr.find_stack_server_resources_by_image(stack_name, server_image_uuid)
            server_resource_list = []
            for server_resource in server_resources: 
                server_resource_list.append(server_resource.to_dict())
            # end-for server_resource
            print "server_resource_list: %s " % (json.dumps(server_resource_list,  indent=2))
        elif (cmd == "si-server-uuid-list") :
            stack_name = self.args["name"]
            wait_for_stack_complete = True
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

            nested_depth = 3
            if (self.args.get("nested_depth", None) != None) :
                nested_depth = int(self.args.get("nested_depth"))
            # end-if

            server_uuid_list = self.heat_stack_mgr.get_stack_server_uuid_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
            print "server_uuid_list (%d): %s " % (len(server_uuid_list), json.dumps(server_uuid_list,  indent=2))
        elif (cmd == "si-server-name-list") :
            stack_name = self.args["name"]
            wait_for_stack_complete = True
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

            nested_depth = 3
            if (self.args.get("nested_depth", None) != None) :
                nested_depth = int(self.args.get("nested_depth"))
            # end-if
            server_name_list = self.heat_stack_mgr.get_stack_server_name_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)

            print "server_name_list (%d): %s " % (len(server_name_list), json.dumps(server_name_list,  indent=2))
        elif (cmd == "si-server-data-list") :
            stack_name = self.args["name"]
            wait_for_stack_complete = True

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

            nested_depth = 3
            if (self.args.get("nested_depth", None) != None) :
                nested_depth = int(self.args.get("nested_depth"))
            # end-if
            server_data_list = self.heat_stack_mgr.get_stack_server_data_list(stack_name, server_image_uuid_name, nested_depth, wait_for_stack_complete)
            print "server_data_list (%d): %s " % (len(server_data_list), json.dumps(server_data_list,  indent=2))
        else :
            logging.error("Invalid command: %s", cmd)
        # end-if

    # end-def apply_command

# end-class HeatStackMgrCmdHandler:

def main(args_str=None):
    heat_stack_mgr_cmd_handler = HeatStackMgrCmdHandler(args_str)
    heat_stack_mgr_cmd_handler.apply_command()
# end-def main

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    sys.exit(main())

