from math import sin, cos, atan, pi

def rotate(points, angle):

    final = []
    angle = angle / (180/pi)

    for point in points:
        rel_angle = atan(point[1]/point[0]) if point[0] else pi/2
        length = ((point[0]**2 + point[1]**2)**(1/2))

        final.append([length * cos(rel_angle + angle), length * sin(rel_angle + angle)])

    return final

def _rotate(points, angle):
    return [[((point[0]**2 + point[1]**2)**(1/2)) * cos((atan(point[1]/point[0]) if point[0] else pi/2) + angle / (180/pi)), 
        ((point[0]**2 + point[1]**2)**(1/2)) * sin((atan(point[1]/point[0]) if point[0] else pi/2) + angle / (180/pi))] for point in points]

print(rotate([[0.707, 0.707], [-0.707, 0.707]], 45))
print(_rotate([[0.707, 0.707], [-0.707, 0.707]], 45))