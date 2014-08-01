#!/usr/bin/env python
#
# Copyright 2014, Mischa Peters <mpeters AT a10networks DOT com>, A10 Networks.
# Version 1.0 - 20140701
#
# Push the Fixed-NAT table from ACOS 2.8.x to an FTP
# server.
#
# Requiers:
#   - Python 2.7.x
#   - aXAPI V2.8
#

import json
import urllib2
import argparse

parser = argparse.ArgumentParser(description="Push the Fixed-NAT table from an A10 device")
parser.add_argument("-d", "--device", required=True, help="A10 device IP address")
parser.add_argument("-l", "--login", default='admin', help="A10 admin (default: admin)")
parser.add_argument("-p", "--password", required=True, help="A10 password")
#
parser.add_argument("--ftp-server", required=True, help="Set the FTP server")
parser.add_argument("--ftp-account", required=True, help="Set the FTP account")
parser.add_argument("--ftp-password", required=True, help="Set the FTP password")
parser.add_argument("--ftp-folder", default='/', help="Set the FTP directory to upload to (default: /)")
parser.add_argument("--table", required=True, help="The Fixed-NAT table to push")

print "DEBUG ==> " + str(parser.parse_args()) + "\n"

try:
    args = parser.parse_args()
    a10_host = args.device
    a10_admin = args.login
    a10_pwd = args.password
    ftp_server = args.ftp_server
    ftp_upload_account = args.ftp_account
    ftp_upload_pwd = args.ftp_password
    ftp_upload_folder = args.ftp_folder
    fixed_nat_table = args.table
except IOError, msg:
    parser.error(str(msg))

def axapi_call(url, data=None):
    result = urllib2.urlopen(url, data).read()
    return result

def axapi_authenticate(base_url, user, pwd):
    url = base_url + "&method=authenticate&username=" + user + "&password=" + pwd
    sessid = json.loads(axapi_call(url))['session_id']
    result = base_url + '&session_id=' + sessid
    return result

try:
    axapi_base_url = 'https://' + a10_host + '/services/rest/V2.8/?format=json'
    session_url = axapi_authenticate(axapi_base_url, a10_admin, a10_pwd)

    response = axapi_call(session_url + '&method=cli.deploy', 'export fixed-nat ' + fixed_nat_table + ' ftp://' + ftp_upload_account + ':' + ftp_upload_pwd + '@' + ftp_server + ftp_upload_folder + fixed_nat_table)

    closed = axapi_call(session_url + '&method=session.close')
except Exception, e:
    print e

print "Download of " + fixed_nat_table + " succesfull!"
