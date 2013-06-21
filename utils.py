import logging
import os.path
import uuid
import sys
import urllib2
import hashlib
import json
import gc
import inspect
import os
import traceback

def ksort(d):
    return [(k,d[k]) for k in sorted(d.keys())]

def sha1(s):
    return hashlib.sha1(s).hexdigest()

def md5(s):
    return hashlib.md5(s).hexdigest()
    
def http_build_query(params, topkey = ''):
    from urllib import quote

    if len(params) == 0:
        return ""

    result = ""

    if type (params) is dict:
        for key in params.keys():
            value = params[key]

            newkey = quote (key)
            if topkey != '':
                newkey = topkey + quote('[' + key + ']')

            if type(value) is dict:
                result += http_build_query (value, newkey)

            elif type(value) is list:
                i = 0
                for val in value:
                    result += newkey + quote('[' + str(i) + ']') + "=" + quote(str(val)) + "&"
                    i = i + 1

            # boolean should have special treatment as well
            elif type(value) is bool:
                result += newkey + "=" + quote (str(int(value))) + "&"

            # assume string (integers and floats work well)
            else:
                result += newkey + "=" + quote (str(value)) + "&"
    elif type(params) is list:
        for key, value in params:
            newkey = quote (key)
            if topkey != '':
                newkey = topkey + quote('[' + key + ']')

            if type(value) is dict:
                result += http_build_query (value, newkey)

            elif type(value) is list:
                i = 0
                for val in value:
                    result += newkey + quote('[' + str(i) + ']') + "=" + quote(str(val)) + "&"
                    i = i + 1

            # boolean should have special treatment as well
            elif type(value) is bool:
                result += newkey + "=" + quote (str(int(value))) + "&"

            # assume string (integers and floats work well)
            else:
                result += newkey + "=" + quote (str(value)) + "&"

    # remove the last '&'
    if (result) and (topkey == '') and (result[-1] == '&'):
        result = result[:-1]

    return result