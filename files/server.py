#!/usr/bin/env python3

import socket
import requests
from json import dumps
from os import environ

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(False)
server.bind(('', 11166))
server.listen(5)

connections = []
message = b''
lastmessage = b''
char = b''

necessaryParams = ["PVE_TOKEN", "PVE_SECRET", "PVE_NODE", "PVE_URL"]

for param in necessaryParams:
    if param not in environ:
        print(param + " missing from config")
        exit(1)

tokenId = environ["PVE_TOKEN"]
secret = environ["PVE_SECRET"]
nodeId = environ["PVE_NODE"]
pveUrl = environ["PVE_URL"]

baseUrl = pveUrl + '/api2/json'
headers = {"Authorization": "PVEAPIToken=" + tokenId + "=" + secret}

postOpts = ["start","stop","reset","reboot","shutdown"]
getOpts = ["current"]

nodemap = {}
for env in environ:
    if "PVE_MAP_" in env:
        nodemap[env.replace("PVE_MAP_","")] = environ[env]

def pveVM(action, id):
    print(action, id)
    if id in nodemap.keys():
        if action in postOpts:
            r = requests.post(baseUrl + "/nodes/" + nodeId + "/qemu/" + nodemap[id] + "/status/" + action, verify=False, headers=headers)
            if r.status_code == 200:
                return "success"
            else:
                return "failure"
        elif action in getOpts:
            r = requests.get(baseUrl + "/nodes/" + nodeId + "/qemu/" + nodemap[id] + "/status/" + action, verify=False, headers=headers)
            if r.status_code == 200:
                if action == "current":
                    return r.json()["data"]["status"]
            else:
                return "failure"
    else:
        return id + " not in nodemap"

while True:
    try:
        connection, address = server.accept()
        connection.setblocking(False)
        connections.append(connection)
        for node in nodemap.keys():
            connection.send(node.encode())
            connection.send(b'\r\n')
        for opt in postOpts:
            connection.send(opt.encode() + b' ')
        for opt in getOpts:
            connection.send(opt.encode() + b' ')
        connection.send(b'\r\n')
    except BlockingIOError:
        pass

    for connection in connections:
        try:
            char = connection.recv(4096)
            message += char
        except BlockingIOError:
            continue
        if char == b'\r':
          connection.send(b'\r\n')
          if len(message.decode("utf-8").split(" ")) != 2:
            connection.send(b'not in available commands')
            connection.send(b'\r\n')
            message = b''
            continue 
          action = message.decode("utf-8").split(" ")[0]
          vm = message.decode("utf-8").split(" ")[1].replace("\r","")
          if action in postOpts or action in getOpts:
              msg = pveVM(action, vm)
              connection.send(b'\r\n' + msg.encode() + b'\r\n')
          else:
              connection.send(b'not in available commands')
          connection.send(b'\r\n')
          lastmessage = message[:-1]
          message = b''
        elif char == b'\x1b[A':
          connection.send(b'\r\n')
          message = lastmessage.decode("utf-8").replace("\r","").encode()
          lastmessage = message
          connection.send(lastmessage)
        elif char == b'\x7f':
          message = message[:-2]
          lastmessage = message
          connection.send(b'\r' + lastmessage)
        
        char = b''
