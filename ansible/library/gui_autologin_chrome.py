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
#                 and python libraray for NS REST API.
#                 
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
        required: False

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
import requests

import subprocess
import json
import base64
import getpass
import argparse
import urllib2
import urllib
import ssl
import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import service
import selenium.webdriver.chrome.service as service
from selenium.webdriver.chrome.options import Options

from ansible.module_utils.basic import AnsibleModule

ns_server_ip = os.environ.get('NS_SERVER_IP') 
ns_username = os.environ.get('NS_USERNAME') 
ns_password = os.environ.get('NS_PASSWORD') 
path = os.environ.get('PATH') 

ns_auth_uri_base="/login/"

def autologin_server_gui_tab(driver, server_gui_url, pos, args):
    tab_name = "CFM_tab_%d" % (pos)  
    if (pos == 0) :
        driver.get(server_gui_url)
        # active_elem = driver.switch_to.active_element
    else :
        driver.execute_script('window.open("{}", "{}");'.format((server_gui_url), tab_name))
        # driver.execute_script('window.open("{}", "_blank");'.format(server_gui_url))
        # More info: https://github.com/SeleniumHQ/selenium/blob/master/py/selenium/webdriver/remote/webdriver.py#L776
        time.sleep(5) # Let the user actually see something!
        driver.switch_to.window(tab_name)
        # driver.execute_script('window.location.href=' + server_gui_url + '&xxx=zzz")')
        # driver.execute_script('window.location.reload(true)')
        # active_elem = driver.switch_to.active_element
        # driver.refresh()
    # end-if pos


    # wait for login page to be displayed
    time.sleep(5) # Let the user actually see something!
    # username = WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located((By.NAME, "username")))

    # active_elem = driver.switch_to.active_element

    # More info: https://github.com/SeleniumHQ/selenium/blob/master/py/selenium/webdriver/remote/webdriver.py#L752
    if ('9091' in server_gui_url) :
        # fill in GUI username and and password 
        # username = active_elem.find_element_by_id('wandlLoginUsernameField-inputEl')
        # username.send_keys('admin')
        # username = active_elem.find_element_by_id('userName')

        # time.sleep(5) # Let the user actually see something!
        cluster_uuid_menu = driver.find_element_by_css_selector('div.ant-select-lg.ant-select.ant-select-enabled.ant-select-allow-clear')
        cluster_uuid_menu.click()
        time.sleep(2) # Let the user actually see something!
        # cluster_uuid_menu_list = driver.find_element_by_css_selector('div.ant-select-selection.ant-select-selection--single')
        cluster_uuid_menu_list = driver.find_element_by_css_selector('ul.ant-select-dropdown-menu.ant-select-dropdown-menu-vertical.ant-select-dropdown-menu-root')
        cluster_uuid_menu_list.find_element_by_css_selector('li').click()
        # cluster_uuid_menu_list.childNodes[0].attr('selected', 'selected');

        username = driver.find_element_by_css_selector('input#userName')
        username.send_keys(args["cfm_username"])
        # password = active_elem.find_element_by_name('password')
        # password.send_keys('Embe1mpls')
        # password = active_elem.find_element_by_id('password')
        password = driver.find_element_by_css_selector('input#password')
        password.send_keys(args["cfm_password"])
        # enable_full_access = active_elem.find_element_by_id('checkbox-1014-inputEl')
        # enable_full_access.click()
        # loginInButton = active_elem.find_element_by_class_name('login-form-button-submit')
        loginInButton = driver.find_element_by_css_selector('span.login-form-button-submit')
        loginInButton.click()
    elif ('/appformix' in server_gui_url) :
        pass
    elif (('http:' in server_gui_url) and ('/project' in server_gui_url)) :
        # driver.execute_script('window.location.href=' + server_gui_url + '&xxx=yyy")')
        # driver.execute_script('window.location.replace(window.location.href + "&xxx=yyy")')
        # time.sleep(5) # Let the user actually see something!
        # time.sleep(30) # Let the user actually see something!
        # username = driver.find_element_by_id('id_username')
        username = driver.find_element_by_css_selector('input#id_username.form-control')
        username.send_keys(args["cfm_username"])
        # password = driver.find_element_by_name('password')
        # password = driver.find_element_by_id('id_password')
        password = driver.find_element_by_css_selector('input#id_password.form-control')
        password.send_keys(args["cfm_password"])
        # loginInButton = driver.find_element_by_id('loginBtn')
        loginInButton = driver.find_element_by_css_selector('button#loginBtn')
        loginInButton.click()
    elif (':8143' in server_gui_url) :
        # time.sleep(5) # Let the user actually see something!
        # username = active_elem.find_element_by_name('username')
        # password = active_elem.find_element_by_name('password')
        # loginInButton = active_elem.find_element_by_id('signin')
        # username = driver.find_element_by_name('username')
        username = driver.find_element_by_css_selector('input[name="username"]')
        username.send_keys(args["cfm_username"])
        # password = driver.find_element_by_name('password')
        password = driver.find_element_by_css_selector('input[name="password"]')
        password.send_keys(args["cfm_password"])
        loginInButton = driver.find_element_by_css_selector('button#signin')
        loginInButton.click()
    # endif server_gui_url
    time.sleep(5) # Let the user actually see something!

# end-def autologin_server_gui_tab

def autologin_server_gui(args):
    result = {
            "data" : { },
            "changed" : False,
            "status" : "Success",
            "message" : "Success",
            "error_message" : ""
            }
    gui_url_list = []

    auth_payload = {
            "grant_type": "password",
            "username": args["cfm_username"],
            "password": args["cfm_password"]
            }

    cfm_gui_url_list = args["cfm_server_url_list"].split(',')
    # gui_url_list = args["gui_url_list"]
    cfm_gui_url = cfm_gui_url_list[0]

    result["data"] = {
            'path'       : path,
            # 'params'     : args,
            'gui_url' : cfm_gui_url
            }
    if (False) :
        return result


    # # capabilities = {'chrome.binary': '/path/to/custom/chrome'}
    options = Options()
    options.add_experimental_option('detach', True)
    # options.add_argument('user-data-dir=/var/tmp/NorthStar')
    # For more info: https://github.com/SeleniumHQ/selenium/blob/master/py/selenium/webdriver/chrome/webdriver.py#L33 
    driver = webdriver.Chrome(options=options)

    # chrome_service = service.Service()
    # chrome_service = service.Service('/Users/subratam/bin/chromedriver')
    # chrome_service.start()
    # capabilities = options.to_capabilities()
    # # driver = webdriver.Remote(chrome_service.service_url, capabilities)
    # driver = webdriver.Remote(chrome_service.service_url, capabilities)
    # driver = webdriver.Remote(chrome_service.service_url, capabilities)

    server_url_list = args["cfm_server_url_list"].split(',')
    for server_url in server_url_list :
        # server_ip = args["server_ip_list"][0]
        gui_url = server_url
        autologin_server_gui_tab(driver, gui_url, len(gui_url_list), args)
        try : 
            pass
        except Exception as ex :
            traceback.print_exc()
            pass
        # end-try
        gui_url_list.append(gui_url)
    # end-for
    result["data"] = {
            'path'     : path,
            # 'params'     : args,
            'gui_url_list' : gui_url_list
            }
    return result

# end-def autologin_gui


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        # name=dict(type='str', required=True),
        # new=dict(type='bool', required=False, default=False)
        cfm_server_url_list=dict(type=str, required=True),
        # server_ip=dict(type=str, required=True),
        cfm_username=dict(type=str, required=True),
        cfm_password=dict(type=str, required=True),
        # ns_server_ip=dict(type=str, required=False, default=ns_server_ip),
        # ns_username=dict(type=str, required=False, default=ns_username),
        # ns_password=dict(type=str, required=False, default=ns_password),
        # ns_version=dict(type=str, required=False, default='3.2'),
        # ns_api_version=dict(type=str, required=False, default='v2')
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
    # module.params["command"] = module.params["action"]
    # print "module.params: %s " % (module.params)

    try :
       result = autologin_server_gui(module.params)
    except Exception as ex :
        err_msg = "Failed to get cluster data : %s - %s" % (str(ex), sys.exc_info()[0])
        # err_msg = "Failed to handle  cmd: '%s' - reason: %s - %s" % (module.params["action"], str(ex), sys.exc_info()[0])
        traceback.print_exc()
        raise ex
        # pass
    # end-try 
    # print(json.dumps(result))


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
    # ns_server_ip = os.environ.get('NS_SERVER_IP') 
    # ns_username = os.environ.get('NS_USERNAME') 
    # ns_password = os.environ.get('NS_PASSWORD') 

    # print "Logging on Stdout (level: %d (debug: %d))" % (logging_level, logging.DEBUG)
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, 
    #             format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    #             datefmt="%Y-%m-%d %H:%M:%S")
    run_module()

if __name__ == '__main__':
    main()

