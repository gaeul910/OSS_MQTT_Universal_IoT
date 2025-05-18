import math 

def range(point1,point2):
    length=math.dist(point1,point2)
    return length 

def slope(point1,point2):
    if(point2[0]-point1[0]==0):
        return 0
    
    return(point2[1]-point1[1])-(point2[0]-point1[0])