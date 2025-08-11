
from __future__ import annotations
from typing import List, Tuple
import random
from .cards import full_deck, remove_cards, deal
from .eval7 import rank_seven

def estimate_equity(hole: List[Tuple[int,int]], n_opponents: int = 1, iters: int = 2000, seed: int = 0) -> float:
    rng = random.Random(seed)
    wins = 0.0
    total = 0
    for i in range(iters):
        deck = full_deck()
        remove_cards(deck, hole)
        # deal opponents
        villains = []
        for _ in range(n_opponents):
            villains.append(deal(deck, 2, rng))
        # deal board
        board = deal(deck, 5, rng)
        hero_rank = rank_seven(hole + board)
        # compare
        best = 1
        winners = 1
        for v in villains:
            r = rank_seven(v + board)
            if r > hero_rank:
                best = -1
                winners = 0
                break
            elif r == hero_rank:
                winners += 1
        if best == 1:
            wins += 1.0 / winners
        total += 1
    return wins / total if total else 0.0
