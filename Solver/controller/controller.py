# controller.py
"""
控制器模組，負責處理用戶輸入、遊戲邏輯和視圖更新。
"""
import tkinter as tk
from tkinter import messagebox
from model.model import Board, TileState, Solver, Direction
from view.view import BoardView

class Controller:
    """控制器類，管理遊戲狀態和用戶交互"""
    
    def __init__(self, root: tk.Tk, w=6, h=5, step_delay=120):
        """初始化控制器
        
        Args:
            root (tk.Tk): Tkinter根視窗
            w (int): 遊戲板寬度
            h (int): 遊戲板高度
            step_delay (int): 步驟間延遲（毫秒）
        """
        self.root = root
        self.board = Board(w, h)
        self.solver = Solver(self.board)
        self.step_delay = step_delay  # 步驟間延遲（動畫）

        # 使用frame放置遊戲板網格，避免pack/grid混用
        self.board_frame = tk.Frame(root)
        self.board_frame.grid(row=0, column=0)

        self.view = BoardView(self.board_frame, self.board, self.on_tile_click)

        # 控制frame
        self.ctrl_frame = tk.Frame(root)
        self.ctrl_frame.grid(row=1, column=0, pady=6)

        self.start_btn = tk.Button(self.ctrl_frame, text='開始解', command=self.on_start)
        self.start_btn.pack(side=tk.LEFT, padx=6)
        self.reset_btn = tk.Button(self.ctrl_frame, text='重置', command=self.on_reset)
        self.reset_btn.pack(side=tk.LEFT, padx=6)
        self.pause_btn = tk.Button(self.ctrl_frame, text='暫停', command=self.on_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=6)

        self.running = False

    # ===== 視圖交互（用戶編輯地圖） =====
    def on_tile_click(self, x: int, y: int): # TODO: 邏輯改在model
        """處理格子點擊事件
        
        Args:
            x (int): x座標
            y (int): y座標
        """
        if self.running: return  # 運行時忽略點擊
        st = self.board.get_state(x, y)
        # 循環 SPACE -> WALL -> START -> SPACE
        if st == TileState.SPACE:
            self.board.set_state(x, y, TileState.WALL)
            # 如果那是起始點，在set_state中處理清除
        elif st == TileState.WALL:
            # 設置為起始點，也清除之前的起始點如果有的話
            # 確保只有一個起始點存在
            # 如果存在，將之前的起始點格子狀態恢復為SPACE
            if self.board.start is not None:
                px, py = self.board.start
                self.board.set_state(px, py, TileState.SPACE)
            self.board.set_state(x, y, TileState.START)
        elif st == TileState.START:
            self.board.set_state(x, y, TileState.SPACE)
        elif st == TileState.FILLED:
            self.board.set_state(x, y, TileState.SPACE)
        self.view.refresh_all()

    # ===== 控制 =====
    def on_start(self):
        """處理開始按鈕點擊"""
        # 確保只有一個起始點
        if not self.board.start:
            messagebox.showinfo('Info', '請選一塊作為起始點。')
            return
        # 初始化解題器
        ok = self.solver.start()
        if not ok:
            messagebox.showinfo('Info', '無法啟動解題器')
            return
        self.running = True
        self._step_loop()

    def on_pause(self):
        """處理暫停按鈕點擊"""
        self.running = False

    def on_reset(self):
        """處理重置按鈕點擊"""
        self.running = False
        w, h = self.board.w, self.board.h
        self.board = Board(w, h)
        self.solver = Solver(self.board)
        # 重新綁定視圖的board引用
        self.view.board = self.board
        self.view.refresh_all()

    # ===== 動畫循環 =====
    def _step_loop(self) -> None:
        """執行一步驟並安排下一個步驟"""
        if not self.running:
            return
        status, payload = self.solver.step()

        if status == 'move':
            frm: tuple[int, int] = payload['from']
            to: tuple[int, int] = payload['to']
            d: Direction = payload['dir']
            # 標記前一個格子的文字為方向
            self.view.set_tile_text(frm[0], frm[1], d.symbol)
            # 視覺上標記新格子為已填充
            self.view.refresh_tile(to[0], to[1])
            self.view.refresh_tile(frm[0], frm[1])
        elif status == 'backtrack':
            popped: tuple[int, int] = payload['popped']
            current: tuple[int, int] = payload['current']
            # 彈出的格子已經在model.step()中恢復為SPACE
            # 清除彈出格子的文字並更新顏色
            self.view.clear_tile_text(popped[0], popped[1])
            self.view.refresh_tile(popped[0], popped[1])
            # 確保當前格子顯示為FILLED（它已經是）
            self.view.refresh_tile(current[0], current[1])
        elif status == 'done':
            self.view.refresh_all()
            messagebox.showinfo('Solved', 'Solver filled all tiles!')
            self.running = False
            return
        elif status == 'fail':
            self.view.refresh_all()
            messagebox.showinfo('Failed', 'No solution found.')
            self.running = False
            return

        # 繼續下一個步驟
        self.root.after(self.step_delay, self._step_loop)
