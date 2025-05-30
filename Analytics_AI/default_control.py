import machine_swich as MS
import point_range as PR
import json

#디폴트 제어는 집에 엄청 가까워졌을때만을 목적으로 하기때문에 레벨은 0 or 1 밖에 없다.
class control:
    def __init__(self):
        self.level=0
        #나중에 리퀘스트로 받아야함
        self.home_point=""
        self.now_point=""
        self.now_uid=""
        self.event=""

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
    
        MS.swich(self.level,self.now_uid)
        print("집을 들어올때 디폴트")
    
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

        MS.swich(self.level,self.now_uid)
        print("집을 나갈때 디폴트")
    
    def control_panel(self,b):
        self.get()
        if b==1:
            self.home_out()
        else:
            return"집을 안나감"