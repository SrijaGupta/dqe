#!/usr/bin/python
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
# Description   : Ansible Module for providing interface between Ansible playbook 
#                 and python libraray for discovering devices (associated with heat
#                 stack for VNF in Openstack) in Junos Space.
#
#

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: my_sample_module

short_description: This is my sample module

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    name:
        description:
            - This is the message to send to the sample module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

import os
import sys
import logging
import traceback

# from jnpr.jedi.openstack.keystone.os_keystone import KeystoneMgr
# from jnpr.jedi.openstack.nova.os_server import NovaServerMgr
# from jnpr.jedi.openstack.heat.os_stack import HeatStackMgr

from jnpr.jedi.jnpr_vnfstack import JnprVNFStack

from ansible.module_utils.basic import AnsibleModule

def build_os_cred_args(args):
    os_cred = {
            "os_auth_url" : args["os_auth_url"],
            "os_username" : args["os_username"],
            "os_password" : args["os_password"],
            "os_tenant_name" : args["os_tenant_name"]
            }
    args["os_cred"] = os_cred
# end-def process_arguments

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        # name=dict(type='str', required=True),
        # new=dict(type='bool', required=False, default=False)

        action=dict(type='str', required=True),
        command=dict(type='str', required=False),


        stack_name=dict(type=str, required=False),
        nested_depth=dict(type=int, required=False, default=4),
        wait_for_stack=dict(type=bool, required=False, default=True),
        skip_ping=dict(type=bool, required=False, default=False),

        stack_resource_type=dict(type=str, required=False),
        stack_resource_name=dict(type=str, required=False),
        server_mgmt_vn_name=dict(type=str, required=False),
        server_image_uuid=dict(type=str, required=False),
        server_image_name=dict(type=str, required=False),
        os_server_name=dict(type=list, required=False),
        os_server_uuid=dict(type=list, required=False),

        os_auth_url=dict(type=str, required=True),
        os_username=dict(type=str, required=True),
        os_password=dict(type=str, required=True),
        os_tenant_name=dict(type=str, required=True),
        os_auth_domain=dict(type=str, required=True),
        os_version=dict(type=str, required=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    module.params["command"] = module.params["action"]
    build_os_cred_args(module.params)

    # Remove all parameters with None value - so that optional values can be specified in task file
    for k,v in module.params.items(): 
        if (v == None) :
            del module.params[k]
            continue
        # end-if
        if (isinstance(v, basestring) and (v.strip() == '') ) :
            del module.params[k]
            continue
        # end-if
    # end-for
    print "module.params: %s " % (module.params)

    jnpr_vnfstack = JnprVNFStack(module.params) 
    try :
        result = jnpr_vnfstack.apply_command(module.params)
    except Exception as ex :
        err_msg = "Failed to handle  cmd: '%s' - reason: %s - %s" % (module.params["action"], str(ex), sys.exc_info()[0])
        traceback.print_exc()
        raise ex
        # pass
    # end-try 

    # os_server_name_list = module.params["os_server_name"]
    # server_mgmt_vn_name = module.params["server_mgmt_vn_name"]
    # print "os_server_name_list(%d): %s " % (len(os_server_name_list), os_server_name_list)
    # server_mgmt_ip_list = jnpr_vnfstack.get_si_mgmt_ip_list(os_server_name_list, server_mgmt_vn_name)
    # result = { "status" : "Success" }
    # print "result: %s " % (result)


    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['command']:
    #     result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if result['status'] == 'Error':
        module.fail_json(msg='Command Exceution Failed.', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    # print "Logging on Stdout (level: %d (debug: %d))" % (logging_level, logging.DEBUG)
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, 
    #             format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    #             datefmt="%Y-%m-%d %H:%M:%S")
    run_module()

if __name__ == '__main__':
    main()
