# model.py
from enum import Enum, auto
from collections.abc import Iterator

class TileState(Enum):
    """格子的狀態種類
    在點擊時依序切換 SPACE -> WALL -> START -> SPACE
    """
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

type coordinate = tuple[int, int]

class Board:
    """遊戲板類，用於管理拼圖的網格狀態
    Attributes:
        w (int): 遊戲板的寬度
        h (int): 遊戲板的高度
        _grid (list[list[TileState]]): 二維列表表示遊戲板上每個格子的狀態
        start (coordinate | None): 起始點的座標，如果存在的話
    """
    
    def __init__(self, w: int, h: int):
        """初始化遊戲板
        Args:
            w (int): 寬度
            h (int): 高度
        """
        self.w = w
        self.h = h
        self._grid: list[list[TileState]] = [[TileState.SPACE for _ in range(w)] for _ in range(h)]
        self.start: coordinate|None = None

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
        self._grid[y][x] = st

    def get_state(self, x:int, y:int) -> TileState:
        """獲取指定座標的格子狀態
        Args:
            x (int): x座標
            y (int): y座標
        Returns:
            TileState: 格子的狀態
        """
        return self._grid[y][x]

    def toggle_tile(self, x: int, y: int) -> None:
        """切換格子的狀態，用於編輯模式
        
        Args:
            x (int): x座標
            y (int): y座標
        """
        st = self.get_state(x, y)
        if st == TileState.SPACE: # 從空白切換為牆壁
            self.set_state(x, y, TileState.WALL)
        elif st == TileState.WALL: # 從牆壁切換為起始點
            # 設置為起始點，也清除之前的起始點(如果有的話)，確保只有一個起始點存在
            if self.start is not None: # 如果已經設起始點了
                self.set_state(*self.start, TileState.SPACE)
            self.set_state(x, y, TileState.START)
            self.start = (x, y) # 更新起始點引用
        elif st == TileState.START: # 從起始點切換為空白
            # 覆蓋了起始點，清除起始點引用
            self.set_state(x, y, TileState.SPACE)
            self.start = None
        else:
            raise ValueError(f"無法切換狀態 {st}，只能切換 SPACE <-> WALL <-> START")

    def all_filled(self) -> bool:
        """檢查所有格子是否都已填充
        Returns:
            bool: 如果所有格子都已填充返回True，否則False
        """
        for row in self._grid:
            for s in row:
                if s == TileState.SPACE:
                    return False
        return True


DIRS = list(Direction)


class Solver:
    """
    專業版解題器：
    - DFS + 回溯
    - 正確狀態建模（位置 + filled）
    - dead-end 剪枝
    - degree heuristic（超關鍵優化）
    """

    def __init__(self, board: Board):
        """初始化解題器
        Args:
            board (Board): 遊戲板實例
        """
        self.running = False
        self.board = board

        self.width = board.w
        self.height = board.h

        # 所有可以填的格子（非牆）
        self.total_cells = {
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if board.get_state(x, y) != TileState.WALL
        }

        self.solution_path = []

    # =========================
    # 對外入口
    # =========================
    def solve(self) -> tuple[bool, list[tuple[coordinate, coordinate, Direction]]]:
        self.running = True
        start: coordinate|None = self.board.start
        if not start:
            return False, []

        visited_states = set()

        success = self._dfs(
            current=start,
            filled=frozenset([start]),
            path=[],
            visited_states=visited_states
        )

        return success, self.solution_path

    # =========================
    # DFS 主體
    # =========================
    def _dfs(self, 
             current: coordinate, 
             filled: frozenset[coordinate], 
             path: list[tuple[coordinate, coordinate, Direction]], 
             visited_states: set):

        # ✅ 成功條件：全部填滿
        if len(filled) == len(self.total_cells):
            self.solution_path = path.copy()
            return True

        state = (current, filled)

        # ✅ 避免重複狀態
        if state in visited_states:
            return False
        visited_states.add(state)

        # =========================
        # 🔥 剪枝 1：dead-end 檢測
        # =========================
        if self._has_dead_end(filled):
            return False

        # =========================
        # 取得可走鄰居
        # =========================
        moves = []

        for d in DIRS:
            nx, ny = current[0] + d.dx, current[1] + d.dy

            if (nx, ny) in filled:
                continue
            if not self._is_valid(nx, ny):
                continue

            moves.append((nx, ny, d))

        # =========================
        # 🔥 剪枝 2：degree heuristic（排序）
        # =========================
        moves.sort(key=lambda m: self._degree(m[0], m[1], filled))

        # =========================
        # DFS 遞迴
        # =========================
        for nx, ny, d in moves:
            new_filled = filled | {(nx, ny)}
            path.append((current, (nx, ny), d))

            if self._dfs((nx, ny), new_filled, path, visited_states):
                return True

            path.pop()

        return False

    # =========================
    # 工具函數
    # =========================

    def _is_valid(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.board.get_state(x, y) != TileState.WALL

    def _neighbors(self, x: int, y: int) -> Iterator[coordinate]:
        for d in DIRS:
            nx, ny = x + d.dx, y + d.dy
            if self._is_valid(nx, ny):
                yield nx, ny

    def _degree(self, x: int, y: int, filled: frozenset[coordinate]) -> int:
        """
        計算「未來可走數量」
        → 越小越優先（關鍵優化）
        """
        count = 0
        for nx, ny in self._neighbors(x, y):
            if (nx, ny) not in filled:
                count += 1
        return count

    def _has_dead_end(self, filled):
        dead_count = 0

        for (x, y) in self.total_cells:
            if (x, y) in filled:
                continue

            free_neighbors = 0
            for nx, ny in self._neighbors(x, y):
                if (nx, ny) not in filled:
                    free_neighbors += 1

            if free_neighbors == 0:
                dead_count += 1

                # ❗關鍵：只能允許「最多一個」死點（終點）
                if dead_count > 1:
                    return True

        return False