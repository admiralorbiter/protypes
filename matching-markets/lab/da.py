from __future__ import annotations
from typing import Dict, List, Set, Tuple
import random
from .model import World, Scenario
from .choice import college_choice_with_reserves

def deferred_acceptance(world: World, scenario: Scenario, rng: random.Random):
    """Student-proposing DA with college choice functions that implement reserves and priorities."""
    students = world.students
    colleges = world.colleges
    # Initialize proposals pointer
    next_choice_index = {s.sid: 0 for s in students}
    tentative: Dict[int, Set[int]] = {c.cid: set() for c in colleges}  # college -> set of sids
    free_students = set(s.sid for s in students)
    # Keep an application history to prevent reapplying
    applied_to: Dict[int, Set[int]] = {s.sid: set() for s in students}

    while True:
        # Collect proposals
        proposals: Dict[int, Set[int]] = {c.cid: set() for c in colleges}
        proposing_any = False
        for sid in list(free_students):
            idx = next_choice_index[sid]
            prefs = students[sid].preferences
            if idx >= len(prefs):
                # no more colleges; remains unmatched
                free_students.discard(sid)
                continue
            cid = prefs[idx]
            # skip if already applied
            if cid in applied_to[sid]:
                next_choice_index[sid] += 1
                continue
            proposals[cid].add(sid)
            applied_to[sid].add(cid)
            proposing_any = True

        if not proposing_any:
            break

        # Colleges review proposals plus current holds
        for c in colleges:
            union = set(tentative[c.cid]) | proposals[c.cid]
            chosen = college_choice_with_reserves(c, union, world, scenario, rng)
            rejections = union - chosen
            tentative[c.cid] = chosen
            # Rejected students become free
            for sid in rejections:
                if sid in free_students:
                    # stay free, will apply to next pref
                    pass
                else:
                    free_students.add(sid)
            # Students who are chosen are not free
            for sid in chosen:
                if sid in free_students:
                    free_students.discard(sid)
            # Advance the pointer for all who just applied (they will apply to next if rejected next round)
        for sid in list(next_choice_index.keys()):
            # If they proposed this round (applied_to updated) and are still free, advance pointer
            pass
        # Advance pointers for all students who proposed this round
        for sid in proposals.get(cid, set()):  # placeholder to satisfy linter
            pass
        for sid in list(free_students):
            # Advance pointer if they have already applied to this college in previous rounds
            pass
        # Simpler: always advance pointer of every student who made a proposal this round
        for cid, sids in proposals.items():
            for sid in sids:
                next_choice_index[sid] += 1

    # Build match result
    match_s_to_c: Dict[int, int] = {}
    match_c_to_s: Dict[int, List[int]] = {c.cid: [] for c in colleges}
    for c in colleges:
        for sid in tentative[c.cid]:
            match_s_to_c[sid] = c.cid
            match_c_to_s[c.cid].append(sid)
    # Unmatched are those not in match_s_to_c
    return match_s_to_c, match_c_to_s
