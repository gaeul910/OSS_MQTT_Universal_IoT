import machine_swich as MS
import point_range as PR
import json
import set_of_request as RR

#디폴트 제어는 집에 엄청 가까워졌을때만을 목적으로 하기때문에 레벨은 0 or 1 밖에 없다.
class control:
    def __init__(self):
        self.level=0
        #나중에 리퀘스트로 받아야함
        self.home_point=""
        self.now_point=""
        self.uid=RR.uid_get()
        self.event=""
        self.route=""
        self.not_work_exit=False
        self.event_id = None
    

    def get (self):
        self.level=0
        p=RR.home_get(self.uid)
        if p==404:
            print("집 좌표가 없습니다. 집 좌표를 설정해주세요.")
            return
        #요청받는 값은 json형태이다              
        if isinstance(p,list):          
             p=dict(p[0])
        home_point=p["coordinate"]
        self.home_point=home_point.replace("POINT(","").replace(")","")
        #집의 좌표를 요청해서 받는다

        self.now_point=RR.point_get(self.uid)
        if self.not_work_exit:
            self.route=RR.route_get(self.now_point,self.route)# 도착을 하면 get함수로 받는것이 아니라 work_exit.py에서 받음다만 출근길을 벗어났을때는 이걸 사용함 그때 해결법은?
        #현재 좌표를 입력받는다. 나중에 리퀘스트로 받아야함

        res=RR.favorite_point_get(self.uid)
        if len(res)<=1:
            print("즐겨찾기 포인트가 없습니다.")
            return
        #요청받는 값은 json형태이다                
        for p in res[1:]:
        #if문으로 나중에 오류코드나오면 좌표를 저장하지않는다 회사위치를 어떻게 받냐 get 실시간 location_id로 get_event( id )
            work_point=p["coordinate"]
            work_point=work_point.replace("POINT(","").replace(")","")
            if work_point:
                work_data= list(map(float, work_point.split()))
                now_data=list(map(float, self.now_point.split()))
                if PR.range(work_data,now_data)<100:
                    self.event="특정 장소 도착"
                    self.event_id=p['id']
                    return
        #회사의 좌표가 있다면 요청해서 받는다

        
    
    def home_in(self):
        
        data=self.home_point.split()
        home_point=[]
        home_point.append(float(data[0]))
        home_point.append(float(data[1]))
        print(home_point)
         # 집의 좌표를 실수형으로 저장


        data=self.now_point.split()
        now_point=[]
        now_point.append(float(data[0])) 
        now_point.append(float(data[1])) 

        if PR.range(home_point,now_point)<500:
                 self.level=1
                 return "곧 집에 들어옴"
        #현재 위치를 근거로 집 위치와 비교해서 곧 도착하는지 확인하기
        else :
            return "아직 아님"
    
    
    def home_out(self):
        data=self.home_point.split()
        home_point=[]
        home_point.append(float(data[0]))
        home_point.append(float(data[1]))
        print(home_point)
         # 집의 좌표를 실수형으로 저장

        data=self.now_point.split()
        now_point=[]
        now_point.append(float(data[0])) 
        now_point.append(float(data[1])) 
        print("집과 현재 위치까지의 거리:",PR.range(home_point,now_point))
        if PR.range(home_point,now_point)>=500:
            self.level=0
            return"집을 나감"
        #현재 위치를 근거로 집 위치와 비교해서 나갔는지 확인하기
        else:
            return"집을 안나감"
        
