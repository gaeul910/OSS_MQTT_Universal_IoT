import json
import machine_swich as MS
import point_range as pr
#키고 끄는것 혹은 어떤 기기를 끄고 끌지는 숫자로 상황을 판별해서 뭘 키고 끌지 결정하는 파일

num=8

dir=[]

for i in range(0,num):
    filename=f"./test{i}.json"
    with open(filename,"r") as f:
     p=json.load(f)                
     if isinstance(p,list):          
         p=dict(p)
         
     dir.append(p)                        
#json 형태의 데이터들을 퇴근길이라고 할때 경로들을 리스트 형태안에 딕셔너리 파일로 만들어주는 작업


point=[]
for i in range(0,num):
    pointer=dir[i]["coordness"]
    pointer=(pointer.replace("POINT(","").replace(")",""))
    point.append(list(map(float, pointer.split())))
#json 파일들에 있는 좌표들을 전부 point 배열에 저장해준다

print(point)
#포인트에 뭐가 들어갔는지 확인하는 용도 나중에 지워야함

request=open("test.json","r")
#요청받는 값은 json형태이다
with request as f:
     p=json.load(f)                
     if isinstance(p,list):          
        p=dict(p[0])

     now_uid=p["uid"]    
     now_point=p["coordness"]
     now_point=now_point.replace("POINT(","").replace(")","")
#현재 좌표를 요청해서 이 변수에 받는다 만약 딕셔너리로 받는다고 가정을 한다면

data=now_point.split()
now_point=[]
now_point.append(float(data[0]))
now_point.append(float(data[1]))
#좌표 넣기


print(now_point)
#위도,경도에 뭐가 들어가있는지 확인하는 용도 나중에 지워야함

status=1
#머신을 어떤 상태로 만들지 결정하기 
leng=len(point)

for i in range(0,leng):
    if pr.range(now_point,point[i])>5:
        status=0
        break
    
    if i == leng - 2:
        MS.swich(status,now_uid)
    # 거의 도착했다고 판단하고 미리 켜놓기

if status==0:
    MS.swich(status,now_uid)
# 혹시라도 거의 도착했는데 방향을 틀면 다시 꺼놓기