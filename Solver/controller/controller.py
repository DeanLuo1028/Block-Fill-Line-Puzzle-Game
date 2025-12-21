# controller.py
import tkinter as tk
from tkinter import messagebox
from typing import Tuple
from model.model import Board, TileState, Solver, Direction
from view.view import BoardView

class Controller:
    def __init__(self, root: tk.Tk, w=6, h=5, step_delay=120):
        self.root = root
        self.board = Board(w, h)
        self.solver = Solver(self.board)
        self.step_delay = step_delay  # ms between steps (animation)

        # use a frame for board grid so pack/grid don't mix on same parent
        self.board_frame = tk.Frame(root)
        self.board_frame.grid(row=0, column=0)

        self.view = BoardView(self.board_frame, self.board, self.on_tile_click)

        # control frame
        self.ctrl_frame = tk.Frame(root)
        self.ctrl_frame.grid(row=1, column=0, pady=6)

        self.start_btn = tk.Button(self.ctrl_frame, text='Start Solver', command=self.on_start)
        self.start_btn.pack(side=tk.LEFT, padx=6)
        self.reset_btn = tk.Button(self.ctrl_frame, text='Reset', command=self.on_reset)
        self.reset_btn.pack(side=tk.LEFT, padx=6)
        self.pause_btn = tk.Button(self.ctrl_frame, text='Pause', command=self.on_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=6)

        self.running = False

    # ===== View interactions (user editing map) =====
    def on_tile_click(self, x:int, y:int):
        if self.running: return  # ignore clicks while running
        st = self.board.get_state(x, y)
        # cycle SPACE -> WALL -> START -> SPACE
        if st == TileState.SPACE:
            self.board.set_state(x, y, TileState.WALL)
            # if that was start, clear start handled in set_state
        elif st == TileState.WALL:
            # set as start, also clear previous start if any
            # ensure only one start exists
            # clear previous start tile state back to SPACE if exists
            if self.board.start is not None:
                px, py = self.board.start
                self.board.set_state(px, py, TileState.SPACE)
            self.board.set_state(x, y, TileState.START)
        elif st == TileState.START:
            self.board.set_state(x, y, TileState.SPACE)
        elif st == TileState.FILLED:
            self.board.set_state(x, y, TileState.SPACE)
        self.view.refresh_all()

    # ===== Controls =====
    def on_start(self):
        # ensure there's exactly one start
        if not self.board.start:
            messagebox.showinfo('Info', 'Please place exactly one START tile.')
            return
        # initialize solver
        ok = self.solver.start()
        if not ok:
            messagebox.showinfo('Info', 'Cannot start solver.')
            return
        self.running = True
        self._step_loop()

    def on_pause(self):
        self.running = False

    def on_reset(self):
        self.running = False
        w, h = self.board.w, self.board.h
        self.board = Board(w, h)
        self.solver = Solver(self.board)
        # rebind the view's board reference
        self.view.board = self.board
        self.view.refresh_all()

    # ===== Animation loop =====
    def _step_loop(self) -> None:
        if not self.running:
            return
        status, payload = self.solver.step()

        if status == 'move':
            frm: Tuple[int, int] = payload['from']
            to: Tuple[int, int] = payload['to']
            d: Direction = payload['dir']
            # mark previous tile's text as direction
            self.view.set_tile_text(frm[0], frm[1], d.symbol)
            # mark new tile as filled visually
            self.view.refresh_tile(to[0], to[1])
            self.view.refresh_tile(frm[0], frm[1])
        elif status == 'backtrack':
            popped: Tuple[int, int] = payload['popped']
            current: Tuple[int, int] = payload['current']
            # popped tile was already reverted to SPACE in model.step()
            # clear popped tile text & update colors
            self.view.clear_tile_text(popped[0], popped[1])
            self.view.refresh_tile(popped[0], popped[1])
            # ensure current tile shows as FILLED (it already is)
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

        # continue next step
        self.root.after(self.step_delay, self._step_loop)
