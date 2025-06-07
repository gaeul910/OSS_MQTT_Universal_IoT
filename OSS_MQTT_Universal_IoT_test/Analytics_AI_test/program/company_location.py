import pandas as pd
from datetime import timedelta, datetime,date
from sklearn.cluster import DBSCAN
import numpy as np
from collections import defaultdict
import json
import uuid
import random
import set_of_request as r

#처음 받은 데이터를 계산하기 쉽게 나누는 중
def cluster_to_log_entries(cluster_store):
    log_entries = []
    for i, (cid, info) in enumerate(cluster_store.items(), start=1):
        lat = round(info['lat'], 6)
        lon = round(info['lon'], 6)
        latest_date = datetime.fromisoformat(info['last_visit'])
        log_entries.append({
            "id": info.get("id", i), 
            "coordness": f"POINT({lon:.6f} {lat:.6f})",
            "time": latest_date.isoformat() + "Z",
            "uid": info.get("uid", str(uuid.uuid4())), 
        })
    return log_entries

# 유틸
def parse_point(coordness):
    lon, lat = coordness.replace("POINT(", "").replace(")", "").split()
    return float(lon), float(lat)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0088  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c * 1000  # meters

def is_same_cluster(lat1, lon1, lat2, lon2, threshold=30):
    return haversine_distance(lat1, lon1, lat2, lon2) <= threshold

# 클러스터 없으면 만들기
def detect_initial_clusters(logs):
    logs = logs.copy()
    logs['timestamp'] = pd.to_datetime(logs['timestamp'])
    logs = logs.sort_values(by='timestamp')

    coords = np.radians(logs[['lat', 'lon']].to_numpy())
    kms_per_radian = 6371.0088
    eps_km = 0.03  # 30m 이내
    db = DBSCAN(eps=eps_km / kms_per_radian, min_samples=7, algorithm='ball_tree', metric='haversine')
    labels = db.fit_predict(coords)
    logs['cluster'] = labels
    logs['date'] = logs['timestamp'].dt.date

    cluster_day_duration = defaultdict(timedelta)
    grouped = logs.groupby(['cluster', 'date'])
    for (cid, day), group in grouped:
        if cid == -1:
            continue
        duration = group['timestamp'].max() - group['timestamp'].min()
        if duration >= timedelta(minutes=60):
            cluster_day_duration[cid, day] += duration

    cluster_visit_days = defaultdict(set)
    for (cid, day), duration in cluster_day_duration.items():
        cluster_visit_days[cid].add(day.isoformat())

    cluster_store = {}
    for cid, days in cluster_visit_days.items():
        #초기 방문일수로 필터링
        if len(days) >= 10:
            cluster_points = logs[logs['cluster'] == cid][['lat', 'lon', 'uid']]
            
            representative_uid = cluster_points['uid'].iloc[0]
            center = cluster_points[['lat', 'lon']].mean()
            
            cluster_store[cid] = {
                "lat": center['lat'],
                "lon": center['lon'],
                "status": set(days),
                "uid": representative_uid,
            }

    return cluster_store

# 업데이트!!!!
def update_or_create_cluster(log, cluster_store, logs_df, min_points=7, radius_m=30):
    lat, lon = log['lat'], log['lon']
    date = log['timestamp'].date().isoformat()

    # 기존 클러스터에 속하는지 확인
    for cid, info in cluster_store.items():
        if is_same_cluster(lat, lon, info['lat'], info['lon']):
            info['status'].add(date)
            return  # 기존 클러스터에 포함되었으므로 종료

    same_day_logs = logs_df[logs_df['timestamp'].dt.date == log['timestamp'].date()]
    nearby_count = 0

    for _, row in same_day_logs.iterrows():
        dist = haversine_distance(lat, lon, row['lat'], row['lon'])
        if dist <= radius_m:
            nearby_count += 1
        if nearby_count >= min_points:
            break

    # 조건 미달이면 클러스터 생성하지 않음
    if nearby_count < min_points:
        return

    new_cid = max(cluster_store.keys(), default=-1) + 1
    cluster_store[new_cid] = {
        "lat": lat,
        "lon": lon,
        "status": {date},
        "uid": log['uid'],
    }
# 로그로 만들기
def preprocess_logs(raw_logs):
    parsed_data = []
    for log in raw_logs:
        lat, lon = parse_point(log['coordinate'])
        parsed_data.append({
            "timestamp": pd.to_datetime(log['time']),
            "lat": lat,
            "lon": lon,
            "uid": log['uid']
        })
    return pd.DataFrame(parsed_data)

def cluster_store_to_log_entries(cluster_store):
    log_entries = []
    for i, (cid, info) in enumerate(cluster_store.items(), start=1):
        # 좌표 소수점 6자리까지 포맷
        lat = round(info['lat'], 6)
        lon = round(info['lon'], 6)
        log_entries.append({
            "coordness": f"POINT({lon:.6f} {lat:.6f})",
            "stat": len(info.get('status', [])),
            "uid": info.get("uid", str(uuid.uuid4())), 
        })
    return log_entries

def convert_favpoints_to_cluster_store(favpoints):
    cluster_store = {}
    for item in favpoints:
        lat, lon = parse_point(item['coordinate'])
        cluster_store[item['id']] = {
            "lat": lat,
            "lon": lon,
            "status": set(),  # 방문일자 집합 초기화 (없으면 비어있는 상태)
            "uid": item['uid']
        }
    return cluster_store


def update(uid):
   
    raw_logs = r.month_points_get(uid) 
    logs = preprocess_logs(raw_logs)

    res = r.favorite_point_get(uid)
    # 1. 초기 클러스터 생성
    if len(res)<=1:
        cluster_store = detect_initial_clusters(logs)
    else:
        cluster_store = convert_favpoints_to_cluster_store(res)

    # 2. 실시간 로그 업데이트 실행 (마지막 날짜 기준)
    for _, row in logs.iterrows():
        update_or_create_cluster(row, cluster_store, logs_df=logs)


    cluster_store = {
        cid: info for cid, info in cluster_store.items()
        #방문일수로 필터링
        if len(info['status']) >= 10
    }
    print("필터링 이후 클러스터 개수:", len(cluster_store))
    # 결과 출력 내가 너한테 데이터를 줄때 클러스터 데이터랑// 회사 좌표를 줄꺼야

    for cid in cluster_store:
        cluster_store[cid]["status"] = set()  # 방문일수를 0으로 설정

    output=cluster_store_to_log_entries(cluster_store)
    if not output:
        print("보낼 데이터가 존재하지 않음")
        return
    r.favorite_point_post(output)  # 클러스터 데이터를 서버에 전송
    return 