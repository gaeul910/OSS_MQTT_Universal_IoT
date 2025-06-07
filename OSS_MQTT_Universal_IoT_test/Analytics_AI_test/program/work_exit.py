import json
import machine_swich as MS
import point_range as pr
import time
import set_of_request as RR
#키고 끄는것 혹은 어떤 기기를 끄고 끌지는 숫자로 상황을 판별해서 뭘 키고 끌지 결정하는 파일


def exit(uid,event_id):
    point=[]
    route=RR.route_need(event_id)
    if route == "루트없음":
        return "퇴근길아님"
    coords_str = route["route"].replace("LINESTRING(", "").replace(")", "")

    # 각 좌표를 튜플(float, float)로 변환하여 리스트 생성
    point = [tuple(map(float, pair.split())) for pair in coords_str.split(",")]
    print("Work_exit:",point)
    #포인트에 뭐가 들어갔는지 확인하는 용도 나중에 지워야함
    if len(point) <= 2:
        return "퇴근길아님"

    status=0
    #머신을 어떤 상태로 만들지 결정하기 
    leng = len(point) - 2
    i = 0

    while (1):
        now_point=RR.point_get(uid)
        data=now_point.split()
        now_point=[]
        now_point.append(float(data[0]))
        now_point.append(float(data[1]))
        #좌표 넣기
        # 출발지에서 벗어나면(100m 이상) 반복문 탈출해서 퇴근길 판단 진행
        if pr.range(now_point, point[0]) < 100:
            print("아직 출발지 근처입니다. 퇴근길 아님.")
            # 다음 좌표로 넘어가도록 continue가 아니라 break로 변경
            break

        if(i!=leng-1):
            print(now_point,"\ni: ",i,"\n좌표사이의 거리: ",pr.range(now_point,point[i]),"\n좌표사이의 거리: ",pr.range(point[i],point[i+1]),"\n현재좌표사이의 기울기: ",pr.slope(now_point,point[i]),"\n좌표사이의 기울기: ",pr.slope(point[i+1],point[i]))
        #위도,경도에 뭐가 들어가있는지 확인하는 용도 나중에 지워야함

        advanced = False
        for skip in range(1, 4):
            if i + skip >= leng:
                if(status==1):
                    return "퇴근길맞음"
                break

            dist = pr.range(now_point, point[i + skip])
            if dist < 500:
                print(f"{skip}단계 건너뛰기 허용됨, 거리: {dist:.2f}m")
                i += skip
                advanced = True
                break
            print(i,leng-1)

        if not advanced:
            print("경로에서 너무 벗어났습니다. 종료")
            status = 0
            break

        if i == leng - 1:
            status=1
            MS.switch(status,uid)
        # 거의 도착했다고 판단하고 미리 켜놓기
    
            
    #30초마다 좌표를 확인해준다.

    if status==0:
        MS.switch(status,uid)
        return "퇴근길아님"
# 혹시라도 거의 도착했는데 방향을 틀면 다시 꺼놓기