import machine_swich as MS
import json

#디폴트 제어는 집에 엄청 가까워졌을때만을 목적으로 하기때문에 레벨은 0 or 1 밖에 없다.
def home():
    revel=0
    request=open("test7.json","r")
    #요청받는 값은 json형태이다
    with request as f:
        p=json.load(f)                
        if isinstance(p,list):          
          p=dict(p[0])

        home_point=p["coordness"]
        home_point=home_point.replace("POINT(","").replace(")","")
        #집의 좌표를 요청해서 받는다
    data=home_point.split()
    home_row=float(data[0])
    home_column=float(data[1])
    print(home_row,home_column)
    # 집의 좌표를 실수형으로 저장

    request=open("test.json","r")
    #요청받는 값은 json형태이다
    with request as f:
        p=json.load(f)                
        if isinstance(p,list):          
           p=dict(p[0])

        now_point=p["coordness"]
        now_point=now_point.replace("POINT(","").replace(")","")
    #현재 좌표를 요청해서 이 변수에 받는다 만약 딕셔너리로 받는다고 가정을 한다면

    data=now_point.split()  
    now_row=float(data[0])
    now_column=float(data[1])

    if home_row-10 < now_row <home_row+10:
       if home_column-10 < now_column < home_column+10:
          revel=1


    MS.swich(revel)

    

    

    
home()
#좌표가 제대로 나오는지 확인용 나중에 지워야함