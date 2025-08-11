from __future__ import annotations
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import math, random
from .model import World, Student, College, Scenario

def norm_gpa(g: float) -> float:
    return max(0.0, min(1.0, g/4.0))

def norm_test(t: int) -> float:
    # 400..1600 -> 0..1
    return max(0.0, min(1.0, (t - 400) / 1200.0))

def score_student_for_college(s: Student, c: College, world: World, legacy_on_private: bool, rng: random.Random) -> float:
    # Apply test policy logic
    use_test = (c.test_policy == "required" and s.test_score is not None) or (c.test_policy == "optional" and s.test_score is not None)
    weights_sum = c.w_gpa + c.w_rigor + c.w_context + (c.w_test if use_test else 0.0)
    # Renormalize if test not used
    w_gpa = c.w_gpa / weights_sum
    w_rigor = c.w_rigor / weights_sum
    w_context = c.w_context / weights_sum
    w_test = (c.w_test / weights_sum) if use_test else 0.0
    base = w_gpa*norm_gpa(s.gpa) + w_rigor*s.rigor + w_context*(0.5 + 0.5*s.hs_context) + (w_test*norm_test(s.test_score) if use_test else 0.0)
    # Legacy bonus if applicable
    legacy_bonus = 0.0
    if (legacy_on_private and c.legacy_enabled) and (world.legacy_map.get(c.cid) and s.sid in world.legacy_map[c.cid]):
        legacy_bonus = c.legacy_weight
    # Small jitter for tie-breaking (deterministic via rng)
    return base + legacy_bonus + 1e-6 * rng.random()

def eligible_for_college(s: Student, c: College) -> bool:
    if c.test_policy == "required" and s.test_score is None:
        return False
    return True

def college_choice_with_reserves(c: College, proposers: Set[int], world: World, scenario: Scenario, rng: random.Random) -> Set[int]:
    """Return the set of chosen students among proposers, using reserves and priority.
    Reserves handled in fixed order: in_state, first_gen, pell, rural, then general seats.
    A student can occupy only one seat.
    """
    # Determine reserve seats
    r_in_state = int(round(c.capacity * (c.reserve_in_state if c.is_public else 0.0)))
    r_fg = int(round(c.capacity * max(c.reserve_first_gen, scenario.reserve_first_gen)))
    r_pell = int(round(c.capacity * max(c.reserve_pell, scenario.reserve_pell)))
    r_rural = int(round(c.capacity * max(c.reserve_rural, scenario.reserve_rural)))

    # Effective legacy policy
    legacy_on = scenario.legacy_on_private or c.is_public

    # Build eligible list
    eligible = [sid for sid in proposers if eligible_for_college(world.students[sid], c)]
    # Precompute scores
    scores = {sid: score_student_for_college(world.students[sid], c, world, legacy_on, rng) for sid in eligible}

    chosen: Set[int] = set()
    def pick_top(cands: List[int], k: int):
        nonlocal chosen
        if k <= 0 or not cands:
            return
        # sort by score desc
        cands_sorted = sorted(cands, key=lambda x: scores[x], reverse=True)
        for sid in cands_sorted:
            if len(chosen) >= k + len(chosen):  # no-op condition placeholder
                break
        chosen.update(cands_sorted[:k])

    # a helper to select up to k from candidates, skipping already chosen
    def select_k_from(predicate, k: int):
        pool = [sid for sid in eligible if sid not in chosen and predicate(world.students[sid])]
        if k <= 0 or not pool:
            return
        pool_sorted = sorted(pool, key=lambda sid: scores[sid], reverse=True)
        chosen.update(pool_sorted[:k])

    # Reserve order: in_state, first_gen, pell, rural
    select_k_from(lambda s: (s.state == c.state), min(r_in_state, c.capacity))
    select_k_from(lambda s: s.first_gen, max(0, min(r_fg, c.capacity - len(chosen))))
    select_k_from(lambda s: s.pell, max(0, min(r_pell, c.capacity - len(chosen))))
    select_k_from(lambda s: s.rural, max(0, min(r_rural, c.capacity - len(chosen))))

    # Fill remaining general seats
    remaining = max(0, c.capacity - len(chosen))
    if remaining > 0:
        pool = [sid for sid in eligible if sid not in chosen]
        pool_sorted = sorted(pool, key=lambda sid: scores[sid], reverse=True)
        chosen.update(pool_sorted[:remaining])

    # Ensure capacity respected
    if len(chosen) > c.capacity:
        # Trim lowest-scoring to capacity
        trimmed = sorted(list(chosen), key=lambda sid: scores[sid], reverse=True)[:c.capacity]
        chosen = set(trimmed)

    return chosen
