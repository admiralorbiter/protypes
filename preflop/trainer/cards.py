
from __future__ import annotations
import random
from typing import List, Tuple

RANK_CHARS = "23456789TJQKA"
SUIT_CHARS = "cdhs"  # clubs, diamonds, hearts, spades
RANK_TO_VAL = {r:i+2 for i,r in enumerate(RANK_CHARS)}
VAL_TO_RANK = {v:k for k,v in RANK_TO_VAL.items()}

def card_from_str(s: str) -> Tuple[int,int]:
    s = s.strip()
    r = s[0].upper()
    u = s[1].lower()
    return (RANK_TO_VAL[r], SUIT_CHARS.index(u))

def card_to_str(c: Tuple[int,int]) -> str:
    v, u = c
    return f"{VAL_TO_RANK[v]}{SUIT_CHARS[u]}"

def full_deck() -> List[Tuple[int,int]]:
    return [(v,u) for v in range(2,15) for u in range(4)]

def remove_cards(deck: List[Tuple[int,int]], cards: List[Tuple[int,int]]) -> None:
    s = set(cards)
    deck[:] = [c for c in deck if c not in s]

def deal(deck: List[Tuple[int,int]], n: int, rng: random.Random) -> List[Tuple[int,int]]:
    # Fisher-Yates-ish: pick without replacement
    res = []
    for _ in range(n):
        i = rng.randrange(len(deck))
        res.append(deck.pop(i))
    return res
