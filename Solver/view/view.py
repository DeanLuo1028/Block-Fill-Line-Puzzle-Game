# view.py
import tkinter as tk
from typing import Callable, List
from model.model import TileState, Board

FONT = ('Arial', 12)

class BoardView:
    def __init__(self, master, board: Board, on_click_tile: Callable[[int, int], None]):
        """
        master: parent tk widget
        board: model.Board
        on_click_tile: callback(x,y)
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
        st = self.board.get_state(x, y)
        btn = self.buttons[y][x]
        if st == TileState.WALL:
            btn.config(bg='black', text=f'{x},{y}')
        elif st == TileState.SPACE:
            btn.config(bg='white', text=f'{x},{y}')
        elif st == TileState.START:
            btn.config(bg='blue', text='START')
        elif st == TileState.FILLED:
            # Filled tiles keep their text (controller may set direction)
            # if text hasn't been set, show empty placeholder
            cur_text = btn.cget('text')
            if cur_text in (f'{x},{y}', 'START'):
                btn.config(bg='green', text='')
            else:
                btn.config(bg='green')

    def refresh_all(self) -> None:
        for y in range(self.board.h):
            for x in range(self.board.w):
                self.refresh_tile(x, y)

    def set_tile_text(self, x:int, y:int, text:str) -> None:
        self.buttons[y][x].config(text=text)

    def clear_tile_text(self, x:int, y:int) -> None:
        self.buttons[y][x].config(text=f'{x},{y}')
