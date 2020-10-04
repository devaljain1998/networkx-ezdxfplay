def get_line_points_2d(line) -> tuple:
    """This function returns fetches the following points from the line: x1, y1, x2, y2

    Args:
        line (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].

    Returns:
        tuple: Returns a tuple of coordinate in the following order: x1, y1, x2, y2.
    """
    return line[0][0], line[0][1], line[1][0], line[1][1]

def are_lines_overlapping(line1, line2, slope) -> bool:
    """This function checks whether the two lines are overlapping or not.

    Args:
        line1 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
        line2 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].

    Returns:
        bool: True if lines are overlapping otherwise False.
    """        
    x11, y11, x12, y12 = get_line_points_2d(line1)
    x21, y21, x22, y22 = get_line_points_2d(line2)
    
    def in_range(a, a1, a2):
        min_a = min(a1, a2)
        max_a = max(a1, a2)
        return (a >= min_a and a <= max_a) or (min_a >= a and max_a <= a)
        
    #Check if the lines are overlapping
    if slope == 0 or slope == inf:
        is_overlapping_line1 = (in_range(x11, x21, x22) or in_range(x12, x21, x22)
                        or in_range(y11, y21, y22) or in_range(y12, y21, y22))
        is_overlapping_line2 = (in_range(x21, x11, x12) or in_range(x22, x11, x12)
                        or in_range(y21, y11, y12) or in_range(y22, y11, y12))
    else:
        is_overlapping_line1 = (
            (in_range(x11, x21, x22) or in_range(x12, x21, x22))
                        and 
            (in_range(y11, y21, y22) or in_range(y12, y21, y22)))
        is_overlapping_line2 = (
            (in_range(x21, x11, x12) or in_range(x22, x11, x12))
                        and 
            (in_range(y21, y11, y12) or in_range(y22, y11, y12)))
        
    #Anyone of the line1 or line2 should fall inside each other
    return is_overlapping_line1 or is_overlapping_line2

def is_line_decreasing_on_x_2d(line) -> bool:
    """Function to check whether the line is decreasing with respect to x-axis.
    The condition for decreasing:
    if x1 > x2.

    Args:
        line (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].

    Returns:
        bool: Returns True is the line is decreasing otherwise False.
    """
    x1, y1, x2, y2 = get_line_points_2d(line)
    return (x1 > x2)

def is_line_decreasing_on_y_2d(line) -> bool:
    """Function to check whether the line is decreasing with respect to y-axis.
    The condition for decreasing:
    if y1 > y2.

    Args:
        line (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].

    Returns:
        bool: Returns True is the line is decreasing otherwise False.
    """
    x1, y1, x2, y2 = get_line_points_2d(line)
    return (y1 > y2)


def get_mid_points_between_points(point1, point2) -> tuple:
    """This function returns mid point between two points.

    Args:
        point1 (tuple): Point which will be of format (x, y).
        point2 (tuple): Point which will be of format (x, y).

    Returns:
        tuple: Mid Point: (((x1 + x2) / 2)), ((y1 + y2) / 2)))
    """
    mid_point = []
    # x coordinate
    mid_point.append(((point1[0] + point2[0]) / 2))
    
    # y coordinate
    mid_point.append(((point1[1] + point2[1]) / 2))

    # z coordinate    
    if len(point1) > 2:
            mid_point.append(((point1[2] + point2[2]) / 2))
            
    return tuple(mid_point)
