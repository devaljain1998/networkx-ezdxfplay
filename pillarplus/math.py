# Docstrings in code planning and documentation

# Remove * import

from math import *
import sympy as sp
from ezdxf.math import Vector

# angle in radians


def directed_points_on_line(point, angle, width):
    x1 = point[0] + width * cos(angle)
    y1 = point[1] + width * sin(angle)
    x2 = point[0] - width * cos(angle)
    y2 = point[1] - width * sin(angle)
    return (x1, y1), (x2, y2)


def is_between(point, line_start, line_end):
    return round(find_distance(line_start, point) + find_distance(point, line_end), 5) == round(find_distance(line_start, line_end), 5)


def find_distance(p1, p2):
    distance = ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    return distance


def find_distance_3d(p1, p2):
    distance = ((p1[0] - p2[0])**2 + (p1[1] - p2[1])
                ** 2 + (p1[2] - p2[2])**2)**0.5
    return distance

# condition is either farthest or nearest


def find_point_by_distance(points, end, condition):
    point = points[0]
    distance = find_distance(point, end)
    for p in points:
        dist_temp = find_distance(p, end)
        if (dist_temp > distance and condition == 'farthest') or (dist_temp < distance and condition == 'nearest'):
            point = p
            distance = dist_temp
    return point


def find_perpendicular_point(center, line_start, line_end):
    x1, y1 = line_start[0], line_start[1]
    x2, y2 = line_end[0], line_end[1]
    x3, y3 = center[0], center[1]
    try:
        k = ((y2 - y1) * (x3 - x1) - (x2 - x1) * (y3 - y1)) / \
            ((y2 - y1)**2 + (x2 - x1)**2)
    except:
        return(x1, y1)
    x4 = x3 - k * (y2 - y1)
    y4 = y3 + k * (x2 - x1)
    return(x4, y4)


def find_intersection_point(s1, e1, s2, e2):
    p1, p2, p3, p4 = sp.Point(s1), sp.Point(e1), sp.Point(s2), sp.Point(e2)
    l1 = sp.Line(p1, p2)
    l2 = sp.Line(p3, p4)
    intersection_point = l1.intersection(l2)
    return (intersection_point[0].x, intersection_point[0].y)

# returns tan(theta) value
def find_intersection_point_1(s1,e1,s2,e2):
    # find intersection forcefully 
    line1 = (s1,e1)
    line2 = (s2,e2)
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (x, y)



def find_slope(start, end):
    x1, y1 = start[0], start[1]
    x2, y2 = end[0], end[1]

    if x2 == x1:
        slope = inf
    else:
        slope = (y2 - y1) / (x2 - x1)
    return slope


# returns angle in radians
def find_slope_angle(start, end):
    # Independent of start and end
    slope = find_slope(start, end)
    return atan(slope)


# returns angle in radians
def find_perpendicular_slope_angle(start, end):
    slope = find_slope(start, end)
    return pi / 2 + atan(slope)


def find_directed_point(start, end, margin):
    angle = find_slope_angle(start, end)
    p1, p2 = directed_points_on_line(start, angle, margin)
    d1 = find_distance(p1, end)
    d2 = find_distance(p2, end)
    if d1 < d2:
        return p1
    else:
        return p2


def find_rotation(line_start, line_end):
    vector = Vector(line_end) - Vector(line_start)
    angle = vector.angle_deg
    return round(angle)


def is_inverted(point, from_point, to_point):
    from_vector = Vector(point) - Vector(from_point)
    to_vector = Vector(to_point) - Vector(point)
    return to_vector.cross(from_vector).z < 0


def is_parallel(line1, line2):
    return find_slope(line1[0], line1[1]) == find_slope(line2[0], line2[1])


def convert_to_clockwise(point_list):
    """
    Return a clockwise orientation of points of a polygon.

    Takes in a list of points that form a polygon. Each point is (x,y,z).
    Consider z = 0, find their orientation. Reverse the list to change
    anti-clockwise orientation to clockwise.

    Parameters:
        points_list (list): List of points that form corner of polygon

    Returns:
        list: Same or reversed list of points

    Raises:
        IOError: Points don't form a polygon or are not closed
    """
    clockwise = 0
    anti_clickwise = 0
    for i in range(0, len(point_list) - 2):
        p1 = point_list[i]
        p2 = point_list[i + 1]
        p3 = point_list[i + 2]
        x1, y1 = p1[:2]
        x2, y2 = p2[:2]
        x3, y3 = p3[:2]
        det = x1 * (y2 - y3) - y1 * (x2 - x3) + \
            (x2 * y3 - y2 * x3)  # determinant
        if det > 0:
            anti_clickwise += 1
        else:
            clockwise += 1

    if clockwise > anti_clickwise:
        return point_list
    else:
        return [ele for ele in reversed(point_list)]


def form_pair_from_list(l):
    l_pairs = []
    length = len(l)
    for i in range(length):
        l_pairs.append((l[i], l[(i + 1) % length]))
    return l_pairs


def get_side_points(point, angle, auto_center_dist, auto_behind_dist, auto_side_left,
                    auto_side_right):
    angle = angle * pi / 180

    if auto_center_dist is not None:
        center_point = directed_points_on_line(point, angle, auto_center_dist)[0]
    else:
        center_point = point

    if auto_behind_dist is None:
        return center_point, None, None, None

    back_point = directed_points_on_line(point, angle, auto_behind_dist)[0]

    if auto_side_left is not None:
        back_point_left = directed_points_on_line(
            back_point, angle + pi / 2, auto_side_left)[0]
    else:
        back_point_left = None

    if auto_side_right is not None:
        back_point_right = directed_points_on_line(
            back_point, angle - pi / 2, auto_side_right)[0]
    else:
        back_point_right = None
    return center_point, back_point, back_point_left, back_point_right


def find_upper(n, range_list):
    """
    """
    upper = 3
    return upper

# New functions


def onLine(p, q, r):
    if(q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1])):
        return True
    return False


def orient(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    # print(val)
    if(val == 0):
        return 0
    if(val > 0):
        return 1
    else:
        return 2


def inter(p1, q1, p2, q2):
    o1 = orient(p1, q1, p2)
    o2 = orient(p1, q1, q2)
    o3 = orient(p2, q2, p1)
    o4 = orient(p2, q2, q1)
    # print(o1,o2,o3,o4)
    if(o1 != o2 and o3 != o4):
        # print('lala')
        return True

    if(o1 == 0 and onLine(p1, p2, q1)):
        return True
    if(o2 == 0 and onLine(p1, q2, q1)):
        return True
    if(o3 == 0 and onLine(p2, p1, q2)):
        return True
    if(o4 == 0 and onLine(p2, q1, q2)):
        return True
    return False

def onSegment(p, q, r): 
    if ( (q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and 
           (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))): 
        return True
    return False
  
def orientation(p, q, r): 
    val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1])) 
    if (val > 0):  
        return 1
    elif (val < 0):  
        return 2
    else:  
        return 0
def doIntersect(p1,q1,p2,q2): 
    
    o1 = orientation(p1, q1, p2) 
    o2 = orientation(p1, q1, q2) 
    o3 = orientation(p2, q2, p1) 
    o4 = orientation(p2, q2, q1) 
    if ((o1 != o2) and (o3 != o4)): 
        return True
    if ((o1 == 0) and onSegment(p1, p2, q1)): 
        return True
    if ((o2 == 0) and onSegment(p1, q2, q1)): 
        return True
    if ((o3 == 0) and onSegment(p2, p1, q2)): 
        return True
    if ((o4 == 0) and onSegment(p2, q1, q2)): 
        return True 
    return False


def check_point_in_polygon(p, l):
    inf = 10 * max([a[0] for a in l])
    if len(l) < 3:
        return False
    ext = (inf, p[1])
    count = 0
    i = 0
    fl = False
    while(i != 0 or fl == False):
        next = (i + 1) % len(l)
        if(inter(l[i], l[next], p, ext)):
            if(orient(l[i], p, l[next]) == 0):
                return onLine(l[i], p, l[next])
            count += 1
        fl = True
        i = next
    return count & 1


def find_mid_point(start, end):
    x = (start[0] + end[0]) / 2
    y = (start[1] + end[1]) / 2
    z = (start[2] + end[2]) / 3
    return (x, y, z)


def find_centroid(points):
    centroid_x = 0
    centroid_y = 0
    centroid_z = 0
    length = len(points)

    for point in points:
        centroid_x += point[0]
        centroid_y += point[1]
        centroid_z += point[2]

    centroid_x /= length
    centroid_y /= length
    centroid_z /= length

    return centroid_x, centroid_y, centroid_z

def find_angle(p1,p2,p3):
    #in Radian
    
    angle1 = atan2(p3[1]-p2[1], p3[0]-p2[0]);
    angle2 = atan2(p1[1]-p2[1], p1[0]-p2[0]);
    angle = angle1 - angle2;
    if (angle < 0):
        angle += 2 * pi;

    return angle

def check_unnecessary_points_on_polyline(rooms_dict_list):
    flag = 0
    unnecessary_polyline_layers = []
    for room in rooms_dict_list:
        coordinates = []
        for point in room['corners']:
            coordinates.append(point)
        coordinates_length = len(coordinates)
        for i in range(coordinates_length):
            angle = find_angle(coordinates[i%coordinates_length],
                       coordinates[(i+1)%coordinates_length],
                       coordinates[(i+2)%coordinates_length])
            if 179 <= angle*(180/pi) <= 182:
                flag = 1
                unnecessary_polyline_layers.append(room['room_name'])
    if len(unnecessary_polyline_layers) == 0:
        return False
    else:
        return unnecessary_polyline_layers

# Testing
print(find_rotation((0, 0), (-1, 1)))
print(find_rotation((0, 0), (-1, -1)))
print(find_rotation((0, 0), (1, 1)))
print(find_rotation((0, 0), (1, -1)))
print(get_side_points((0, 0), 90, None, 10, 10, 10))

# print(is_inverted((0,0),(1,1),(1,0)))
# print(find_rotation((1,0),(0,-0.5)))
# print(atan(inf))
