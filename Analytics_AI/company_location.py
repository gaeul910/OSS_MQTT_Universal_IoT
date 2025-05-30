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
    return log_entries

