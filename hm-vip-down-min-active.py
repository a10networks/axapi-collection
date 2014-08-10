#!/usr/bin/env python
#
# Copyright 2014, Fadi Hafez <fhafez AT a10networks DOT com>, A10 Networks.
# Version 1.0 - 20140729
# Version 1.1 - 20140810 - PEP8 Compliant (-3 exceptions)
#
# Reference: AX_aXAPI_Ref_v2-20120211.pdf
#
# RETURNS:
#   0: Success
#   1: Failed
#
import sys
import json
import urllib
import urllib2

from xml.dom import minidom

SG_NAME = "sg"
host = "192.168.91.103"
username = "admin"
password = "a10"

FAIL = 1
SUCCESS = 0


class path:
    @classmethod
    def v1(cls):
        return "/services/rest/V1/"

    @classmethod
    def v2(cls):
        return "/services/rest/V2/"

    @classmethod
    def sessionID(cls):
        return "?session_id="


class auth:
    @classmethod
    def sessionID(cls, host, username, password):
        services_path = path.v2()
        sid_url = "http://" + host + services_path
        method = 'authenticate'
        authparams = urllib.urlencode({'method': method,
                                       'username': username,
                                       'password': password
                                       })

        request = urllib2.Request(sid_url, authparams)
        request.add_header('Connection',  'Keep-Alive')
        response = urllib2.urlopen(request)

        sessionID = minidom.parse(response).getElementsByTagName('session_id')[0].childNodes[0].nodeValue
        return sessionID

    @classmethod
    def sessionClose(cls, host, sid):
        method = "method=session.close"
        response = req.get(host, method, sid)
        return response


class req:
    @classmethod
    def get(cls, host, method, sid):
        url = "https://" + host + path.v2() + path.sessionID() + sid + "&" + \
            method.__str__() + "&format=json"
        # print url
        data = urllib.urlopen(url.__str__()).read()
        return data

    @classmethod
    def post(cls, host, method, sid, config):
        url = "https://" + host + path.v2() + path.sessionID() + sid + "&" + \
            method.__str__() + "&format=json"
        # print url
        # print config
        data = urllib.urlopen(url.__str__(), config).read()
        return data

# Authenticate and get session ID
sid = auth.sessionID(host, username, password)

# Get the Service Group details
result = req.get(host, "method=slb.service_group.search&name=" + SG_NAME, sid)

# Extract the min_active_servers value
result_list = json.loads(result)
min_active_server_status = result_list["service_group"]["min_active_member"]["status"]
min_active_server_num = result_list["service_group"]["min_active_member"]["number"]

# if the minimum_active_servers is disabled then
# just quit with SUCCESS return code
if min_active_server_status == 0:
    # disconnect from the API
    result = auth.sessionClose(host, sid)
    sys.exit(SUCCESS)


# Get the Service Group statistics
result = req.get(host, "method=slb.service_group.fetchStatistics&name=" +
                 SG_NAME, sid)
result_list = json.loads(result)

up_port_count = 0
for member in result_list["service_group_stat"]["member_stat_list"]:
    server_name = member["server"]
    server_port = member["port"]

    # Get the status of the server port from the server statistics
    result = req.get(host, "method=slb.server.fetchStatistics&name=" +
                     server_name, sid)
    result_server_list = json.loads(result)
    for port in result_server_list["server_stat"]["port_stat_list"]:
        if port["port_num"] == server_port:
            if port["status"] == 1:
                up_port_count += 1
                break

# disconnect from the API
result = auth.sessionClose(host, sid)

if up_port_count < min_active_server_num:
    sys.exit(FAIL)
else:
    sys.exit(SUCCESS)
