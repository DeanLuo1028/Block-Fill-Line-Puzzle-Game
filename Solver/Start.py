# Start.py
"""
主程式入口點，用於啟動解題器。
"""

from controller.controller import Controller

if __name__ == '__main__':
    w, h, step_delay = 6, 5, 0
    while True:
        user_input = list(map(int, input("請輸入寬、高、每步間隔時間(毫秒)：").split()))
        match user_input:
            case []:
                pass
            case [a]:
                w = h = a
            case [a, b]:
                w, h = a, b
            case [a, b, c]:
                w, h, step_delay = a, b, c
            case _:
                print("輸入格式錯誤，請重新輸入：")
                continue
        break
    
    Controller(w, h, step_delay)