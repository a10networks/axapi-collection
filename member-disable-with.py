#!/usr/bin/env python
#################################################
#
# menber-disable-with.py
#  (c) A10 Networks -- MP
#   v1 20140701
#
#################################################
#
# aXAPI script
# Change status of a member with "disable-with-health-check"
# in 2.7.2-P2 to gracefully shutdown a member.
#
# Requiers:
#   - Python 2.7.x
#   - aXAPI V2.1
#   - ACOS 2.7.2-P2
#
# Questions & comments welcome.
#  mpeters AT a10networks DOT com
#
#################################################

import json
import urllib2
import argparse

parser = argparse.ArgumentParser(description="Script to change the status of a member in a service-group")
parser.add_argument("-d", "--device", required=True, help="A10 device IP address")
parser.add_argument("-l", "--login", default='admin', help="A10 admin (default: admin)")
parser.add_argument("-p", "--password", required=True, help="A10 password")
#
parser.add_argument("-s", "--service-group", required=True, help="Select the service-group")
parser.add_argument("-m", "--member", required=True, help="Select the member")
parser.add_argument("--priority", default='8', help="Set the member prioriry (default: 8)")
parser.add_argument("--port", default='80', help="Set the member port (default: 80)")
parser.add_argument("--status", default='disable-with-health-check', choices=['enable', 'disable', 'disable-with-health-check'], help="Set the member status (default: disable-with-health-check)")

print "DEBUG ==> " + str(parser.parse_args()) + "\n"

try:
    args = parser.parse_args()
    a10_host = args.device
    a10_admin = args.login
    a10_pwd = args.password
    service_group = args.service_group
    service_group_member = args.member
    service_group_member_priority = args.priority
    service_group_member_port = args.port
    service_group_member_status = args.status
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
    axapi_base_url = 'https://' + a10_host + '/services/rest/V2.1/?format=json'
    session_url = axapi_authenticate(axapi_base_url, a10_admin, a10_pwd)

    command = ("slb service-group " + service_group + " tcp\n"
        "member " + service_group_member + ":" + service_group_member_port + " " + service_group_member_status)

    print "===> Set service-group member disable-with-health-check"
    response = axapi_call(session_url + '&method=cli.deploy', command)
    print response
    print "<=== Status: " + str(json.loads(response)['response']['status'])

    print "\n===> Collect current connections"
    json_post = { 'name': service_group_member }
    response = axapi_call(session_url + '&method=slb.server.fetchStatistics', json.dumps(json_post))
    print response
    print "<=== Current Connections: " + str(json.loads(response)['server_stat']['cur_conns'])

    closed = axapi_call(session_url + '&method=session.close')
except Exception, e:
    print e
