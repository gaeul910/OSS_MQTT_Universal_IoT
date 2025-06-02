from math import radians, sin, cos, sqrt, atan2

def range(point1,point2):
    R = 6371 * 1000  # 지구 반지름 (미터 단위)
    
    dlat = radians(point2[1] - point1[1])
    dlon = radians(point2[0] - point1[0])
    
    a = sin(dlat/2)**2 + cos(radians(point1[1])) * cos(radians(point2[1])) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def slope(point1,point2):
    if(point2[0]-point1[0]==0):
        return 0
    
    return(point2[1]-point1[1])-(point2[0]-point1[0])