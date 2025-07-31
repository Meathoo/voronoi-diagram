import math

class Line:
    def __init__(self, p1, p2, circumcenter=None, isHyper=False):
        self.p1 = p1
        self.p2 = p2
        self.points = [p1, p2]
        self.center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        sort_counterclockwise(self.points, self.center)
        self.length = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

        self.slope = self.cal_slope()
        self.verticalSlope = 1e-10 if self.slope == float('inf') else -1 / self.slope  # vertical line slope

        self.b = self.center[1] - self.slope * self.center[0]  # y = mx + b
        self.vb = self.center[1] - self.verticalSlope * self.center[0]  # y = mx + b

        self.vector = (self.p1[0]-self.p2[0],self.p1[1]-self.p2[1])
        self.vertiVectors = rotate_right_90(self.vector)

        self.canvasLine = self.findRay2Points()  #  #self.find_border_points()  # [(x,y),(x,y)]

        self.isHyper = isHyper
        self.hasCut = False 
        self.circumcenter = circumcenter

    def cal_slope(self):
        if self.p1[0] == self.p2[0]:  # vertical line
            return float('inf')
        slope = (self.p1[1] - self.p2[1]) / (self.p1[0] - self.p2[0])
        slope = slope if slope != 0 else 1e-10 # horizontal line and avoid division by zero
        return slope
    
    def find_border_points(self):
        legal_points = set() # Use set to avoid duplicate points
        axis = [0.0, 600.0] # x=0,x=600,y=0,y=600
        for xv in axis:
            y = self.verticalSlope * (xv - self.center[0]) + self.center[1] # (0,y) ,(600,y)
            x = (xv - self.center[1]) / self.verticalSlope + self.center[0] # (x,0) ,(x,600)
            if y >= 0 and y <= 600:
                legal_points.add((xv, y))
            if x >= 0 and x <= 600:
                legal_points.add((x, xv))
        return sorted(list(legal_points), key=lambda p : p[1])
    
    def findRay2Points(self):
        d = 50
        # print(f'移動量 x: {d * unit_v[0]}, y: {d * unit_v[1]}')
        v = self.vertiVectors
        p1,p2 = (self.center[0] + d * v[0], self.center[1] + d * v[1]), (self.center[0] - d * v[0], self.center[1] - d * v[1])
        return sorted([p1,p2], key=lambda p : p[1])
    
class ThreePoints():
    def __init__(self, p1, p2, p3):
        self.points = [p1,p2,p3]
        self.center_of_all = ((p1[0] + p2[0] + p3[0]) / 3, (p1[1] + p2[1] + p3[1]) / 3)
        sort_counterclockwise(self.points, self.center_of_all)
        self.lines = [Line(self.points[0], self.points[1]), Line(self.points[1], self.points[2]), Line(self.points[2], self.points[0])]
        self.isThreeParallel = True if self.lines[0].slope == self.lines[1].slope and self.lines[1].slope == self.lines[2].slope else False
        if not self.isThreeParallel:
            self.circumcenter = self.findCircumcenter(self.lines)
            self.reset_line_circumcenter()
        self.vectors = [line.vector for line in self.lines]
        self.vertiVectors = [rotate_right_90(v) for v in self.vectors]
    
    def findCircumcenter(self, lines : list[Line]):
        for i in range(len(lines)):
            m1, b1 = lines[i].verticalSlope, lines[i].vb
            for j in range(i + 1, len(lines)):
                m2, b2 = lines[j].verticalSlope, lines[j].vb
                if m1 == m2:  # Parallel lines --------- should not happen in here
                    continue
                x = (b2 - b1) / (m1 - m2)
                y = m1 * x + b1
                return (x, y)  # Return the circumcenter coordinates
    
    def reset_line_circumcenter(self):
        for i in range(3):
            self.lines[i].circumcenter = self.circumcenter

def rotate_right_90(v):
    x, y = v
    return (y, -x)

def sort_counterclockwise(points, center):
    # def angle_from_center(p):
    #     return (p[0] - self.center_of_all[0]) ** 2 + (p[1] - self.center_of_all[1]) ** 2
    def angle(p):
        return math.atan2(p[0] - center[0], p[1] - center[1])
    points.sort(key=angle)