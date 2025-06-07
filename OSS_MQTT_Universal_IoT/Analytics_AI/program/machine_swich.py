import requests as r
from datetime import datetime


def switch(a,uid):
    if a:
        machine_status="머신들이 작동을 시작하였습니다"
    else: 
        machine_status="머신들이 작동을 멈춥니다"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # r.head('{"uid": "0"}')
    headers = {"uid": uid, "content-type": "application/json"}
    data = '{"content": "%s", "time": "%s", "about": 1}'%(machine_status,now)
    #res = r.post("http://localhost:3000/notification/postnoti", headers=headers,data=data)
    print(data,"  ",headers)
