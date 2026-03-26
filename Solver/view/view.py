# view.py
"""
視圖模組，負責顯示遊戲板和處理用戶界面。
"""
import tkinter as tk
from typing import Callable, List
from model.model import TileState, Board

FONT = ('Arial', 12)

class BoardView:
    """遊戲板視圖類，管理Tkinter按鈕網格"""
    
    def __init__(self, master, board: Board, on_click_tile: Callable[[int, int], None]):
        """
        初始化遊戲板視圖
        
        Args:
            master: 父Tkinter控件
            board (Board): 模型的Board實例
            on_click_tile (Callable[[int, int], None]): 點擊格子的回調函數(x,y)
        """
        self.master = master
        self.board = board
        self.on_click_tile = on_click_tile
        self.buttons: List[List[tk.Button]] = []
        # 建立frame以用grid放置按鈕（我們要讓控制器管理整體佈局）
        for y in range(board.h):
            row: List[tk.Button] = []
            for x in range(board.w):
                btn = tk.Button(master, width=6, height=3,
                                command=lambda x=x, y=y: on_click_tile(x, y),
                                text=f'{x},{y}', font=FONT)
                btn.grid(row=y, column=x)
                row.append(btn)
            self.buttons.append(row)

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
