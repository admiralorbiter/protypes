
from __future__ import annotations
from typing import List, Tuple
from itertools import combinations
from .eval5 import rank_five

def rank_seven(cards: List[Tuple[int,int]]) -> Tuple[int, List[int]]:
    # Return best 5-card rank tuple among 7 cards
    best = None
    for combo in combinations(cards, 5):
        r = rank_five(list(combo))
        if best is None or r > best:
            best = r
    return best
