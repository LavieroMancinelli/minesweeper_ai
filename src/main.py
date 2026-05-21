import pygame
import numpy as np
import constants
from env import Env
from renderer import Renderer
from constants import BOARD_SIZE
from constraint_agent import constraint_step


def run(mode="human", agent=None, fps=60):
    env = Env(rows=BOARD_SIZE, cols=BOARD_SIZE, num_mines=5)
    renderer = Renderer(env)

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
        if mode == "agent" and agent == "constraint" and not env.game_over:
            constraint_step(env)

        renderer.draw()
        renderer.clock.tick(fps)
    renderer.close()
    
if __name__ == "__main__":
    run(mode="agent", agent="constraint")
