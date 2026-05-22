"""
Headless evaluation of the constraint solver.

Runs the solver on many randomly generated boards across difficulty settings
and reports win rate and average moves. No pygame / display required.

Usage:
    python evaluate.py [n_games]
"""

import sys
import numpy as np
from env import Env
from solver import ConstraintSolver

# Difficulty presets. The proposal targets 9x9, 16x16, 30x16.
# The current Env is square (uses rows/cols) and guarantees a 3x3 safe
# center, so these run as-is.
DIFFICULTIES = {
    "easy":         dict(rows=9,  cols=9,  num_mines=10),
    "intermediate": dict(rows=16, cols=16, num_mines=40),
    "expert":       dict(rows=16, cols=30, num_mines=99),
}

MAX_STEPS = 10000  # safety cap so a stuck game can't loop forever


def play_one(cfg, seed):
    env = Env(rows=cfg["rows"], cols=cfg["cols"],
              num_mines=cfg["num_mines"], seed=seed)
    solver = ConstraintSolver(env)
    steps = 0
    while not env.game_over and steps < MAX_STEPS:
        progressed = solver.step()
        steps += 1
        if not progressed and not env.game_over:
            break
    return env.won, steps


def evaluate(n_games=200):
    print(f"Evaluating constraint solver over {n_games} games per difficulty\n")
    print(f"{'difficulty':<14}{'win rate':>10}{'wins':>8}{'avg moves':>12}")
    print("-" * 44)
    results = {}
    for name, cfg in DIFFICULTIES.items():
        wins = 0
        total_moves = 0
        for g in range(n_games):
            won, steps = play_one(cfg, seed=g)
            wins += int(won)
            total_moves += steps
        rate = wins / n_games
        avg_moves = total_moves / n_games
        results[name] = dict(win_rate=rate, wins=wins, games=n_games,
                             avg_moves=avg_moves)
        print(f"{name:<14}{rate*100:>9.1f}%{wins:>8}{avg_moves:>12.1f}")
    print()
    return results


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    evaluate(n)
