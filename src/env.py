import numpy as np
from constants import BOARD_SIZE, CELL_SIZE, MARGIN, HEADER_HEIGHT, HIDDEN, FLAGGED, MINE_HIT

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
        self.revealed[self.rows // 2, self.cols // 2] = True
        self.compute_adjacency

    def place_mines(self):
        center = (self.rows // 2) * self.cols + (self.cols //2) # center cell never has mine
        guar_safe = [center-self.cols-1, center-self.cols, center-self.cols+1, center-1, center, center+1, center+self.cols-1, center+self.cols, center+self.cols+1]
        candidates = np.delete(np.arange(self.rows * self.cols), guar_safe)
        mines_i = np.random.choice(candidates, self.num_mines, replace=False)
        mines_flat = np.zeros(self.rows * self.cols, dtype=bool)
        mines_flat[mines_i] = True
        self.mine_grid = mines_flat.reshape(self.rows, self.cols)
        self.compute_adjacency()
    
    def compute_adjacency(self):
        for i in range(self.rows):
            for j in range(self.cols):
                neighborhood = self.mine_grid[max(0, i-1):i+2, max(0, j-1):j+2]
                self.adj_counts[i, j] = neighborhood.sum() - self.mine_grid[i, j]

    def get_obs(self):
        obs = np.full((self.rows, self.cols), HIDDEN, dtype=int)
        obs[self.revealed] = self.adj_counts[self.revealed]
        obs[self.flagged & ~self.revealed] = FLAGGED

        if self.game_over and not self.won:
            obs[self.mine_grid & self.revealed] = MINE_HIT
            
        return obs   
    
    def take_action(self, row, col, action="reveal"):
        # invalid position
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        # actions are "reveal" and "flag"
        if action == "flag":
            if not self.revealed[row, col]:
                self.flagged[row, col] = not self.flagged[row, col]
            return
        
        # reveal on already revealed
        if self.revealed[row,col]:
            return

        # reveal on mine
        if self.mine_grid[row,col]:
            self.revealed[row,col] = True
            self.game_over = True
            self.won = False
            return

        # reveal on safe
        self.revealed[row,col] = True
        self.compute_adjacency()

        if self.revealed.sum() >= self.rows * self.cols - self.num_mines:
            self.revealed[row,col] = True
            self.game_over = True
            self.won = True
            return
