# main.py
import tkinter as tk
from controller.controller import Controller

if __name__ == '__main__':
    user_input = input()
    w, h = map(int, user_input.split()) if user_input != "" else (6, 5)
    root = tk.Tk()
    root.title('Block Fill Line Puzzle - Solver')
    Controller(root, w=w, h=h, step_delay=0)
    root.mainloop()
