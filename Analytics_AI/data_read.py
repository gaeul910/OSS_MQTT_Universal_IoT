import json

num=8   
# 8은 임시 데이터 개수 근데 한개 아무것도 아닌거 +함으로 -1을 해줘야함 
#for i in range(0,7):
#    pilename=f"./test{num}.json"                           
#    with open(pilename,"w") as t:   #딕셔너리를 json파일로 
#         json.dump(dir,t, indent=2)
#         num+=1
# 주간의 좌표 결과를 딕셔너리 형태 데이터를 json형태의 파일로 만들어주는 작업


dir=[]

for i in range(0,num):
    pilename=f"./test{i}.json"
    with open(pilename,"r") as f:
     p=json.load(f)                
     if isinstance(p,list):          
         p=dict(p)
         
     dir.append(p)                        
#딕셔너리로 저장되어있는 경로들을 리스트 형태안에 딕셔너리 파일로 만들어주는 작업


point=[]
for i in range(0,num):
    pointer=dir[i]["coordness"]
    point.append(pointer.replace("POINT(","").replace(")",""))

#딕셔너리 파일들 좌표를 point라는 리스트에 넣어주는것
sear=7
#찾으려는 좌표를 쳐서 받기
data=point[sear].split()  
row=float(data[0])
column=float(data[1])
#그 좌표를 넣고
print(row,column)
status=1
len=7

arr=[
   [120,40],
   [120,40],
   [120,40],
   [120,40],
   [120,40],
   [120,40],
   [120,40]
]
#arr은 임시 경로

for i in range(0,len):
    if arr[i][0]-10  < row < arr[i][0]+10:
        if arr[i][1]-10 < column < arr[i][1]+10:
            status=0
            break
#좌표가 경로에 벗어났는지 안 벗어났는지 체크한다
print(status)