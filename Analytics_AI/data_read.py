import json

with open("./test.json","r") as f:
    dir = json.load(f)                # .json 확장자 파일에서 딕셔너리 형태로 정보 저장
    if isinstance(dir,list):          # 만약 받아오는게 리스트일 경우 딕셔너리로 바꿈
      dir=dict(dir[0])
    print(dir)                        # 잘 저장 되었는지 확인용




with open("./test1.json","w") as t:   #딕셔너리를 json 파일형태로 저장
    json.dump(dir,t, indent=2)
