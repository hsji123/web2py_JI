# -*- coding: utf-8 -*-
# try something like
import httplib
import time
state2 = ''

def index():
    return dict(message="hello from hue.py")

def hue2on():
    global state2
    conn.request("PUT", "/api/newdeveloper/lights/2/state", '{"on":true}')
    response = conn.getresponse()
    data = response.read()
    state2 = data + '<br>'
    time.sleep(2)
    return
