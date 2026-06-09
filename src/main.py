import pygame
import numpy as np
import constants
from env import Env
from renderer import Renderer
from constants import BOARD_SIZE
from solver import solver_step
from baseline_solver import BaselineSolver
import sys


def run(mode="human", agent=None, fps=60):
    env = Env(rows=BOARD_SIZE, cols=BOARD_SIZE, num_mines=40)
    renderer = Renderer(env)
    baseline = BaselineSolver() if agent == "baseline" else None

    running = True
    while (running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if mode == "human" and not env.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cell = renderer.cell_at_pos(*event.pos)
                    if cell is not None:
                        row,col = cell
                        action = "flag" if event.button == 3 else "reveal"
                        env.take_action(row,col,action)
        if mode == "agent" and agent == "solver" and not env.game_over:
            solver_step(env)
        if mode == "agent" and agent == "baseline" and not env.game_over and baseline:
            baseline.runStep(env)

        renderer.draw()
        renderer.clock.tick(fps)
    renderer.close()
    
if __name__ == "__main__":
    solver = sys.argv[1] if len(sys.argv) > 1 else None
    if solver == "human":
        run(mode="human")
    elif solver == "solver":
        run(mode="agent", agent="solver")
    elif solver == "baseline":
        run(mode="agent", agent="baseline")
    else:
        run(mode="human")