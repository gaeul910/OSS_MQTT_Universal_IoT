import pandas as pd
from datetime import timedelta, datetime,date
from sklearn.cluster import DBSCAN
import numpy as np
from collections import defaultdict
import json
import uuid
import random
import requests as r

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

# -------------------- 유틸리티 함수 --------------------
def parse_point(coordness):
    lon, lat = coordness.replace("POINT(", "").replace(")", "").split()
    return float(lat), float(lon)

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

# -------------------- 클러스터 초기화 (DBSCAN) --------------------
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
            cluster_points = logs[logs['cluster'] == cid][['lat', 'lon']]
            center = cluster_points.mean()
            cluster_store[str(center['uid'])] = {
                "lat": center['lat'],
                "lon": center['lon'],
                "visit_days": set(days),
                "last_visit": max(days)
            }

    return cluster_store

# -------------------- 클러스터 업데이트 --------------------
def update_or_create_cluster(log, cluster_store):
    lat, lon = log['lat'], log['lon']
    date = log['timestamp'].date().isoformat()

    for cid, info in cluster_store.items():
        if is_same_cluster(lat, lon, info['lat'], info['lon']):
            info['visit_days'].add(date)
            info['last_visit'] = max(info['last_visit'], date)
            return

    cluster_store[str(log['uid'])] = {
        "lat": lat,
        "lon": lon,
        "visit_days": {date},
        "last_visit": date
    }

    return log_entries

