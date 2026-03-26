# Start.py
"""
主程式入口點，用於啟動解題器。
"""
import tkinter as tk
from controller.controller import Controller

if __name__ == '__main__':
    # 從用戶輸入獲取寬度和高度，預設為6x5
    user_input = input()
    w, h = map(int, user_input.split()) if user_input != "" else (6, 5)
    root = tk.Tk()
    root.title('Block Fill Line Puzzle - Solver')
    Controller(root, w=w, h=h, step_delay=0)
    root.mainloop()
