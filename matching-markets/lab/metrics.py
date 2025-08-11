from __future__ import annotations
from typing import Dict, List, Tuple
from collections import defaultdict
from .model import World

def summarize(world: World, match_s_to_c: Dict[int, int]) -> Dict:
    students = world.students
    colleges = {c.cid: c for c in world.colleges}
    total = len(students)
    admitted = set(match_s_to_c.keys())
    res = {
        "overall": {
            "admit_rate": len(admitted)/total
        },
        "by_group": {},
        "by_college": {}
    }

    def agg(mask):
        n = len(mask)
        admits = sum(1 for sid in mask if sid in admitted)
        return {"count": n, "admit_rate": (admits/n if n>0 else 0.0)}

    # Build groups
    groups = {
        "first_gen": [s.sid for s in students if s.first_gen],
        "non_first_gen": [s.sid for s in students if not s.first_gen],
        "pell": [s.sid for s in students if s.pell],
        "rural": [s.sid for s in students if s.rural],
    }
    # Income quintiles
    for q in range(1,6):
        groups[f"income_q{q}"] = [s.sid for s in students if s.income_quintile == q]

    # In-state overall: define relative to the college they matched
    in_state_admits = 0
    out_state_admits = 0
    for sid, cid in match_s_to_c.items():
        s = students[sid]
        c = colleges[cid]
        if s.state == c.state:
            in_state_admits += 1
        else:
            out_state_admits += 1
    res["overall"]["in_state_share_among_admits"] = (in_state_admits / max(1, (in_state_admits + out_state_admits)))

    for name, mask in groups.items():
        res["by_group"][name] = agg(mask)

    # College-level fill & reserve utilization (approximate: count of in-state etc. among admits)
    for c in world.colleges:
        sids = [sid for sid, cid in match_s_to_c.items() if cid == c.cid]
        n = len(sids)
        in_state = sum(1 for sid in sids if world.students[sid].state == c.state)
        fg = sum(1 for sid in sids if world.students[sid].first_gen)
        pell = sum(1 for sid in sids if world.students[sid].pell)
        rural = sum(1 for sid in sids if world.students[sid].rural)
        res["by_college"][c.cid] = {
            "name": c.name,
            "capacity": c.capacity,
            "filled": n,
            "fill_rate": n / c.capacity if c.capacity else 0.0,
            "in_state_share": in_state / n if n else 0.0,
            "first_gen_share": fg / n if n else 0.0,
            "pell_share": pell / n if n else 0.0,
            "rural_share": rural / n if n else 0.0,
        }
    return res

def diff_metrics(base: Dict, alt: Dict) -> Dict:
    """Compute deltas alt - base for comparable fields."""
    def get(d, path, default=0.0):
        cur = d
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return default
        return cur
    out = {"overall": {}, "by_group": {}}
    # Overall deltas
    for k in ["admit_rate", "in_state_share_among_admits"]:
        out["overall"][k] = get(alt, ["overall", k]) - get(base, ["overall", k])
    # Group deltas
    for g in alt["by_group"].keys():
        out["by_group"][g] = {
            "admit_rate": get(alt, ["by_group", g, "admit_rate"]) - get(base, ["by_group", g, "admit_rate"]),
            "count": get(alt, ["by_group", g, "count"]) - get(base, ["by_group", g, "count"])
        }
    return out
