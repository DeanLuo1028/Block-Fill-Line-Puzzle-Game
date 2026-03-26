# model.py
from enum import Enum, auto
from typing import Iterator

class TileState(Enum):
    """格子的種類"""
    SPACE = auto()
    WALL = auto()
    START = auto()
    FILLED = auto()


class Direction(Enum):
    """轉向的方向"""
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

    @property
    def dx(self):
        """獲取方向的x軸偏移量"""
        return self.value[0]
    
    @property
    def dy(self):
        """獲取方向的y軸偏移量"""
        return self.value[1]
    
    @property
    def symbol(self) -> str:
        """獲取表示方向的符號。

        返回:
            Literal['↑', '→', '↓', '←']: 方向的符號
        """
        return {
            Direction.UP: '↑',
            Direction.RIGHT: '→',
            Direction.DOWN: '↓',
            Direction.LEFT: '←'
        }[self]  # 這是一個set[dict[Direction, str]]，{}[self]表示自己的符號


class Board:
    """遊戲板類，用於管理拼圖的網格狀態"""
    
    def __init__(self, w: int, h: int):
        """初始化遊戲板
        Args:
            w (int): 寬度
            h (int): 高度
        """
        self.w = w
        self.h = h
        self.grid: list[list[TileState]] = [[TileState.SPACE for _ in range(w)] for _ in range(h)]
        self.start: tuple[int,int]|None = None

    def in_bounds(self, x:int, y:int) -> bool:
        """檢查座標是否在遊戲板範圍內
        Args:
            x (int): x座標
            y (int): y座標
            
        Returns:
            bool: 如果在範圍內返回True，否則False
        """
        return 0 <= x < self.w and 0 <= y < self.h

    def set_state(self, x:int, y:int, st: TileState) -> None:
        """設置指定座標的格子狀態
        Args:
            x (int): x座標
            y (int): y座標
            st (TileState): 要設置的狀態
        """
        self.grid[y][x] = st
        if st == TileState.START:
            self.start = (x, y)
        elif self.start == (x, y) and st != TileState.START:
            # 如果覆蓋了起始點，清除起始點引用
            self.start = None

    def get_state(self, x:int, y:int) -> TileState:
        """獲取指定座標的格子狀態
        Args:
            x (int): x座標
            y (int): y座標
        Returns:
            TileState: 格子的狀態
        """
        return self.grid[y][x]

    def all_filled(self) -> bool:
        """檢查所有格子是否都已填充
        Returns:
            bool: 如果所有格子都已填充返回True，否則False
        """
        for row in self.grid:
            for s in row:
                if s == TileState.SPACE:
                    return False
        return True


class Solver:
    """解題器類，使用DFS逐步解決拼圖，並記錄死胡同"""
    
    def __init__(self, board: Board):
        """初始化解題器
        Args:
            board (Board): 遊戲板實例
        """
        self.board = board
        self.path: list[tuple[int,int]] = []       # 訪問順序的堆疊（已填充）
        self.visited: set[tuple[int,int]] = set()  # 當前搜索中訪問的節點
        self.tried_dirs: dict[tuple[int,int], set[Direction]] = {}  # 記錄每個位置嘗試過的方向
        self.dead_ends: set[tuple[int,int]] = set()
        self.running = False
        
        # self.attempts_cnt = 0 # debug 用

    def start(self) -> bool:
        """開始解決拼圖
        Returns:
            bool: 如果解題器成功啟動返回True，否則False
        """
        if not self.board.start:
            return False
        sx, sy = self.board.start
        # 初始化狀態：將起始點標記為FILLED並推入路徑
        self.board.set_state(sx, sy, TileState.FILLED)
        self.path = [(sx, sy)]
        self.visited = { (sx, sy) }
        self.tried_dirs = {}
        self.dead_ends = set()
        self.running = True
        return True

    def step(self) -> tuple[str, dict[str, tuple[int,int] | Direction] | None]:
        """執行單一解題步驟，返回操作狀態與相關資訊。
        Returns:
            tuple [str, dict[str, tuple[int, int] | Direction] | None]:
                - 第一元素：狀態字串，可為 'move'（前進）、'backtrack'（回溯）、'done'（完成）、'fail'（失敗）
                - 第二元素（詳細資訊）：
                  * 'move': {'from': (x, y), 'to': (nx, ny), 'dir': Direction} – 前進資訊
                  * 'backtrack': {'popped': (x, y), 'current': (cx, cy)} – 回溯資訊
                  * 'done'/'fail': None
        """
        if not self.running:
            return ('fail', None)

        # 檢查是否已完全填充（勝利條件）
        if self.board.all_filled():
            self.running = False
            
            # print(f'共嘗試了 {self.attempts_cnt} 步') # debug 用
            
            return ('done', None)

        if not self.path:
            self.running = False
            return ('fail', None)

        # self.attempts_cnt += 1 # debug 用
        
        cur = self.path[-1]
        cx, cy = cur


        # 初始化當前位置的已嘗試方向集合
        if cur not in self.tried_dirs:
            self.tried_dirs[cur] = set()


        # 依序嘗試上、右、下、左四方向
        for d in Direction:

            if d in self.tried_dirs[cur]:
                continue
            self.tried_dirs[cur].add(d)  # 記錄已嘗試此方向，避免重複


            nx, ny = cx + d.dx, cy + d.dy
            if not self.board.in_bounds(nx, ny):
                continue
            st = self.board.get_state(nx, ny)
            if st == TileState.SPACE:
                # 有效移動：填充新位置，推入路徑堆疊
                self.board.set_state(nx, ny, TileState.FILLED)
                # 前一格保持FILLED狀態，由控制器更新顯示方向符號
                self.path.append((nx, ny))
                self.visited.add((nx, ny))
                return ('move', {'from': (cx, cy), 'to': (nx, ny), 'dir': d})

            # 遇牆壁、已填或起始點：無法前進，試下一方向

        # 無有效前進方向：死巷，回溯
        self.dead_ends.add(cur)
        # 彈出路徑頂端，回溯至前一位置；恢復為空白（起始點亦允許）
        popped = self.path.pop()
        # 控制器依回溯操作更新視圖（清除方向符號、顏色）
        self.board.set_state(popped[0], popped[1], TileState.SPACE)
        # 清理追蹤資料
        if popped in self.visited:
            self.visited.remove(popped)
        if popped in self.tried_dirs:
            del self.tried_dirs[popped]


        if not self.path:
            # 彈出了起始點且沒有路徑剩下 -> 失敗
            self.running = False
            return ('fail', None)

        current_after = self.path[-1]
        return ('backtrack', {'popped': popped, 'current': current_after})
