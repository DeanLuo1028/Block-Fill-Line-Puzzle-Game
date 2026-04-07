# view.py
"""
視圖模組，負責顯示遊戲板和處理用戶界面。
"""
import tkinter as tk
from tkinter import messagebox
from collections.abc import Callable
from model.model import TileState, Board

FONT = ('Arial', 12)

from typing import Never
def null_command() -> Never:
    """空命令函數，作為按鈕的初始命令佔位符"""
    raise RuntimeError("不應呼叫此佔位函數")

class BoardView:
    """遊戲板視圖類，管理Tkinter按鈕網格"""
    
    def __init__(self, board: Board):
        """
        初始化遊戲板視圖
        
        Args:
            board (Board): 模型的Board實例
            on_click_tile (Callable[[int, int], None]): 點擊格子的回調函數(x,y)
        """
        self.root = tk.Tk()
        self.root.title('Block Fill Line Puzzle - Solver')
        self.board = board
        self.buttons: list[list[tk.Button]] = []
        
        # 使用frame放置遊戲板網格，避免pack/grid混用
        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=0, column=0)

        # 建立按鈕網格
        for y in range(board.h):
            row: list[tk.Button] = []
            for x in range(board.w):
                btn = tk.Button(self.board_frame, width=6, height=3,
                                command=null_command,
                                text=f'{x},{y}', font=FONT)
                btn.grid(row=y, column=x)
                row.append(btn)
            self.buttons.append(row)

        # 控制frame
        self.ctrl_frame = tk.Frame(self.root)
        self.ctrl_frame.grid(row=1, column=0, pady=6)

        self.start_btn = tk.Button(self.ctrl_frame, text='開始解', command=null_command)
        self.start_btn.pack(side=tk.LEFT, padx=6)
        self.reset_btn = tk.Button(self.ctrl_frame, text='重置', command=null_command)
        self.reset_btn.pack(side=tk.LEFT, padx=6)
        self.pause_btn = tk.Button(self.ctrl_frame, text='暫停', command=null_command)
        self.pause_btn.pack(side=tk.LEFT, padx=6)

    def set_callbacks(self, on_start: Callable[[], None], on_reset: Callable[[], None], on_pause: Callable[[], None]):
        """設置控制按鈕的回調函數"""
        self.start_btn.config(command=on_start)
        self.reset_btn.config(command=on_reset)
        self.pause_btn.config(command=on_pause)

    def set_on_click_tile(self, on_click_tile: Callable[[int, int], None]):
        """設置格子點擊回調"""
        for y in range(self.board.h):
            for x in range(self.board.w):
                self.buttons[y][x].config(command=lambda x=x, y=y: on_click_tile(x, y))

    def show_message(self, title: str, message: str):
        """顯示消息框"""
        messagebox.showinfo(title, message)

    def refresh_tile(self, x:int, y:int) -> None:
        """刷新指定格子的顯示
        
        Args:
            x (int): x座標
            y (int): y座標
        """
        st = self.board.get_state(x, y)
        btn = self.buttons[y][x]
        if st == TileState.WALL:
            btn.config(bg='black', text=f'{x},{y}')
        elif st == TileState.SPACE:
            btn.config(bg='white', text=f'{x},{y}')
        elif st == TileState.START:
            btn.config(bg='blue', text='START')
        elif st == TileState.FILLED:
            # 已填充的格子保持其文字（控制器可能設置方向）
            # 如果文字尚未設置，顯示空占位符
            cur_text = btn.cget('text')
            if cur_text in (f'{x},{y}', 'START'):
                btn.config(bg='green', text='')
            else:
                btn.config(bg='green')

    def refresh_all(self) -> None:
        """刷新所有格子的顯示"""
        for y in range(self.board.h):
            for x in range(self.board.w):
                self.refresh_tile(x, y)

    def set_tile_text(self, x:int, y:int, text:str) -> None:
        """設置指定格子的文字
        
        Args:
            x (int): x座標
            y (int): y座標
            text (str): 要設置的文字
        """
        self.buttons[y][x].config(text=text)

    def clear_tile_text(self, x:int, y:int) -> None:
        """清除指定格子的文字，恢復為座標顯示
        
        Args:
            x (int): x座標
            y (int): y座標
        """
        self.buttons[y][x].config(text=f'{x},{y}')
