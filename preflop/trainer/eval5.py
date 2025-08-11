
from __future__ import annotations
from typing import List, Tuple

# Hand categories
# 8 = Straight Flush, 7 = Four of a Kind, 6 = Full House, 5 = Flush, 4 = Straight,
# 3 = Three of a Kind, 2 = Two Pair, 1 = One Pair, 0 = High Card

def rank_five(cards: List[Tuple[int,int]]) -> Tuple[int, List[int]]:
    vs = sorted([v for v,_ in cards], reverse=True)
    suits = [s for _,s in cards]
    # counts by value
    counts = {}
    for v in vs:
        counts[v] = counts.get(v, 0) + 1
    by_count = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)  # sort by count then value
    is_flush = len(set(suits)) == 1

    # straight detection (with wheel)
    uniq = sorted(set(vs), reverse=True)
    # Handle wheel: A,5,4,3,2
    if 14 in uniq:
        uniq.append(1)
    straight_high = 0
    for i in range(len(uniq)-4):
        window = uniq[i:i+5]
        if window[0] - window[-1] == 4 and len(window) == 5:
            straight_high = window[0]
            break

    if is_flush and straight_high:
        return (8, [straight_high])
    # Four of a kind
    if by_count[0][1] == 4:
        four_val = by_count[0][0]
        kicker = max([v for v in vs if v != four_val])
        return (7, [four_val, kicker])
    # Full house
    if by_count[0][1] == 3 and by_count[1][1] >= 2:
        trips = by_count[0][0]
        pair = by_count[1][0]
        return (6, [trips, pair])
    if is_flush:
        return (5, sorted(vs, reverse=True))
    if straight_high:
        return (4, [straight_high])
    if by_count[0][1] == 3:
        trips = by_count[0][0]
        kickers = [v for v in vs if v != trips][:2]
        return (3, [trips] + kickers)
    if by_count[0][1] == 2 and by_count[1][1] == 2:
        p1 = by_count[0][0]
        p2 = by_count[1][0]
        kicker = max([v for v in vs if v != p1 and v != p2])
        top, bot = (p1, p2) if p1 > p2 else (p2, p1)
        return (2, [top, bot, kicker])
    if by_count[0][1] == 2:
        pair = by_count[0][0]
        kickers = [v for v in vs if v != pair][:3]
        return (1, [pair] + kickers)
    return (0, sorted(vs, reverse=True))

def compare_5(a: List[Tuple[int,int]], b: List[Tuple[int,int]]) -> int:
    ra = rank_five(a)
    rb = rank_five(b)
    if ra[0] != rb[0]:
        return 1 if ra[0] > rb[0] else -1
    # compare tiebreakers lexicographically
    for x,y in zip(ra[1], rb[1]):
        if x != y:
            return 1 if x > y else -1
    return 0
