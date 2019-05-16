import math

def line_move(x,y,vx,vy):
    return (x+vx, y+vy)

def circle_move(x,y, x0, y0, w):
    r = math.sqrt((x-x0)**2+(y-y0)**2)
    phase= math.acos((x-x0)/r)

    return (x0+r*math.cos(phase+w), y0+r*math.sin(phase+w))

    
