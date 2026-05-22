"""
Constraint-based Minesweeper solver.

Reads board state through Env.get_obs() and acts through Env.take_action(),
so it plugs into the existing environment without modifying it.

Strategy (in priority order, matching the project proposal):
  1. Rule-based deductions on single clues:
       - if (clue - adjacent flags) == number of hidden neighbors  -> all hidden neighbors are mines
       - if adjacent flags == clue                                 -> all hidden neighbors are safe
  2. Constraint propagation via the subset rule: if the cells of one clue
     are a subset of another, the difference of their mine-counts constrains
     the difference of their cell sets.
  3. Global mine-count constraint for the endgame (all remaining hidden cells
     are mines / all are safe once the count forces it).
  4. Probability-based guessing when no certain move exists: estimate each
     frontier cell's mine probability from local constraints, fall back to the
     global density for interior cells, and reveal the lowest-probability cell.
"""

import numpy as np
from constants import HIDDEN, FLAGGED, MINE_HIT


def neighbors(r, c, rows, cols):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc


class ConstraintSolver:
    def __init__(self, env):
        self.env = env
        # Internal mine knowledge: which cells the solver has *deduced* are mines.
        # We use the env's flag mechanism to mark them so the renderer shows it too.
        self.last_reason = None  # for visualization / logging

    # ---- board views -------------------------------------------------------
    def _obs(self):
        return self.env.get_obs()

    def _hidden_cells(self, obs):
        cells = []
        for r in range(self.env.rows):
            for c in range(self.env.cols):
                if obs[r, c] == HIDDEN:
                    cells.append((r, c))
        return cells

    def _flag_count(self):
        return int(self.env.flagged.sum())

    # ---- constraint extraction --------------------------------------------
    def _constraints(self, obs):
        """
        Each numbered, revealed cell becomes a constraint:
            (set_of_hidden_neighbor_cells, mines_remaining_among_them)
        where mines_remaining = clue - (already-flagged neighbors).
        Only constraints with at least one hidden (unflagged) neighbor are kept.
        """
        rows, cols = self.env.rows, self.env.cols
        constraints = []
        for r in range(rows):
            for c in range(cols):
                v = obs[r, c]
                if v < 0:  # HIDDEN, FLAGGED, or MINE_HIT — not a clue
                    continue
                hidden_neighbors = []
                flagged_neighbors = 0
                for nr, nc in neighbors(r, c, rows, cols):
                    nv = obs[nr, nc]
                    if nv == HIDDEN:
                        hidden_neighbors.append((nr, nc))
                    elif nv == FLAGGED:
                        flagged_neighbors += 1
                if hidden_neighbors:
                    remaining = v - flagged_neighbors
                    constraints.append((frozenset(hidden_neighbors), remaining))
        return constraints

    # ---- deduction layers --------------------------------------------------
    def _basic_deductions(self, constraints):
        """Returns (safe_cells, mine_cells) deducible from single constraints."""
        safe, mines = set(), set()
        for cells, k in constraints:
            if k == 0:
                safe |= set(cells)            # no mines left here -> all safe
            elif k == len(cells):
                mines |= set(cells)           # every cell must be a mine
        return safe, mines

    def _subset_deductions(self, constraints):
        """
        Subset / constraint-propagation rule.
        If (A, a) and (B, b) are constraints with A subset of B, then the
        cells in B minus A contain exactly (b - a) mines. If that difference is 0,
        those cells are all safe; if it equals their count, they're all mines.
        """
        safe, mines = set(), set()
        for A, a in constraints:
            for B, b in constraints:
                if A is B or not A < B:       # strict subset only
                    continue
                diff = B - A
                d = b - a
                if d == 0:
                    safe |= set(diff)
                elif d == len(diff):
                    mines |= set(diff)
        return safe, mines

    def _global_deductions(self, obs):
        """
        Global mine-count constraint for the endgame.
        If the number of mines not yet flagged equals the number of hidden
        unflagged cells, they are all mines. If zero mines remain, all hidden
        cells are safe.
        """
        safe, mines = set(), set()
        hidden = self._hidden_cells(obs)
        mines_left = self.env.num_mines - self._flag_count()
        if not hidden:
            return safe, mines
        if mines_left == 0:
            safe |= set(hidden)
        elif mines_left == len(hidden):
            mines |= set(hidden)
        return safe, mines

    # ---- probability fallback ---------------------------------------------
    def _probabilities(self, obs, constraints):
        """
        Estimate each hidden cell's probability of being a mine.
        Frontier cells (those appearing in a constraint) get the average of
        k/len(cells) over the constraints they belong to. Interior hidden cells
        (in no constraint) get the global density of remaining mines over
        remaining interior cells. Returns dict cell -> probability.
        """
        hidden = self._hidden_cells(obs)
        prob = {}
        contrib = {cell: [] for cell in hidden}
        frontier = set()
        for cells, k in constraints:
            if not cells:
                continue
            p = k / len(cells)
            for cell in cells:
                if cell in contrib:
                    contrib[cell].append(p)
                    frontier.add(cell)

        mines_left = self.env.num_mines - self._flag_count()
        # expected mines accounted for by the frontier (rough estimate)
        frontier_expected = sum(np.mean(contrib[c]) for c in frontier) if frontier else 0.0
        interior = [c for c in hidden if c not in frontier]
        if interior:
            interior_mines = max(mines_left - frontier_expected, 0.0)
            interior_p = min(max(interior_mines / len(interior), 0.0), 1.0)
        else:
            interior_p = 0.0

        for cell in hidden:
            if contrib[cell]:
                prob[cell] = float(np.mean(contrib[cell]))
            else:
                prob[cell] = interior_p
        return prob

    # ---- one step ----------------------------------------------------------
    def step(self):
        """
        Perform a single deduction-and-act step. Returns True if the game is
        still in progress (an action was taken or could be), False if over.
        """
        if self.env.game_over:
            return False

        obs = self._obs()
        constraints = self._constraints(obs)

        # Layer 1: basic single-clue deductions
        safe, mines = self._basic_deductions(constraints)

        # Layer 2: subset / constraint propagation
        if not safe and not mines:
            safe, mines = self._subset_deductions(constraints)

        # Layer 3: global mine-count constraint
        if not safe and not mines:
            safe, mines = self._global_deductions(obs)

        # Filter out anything already resolved
        safe = {(r, c) for (r, c) in safe if obs[r, c] == HIDDEN}
        mines = {(r, c) for (r, c) in mines if obs[r, c] == HIDDEN}

        # Flag deduced mines (safe to do; helps later constraints + the renderer)
        if mines:
            for (r, c) in mines:
                if not self.env.flagged[r, c]:
                    self.env.take_action(r, c, "flag")
            self.last_reason = "deduced mine(s) -> flagged"
            return not self.env.game_over

        # Reveal a deduced safe cell
        if safe:
            r, c = next(iter(safe))
            self.last_reason = "deduced safe -> revealed"
            self.env.take_action(r, c, "reveal")
            return not self.env.game_over

        # Layer 4: no certainty -> probability guess
        prob = self._probabilities(obs, constraints)
        if not prob:
            return False
        (r, c), p = min(prob.items(), key=lambda kv: kv[1])
        self.last_reason = f"guess p(mine)={p:.2f} -> revealed"
        self.env.take_action(r, c, "reveal")
        return not self.env.game_over


def solver_step(env):
    """Module-level convenience entry point, mirroring constraint_step(env)."""
    if not hasattr(solver_step, "_cache"):
        solver_step._cache = {}
    s = solver_step._cache.get(id(env))
    if s is None:
        s = ConstraintSolver(env)
        solver_step._cache[id(env)] = s
    return s.step()
