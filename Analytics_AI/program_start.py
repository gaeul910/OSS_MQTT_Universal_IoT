import default_control as DC
import work_exit as WE
import machine_swich as MS
import time
import json
import os
from datetime import datetime, timedelta
import set_of_request as RR
import company_location as CL

LAST_RUN_FILE = "last_run.json"
INTERVAL_DAYS = 30  

def get_last_run_date():
    if not os.path.exists(LAST_RUN_FILE):
        return None  # 실행 이력 없음
    with open(LAST_RUN_FILE, "r") as f:
        data = json.load(f)
        return datetime.fromisoformat(data["last_run"])

def save_last_run_date():
    with open(LAST_RUN_FILE, "w") as f:
        json.dump({"last_run": datetime.now().isoformat()}, f)

def should_update():
    last_run = get_last_run_date()
    if not last_run:
        return True 
    next_due = last_run + timedelta(days=INTERVAL_DAYS)
    return datetime.now() >= next_due

def update_clusters():
    CL.update()
    save_last_run_date()

