
from __future__ import annotations
from typing import Tuple, Dict
from math import comb

# Helper combinatorics on flop (3 cards from 50 unseen)
TOTAL_FLOP = comb(50, 3)
TOTAL_RIVER = comb(50, 5)

def is_pocket_pair(c1: Tuple[int,int], c2: Tuple[int,int]) -> bool:
    return c1[0] == c2[0]

def is_suited(c1: Tuple[int,int], c2: Tuple[int,int]) -> bool:
    return c1[1] == c2[1]

def rank_gap(c1: Tuple[int,int], c2: Tuple[int,int]) -> int:
    return abs(c1[0] - c2[0])

def flop_set_prob_pocket_pair() -> Dict[str, float]:
    # Exactly set: choose 1 of the 2 remaining of that rank and 2 from the 48 others
    set_only = (comb(2,1)*comb(48,2)) / TOTAL_FLOP
    quads = (comb(2,2)*comb(48,1)) / TOTAL_FLOP
    set_or_better = set_only + quads
    return {"set_only": set_only, "quads": quads, "set_or_better": set_or_better}

def flop_pair_or_better_unpaired() -> Dict[str, float]:
    # two different ranks in hand
    # P(no pair on flop) = C(44,3)/C(50,3) since 6 cards (3 of each rank) would pair us
    no_pair = comb(44,3) / TOTAL_FLOP
    pair_or_better = 1.0 - no_pair
    # two pair: exactly one of each rank + a third of other ranks
    two_pair = (comb(3,1)*comb(3,1)*comb(44,1)) / TOTAL_FLOP
    # trips (using one hole card + two board of same rank)
    trips = (2 * comb(3,2) * comb(47,1)) / TOTAL_FLOP  # choose which rank matches (2 choices)
    # Note: pair_or_better = pair_only + two_pair + trips; but we don't compute pair_only directly here
    return {"pair_or_better": pair_or_better, "two_pair": two_pair, "trips": trips}

def flop_flush_stats_suited() -> Dict[str, float]:
    # With two suited hole cards: 11 suited remain, 39 off-suit
    flush = comb(11,3) / TOTAL_FLOP
    flush_draw = comb(11,2) * comb(39,1) / TOTAL_FLOP
    backdoor_draw = comb(11,1) * comb(39,2) / TOTAL_FLOP  # exactly one suited card
    return {"flush_flop": flush, "flush_draw": flush_draw, "backdoor_flush": backdoor_draw}

def river_flush_prob_two_suited() -> float:
    # Probability to have a flush by river with two suited cards = at least 3 of suit among 5 board cards
    total = TOTAL_RIVER
    good = 0
    # 11 suited remain, 39 off-suit
    for k in range(3, 6):
        good += comb(11, k) * comb(39, 5-k)
    return good / total

def approx_oesd_prob_on_flop(c1: Tuple[int,int], c2: Tuple[int,int]) -> float:
    # Very rough approximation: only for true connectors with gap 1 (e.g., 65, JT).
    # This is a quick analytic for education; exact depends on ranks near edges.
    v1, v2 = sorted((c1[0], c2[0]))
    if abs(v1 - v2) != 1:
        return 0.0
    # Middle cards have more possibilities; edges (A-K or 2-3) have fewer.
    # Approximate with an average 9.6% (common OESD on flop for connectors)
    # Adjust down a bit for A-K and 2-3
    if (v1, v2) in [(2,3), (13,14)]:
        return 0.085
    return 0.096
