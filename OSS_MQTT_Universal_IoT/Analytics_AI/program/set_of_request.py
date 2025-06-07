import requests as r
import json
from datetime import datetime, timedelta



route_adress="http://Integration-Server:3000/location/fav/route"
favpoint_adress="http://Integration-Server:3000/location/fav/point"


def route_get(pointer,route):
    # route가 비어있으면 바로 pointer 저장
    if not route:
        return pointer

    # 현재 pointer 좌표 분리
    try:
        new_lat, new_lon = map(float, pointer.strip().split())
    except ValueError:
        return route  # 잘못된 포맷이면 무시

    # 마지막 좌표만 가져와 비교
    last_point = route.strip().split(',')[-1].strip()
    try:
        last_lat, last_lon = map(float, last_point.split())
    except ValueError:
        return route

    # 같은 좌표면 추가하지 않음
    if new_lat == last_lat and new_lon == last_lon:
        return route

    # 다르면 이어붙임
    return route + "," + pointer

def route_send(uid,route,location_id):
        headers = {"Content-Type": "application/json", "session-token": token_get()}
        data = f'{{"uid": {uid}, "endlocation_id": 0, "startlocation_id":{location_id}, "route": "LINESTRING({route})", "status": 1}}'
        res = r.post(route_adress, headers=headers,data=data)
        print(res.text)
        route = ""
        return route
    #보낼때 요청을 한번해서 확인을 한다 받아지는지 안받아지는지 그리고 나서 없으면 집어넣고 있으면 그냥 공중 분해 시켜버린다.

def route_exist_send(uid,route,location_id):
    headers = {"Content-Type": "application/json", "session-token": token_get()}
    data = f'{{"startlocation_id": {location_id}}}'
    res = r.get(route_adress, headers=headers, data=data)
    if res.text==f'No data found for startlocation_id: {location_id}':
        return route_send(uid,route,location_id)
    else:
        return "루트 이미 있음"
    
def route_need(startlocation_id):
    headers = {"Content-Type": "application/json", "session-token": token_get()}
    data = f'{{"startlocation_id": {startlocation_id}}}'
    res = r.get(route_adress, headers=headers, data=data)
    if res.status_code != 200 or res.text == f'No data found for startlocation_id: {startlocation_id}':
        return "루트없음"
    else:
        res=res.json()
        res=dict(res[0])
        return res

def favorite_point_post(cluster_store):
    if not cluster_store:
        print("cluster_store가 비어 있음. 처리 중단")
        return"cluster_store가 비어 없다 처리 중단한다"
    uid=cluster_store[0]["uid"]
    exist_points = favorite_point_get(uid)
    for favpoint in cluster_store:
        d=1
        if exist_points != 404:
            for exist_point in exist_points:
                if point_to_tuple(exist_point["coordinate"]) == point_to_tuple(favpoint["coordness"]):
                    d=0
                    break
        if d==1:    
            headers = {"content-type": "application/json", "session-token": token_get()}
            data = f'{{"uid": {favpoint["uid"]}, "coordinate": "{favpoint["coordness"]}", "status": 0, "alias": 1}}'
            res = r.post(favpoint_adress, headers=headers,data=data)
            return "잘 저장됨"

def favorite_point_get(uid):
    headers = {"Content-Type": "application/json", "session-token": token_get()}
    data = f'{{"uid": {uid}}}'
    res = r.get(favpoint_adress, headers=headers, data=data)
    if res.status_code != 200:
        return 404
    else:
        return res.json()


def uid_get():
    headers = {"Content-Type": "application/json", "Session-Token": token_get()}
    res = r.get("http://Integration-Server:3000/users", headers=headers)
    if res.status_code != 200:
        return "아직 유저가 없음"
    p=res.json()
    p=dict(p[1])
    uid=p['uid']
    return uid

def token_get():
    res=r.get("http://Integration-Server:3000/service_connect")
    return res.text
 
def point_get(uid):
    headers = {"Content-Type": "application/json", "session-token": token_get()}
    data = f'{{"uid": {uid}}}'
    res=r.get("http://Integration-Servert:3000/location/latest", headers=headers, data=data)
    if res.status_code != 200:
        return "Error: Unable to fetch point data"
    now_point_data = res.json()
    now_point= now_point_data["coordinate"]
    now_point = now_point.replace("POINT(", "").replace(")", "")
    return now_point

def month_points_get(uid):
    headers = {"Content-Type": "application/json", "session-token": token_get()}
    now_date = datetime.now()
    one_month_ago = now_date - timedelta(days=30)
    data = f'{{"uid": {uid}, "search_time": "{one_month_ago.strftime("%Y-%m-%d %H:%M:%S")}"}}'               
    res = r.get("http://Integration-Server:3000/location/month_points", headers=headers,data=data)
    if res.status_code != 200:
        return "아직 어떤 기록도 없음"
    return res.json()

def home_get(uid):
    headers = {"Content-Type": "application/json", "session-token": token_get()}
    data = f'{{"uid": {uid}}}'
    res = r.get(favpoint_adress, headers=headers, data=data)
    if res.status_code != 200 :
        return "아직 집이 없음"
    res = res.json()
    home=res[0]
    return home

def point_to_tuple(wkt_str):
    wkt_str = wkt_str.strip()
    if wkt_str.startswith("POINT(") and wkt_str.endswith(")"):
        wkt_str = wkt_str[6:-1]  # remove 'POINT(' and ')'
    return tuple(map(float, wkt_str.split()))