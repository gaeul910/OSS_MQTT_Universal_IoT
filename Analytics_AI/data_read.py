import json

with open("./test.json","r") as f:
    dir = json.load(f)                
# .json �솗�옣�옄 �뙆�씪�뿉�꽌 �뵓�뀛�꼫由� �삎�깭濡� �젙蹂� ����옣
    if isinstance(dir,list):          
# 留뚯빟 諛쏆븘�삤�뒗寃� 由ъ뒪�듃�씪 寃쎌슦 �뵓�뀛�꼫由щ줈 諛붽퓞
      dir=dict(dir[0])
    print(dir)                      
# �옒 ����옣 �릺�뿀�뒗吏� �솗�씤�슜

with open("./test1.json","w") as t:   
#�뵓�뀛�꼫由щ�� json �뙆�씪�삎�깭濡� ����옣
    json.dump(dir,t, indent=2)

pointer=dir["coordness"]
point=pointer.replace("POINT(","").replace(")","")
data=point.split()

row=float(data[0])
column=float(data[1])
status=0
len=7

for i in range(0,len):
   if 120-10 < row < 120+10:
      if 40-10 < column < 40+10:
         status=1
         break
         
print(status)