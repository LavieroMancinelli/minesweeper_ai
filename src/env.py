import numpy as np
from constants import BOARD_SIZE, CELL_SIZE, MARGIN, HEADER_HEIGHT, COLOR_HIDDEN

class Env:
    def __init__(self, rows=BOARD_SIZE, cols=BOARD_SIZE, num_mines=5, seed=None):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        np.random.seed(seed)

        self.mine_grid = None
        self.revealed = None
        self.adj_counts = None
        self.flagged = None
        self.game_over = False
        self.won = False
        self.first_move = True

        self.setup()

    def setup(self):
        self.mine_grid = np.zeros((self.rows, self.cols), dtype=bool)
        self.revealed = np.zeros((self.rows, self.cols), dtype=bool)
        self.adj_counts = np.zeros((self.rows, self.cols), dtype=int)
        self.flagged = np.zeros((self.rows, self.cols), dtype=bool)
        self.game_over = False
        self.won = False
        self.first_move = True
        self.place_mines()

    def place_mines(self):
        mines_flat = np.zeros(self.rows * self.cols, dtype=bool)
        mines_i = np.random.choice(len(mines_flat), self.num_mines, replace=False)
        mines_flat[mines_i] = True
        self.mine_grid = mines_flat.reshape(self.rows, self.cols)
        self.adj_counts = self.compute_adjacency()
    
    def compute_adjacency(self):
        adj_counts = np.zeros((self.rows, self.cols), dtype=int)
        for i in range(self.rows):
            for j in range(self.cols):
                adj_mines = 0

                if i-1 >= 0 and i-1 < self.rows and j-1 >= 0 and j-1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i-1, j-1]
                if j-1 >= 0 and j-1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i, j-1]
                if i+1 >= 0 and i+1 < self.rows and j-1 >= 0 and j-1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i+1, j-1]
                if i-1 >= 0 and i-1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i-1, j]
                self.adj_counts[i,j] += self.mine_grid[i, j]
                if i+1 >= 0 and i+1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i+1, j]
                if i-1 >= 0 and i-1 < self.rows and j+1 >= 0 and j+1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i-1, j+1]
                if j+1 >= 0 and j+1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i, j+1]
                if i+1 >= 0 and i+1 < self.rows and j+1 >= 0 and j+1 < self.rows:
                    self.adj_counts[i,j] += self.mine_grid[i+1, j+1]
