import requests as r
from datetime import datetime
import threading
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

stats_server="http://Integration-Server:3000/protocol/mqtt/getstats"
device_server="http://Integration-Server:3000/protocol/mqtt/command"
notification_server="http://Integration-Server:3000/notification/postnoti"

def switch(a, uid):
    if a:
        machine_status = "on"
    else:
        machine_status = "off"
    c = machine_status()
    if c == "머신정보없음":
        return
    for i in c:
        device_id, machine_stat = i.split()
        if machine_status == "on":
            if machine_stat == "0":
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                headers = {"content-type": "application/json", "session-token": "token"}
                data = f'{{"device_id": "{device_id}", "topic": "broadcast", "command": "{machine_status}"}}'
                res = r.post(device_server, headers=headers, data=data)
                headers = {"uid": uid, "content-type": "application/json"}
                data = f'{{"content": "꺼져있던 머신 켜짐", "time": "{now}", "about": 1}}'
                res = r.post(notification_server, headers=headers, data=data)
        if machine_status == "off":
            if machine_stat == "1":
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                headers = {"content-type": "application/json", "session-token": "token"}
                data = f'{{"device_id": "{device_id}", "topic": "broadcast", "command": "{machine_status}"}}'
                res = r.post(device_server, headers=headers, data=data)
                headers = {"uid": uid, "content-type": "application/json"}
                data = f'{{"content": "켜져있던 머신 꺼짐", "time": "{now}", "about": 1}}'
                res = r.post(notification_server, headers=headers, data=data)
    return "OK"

 

def machine_status():
    headers = {"content-type": "application/json", "session-token": "token"}
    res = r.get(stats_server, headers=headers)
    if res.status_code != 200:
        return "머신정보없음"
    status=res.json()
    machine=status["stats"]
    return machine