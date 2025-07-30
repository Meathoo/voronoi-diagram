from voronoi import Voronoi
import tkinter as tk

def main():
    root = tk.Tk()
    app = Voronoi(root)
    root.mainloop()

if __name__ == "__main__":
    main()