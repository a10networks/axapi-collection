#!/usr/bin/env python
#################################################
#
# reset-config.py
#  (c) A10 Networks -- MP
#   v1 20140710
#   v2 20140711 - added upgrade
#   v3 20140712 - moved to aXAPI V2.1
#   v4 20140713 - moved result to function
#
#################################################
#
# aXAPI script
# Reset a training lab to default config
#
# Requiers:
#   - Python 2.7.x
#   - aXAPI V2.1
#   - ACOS 2.7.1-Px or higher
#
# Questions & comments welcome.
#  mpeters AT a10networks DOT com
#
#################################################

import json
import urllib2
import argparse

#################################################
# Set specific defaults
#################################################
FTP = '<FTP Server IP>'
ACOS = '<Default ACOS Build>'

tftp_lab1 = "tftp://172.31.81.10/sx"
devices_lab1 = {'172.31.81.11': '1', '172.31.81.21': '2', '172.31.81.31': '3', '172.31.81.41': '4', '172.31.81.51': '5', '172.31.81.61': '6', '172.31.81.71': '7', '172.31.81.81': '8', '172.31.81.91': '9', '172.31.81.91': '9', '172.31.81.101': '10', '172.31.81.111': '11', '172.31.81.121': '12'}
tftp_lab2 = "tftp://172.31.82.10/sx"
devices_lab2 = {'172.31.82.11': '1', '172.31.82.21': '2', '172.31.82.31': '3', '172.31.82.41': '4', '172.31.82.51': '5', '172.31.82.61': '6', '172.31.82.71': '7', '172.31.82.81': '8', '172.31.82.91': '9', '172.31.82.91': '9', '172.31.82.101': '10', '172.31.82.111': '11', '172.31.82.121': '12'}
#################################################

parser = argparse.ArgumentParser(description="Script to clear out training config")
parser.add_argument("-d", "--device", required=True, choices=['lab1', 'lab2'], help="Training Lab")
parser.add_argument("-l", "--login", default='admin', help="A10 admin (default: admin)")
parser.add_argument("-p", "--password", required=True, help="A10 password")
#
parser.add_argument("-a", "--action", required=True, choices=['restore', 'backup', 'reboot', 'clear-log', 'upgrade'], help="Action to perform")
parser.add_argument("--partition", default='primary', help="Boot Partition to use (default: primary)")
parser.add_argument("--file", default=ACOS, help="ACOS Version (default: " + ACOS + ")")
parser.add_argument("--ftpserver", default=FTP, help="FTP Server (default: " + FTP + ")")
parser.add_argument("--ftpuser", default='annonymous', help="FTP Username (default: anonymous)")
parser.add_argument("--ftppass", default='ftp@ftp.com', help="FTP Pass (default: ftp@ftp.com)")

print "DEBUG ==> " + str(parser.parse_args()) + "\n"

try:
    args = parser.parse_args()
    a10_host = args.device
    a10_admin = args.login
    a10_pwd = args.password
    action = args.action
    a10_partition = args.partition
    ftp_file = args.file
    ftp_host = args.ftpserver
    ftp_user = args.ftpuser
    ftp_pass = args.ftppass
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

def axapi_result(result):
    status = str(json.loads(response)['response']['status'])
    if status == 'fail':
        return result
    else:
        return status

try:
    if a10_host == 'lab1':
        devices = devices_lab1.items()
        tftp = tftp_lab1
    if a10_host == 'lab2':
        devices = devices_lab2.items()
        tftp = tftp_lab2
    if a10_partition == 'primary':
        destination = '0'
    else:
        destination = '1'

    for item in devices:
        a10_host = item[0]
        tftp_file = item[1]

        print "===> Start for host: " + a10_host

        axapi_base_url = 'https://' + a10_host + '/services/rest/V2.1/?format=json'
        session_url = axapi_authenticate(axapi_base_url, a10_admin, a10_pwd)

        if action == 'restore':
            print "===> Restore Config"
            response = axapi_call(session_url + '&method=cli.deploy', 'restore ' + tftp + tftp_file)
            print "<=== Status: " + axapi_result(response)

        if action == 'backup':
            print "===> Backup Config"
            response = axapi_call(session_url + '&method=cli.deploy', 'backup system ' + tftp + tftp_file)
            print "<=== Status: " + axapi_result(response)

        if action == 'reboot':
            print "===> Reboot Instance"
            response = axapi_call(session_url + '&method=system.action.reboot&write_memory=1')
            print "<=== Status: " + axapi_result(response)

        if action == 'clear-log':
            print "===> Clear Log"
            response = axapi_call(session_url + '&method=system.log.clear')
            print "<=== Status: " + axapi_result(response)

        if action == 'upgrade':
            print "===> Upgrade"
            json_post = {'sys_maintain': { 'media': '0', 'destination': destination, 'reboot': '0', 'remote': { 'protocol': '1', 'host': ftp_host, 'location': ftp_file, 'username': ftp_user, 'password': ftp_pass }}}
            response = axapi_call(session_url + '&method=system.maintain.upgrade', json.dumps(json_post))
            print "<=== Status: " + axapi_result(response)

        closed = axapi_call(session_url + '&method=session.close')
except Exception, e:
    print e
