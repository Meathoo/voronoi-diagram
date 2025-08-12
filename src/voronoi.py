from read import readInput
from algo import *
import tkinter as tk
from line import *

r = 3
color_idx = 0
color_list = [
    "#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF",  # 紅綠藍黃紫青
    "#800000", "#008000", "#000080", "#808000", "#800080", "#008080",  # 深色系
    "#FFA500", "#A52A2A", "#7FFF00", "#DC143C", "#00CED1", "#FF1493",  # 橙褐草紅青粉
    "#1E90FF", "#B22222", "#228B22", "#DAA520", "#4B0082", "#FF69B4",  # 藍綠金靛粉紅
    "#CD5C5C", "#20B2AA", "#90EE90", "#FFD700",  # 柔色
    "#9932CC", "#E9967A", "#F08080", "#66CDAA", "#8FBC8F", "#C71585"   # 更多混色
]

def draw_line(canvas, p1, p2):
    canvas.create_line(p1[0], p1[1], p2[0], p2[1], width=2, fill=color_list[color_idx % len(color_list)])
    color_idx += 1


class Voronoi:
    def __init__(self, root):
        self.root = root
        self.root.title("Voronoi")
        self.points = []
        self.data = []
        self.data_index = 0
        self.waiting = False
        self.cvh_history = []
        self.cvh_history_t = False
        self.history = []
        self.history_t = None
        self.stepMode = False
        self.merge_history = []
        self.mergeidx = 0

        # create canvas
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.canvas.pack()

        # clear button
        self.clear_button = tk.Button(self.root, text="Clear", font=("consolas"), command=self.clear_canvas)
        self.clear_button.pack(side='left', padx=3, pady=3)

        # read data button
        self.read_data_button = tk.Button(self.root, text="Read Data", font=("consolas"), command = self.read_data)
        self.read_data_button.pack(side='left', padx=3, pady=3)

        # execute button
        self.execute_button = tk.Button(self.root, text="Execute", font=("consolas"), command=self.exeDraw)

        # execute button
        self.next_button = tk.Button(self.root, text="Step", font=("consolas"), command=self.stepDraw)

        # read next data button
        self.read_next_data_button = tk.Button(self.root, text="Next Data", font=("consolas"), command=self.read_next_data)

        self.position_label = tk.Label(text="", font=("consolas"))
        self.position_label.pack(side='right', pady=3)

        # binding mouse click to draw points
        self.canvas.bind("<Motion>", self.update_position)
        self.canvas.bind("<Button-1>", self.draw_point_event)

    def draw_point_event(self, event):
        self.read_data_button.pack_forget()
        self.read_next_data_button.pack_forget()
        self.execute_button.pack(side='left')
        self.next_button.pack(side='left')
        self.points.append((event.x, event.y))
        self.draw_point(event.x, event.y)
        print(f'({event.x},{event.y})')

    def draw_point(self, x, y, color='red'):
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
        bx,by = 15,15
        if y < 300 and x>300:
            bx = -60
        elif y > 300 and x<300:
            by = -15
        elif y > 300 and x>300:
            bx,by = -60,-15
        self.canvas.create_text(x+bx, y+by, text=f"({int(x)},{int(y)})", anchor="w", font=("consolas", 8))
        
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.points.clear()

    def read_data(self):
        self.data = readInput()
        print(self.data)
        self.data_index = 0
        self.read_data_button.pack_forget()
        self.read_next_data_button.pack(side='left', padx=3, pady=3)
        self.read_next_data()
        

    def read_next_data(self):
        self.clear_canvas()
        self.points.clear()
        self.history.clear()
        self.merge_history.clear()
        self.mergeidx = 0
        self.cvh_history.clear()
        self.cvh_history_t = 0
        self.stepMode = False
        self.execute_button.pack(side='left', padx=3)
        self.next_button.pack(side='left', padx=3, pady=3)
        n = int(self.data[self.data_index])
        if n == 0:
            print('讀入點數為零，檔案測試停止')
            self.read_data_button.pack(side='left', padx=3, pady=3)
            self.read_next_data_button.pack_forget()
            self.execute_button.pack_forget()
            self.next_button.pack_forget()
            return

        print(f'點數：{n}')
        for j in range(n):
            # print(self.data_index + j + 1)
            # print(self.data[self.data_index + j + 1])
            x, y = map(int, self.data[self.data_index + j + 1].split(' '))
            print(f'座標：({x},{y})')
            self.points.append((x, y))
            self.draw_point(x, y)
        self.data_index += n + 1

    def execute(self):
        pointNum = len(self.points)
        if pointNum<2:
            print('少於兩點，無法繪製Voronoi圖')
            return [],[]
        if has_duplicates(self.points):
            print('有兩個點重複，無法繪製Voronoi圖')
            return [],[]
        lines, convexhull, history, cvh_history= sol(self.points, pointNum, canvas=self.canvas)
        self.cvhLastIdx = len(cvh_history)-1
        print("cvh_history length:",len(cvh_history))
        return history, cvh_history
    
    def exeDraw(self):
        if not self.stepMode:
            self.history, self.cvh_history = self.execute()
            if self.history == []:
                return
            self.stepMode = True
        self.history_t = len(self.history)-1
        self.cvh_history_t = len(self.cvh_history)-1
        self.stepDraw()

    def stepDraw(self):
        if not self.stepMode:
            self.clear_lines()
            self.history.clear()
            self.cvh_history.clear()
            self.cvh_history_t = 0
            self.merge_history.clear()
            self.mergeidx = 0
            self.history, self.cvh_history = self.execute()
            if self.history == []:
                return
            self.stepMode = True
            self.history_t = 0
            print(len(self.history))
        else:
            for line in self.history[self.history_t]: # clear the old lines if hyperplane exist or it has been merged
                if line.afterMerge:
                    self.merge_history.append((self.merge_history[-1] if self.merge_history else []) + self.history[self.history_t]) # backup merge subgraph
                if line.isHyper:
                    self.clear_lines()
                    if len(self.merge_history) and (not self.cvh_history_t >= self.cvhLastIdx):
                        draw_lines(self.merge_history[-1], self.canvas)
                    break
        
        if (self.cvh_history_t+1) % 3 == 0:
            self.clear_lines()
            if len(self.merge_history) and (not self.cvh_history_t >= self.cvhLastIdx):
                draw_lines(self.merge_history[-1], self.canvas)

        if len(self.points)>3 and (self.cvh_history_t+1) %3 == 0 or len(self.history[self.history_t]) == 0:
            draw_lines(self.cvh_history[self.cvh_history_t], self.canvas)
            self.cvh_history_t += 1

        draw_lines(self.history[self.history_t], self.canvas)

        self.history_t +=1
        if self.history_t >= len(self.history):
            self.stepMode = False
        
    def clear_lines(self):
        self.canvas.delete("all")
        for p in self.points:
            self.draw_point(p[0], p[1])
    
    def update_position(self, event):
        x, y = event.x, event.y
        self.position_label.config(text=f"Cursor : ({x}, {y})")