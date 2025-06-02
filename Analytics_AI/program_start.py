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

class UserTracker:
    def __init__(self):
        self.user = DC.control()
        self.status = "in"  # 집에 있는 상태로 시작
        self.event = None

    def wait_until_leave_home(self):
        print("실시간으로 데이터 받는중")
        while self.status == "in":
            self.user.route=""
            time.sleep(3)

            if should_update():
                update_clusters()
            else:
                print("아직 30일이 안됐음")

            self.user.get()
            if self.user.home_out() == '집을 나감':
                self.status = "out"
                print("집을 나감")
                MS.switch(0,self.user.now_uid)
                break

    def monitor_while_out(self):
        print("밖에 있음 ...")

        while self.status == "out":
            time.sleep(3)
            self.user.get()

            if self.user.event == "특정 장소 도착":#if_send는 요청이 비어있을때만 보내는 함수이다
                RR.route_exist_send(self.user.route)#없을때는 false를 반환하므로
                self.event = WE.exit(self.user.now_uid)
                print(f"특정 장소 도착 이벤트 발생: {self.event}")
                return

            if self.user.home_in() == '곧 집에 들어옴':
                self.prepare_home_entry()
                return

    def monitor_until_home(self):
        print("퇴근길 아님")
        while self.status == "out":
            time.sleep(3)
            self.user.get()
            if self.user.home_in() == "곧 집에 들어옴":
                self.prepare_home_entry()
                return

    def prepare_home_entry(self):
        print("곧 집에 들어옵니다")
        MS.switch(1,self.user.now_uid)
        self.status = "in"
        self.event = None

