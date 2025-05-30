import requests as rq
from datetime import datetime

def transmit(uid,machine_status):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # r.head('{"uid": "0"}')
    headers = {"uid": uid, "content-type": "application/json"}
    data = '{"content": "%s", "time": "%s", "about": 1}'%(machine_status,now)
    print(data,"  ",headers)
    #내용이 잘 들어가는지 확인용
    #res = r.post("http://localhost:3000/notification/postnoti", headers=headers,data=data)