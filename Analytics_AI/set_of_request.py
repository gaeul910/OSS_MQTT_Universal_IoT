import requests as r

def route_get(pointer,route):
    if not route== "":
        route+=","+pointer
    else:
        route = pointer
    return route

def route_send(route):
        headers = {"content-type": "application/json"}
        data = f'{{"uid": 123, "endlocation_id": 0, "startlocation_id": 1, "route": "LINESTRING({route})", "status": 1}}'
        #res = r.post("http://localhost:3000/location/fav/point", headers=headers,data=data)
        route = ""
        return route
    #보낼때 요청을 한번해서 확인을 한다 받아지는지 안받아지는지 그리고 나서 없으면 집어넣고 있으면 그냥 공중 분해 시켜버린다.

def route_exist_send(route):
    res = r.get("http://localhost:3000/location/fav/route")
    if res.status_code==404:
        return route_send(route)
    else:
        route = ""
        return route
    
def route_request():
    headers = {"Content-Type": "application/json"}
    data = '{"route_id": 0}'
    res = r.get("http://localhost:3000/location/fav/route", headers=headers, data=data)
    return res.json()

def favorite_point_post(cluster_store):
    for favpoint in cluster_store:
        headers = {"content-type": "application/json"}
        data = f'{{"uid": {favpoint["uid"]}, "time": "2025-01-01 00:00:00", "coordinate": "{favpoint["coordness"]}", "status": {favpoint["stat"]}, "alias": "Company"}}'
        res = r.post("http://localhost:3000/location/fav/point", headers=headers,data=data)

def uid_get():
    headers = {"content-type": "application/json"}
    data={}
    res=r.get("http://localhost:3000/#########서버 어쩌고 저쩌고####### 해줘라", headers=headers, data=data)

 