import tkinter as tk
from line import Line

color_idx = 0

color_list = [
    "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", # 紅綠藍黃紫青
    "#800000", "#008000", "#000080", "#808000", "#800080", "#008080",  # 深色系
    "#FFA500", "#A52A2A", "#7FFF00", "#DC143C", "#00CED1", "#FF1493",  # 橙褐草紅青粉
    "#1E90FF", "#B22222", "#228B22", "#DAA520", "#4B0082", "#FF69B4",  # 藍綠金靛粉紅
    "#CD5C5C", "#20B2AA", "#90EE90", "#ADD8E6", "#D3D3D3", "#FFD700",  # 柔色
    "#9932CC", "#E9967A", "#F08080", "#66CDAA", "#ADD8E6", "#C71585"   # 更多混色
]

def draw_line(canvas, p1, p2, line):
    if line.erase:
        return
    # global color_idx
    w =  2
    color = "#DC143C" if line.Lpart else "#1E90FF"
    color = "black" if line.isHyper else color#color_list[color_idx % len(color_list)]
    color = "#ADD8E6" if line.afterMerge else color
    color = "#AFAFAF" if line.isConvexHull else color
    color = "#00FF00" if line.isTengent else color
    canvas.create_line(p1[0], p1[1], p2[0], p2[1], width=w, fill=color)
    # color_idx += 1

def draw_lines(lines: list[list[Line]], canvas):
    # print("輸出線:", lines)
    # print("輸出線段數: ", len(lines))
    # print("drawLINE:",lines)
    for line in lines:
        # if type(line) == list:
        #     line = line[0]
        p1,p2 = line.points if line.isConvexHull else line.canvasLine
        # print("輸出線段: ",p1,p2)

        draw_line(canvas, p1, p2, line)
