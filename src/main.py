import pygame
import numpy as np
import constants
from env import Env
from renderer import Renderer
from constants import BOARD_SIZE


def run(mode="human", agent=None, fps=10):
    env = Env(rows=BOARD_SIZE, cols=BOARD_SIZE, num_mines=5)
    renderer = Renderer(env)
    renderer.draw()
    
if __name__ == "__main__":
    run()
