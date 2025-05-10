import json
import machine_swich as MS
#키고 끄는것 혹은 어떤 기기를 끄고 끌지는 숫자로 상황을 판별해서 뭘 키고 끌지 결정 

num=8

dir=[]

for i in range(0,num):
    filename=f"./test{i}.json"
    with open(filename,"r") as f:
     p=json.load(f)                
     if isinstance(p,list):          
         p=dict(p)
         
     dir.append(p)                        
#딕셔너리로 저장되어있는 경로들을 리스트 형태안에 딕셔너리 파일로 만들어주는 작업


point=[]
for i in range(0,num):
    pointer=dir[i]["coordness"]
    pointer=(pointer.replace("POINT(","").replace(")",""))
    point.append(list(map(float, pointer.split())))
#json 파일들에 있는 좌표들을 전부 point 배열에 저장해준다

print(point)

request=open("test.json","r")
with  request as f:
     p=json.load(f)                
     if isinstance(p,list):          
         p=dict(p[0])

     now_point=p["coordness"]
     now_point=now_point.replace("POINT(","").replace(")","")
#현재 좌표를 요청해서 이 변수에 받는다 만약 딕셔너리로 받는다고 가정을 한다면

data=now_point.split()  
row=float(data[0])
column=float(data[1])
#그 좌표를 넣기
print(row,column)
status=1
#머신을 어떤 상태로 만들지 결정하기 
leng=len(point)

for i in range(0,leng):
    if row < point[i][0]-10 or row > point[i][0]+10: 
        status=0
        break
    #위도
    elif column < point[i][1]-10 or column > point[i][1]+10:
        status=0
        break
    #경도
    
   
    if i == leng - 2:
        MS.swich(status)
    # 거의 도착했다고 판단하고 미리 켜놓기

if status==0:
    MS.swich(status)

# 혹시라도 거의 도착했는데 방향을 틀면 다시 꺼놓기
# 알림 구현 및 데이터 베이스에서 좌표 받아서 경로 구현 