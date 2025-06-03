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
        self.now_uid=""
        self.event=""
        self.route=""
        self.not_work_exit=False
    

    def get (self):
        self.level=0
        request=open("test7.json","r")
        #요청받는 값은 json형태이다
        with request as f:
         p=json.load(f)                
         if isinstance(p,list):          
              p=dict(p[0])
         self.now_uid=p["uid"]
         home_point=p["coordness"]
         self.home_point=home_point.replace("POINT(","").replace(")","")
        #집의 좌표를 요청해서 받는다


        """request=open("test.json","r")
        #요청받는 값은 json형태이다
        with request as f:
            p=json.load(f)                
            if isinstance(p,list):          
                p=dict(p[0])

            self.now_uid=p["uid"]    
            now_point=p["coordness"]
            self.now_point=now_point.replace("POINT(","").replace(")","")
    #현재 좌표를 요청해서 이 변수에 받는다 만약 딕셔너리로 받는다고 가정을 한다면"""
        
        self.now_point=input("현재 좌표를 입력해주세용 : ")
        if self.not_work_exit:
            RR.route_get(self.now_point,self.route)# 도착을 하면 get함수로 받는것이 아니라 work_exit.py에서 받음다만 출근길을 벗어났을때는 이걸 사용함 그때 해결법은?
        #현재 좌표를 입력받는다. 나중에 리퀘스트로 받아야함

        request=open("test0.json","r")
        #요청받는 값은 json형태이다
        with request as f:
         p=json.load(f)                
         if isinstance(p,list):          
              p=dict(p[0])

        #if문으로 나중에 오류코드나오면 좌표를 저장하지않는다
         work_point=p["coordness"]
         work_point=work_point.replace("POINT(","").replace(")","")
         if work_point:
            work_data= list(map(float, work_point.split()))
            now_data=list(map(float, self.now_point.split()))
            if PR.range(work_data,now_data)<100:
                self.event="특정 장소 도착"
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
        print(PR.range(home_point,now_point))
        if PR.range(home_point,now_point)>=500:
            self.level=0
            return"집을 나감"
        #현재 위치를 근거로 집 위치와 비교해서 나갔는지 확인하기
        else:
            return"집을 안나감"