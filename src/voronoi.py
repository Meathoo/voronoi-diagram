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
        self.history = []
        self.history_t = None
        self.stepMode = False

        # create canvas
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.canvas.pack()

        # clear button
        self.clear_button = tk.Button(self.root, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side='left', padx=3, pady=3)

        # read data button
        self.read_data_button = tk.Button(self.root, text="Read Data", command = self.read_data)
        self.read_data_button.pack(side='left', padx=3, pady=3)

        # execute button
        self.execute_button = tk.Button(self.root, text="Execute", command=self.exeDraw)

        # execute button
        self.next_button = tk.Button(self.root, text="Step", command=self.stepDraw)

        # read next data button
        self.read_next_data_button = tk.Button(self.root, text="Read Next Data", command=self.read_next_data)

        # binding mouse click to draw points
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
        self.canvas.create_text(x+15, y+15, text=f"({int(x)},{int(y)})", anchor="w", font=("Arial", 10))
    
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
        self.stepMode = False
        self.execute_button.pack(side='left', padx=3)
        self.next_button.pack(side='left', padx=3, pady=3)
        n = int(self.data[self.data_index])
        if n == 0:
            print('讀入點數為零，檔案測試停止')
            self.read_data_button.pack()
            self.read_next_data_button.pack_forget()
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
            return []
        if has_duplicates(self.points):
            print('有兩個點重複，無法繪製Voronoi圖')
            return []
        lines, history = sol(self.points, pointNum, canvas=self.canvas)
        return history
    
    def exeDraw(self):
        if not self.stepMode:
            self.history = self.execute()
            if self.history == []:
                return
            self.stepMode = True
        self.history_t = len(self.history)-1
        self.stepDraw()

    def stepDraw(self):
        if not self.stepMode:
            self.clear_lines()
            self.history.clear()
            self.history = self.execute()
            print("history: ", self.history)
            if self.history == []:
                return
            self.stepMode = True
            self.history_t = 0
            print(len(self.history))
        else:
            for line in self.history[self.history_t]: # clear the old lines if the hyperplane exist
                if line.isHyper:
                    self.clear_lines()
                    break

        draw_lines(self.history[self.history_t], self.canvas)
        self.history_t +=1
        if self.history_t >= len(self.history):
            self.stepMode = False
        
    def clear_lines(self):
        self.canvas.delete("all")
        for p in self.points:
            self.draw_point(p[0], p[1])
        