# controller.py
"""
控制器模組，負責處理用戶輸入、遊戲邏輯和視圖更新。
"""
from model.model import Board, Solver, Direction
from view.view import BoardView

class Controller:
    """控制器類，管理遊戲狀態和用戶交互"""
    
    def __init__(self, w: int, h: int, step_delay=0):
        """初始化控制器
        
        Args:
            w (int): 遊戲板寬度
            h (int): 遊戲板高度
            step_delay (int): 步驟間延遲（毫秒）
        """
        self.board = Board(w, h)
        self.solver = Solver(self.board)
        self.view = BoardView(self.board)
        self.step_delay = step_delay # 步驟間延遲（動畫）

        self.running = False
        
        self.view.set_callbacks(self.on_start, self.on_reset, self.on_pause)
        self.view.set_on_click_tile(self.on_tile_click)
        self.view.refresh_all()
        self.view.root.mainloop()

    # ===== 視圖交互（用戶編輯地圖） =====
    def on_tile_click(self, x: int, y: int):
        """處理格子點擊事件
        
        Args:
            x (int): x座標
            y (int): y座標
        """
        if self.running: return  # 運行時忽略點擊
        self.board.toggle_tile(x, y)
        self.view.refresh_all()

    # ===== 控制 =====
    def on_start(self):
        """處理開始按鈕點擊"""
        # 確保只有一個起始點
        if not self.board.start:
            self.view.show_message('Info', '請選一塊作為起始點。')
            return
        # 讓解題器準備開始
        self.solver.start()
        
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
        
        # assert 只是為了消警告
        if status == 'move':
            assert isinstance(payload, dict)
            frm = payload['from']; assert isinstance(frm, tuple) and len(frm) == 2
            to = payload['to']; assert isinstance(to, tuple) and len(to) == 2
            d = payload['dir']; assert isinstance(d, Direction)
            # 標記前一個格子的文字為方向
            self.view.set_tile_text(frm[0], frm[1], d.symbol)
            # 視覺上標記新格子為已填充
            self.view.refresh_tile(to[0], to[1])
            self.view.refresh_tile(frm[0], frm[1])
        elif status == 'backtrack':
            assert isinstance(payload, dict)
            popped = payload['popped']; assert isinstance(popped, tuple) and len(popped) == 2
            current = payload['current']; assert isinstance(current, tuple) and len(current) == 2
            # 彈出的格子已經在model.step()中恢復為SPACE
            # 清除彈出格子的文字並更新顏色
            self.view.clear_tile_text(popped[0], popped[1])
            self.view.refresh_tile(popped[0], popped[1])
            # 確保當前格子顯示為FILLED（它已經是）
            self.view.refresh_tile(current[0], current[1])
        elif status == 'done':
            self.view.refresh_all()
            self.view.show_message('Solved', 'Solver filled all tiles!')
            self.running = False
            return
        elif status == 'fail':
            self.view.refresh_all()
            self.view.show_message('Failed', 'No solution found.')
            self.running = False
            return

        # 繼續下一個步驟
        self.view.root.after(self.step_delay, self._step_loop)
