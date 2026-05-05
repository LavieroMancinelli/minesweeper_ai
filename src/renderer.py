import pygame
from env import Env
from constants import BOARD_SIZE, CELL_SIZE, MARGIN, HEADER_HEIGHT, COLOR_HIDDEN, COLOR_REVEALED, COLOR_FLAG, COLOR_MINE, COLOR_NUMBER, HIDDEN, FLAGGED, MINE_HIT

class Renderer:
    def __init__(self, env: Env):
        pygame.init()
        self.env = env
        self.cell_size = CELL_SIZE
        self.margin = MARGIN
        self.header_h = HEADER_HEIGHT
        self.width = (self.cell_size + self.margin) * env.cols + self.margin
        self.height = (self.cell_size + self.margin) * env.rows + self.margin + self.header_h
        self.font_num = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_ui = pygame.font.SysFont("monospace", 18)


        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()

    def cell_rect(self, row, col) -> pygame.Rect:
        x = self.margin + col * (self.cell_size + self.margin)
        y = self.header_h + self.margin + row * (self.cell_size + self.margin)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def cell_at_pos(self, px, py):
        col = (px - self.margin) // (self.cell_size + self.margin)
        row = (py - self.header_h - self.margin) // (self.cell_size + self.margin)
        if row >= 0 and row < self.env.rows and col >= 0 and col < self.env.cols:
            rect = self.cell_rect(row, col)
            if rect.collidepoint(px, py):
                return row, col
        return None

    def draw(self):
        env = self.env
        obs = env.get_obs()

        for row in range(env.rows):
            for col in range(env.cols):
                rect = self.cell_rect(row,col)
                val = obs[row,col]

                if val == HIDDEN:
                    pygame.draw.rect(self.screen, COLOR_HIDDEN, rect)
                    pygame.draw.line(self.screen, (210,210,210), rect.topleft, rect.topright)
                    pygame.draw.line(self.screen, (210,210,210), rect.topleft, rect.bottomleft)
                    pygame.draw.line(self.screen, (130,130,130), rect.bottomleft, rect.bottomright)
                    pygame.draw.line(self.screen, (130,130,130), rect.topright, rect.bottomright)
                elif val == FLAGGED:
                    pygame.draw.rect(self.screen, COLOR_HIDDEN, rect)
                    flag = self.font_num.render("F", True, COLOR_FLAG, None)
                    self.screen.blit(flag, flag.get_rect(center=rect.center))
                elif val == MINE_HIT:
                    pygame.draw.rect(self.screen, COLOR_HIDDEN, rect)
                    flag = self.font_num.render("M", True, COLOR_FLAG, None)
                    self.screen.blit(flag, flag.get_rect(center=rect.center))
                else: # revealed safe
                    pygame.draw.rect(self.screen, COLOR_REVEALED, rect)
                    num = self.font_num.render(str(val), True, COLOR_NUMBER, None)
                    self.screen.blit(num, num.get_rect(center=rect.center))

        pygame.display.flip()

    def close(self):
        pygame.quit()
