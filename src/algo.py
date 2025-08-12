from line import *
from drawline import *
import copy

history_lines = []
history_cvhlines = []

def sol(points : list, pointNum: int, canvas, Lpart = None):
    if pointNum > 3:
        pointsL, pointsR = divide(points, pointNum)
        linesL, cvhL, _, _ = sol(pointsL, len(pointsL), canvas, Lpart=True)
        linesR, cvhR, _, _ = sol(pointsR, len(pointsR), canvas, Lpart=False)
        print("LR: ",pointsL, pointsR)
        # draw_lines(linesL+linesR,canvas)
        # return linesL+linesR
        return *merge(cvhL, cvhR, linesL, linesR, canvas), history_lines, history_cvhlines
    elif pointNum == 3:
        return *solThree(ThreePoints(points[0], points[1], points[2], Lpart=Lpart)), history_lines, history_cvhlines
    elif pointNum == 2 :
        return *solTwo(Line(points[0], points[1], Lpart=Lpart)), history_lines, history_cvhlines

def solTwo(line : Line):
    history_lines.append([copy.deepcopy(line)])
    return [line], line.points

def solThree(threePoints : ThreePoints):
    convexHull = threePointConvexhull(threePoints.points)
    res = solveCircumcenter(threePoints)
    if threePoints.isThreeParallel:
        res = res + solveThreeParallel(threePoints, convexHull)
    history_lines.append(copy.deepcopy(res))
    return res, convexHull
    
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
 

def merge(cvhL : list, cvhR : list, linesL, linesR, canvas):
    hyperplane_result = []
    history_hyperplane = []
    history_intersection = []
    history_linesIdx = []

    lines = linesL+linesR

    cvhL_lines, cvhR_lines = [Line(cvhL[i], cvhL[nextIndex(i,cvhL)], isConvexHull=True) for i in range(len(cvhL))], [Line(cvhR[i], cvhR[nextIndex(i,cvhR)], isConvexHull=True) for i in range(len(cvhR))]
    history_lines.append([])  #停留一步
    history_cvhlines.append(copy.deepcopy(cvhL_lines))

    history_lines.append([]) #停留一步
    history_cvhlines.append(copy.deepcopy(cvhR_lines))

    cvh_lines, cvh, lp, rp, llp, lrp = mergeConvexHull(cvhL, cvhR) # upperTengent: [lp,rp], lowerTengent: [llp,lrp]
    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!cvh", cvhL)
    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!cvh", cvhR)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!cvh", cvh)
    
    history_lines.append(copy.deepcopy(lines))
    history_cvhlines.append(copy.deepcopy(cvh_lines))

    LowerTengentLine = Line(llp, lrp, isHyper=1)

    print("\n上切線：",lp,rp,"\n下切線：",llp,lrp,'\n')
    while 1:
        print("切線: ",lp,rp)
        hyperplaneline = Line(lp,rp,isHyper=True)
        history_hyperplane.append(hyperplaneline)
        pairs = getIntersections(hyperplaneline, lines, history_linesIdx, history_intersection) # [((x,y),idx),((x,y),idx), ...]
        if len(pairs)==0 or (lp == llp and rp == lrp) : # 若提早遇到沒交點 必差下切線 下切線也不會有跟其他中垂線的交點
            reviseLineByKnown2Points(LowerTengentLine,a=history_intersection[-1],b=LowerTengentLine.canvasLine[1])
            hyperplane_result.append(LowerTengentLine)
            history_lines.append(copy.deepcopy(lines)+copy.deepcopy(hyperplane_result))
            break
        pairs.sort(key= lambda pair : pair[0][1]) # sort by lower y value 原則上由上到下
        print("可能的交點:",pairs)
        intersection, target_line, idx = pairs[0][0], lines[pairs[0][1]], pairs[0][1]
        history_intersection.append(intersection)
        print("第一優先交點:",intersection,",兩點", lines[idx].points,"的中垂線")

        # avoid duplicate intersection
        print("忽略該兩點", lines[idx].points,"的中垂線")
        history_linesIdx.append(idx)

        # 找下個hyperplane的兩點，以利於分割
        isLeft = True if target_line in linesL else False
        if isLeft:
            print("lp: ", lp)
            print("points: ", target_line.points)
            # print("XOR: ", target_line.points.index(lp)^1)
            print(target_line.points)
            lp = target_line.points[target_line.points.index(lp)^1]
        else:
            print("rp: ", rp)
            print("points: ", target_line.points)
            # print("XOR: ", target_line.points.index(rp)^1)
            rp = target_line.points[target_line.points.index(rp)^1]

        reviseHyperLine(hyperplaneline, history_intersection) # revise hyperplane
        hyperplane_result.append(hyperplaneline)
        history_lines.append(copy.deepcopy(lines)+copy.deepcopy(hyperplane_result)) # add the line to history
        # draw_lines(lines+hyperplane_result, canvas) # 畫出hyperplane


    hascutBorder = []
    # 消中垂線
    i = 0 # hyper id
    for idx in history_linesIdx:
        print("兩點",lines[idx].points,"的中垂線\ni =",i)
        print("hyper1起點:",history_hyperplane[i].canvasLine[0],", hyper2終點:",history_hyperplane[i+1].canvasLine[1])
        hascutBorder.append(reviseCanvasLine(lines, idx, history_hyperplane[i].canvasLine[0], history_intersection[i],  history_hyperplane[i+1].canvasLine[1]))
        i+=1
    for p in hascutBorder:
        deepErase(p,lines)
        
    history_lines.append(copy.deepcopy(lines)+copy.deepcopy(hyperplane_result))
    # reset
    all_lines = lines+hyperplane_result
    for line in all_lines:
        line.isHyper = False
        line.afterMerge = True
        line.remain = False
    history_lines.append(copy.deepcopy(all_lines))

    return all_lines, cvh

def mergeConvexHull(cvhL,cvhR):
    upL, upR = findTangent(cvhL, cvhR, isUpper=1)
    lowL, lowR = findTangent(cvhL, cvhR, isUpper=0)
    i_upL, i_upR, i_lowL, i_lowR = cvhL.index(upL),cvhR.index(upR),cvhL.index(lowL),cvhR.index(lowR)
    merged_cvh = []

    print("in mergeConvexHull cvhL", cvhL)
    print("in mergeConvexHull cvhR", cvhR)
    print("in mergeConvexHull 上切:", upL, upR)
    print("in mergeConvexHull 下切:", lowL, lowR)

    # 從 lowL (左側底) 開始，沿左側凸包逆時針到 upL（包含）
    i = i_lowL
    merged_cvh.append(cvhL[i])
    while i != i_upL:
        i = nextIndex(i,cvhL)
        # i = len(cvhL)-1 if i-1<0 else i-1
        merged_cvh.append(cvhL[i])

    # 從 upR 開始，沿右側凸包逆時針到 lowR（包含）
    i = i_upR
    merged_cvh.append(cvhR[i])
    while i != i_lowR:
        i = nextIndex(i,cvhR)
        # i = len(cvhR)-1 if i-1<0 else i-1
        merged_cvh.append(cvhR[i])

    upT_i, lowT_i = merged_cvh.index(upL), merged_cvh.index(lowR)

    cvh_lines = [Line(merged_cvh[i], merged_cvh[nextIndex(i,merged_cvh)], isConvexHull=True, isTengent= True if i==upT_i or i==lowT_i else False) for i in range(len(merged_cvh))]

    return cvh_lines, merged_cvh, upL, upR, lowL, lowR

def findTangent(pointsL, pointsR, isUpper=1):

    lp,rp = max(pointsL, key=lambda p: (p[0], -p[1])), min(pointsR, key=lambda p: (p[0], p[1]))
    # print("in findtengent: ",lp,rp)

    orderL = pointsL[::-1] if isUpper else pointsL[:] #上切線 ： 左逆時針,右順時針
    orderR = pointsR[:] if isUpper else pointsR[::-1] #下切線 ： 左順時針,右逆時針

    iL,iR = orderL.index(lp), orderR.index(rp)

    while True:
        moved = False
        while isClockwise(orderR[iR], orderL[iL], orderL[nextIndex(iL,orderL)]) == isUpper:
            iL = nextIndex(iL,orderL)
            moved = True
        while isClockwise(orderL[iL], orderR[iR], orderR[nextIndex(iR,orderR)]) == (isUpper ^ 1):
            iR = nextIndex(iR,orderR)
            moved = True
        if not moved:
            break
    return orderL[iL], orderR[iR]

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

def isClockwise(a, b, c):
    cross = cal_crossprod(a, b, c) #Vab to Vac
    if cross > 0:
        return 1
    elif cross < 0:
        return 0
    else:
        return -1 #共線（角度為0或180度）

def nextIndex(idx, li):
    return (idx+1) % len(li)
    
def chooseEndPoint(p1, p2, p3, p4):
    cross1 = cal_crossprod(p1, p2, p3)
    cross2 = cal_crossprod(p1, p2, p4)
    # cross > 0 => 逆時針，選擇轉彎角度小的那個
    if cross1 > 0 and cross2 <= 0:
        return p3
    elif cross2 > 0 and cross1 <= 0:
        return p4
    elif cross1 > 0 and cross2 > 0: # 兩個都逆時針 選旋轉得較少角度較小者
        return p3 if cross1 < cross2 else p4
    else:                           # 都順時針或共線，也選轉得較少的那個
        return p3 if abs(cross1) < abs(cross2) else p4

def cal_length(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def threePointConvexhull(li : list):
    cross = cal_crossprod(li[0], li[1], li[2])
    if cross == 0:
        sorted_li = sorted(li, key=lambda p: (p[0], p[1]))
        return [sorted_li[0], sorted_li[-1]]
    if cross > 0:
        return li   # already CCW
    else:
        return li[::-1]

def solveThreeParallel(threePoints : ThreePoints, convexhull) -> list[Line]:
    result = []
    end1, end2 = convexhull
    for line in threePoints.lines:
        if (end1 in line.points) ^ (end2 in line.points):
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
    d = 8999999 # extend length
    for i in range(len(vertiVectors)):
        v = vertiVectors[i]
        # extend_point = (x + d * vectorX, y + d * vectorY)
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
    for i, line in enumerate(lines):
        p2, m2 = line.center, line.verticalSlope
        x, y = getIntersection(p1,m1,p2,m2)
        
        if line.erase:
            continue

        if len(history_intersection)>0 and (y < history_intersection[-1][1] and not isSameValue(y,history_intersection[-1][1])): # hyperplane 是一路往下
            print("本次交點 y value", y,"\n上一次交點 y value",history_intersection[-1][1])
            print("isSame",isSameValue(y,history_intersection[-1][1]))
            print("在前交點上方")
            continue

        if i in history_linesIdx:
            print("處理過的線")
            if isSamePoint((x,y), history_intersection[-1]):
                print("剛處理過的點，去除")
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

def isSameValue(v1,v2):
    thres = 0.1
    return 1 if abs(v1-v2)<thres and abs(v1-v2)<thres else 0

def isSamePoint(p1,p2):
    x1,y1,x2,y2 = p1[0],p1[1],p2[0],p2[1]
    return 1 if isSameValue(x1,x2) and isSameValue(y1,y2) else 0

def on_segment(p, seg):
    (x, y) = p
    (x1, y1), (x2, y2) = seg
    thres = 0.01
    # Allowable slight errors
    return (min(x1, x2)-thres <= x <= max(x1, x2)+thres and
            min(y1, y2)-thres <= y <= max(y1, y2)+thres)

def reviseLineByKnown2Points(line, a=None, b=None):
    if a==None and b:
        line.canvasLine[1] = b
    if a and b==None:
        line.canvasLine[0] = a
    if a and b:
        line.canvasLine = [a, b]
    return
    # 保持線段的順序 新交點再後方(index 1)

def reviseHyperLine(line, history_intersection):
    if len(history_intersection) == 1:
        reviseLineByKnown2Points(line,a=None,b=history_intersection[-1])
    elif len(history_intersection) > 1:
        reviseLineByKnown2Points(line,a=history_intersection[-2],b=history_intersection[-1])
    return

def reviseCanvasLine(lines, i, hyper1point_upper, intersection, hyper2point_lower):
    # 若hyperplane轉向 與 向邊界點轉向相同 則該方向須去除(改成交點與另一側邊界連線)
    cross_hyper = isClockwise(hyper1point_upper, intersection, hyper2point_lower) # v1(upper point to intersection), v2(intersection to lower point)
    cross_upper_border1 = isClockwise(hyper1point_upper,intersection,lines[i].canvasLine[0])
    cross_upper_border2 = isClockwise(hyper1point_upper,intersection,lines[i].canvasLine[1])
    # print("H1->H2方向:",cross_hyper)
    # print(f"H1->{line.canvasLine[0]}方向:", cross_upper_border1)
    # print(f"H1->{line.canvasLine[1]}方向:", cross_upper_border2)
    # cpy = set(line.canvasLine[:])
    # print("Before Cut:", cpy)
    cpy = lines[i].canvasLine[:]
    if cross_hyper == cross_upper_border1:
        lines[i].canvasLine = [intersection, lines[i].canvasLine[1]]
        otherSide = cpy[0]
    elif cross_hyper == cross_upper_border2:
        lines[i].canvasLine = [intersection, lines[i].canvasLine[0]]
        otherSide = cpy[1]

    lines[i].remain = True
    return otherSide

def deepErase(cutPoint, lines):
    for l in lines:
        if cutPoint in l.canvasLine:
            if l.erase or l.remain:
                continue
            l.erase = True
            # print("next Cut point:", l.canvasLine[l.canvasLine.index(cutPoint)^1])
            deepErase(l.canvasLine[l.canvasLine.index(cutPoint)^1], lines)
    return