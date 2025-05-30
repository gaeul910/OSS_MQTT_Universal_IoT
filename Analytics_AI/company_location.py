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
    return log_entries

