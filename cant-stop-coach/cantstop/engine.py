from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import random

from .constants import COLUMN_HEIGHTS, COLUMNS
from .state import GameState

Roll = Tuple[int, int, int, int]
Pairing = Tuple[int, int]

def roll_dice(rng: random.Random) -> Roll:
    return (rng.randint(1,6), rng.randint(1,6), rng.randint(1,6), rng.randint(1,6))

def pairings_from_roll(roll: Roll) -> List[Pairing]:
    d1,d2,d3,d4 = roll
    return [
        (d1+d2, d3+d4),
        (d1+d3, d2+d4),
        (d1+d4, d2+d3)
    ]

def is_column_open(state: GameState, s: int) -> bool:
    return state.claimed_by[s] is None

def can_play_sum(state: GameState, s: int) -> bool:
    if not is_column_open(state, s):
        return False
    # If runner already active here and not at top, you can always move it
    if s in state.turn.active_runners:
        at = state.turn.active_runners[s]
        return at < COLUMN_HEIGHTS[s]
    # Else need a free runner to start
    return state.turn.free_runners > 0

def legal_pairings(state: GameState, roll: Roll) -> List[Pairing]:
    pairs = pairings_from_roll(roll)
    legals = []
    for s1, s2 in pairs:
        p1 = can_play_sum(state, s1)
        # Temporarily simulate first to check if second becomes playable (e.g., double)
        # We'll copy minimal parts
        temp_active = dict(state.turn.active_runners)
        temp_free = state.turn.free_runners
        temp_top1 = COLUMN_HEIGHTS[s1]
        if p1:
            if s1 in temp_active:
                if temp_active[s1] < temp_top1:
                    temp_active[s1] = min(temp_active[s1] + 1, temp_top1)
            else:
                # start runner
                temp_active[s1] = min(state.players[state.current].permanent_pos[s1] + 1, temp_top1)
                temp_free -= 1

        # Now check s2 with updated temp state
        if state.claimed_by[s2] is not None:
            p2 = False
        else:
            if s2 in temp_active:
                p2 = temp_active[s2] < COLUMN_HEIGHTS[s2]
            else:
                p2 = temp_free > 0

        if p1 or p2:
            legals.append((s1, s2))
    # Deduplicate identical pairings if repeated by equal sums
    seen = set()
    uniq = []
    for p in legals:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq

def apply_sum_once(state: GameState, s: int) -> bool:
    """Apply one move for sum s if playable. Returns True if a move was made."""
    if not is_column_open(state, s):
        return False
    top = COLUMN_HEIGHTS[s]
    if s in state.turn.active_runners:
        at = state.turn.active_runners[s]
        if at >= top:
            return False
        state.turn.active_runners[s] = min(at + 1, top)
        return True
    else:
        # Need free runner
        if state.turn.free_runners <= 0:
            return False
        base = state.players[state.current].permanent_pos[s]
        state.turn.active_runners[s] = min(base + 1, top)
        return True

def apply_pairing(state: GameState, pairing: Pairing) -> Dict:
    """Mutates state by applying as many legal moves from the chosen pairing as possible.
    Returns a dict with deltas for UI/analytics."""
    s1, s2 = pairing
    # Track before
    before = dict(state.turn.active_runners)
    moved1 = apply_sum_once(state, s1)
    moved2 = apply_sum_once(state, s2)
    after = state.turn.active_runners
    deltas = {}
    for c in set(list(before.keys()) + list(after.keys())):
        prev = before.get(c, state.players[state.current].permanent_pos[c])
        now = after.get(c, before.get(c, state.players[state.current].permanent_pos[c]))
        if now != prev:
            deltas[c] = now - prev
    return {
        "moved1": moved1,
        "moved2": moved2,
        "deltas": deltas
    }

def stop_and_bank(state: GameState) -> None:
    cur = state.current
    for c, pos in state.turn.active_runners.items():
        # Bank progress
        if pos > state.players[cur].permanent_pos[c]:
            state.players[cur].permanent_pos[c] = pos
        # Claim if at top
        if pos >= COLUMN_HEIGHTS[c]:
            state.claimed_by[c] = cur
            state.players[cur].claimed.add(c)
    # Clear turn
    state.turn.active_runners.clear()
    state.turn.last_roll = None
    # Check win
    if len(state.players[cur].claimed) >= 3:
        state.winner = cur
    else:
        # Next player
        state.current = (state.current + 1) % state.num_players

def compute_turn_gain(state: GameState) -> int:
    cur = state.current
    total = 0
    for c, at in state.turn.active_runners.items():
        base = state.players[cur].permanent_pos[c]
        total += max(0, at - base)
    return total

def finished_columns_this_turn(state: GameState) -> List[int]:
    res = []
    for c, at in state.turn.active_runners.items():
        if at >= COLUMN_HEIGHTS[c]:
            res.append(c)
    return res

def turn_key_for_odds(state: GameState) -> tuple:
    open_cols = tuple(sorted([c for c in COLUMNS if state.claimed_by[c] is None]))
    active = tuple(sorted([(c, state.turn.active_runners[c] >= COLUMN_HEIGHTS[c]) for c in state.turn.active_runners.keys()]))
    free = state.turn.free_runners
    return (open_cols, active, free)
