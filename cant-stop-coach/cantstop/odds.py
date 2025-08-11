from __future__ import annotations
from functools import lru_cache
from typing import Dict, List, Tuple
from .constants import COLUMN_HEIGHTS, COLUMNS
from .state import GameState
from .engine import legal_pairings, pairings_from_roll, turn_key_for_odds, apply_pairing

Roll = Tuple[int,int,int,int]
ALL_ROLLS: List[Roll] = [(a,b,c,d) for a in range(1,7) for b in range(1,7) for c in range(1,7) for d in range(1,7)]

@lru_cache(maxsize=100000)
def _bust_prob_cached(key: tuple) -> float:
    # Reconstruct a minimal pseudo-state from key isn't practical; we instead rely on the caller
    # to pass through a fresh state each time and only use key for caching outcome.
    # This function is a placeholder to host the cache; actual computation is injected.
    return -1.0  # should never be returned

def bust_prob(state: GameState) -> float:
    key = turn_key_for_odds(state)
    # We can't store state in cache directly; use a local closure over current state.
    # Implement manual caching by checking lru_cache dict via wrapped function trick.
    try:
        value = _bust_prob_cached.cache_get(key)  # type: ignore[attr-defined]
        if value is not None:
            return value
    except Exception:
        pass

    busts = 0
    for roll in ALL_ROLLS:
        if not legal_pairings(state, roll):
            busts += 1
    p = busts / 1296.0
    # Save to cache
    try:
        _bust_prob_cached.cache_set(key, p)  # type: ignore[attr-defined]
    except Exception:
        pass
    return p

# Monkey-patch cache helpers since functools doesn't expose get/set
def _cache_get(self, key):
    try:
        return self.cache[key]
    except Exception:
        return None

def _cache_set(self, key, value):
    try:
        self.cache[key] = value
    except Exception:
        pass

# Attach helpers
_bust_prob_cached.cache_get = _cache_get.__get__(_bust_prob_cached)  # type: ignore[attr-defined]
_bust_prob_cached.cache_set = _cache_set.__get__(_bust_prob_cached)  # type: ignore[attr-defined]

def adv_prob_by_column(state: GameState) -> Dict[int, float]:
    cur = state.current
    # Snapshot before
    base_positions = {c: state.players[cur].permanent_pos[c] for c in COLUMNS}
    active_before = dict(state.turn.active_runners)

    res = {c: 0 for c in COLUMNS}
    for roll in ALL_ROLLS:
        legals = legal_pairings(state, roll)
        cols_that_can_advance = set()
        for p in legals:
            # Apply on a temp state copy
            from copy import deepcopy
            s2 = state.copy()
            s2.turn.last_roll = roll
            # track before
            before = dict(s2.turn.active_runners)
            apply_pairing(s2, p)
            after = s2.turn.active_runners
            for c in set(list(before.keys()) + list(after.keys())):
                prev = before.get(c, base_positions[c])
                now = after.get(c, before.get(c, base_positions[c]))
                if now > prev:
                    cols_that_can_advance.add(c)
        for c in cols_that_can_advance:
            res[c] += 1
    # Normalize
    for c in res:
        res[c] = res[c] / 1296.0
    return res
