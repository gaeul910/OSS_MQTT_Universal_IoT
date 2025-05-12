import machine_swich as swich
import json

revel=0
#디폴트 제어는 집에 엄청 가까워졌을때만을 목적으로 하기때문에 레벨은 0 or 1 밖에 없다.
def home():
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
    # 집의 좌표를 실수형으로 저장ㅇ
    
home()