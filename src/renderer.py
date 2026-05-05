import pygame
from env import Env
from constants import BOARD_SIZE, CELL_SIZE, MARGIN, HEADER_HEIGHT, COLOR_HIDDEN

class Renderer:
    def __init__(self, env: Env):
        self.env = env
        self.cell_size = CELL_SIZE
        self.margin = MARGIN
        self.header_h = HEADER_HEIGHT
        self.width = (self.cell_size + self.margin) * env.cols + self.margin
        self.height = (self.cell_size + self.margin) * env.rows + self.margin

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()

    def cell_rect(self, row, col) -> pygame.Rect:
        x = self.margin + col * (self.cell_size + self.margin)
        y = self.header_h + self.margin + row * (self.cell_size + self.margin)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def cell_at_pos(self, px, py):
        col = (px - self.margin) // self.cell_size + self.margin
        row = (py - self.header_h - self.margin) // self.cell_size + self.margin
        if row > 0 and row < self.env.rows and col > 0 and col < self.env.cols:
            rect = self.cell_rect(row, col)
            if rect.collidepoint(px, py):
                return row, col
        return None

    def draw(self):
        env = self.env

        for r in range(env.rows):
            for c in range(env.cols):
                rect = self.cell_rect(r,c)
                pygame.draw.rect(self.screen, COLOR_HIDDEN, rect)
                pygame.draw.line(self.screen, (210,210,210), rect.topleft, rect.topright)
                pygame.draw.line(self.screen, (210,210,210), rect.topleft, rect.bottomleft)
                pygame.draw.line(self.screen, (130,130,130), rect.bottomleft, rect.bottomright)
                pygame.draw.line(self.screen, (130,130,130), rect.topright, rect.bottomright)

        pygame.display.flip()

    def close(self):
        pygame.quit()
