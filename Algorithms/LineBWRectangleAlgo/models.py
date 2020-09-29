class Beam:
    """This class represents a beam object.
    
    Contains:
        -number: int
        -start_point: point
        -end_point: point
        -screen_start_point: point
        -screen_end_point: point
        -width : float
    """
    
    def __init__(self, number: int, start_point: Vec2, end_point: Vec2, 
                    screen_start_point: Vec2, screen_end_point: Vec2, width: float):
        self.number = number
        self.start_point = start_point
        self.end_point = end_point
        self.screen_start_point = screen_end_point
        self.screen_end_point = screen_end_point
        self.width = width