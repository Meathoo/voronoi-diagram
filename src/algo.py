from line import *
from drawline import *
import copy

# 任何使用到線上兩點使用y座標排序的接錯誤，不一定y值大的就是所求，向量均為順時針轉向者才正確

history_lines = []

def sol(points : list, pointNum: int, canvas):
    if pointNum > 3:
        pointsL, pointsR = divide(points, pointNum)
        print("Left: ", pointsL, "\nRight: ", pointsR)
        linesL, _ = sol(pointsL, len(pointsL), canvas)
        linesR, _ = sol(pointsR, len(pointsR), canvas)
        # draw_lines(linesL+linesR,canvas)
        # return linesL+linesR
        return merge(pointsL, pointsR, linesL, linesR, canvas), history_lines
    elif pointNum == 3:
        return solThree(ThreePoints(points[0], points[1], points[2])), history_lines
    elif pointNum == 2 :
        return solTwo(Line(points[0], points[1])), history_lines

def solTwo(line : Line) -> list[Line]:
    history_lines.append([copy.deepcopy(line)])
    return [line]

def solThree(threePoints : ThreePoints) -> list[Line]:
    history_lines.append(copy.deepcopy(solveThreeParallel(threePoints)) + copy.deepcopy(solveCircumcenter(threePoints)))
    return solveThreeParallel(threePoints) + solveCircumcenter(threePoints)
    
def divide(points : list, pointNum: int):
    avg_x=0
    for p in points:
        avg_x+=(p[0]/pointNum)
    print("中心x:", avg_x)
    points.sort(key=lambda p: (p[0], p[1]))
    if len(points[:pointNum//2])==len(points[pointNum//2:]):
        return points[:pointNum//2], points[pointNum//2:]
    
    for i in range(pointNum):
        if points[i][0] > avg_x or (i>0 and points[i][0]==points[i-1][0]):
            return points[:i], points[i:]
        
    return points[:pointNum//2], points[pointNum//2:]
 

def merge(pointsL : list, pointsR : list, linesL, linesR, canvas):
    hyperplane_result = []
    history_intersection = []
    history_linesIdx = []
    meetLowerTengent = False
    # pointsL,pointsR = sorted(pointsL, key=lambda p:p[1]),sorted(pointsR, key=lambda p:p[1])
    lines = linesL+linesR
    for line in lines:
        print(line.canvasLine)
    lp, rp = findTangent(pointsL, pointsR, isUpper=1) #  [(x,y),(x,y)]
    LowerTengent = findTangent(pointsL, pointsR, isUpper=0)
    LowerTengentLine = Line(LowerTengent[0],LowerTengent[1], isHyper=1)
    # 有時不處理下切線會正確，但有時必須處理，而多處理下切線也不會造成錯誤，如講義範例
    print("上切線：",lp,rp,"\n下切線：",LowerTengent[0],LowerTengent[1])
    # while 1:
    for i in range(10):
        hyperplaneline = Line(lp,rp,isHyper=True)
        hyper1point_upper, hyper1point_lower = hyperplaneline.canvasLine # has sorted by y value
        pairs = getIntersections(hyperplaneline, lines, history_linesIdx, history_intersection) # [((x,y),idx),((x,y),idx), ...]
        for (x,y),i in pairs:
            print("可能的交點：", (x,y))
        if len(pairs)==0: # 若提早遇到沒交點 必差下切線
            print("沒有交點了，處理下切線")
            reviseLineByKnown2Points(LowerTengentLine,a=history_intersection[-1],b=LowerTengentLine.canvasLine[1])
            hyperplane_result.append(LowerTengentLine)

            # reviseCanvasLine(lines, history_linesIdx[-1], history_intersection[-2], history_intersection[-1], hyper1point_lower)
            # 消線
            for i, line in enumerate(lines):
                if on_segment(history_intersection[-1], line.canvasLine):
                    print("revise:",line.canvasLine)
                    reviseCanvasLine(lines, i, history_intersection[-2], history_intersection[-1], hyper1point_lower)
            history_lines.append(copy.deepcopy(lines)+copy.deepcopy(hyperplane_result))
            return hyperplane_result + lines

        # lasthyper = hyper1point_upper if len(history_intersection)==0 else history_intersection[-1]
        # pairs.sort(key= lambda pair : cal_length(pair[0],lasthyper))
        pairs.sort(key= lambda pair : pair[0][1]) # sort by lower y value  in the case with very close distance of 2 points, should select the intersection which is the close one to the last intersection 
        intersection, target_line, idx = pairs[0][0], lines[pairs[0][1]], pairs[0][1]
    
        print("第一優先交點:",intersection,",該兩點", lines[idx].points,"的中垂線")

        isLeft = True if target_line in linesL else False
        if isLeft:
            print("lp: ", lp)
            print("points: ", target_line.points)
            # print("XOR: ", target_line.points.index(lp)^1)
            lp = target_line.points[target_line.points.index(lp)^1]
        else:
            print("rp: ", rp)
            print("points: ", target_line.points)
            # print("XOR: ", target_line.points.index(rp)^1)
            rp = target_line.points[target_line.points.index(rp)^1]
        print("新切線(hyper2): ",lp,rp)
        hyperplaneline2 = Line(lp,rp,isHyper=True)

        reviseLineByKnown2Points(hyperplaneline, intersection, history_intersection) # revise hyperplane

        lasthyper = hyper1point_upper if len(history_intersection)==0 else history_intersection[-1]
        
        hyper2destination = chooseEndPoint(lasthyper, intersection, hyperplaneline2.canvasLine[1], hyperplaneline2.canvasLine[0])

        print("上個切線中垂線的上點:",hyper1point_upper,"歷史:",lasthyper,"hyper2destination: ",hyper2destination)
        reviseCanvasLine(lines, idx, lasthyper, intersection, hyper2destination)
        
        history_intersection.append(intersection)

        # avoid duplicate intersection
        print("忽略該兩點", lines[idx].points,"的中垂線")
        history_linesIdx.append(idx)

        hyperplane_result.append(hyperplaneline)
        history_lines.append(copy.deepcopy(lines)+copy.deepcopy(hyperplane_result)) # add the line to history
        # draw_lines(lines+hyperplane_result,canvas)
    return hyperplane_result + lines

def findTangent(pointsL : list, pointsR : list, isUpper = 1):
    LPoints = Line(pointsL[0], pointsL[1]) if len(pointsL) == 2 else ThreePoints(pointsL[0], pointsL[1], pointsL[2])
    RPoints = Line(pointsR[0], pointsR[1]) if len(pointsR) == 2 else ThreePoints(pointsR[0], pointsR[1], pointsR[2])
    
    LClk, RClk = LPoints.points[:], RPoints.points[::-1] #上切線 ： 左逆時針,右順時針
    if not isUpper:
        LClk, RClk = LPoints.points[::-1], RPoints.points[:] #下切線 ： 左順時針,右逆時針

    lp, rp = pointsL[-1], pointsR[0] # 左半最右 右半最左點
    while 1:
        lp_cpy, rp_cpy = lp, rp
        new_lp = nextElement(LClk, lp)
        lp = new_lp if isClockwise(rp, lp, new_lp) == isUpper else lp
        new_rp = nextElement(RClk, rp)
        rp = new_rp if isClockwise(lp, rp, new_rp) == (isUpper^1) else rp
        if lp_cpy == lp and rp_cpy == rp:
            break
    return [lp,rp]

def nextElement(li, cur):
    return li[(li.index(cur)+1) % len(li)]

def cal_crossprod(a, b, c): #Vab to Vac
    # vector A => AB = b - a
    # vector B => AC = c - a
    vA = b[0] - a[0], b[1] - a[1]
    vB = c[0] - a[0], c[1] - a[1]
    cross = vA[0]*vB[1]-vB[0]*vA[1]
    # 外積
    # va = (ax, ay), vb = (bx, by)
    # va x vb = | ax ay |
    #           | bx by | = ax*by-bx*ay
    return cross

def isClockwise(a, b, c): #Vab to Vac
    cross = cal_crossprod(a, b, c)
    if cross > 0:
        return 1
    elif cross < 0:
        return 0
    else:
        return -1 #共線（角度為0或180度）
    
def chooseEndPoint(p1, p2, p3, p4):
    cross1 = cal_crossprod(p1, p2, p3)
    cross2 = cal_crossprod(p1, p2, p4)
    if cross1 < cross2:
        return p3
    else:
        return p4

def cal_length(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def solveThreeParallel(threePoints : ThreePoints) -> list[Line]:
    is_three_parallel = threePoints.isThreeParallel
    result = []
    if is_three_parallel:
        print(f'三條線平行: {is_three_parallel}')
        b1,b2 = threePoints.lines[0].canvasLine # because parallel
        # ----------- not sure can use sort function or not ----------- 
        # print("before: ", threePoints.lines)
        sortedLines = sorted(threePoints.lines, key=lambda line: cal_length(line.center, b1))  # Sort by distance to the first border point
        # print("after: ", sortedLines)
        # ----------- not sure can use sort function or not -----------
        for line in sortedLines[0::2]: # index[0],index[0+2]
            result.append(line)

    return result

def solveCircumcenter(threePoints : ThreePoints):
    no_circumcenter = threePoints.isThreeParallel
    print(f'存在外心: {not no_circumcenter}')
    # print(f'逆:{threePoints.points}')
    if not no_circumcenter:
        circumcenter = threePoints.circumcenter
        print(f'外心: {circumcenter}')
        return cut(threePoints, circumcenter)
    return []

def cut(threePoints : ThreePoints, circumcenter) -> list[Line]:
    result = []
    vertiVectors = threePoints.vertiVectors
    d = 120
    for i in range(len(vertiVectors)):
        v = vertiVectors[i]
        p = (circumcenter[0] + d * v[0], circumcenter[1] + d * v[1])
        # canvas.create_oval(p1[0] - 3, p1[1] - 3, p1[0] + 3, p1[1] + 3, fill='black')
        # canvas.create_oval(p2[0] - 3, p2[1] - 3, p2[0] + 3, p2[1] + 3, fill='black')
        threePoints.lines[i].canvasLine = [circumcenter, p]
        threePoints.lines[i].canvasLine = threePoints.lines[i].canvasLine[:]
        result.append(threePoints.lines[i])
        # draw_line(canvas, circumcenter, p)
    return result

def has_duplicates(points):
    return True if len(points) != len(set(points)) else False

def getIntersections(line1 : Line, lines: list[Line], history_linesIdx, history_intersection):
    p1, m1= line1.center, line1.verticalSlope
    pairs = []
    thres = 0.000000001
    for i, line in enumerate(lines):
        tooClose = 0
        p2, m2 = line.center, line.verticalSlope
        x, y = getIntersection(p1,m1,p2,m2)
        # for (hx,hy) in history_intersection:
        #     if abs(x-hx)<thres and abs(y-hy)<thres:
        #         print("太靠近先前交點")
        #         tooClose = 1
        #         break
        if i in history_linesIdx: #已處理過交點
            print("處理過的線")
            continue
        if (x,y) == (float('inf'),float('inf')):
            print("平行無交點")
            continue
        
        if not on_segment((x,y),line.canvasLine):
            print(f"未在線段上： {(x,y)}未在{line.canvasLine}線段上")
            continue
        pairs.append(((x,y),i)) # tuple(intersection,idx)
    return pairs

def getIntersection(p1, m1, p2, m2):
    if m1 == m2:
        return (float('inf'),float('inf'))  # 平行或重合，無交點
    x = (m1 * p1[0] - m2 * p2[0] + p2[1] - p1[1]) / (m1 - m2)
    y = m1 * (x - p1[0]) + p1[1]
    return (x, y)

def on_segment(p, seg):
    (x, y) = p
    (x1, y1), (x2, y2) = seg
    thres = 0.01
    # Allowable slight errors
    return (min(x1, x2)-thres <= x <= max(x1, x2)+thres and
            min(y1, y2)-thres <= y <= max(y1, y2)+thres)

def reviseLineByKnown2Points(line, intersection=None, history_intersection=None, a=None, b=None):
    if a and b:
        line.canvasLine = [a, b]
        return
    if len(history_intersection) == 0:
        # in first round hyperplaneline.canvasLine[0] already has the lower y value
        line.canvasLine[1] = intersection
    else:
        line.canvasLine = [history_intersection[-1], intersection]

def reviseCanvasLine(lines, idx, hyper1point_upper, intersection, hyper2point_lower):
    if lines[idx].circumcenter != None:
        lines[idx].canvasLine = [intersection, lines[idx].circumcenter]
    else:
        # 若hyperplane轉向 與 向邊界點轉向相同 則該方向須去除(改成交點與另一側邊界連線)
        cross_hyper = isClockwise(hyper1point_upper, intersection, hyper2point_lower) # v1(upper point to intersection), v2(intersection to lower point)
        cross_upper_border1 = isClockwise(hyper1point_upper,intersection,lines[idx].canvasLine[0])
        cross_upper_border2 = isClockwise(hyper1point_upper,intersection,lines[idx].canvasLine[1])
        print("H1->H2方向:",cross_hyper)
        print(f"H1->{lines[idx].canvasLine[0]}方向:", cross_upper_border1)
        print(f"H1->{lines[idx].canvasLine[1]}方向:", cross_upper_border2)
        if cross_hyper == cross_upper_border1:
            lines[idx].canvasLine = sorted([intersection, lines[idx].canvasLine[1]], key=lambda p: p[1])
        elif cross_hyper == cross_upper_border2:
            lines[idx].canvasLine = sorted([intersection, lines[idx].canvasLine[0]], key=lambda p: p[1])

# def solveLowerTengent(LowerTengent, lines, history_tengent, history_linesIdx, history_intersection, hyperplane_result):
#     print("SolvinglowerTengent")
#     Llp,Lrp = LowerTengent
#     lowerTengent = Line(Llp,Lrp,isHyper=True)
#     if not lowerTengent in history_tengent:
#         border_upper, border_lower = lowerTengent.canvasLine # has sorted by y value
#         allLines = lines + hyperplane_result
#         pairs = getIntersections(lowerTengent, allLines, history_linesIdx, history_intersection)
#         pairs.sort(key= lambda pair: -pair[0][1]) # sort by higher y value
#         print("pairs: ", pairs)
#         if len(pairs) == 0:
#             return
#         intersection = pairs[0][0]
#         history_intersection.append(intersection)
#         reviseLineByKnown2Points(lowerTengent, border_lower, history_intersection) # revise hyperplane
#         hyperplane_result.append(lowerTengent) # add last hyperplane

#         for line in lines:
#             if on_segment(intersection,line.canvasLine):
#                 print("revise:",line.canvasLine)
#                 reviseLineByKnown2Points(line, a=history_intersection[-1], b=line.canvasLine[1]) # revise the higher y value point of nonhyperplanes to intersection 
#     return
    