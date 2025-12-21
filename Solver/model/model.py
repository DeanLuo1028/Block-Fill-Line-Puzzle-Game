# model.py
from enum import Enum, auto
from typing import List, Tuple, Dict, Set, Optional, Iterator

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
    def dx(self): return self.value[0]
    @property
    def dy(self): return self.value[1]
    @property
    def symbol(self):
        """Get the symbol representing the direction.

        Returns:
            Literal['↑', '→', '↓', '←']: the symbol for the direction
        """
        return {
            Direction.UP: '↑',
            Direction.RIGHT: '→',
            Direction.DOWN: '↓',
            Direction.LEFT: '←'
        }[self] # 這是一個Set[Dict[Direction, str]]，返回能表示自己的符號

class Board:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.grid: List[List[TileState]] = [[TileState.SPACE for _ in range(w)] for _ in range(h)]
        self.start: Optional[Tuple[int,int]] = None

    def in_bounds(self, x:int, y:int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def set_state(self, x:int, y:int, st: TileState) -> None:
        self.grid[y][x] = st
        if st == TileState.START:
            self.start = (x, y)
        elif self.start == (x, y) and st != TileState.START:
            # clear start reference if overwritten
            self.start = None

    def get_state(self, x:int, y:int) -> TileState:
        return self.grid[y][x]

    def all_filled(self) -> bool:
        for row in self.grid:
            for s in row:
                if s == TileState.SPACE:
                    return False
        return True

    def neighbors(self, x:int, y:int) -> Iterator[tuple[int, int, Direction]]:
        for d in Direction:
            nx, ny = x + d.dx, y + d.dy
            if self.in_bounds(nx, ny):
                yield (nx, ny, d)

# Solver: DFS step-by-step with dead-end memory
class Solver:
    def __init__(self, board: Board):
        self.board = board
        self.path: List[Tuple[int,int]] = []       # stack of visited order (filled)
        self.visited: Set[Tuple[int,int]] = set()  # visited nodes in current search
        self.tried_dirs: Dict[Tuple[int,int], Set[Direction]] = {}  # which dirs tried for a pos
        self.dead_ends: Set[Tuple[int,int]] = set()
        self.running = False
        
        self.attempts_cnt = 0 # will be deleted

    def start(self) -> bool:
        """start to solve the puzzle

        Returns:
            bool: True if solver started successfully, False otherwise
        """
        if not self.board.start:
            return False
        sx, sy = self.board.start
        # initialize state: mark start as FILLED and push to path
        self.board.set_state(sx, sy, TileState.FILLED)
        self.path = [(sx, sy)]
        self.visited = { (sx, sy) }
        self.tried_dirs = {}
        self.dead_ends = set()
        self.running = True
        return True

    def step(self) -> Tuple[str, Optional[Dict[str, Tuple[int,int] | Direction]]]:
        """Execute one solver step.

        Returns:
            Tuple[str, Optional[Dict[str, Tuple[int,int] | Direction]]]: tuple (status, payload)
            status in {'move', 'backtrack', 'done', 'fail'}
            payload for 'move': {'from':(x,y),'to':(nx,ny),'dir':Direction}
            payload for 'backtrack': {'popped':(x,y),'current':(cx,cy)}
            payload for 'done' / 'fail': None
        """
        if not self.running:
            return ('fail', None)

        # Win check
        if self.board.all_filled():
            self.running = False
            
            print(f'共嘗試了 {self.attempts_cnt} 步') # will be deleted
            
            return ('done', None)

        if not self.path:
            self.running = False
            return ('fail', None)

        self.attempts_cnt += 1 # will be deleted
        
        cur = self.path[-1]
        cx, cy = cur

        # ensure tried_dirs entry
        if cur not in self.tried_dirs:
            self.tried_dirs[cur] = set()

        # try directions in order UP, RIGHT, DOWN, LEFT
        for d in Direction:
            if d in self.tried_dirs[cur]:
                continue
            self.tried_dirs[cur].add(d)  # mark attempted for current

            nx, ny = cx + d.dx, cy + d.dy
            if not self.board.in_bounds(nx, ny):
                continue
            st = self.board.get_state(nx, ny)
            if st == TileState.SPACE:
                # valid move: fill neighbor, mark previous as FILLED (already FILLED if start)
                self.board.set_state(nx, ny, TileState.FILLED)
                # previous (cur) remains FILLED; caller (controller/view) will set its text to direction
                self.path.append((nx, ny))
                self.visited.add((nx, ny))
                return ('move', {'from': (cx, cy), 'to': (nx, ny), 'dir': d})

            # if neighbor is WALL / FILLED / START -> cannot move there
            # continue to next direction

        # no direction worked from current -> this is dead end
        self.dead_ends.add(cur)
        # pop current and revert its state to SPACE (unless it's the start and cannot be removed)
        popped = self.path.pop()
        # revert popped tile to SPACE if it's not the original start
        # but we must allow reverting the start too if no solution (as per backtracking)
        # Note: controller will update view text/colors based on returned action.
        self.board.set_state(popped[0], popped[1], TileState.SPACE)
        # remove from visited and tried_dirs
        if popped in self.visited:
            self.visited.remove(popped)
        if popped in self.tried_dirs:
            del self.tried_dirs[popped]

        if not self.path:
            # popped the start and no path left -> fail
            self.running = False
            return ('fail', None)

        current_after = self.path[-1]
        return ('backtrack', {'popped': popped, 'current': current_after})
