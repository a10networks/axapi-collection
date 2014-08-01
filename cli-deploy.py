#!/usr/bin/env python
#
# Copyright 2014, Mischa Peters <mpeters AT a10networks DOT com>, A10 Networks.
# Version 1.0 - 20140713
#
# Quick cli.deploy
#
# Requiers:
#   - Python 2.7.x
#   - aXAPI V2.1
#   - ACOS 2.7.1-Px or higher
#

import json
import urllib2
import argparse

parser = argparse.ArgumentParser(description="Script to run cli.deploy")
parser.add_argument("-d", "--device", required=True, help="A10 device IP address")
parser.add_argument("-l", "--login", default='admin', help="A10 admin (default: admin)")
parser.add_argument("-p", "--password", required=True, help="A10 password")
#
parser.add_argument("-f", "--file", default='commands.txt', help="A10 commands file")

print "DEBUG ==> " + str(parser.parse_args()) + "\n"

try:
    args = parser.parse_args()
    a10_host = args.device
    a10_admin = args.login
    a10_pwd = args.password
    a10_commands_file = args.file
except IOError, msg:
    parser.error(str(msg))

def axapi_call(url, data=None):
    result = urllib2.urlopen(url, data).read()
    return result

def axapi_authenticate(base_url, user, pwd):
    url = base_url + '&method=authenticate&username=' + user + '&password=' + pwd
    sessid = json.loads(axapi_call(url))['session_id']
    result = base_url + '&session_id=' + sessid
    return result

def axapi_result(result):
    status = str(json.loads(response)['response']['status'])
    if status == 'fail':
        return result
    else:
        return status

try:
    print "===> Start for host: " + a10_host

    f = open(a10_commands_file, 'r')
    commands = f.read()
    print "===> Commands: \n" + commands

    axapi_base_url = 'https://' + a10_host + '/services/rest/V2.1/?format=json'
    session_url = axapi_authenticate(axapi_base_url, a10_admin, a10_pwd)

    print "===> CLI Deploy"
    response = axapi_call(session_url + '&method=cli.deploy', commands)
    print "<=== Status: " + axapi_result(response)

    closed = axapi_call(session_url + '&method=session.close')
except Exception, e:
    print e
