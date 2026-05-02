# controller.py
"""
控制器模組，負責處理用戶輸入、遊戲邏輯和視圖更新。
"""
from model.model import Board, Solver, Direction, TileState
from view.view import BoardView


class Controller:
    """控制器類，管理遊戲狀態和用戶交互"""

    def __init__(self, w: int, h: int, step_delay=80):
        self.board = Board(w, h)
        self.solver = Solver(self.board)
        self.view = BoardView(self.board)

        self.step_delay = step_delay
        self.running = False

        # 👉 新增：儲存解答路徑
        self.solution_path = []
        self.step_index = 0

        self.view.set_callbacks(self.on_start, self.on_reset, self.on_pause)
        self.view.set_on_click_tile(self.on_tile_click)
        self.view.refresh_all()
        self.view.root.mainloop()

    # ===== 視圖交互 =====
    def on_tile_click(self, x: int, y: int):
        if self.running:
            return
        self.board.toggle_tile(x, y)
        self.view.refresh_all()

    # ===== 控制 =====
    def on_start(self):
        if self.running:
            return

        if not self.board.start:
            self.view.show_message('Info', '請選一塊作為起始點。')
            return

        # ⭐ 關鍵：一次算完整解
        success, path = self.solver.solve()

        if not success:
            self.view.show_message('Failed', 'No solution found.')
            return

        # 儲存解答
        self.solution_path = path
        self.step_index = 0

        # 初始化起點顯示為 FILLED
        sx, sy = self.board.start
        self.board.set_state(sx, sy, TileState.FILLED)
        self.view.refresh_tile(sx, sy)

        self.running = True
        self._step_loop()

    def on_pause(self):
        self.running = False

    def on_reset(self):
        self.running = False

        w, h = self.board.w, self.board.h
        self.board = Board(w, h)
        self.solver = Solver(self.board)

        self.view.board = self.board
        self.view.refresh_all()

    # ===== 播放解題結果 =====
    def _step_loop(self):
        if not self.running:
            return

        # ⭐ 如果播放完畢
        if self.step_index >= len(self.solution_path):
            self.view.show_message('Solved', 'Solver filled all tiles!')
            self.running = False
            return

        # ⭐ 取得一步
        (x1, y1), (x2, y2), d = self.solution_path[self.step_index]

        # ===== 更新畫面 =====

        # 1️⃣ 設定方向（前一格）
        self.view.set_tile_text(x1, y1, d.symbol)

        # 2️⃣ 填新格子
        self.board.set_state(x2, y2, TileState.FILLED)

        # 3️⃣ 刷新顯示
        self.view.refresh_tile(x1, y1)
        self.view.refresh_tile(x2, y2)

        # 下一步
        self.step_index += 1

        # 下一幀
        self.view.root.after(self.step_delay, self._step_loop)