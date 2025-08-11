
from __future__ import annotations
import numpy as np
from typing import List, Dict, Tuple
import pandas as pd

def simulate_shows(plan: List[Dict], seg_table: pd.DataFrame, iters: int = 10000, seed: int = 0) -> Dict:
    rng = np.random.default_rng(seed)
    totals = np.zeros(iters, dtype=int)

    for item in plan:
        event_type = item["event_type"]
        industry = item["industry"]
        n = int(item["reachouts"])
        row = seg_table[(seg_table["event_type"]==event_type) & (seg_table["industry"]==industry)]
        if row.empty:
            # Fallback to overall event_type average if industry unseen
            row = seg_table[(seg_table["event_type"]==event_type)]
            if row.empty:
                raise ValueError(f"No history for event_type '{event_type}'")
            # Use weighted mean across industries
            a_resp = row["a_resp"].sum()
            b_resp = row["b_resp"].sum()
            a_show = row["a_show"].sum()
            b_show = row["b_show"].sum()
        else:
            r = row.iloc[0]
            a_resp, b_resp, a_show, b_show = r["a_resp"], r["b_resp"], r["a_show"], r["b_show"]
        # Sample rates from Beta posteriors
        p_resp = rng.beta(a_resp, b_resp, size=iters)
        p_show = rng.beta(a_show, b_show, size=iters)
        # Binomial draws
        commits = rng.binomial(n, p_resp)
        shows = rng.binomial(commits, p_show)
        totals += shows

    return {
        "totals": totals,
        "expected": float(np.mean(totals)),
        "p10": int(np.percentile(totals, 10)),
        "p50": int(np.percentile(totals, 50)),
        "p90": int(np.percentile(totals, 90)),
    }

def probability_metrics(totals: np.ndarray, target: int) -> Dict:
    hit = np.mean(totals >= target)
    over = np.mean(totals > target)
    return {"p_hit": float(hit), "p_overfill": float(over)}

def suggest_plan(baseline_plan: List[Dict], seg_table: pd.DataFrame, target: int, conf: float = 0.8, max_scale: float = 10.0, seed: int = 42) -> Dict:
    """Scale the given plan uniformly until P(hit target) >= conf, using quick search.
    Returns suggested reachouts per segment and a quick validation with fewer iters.
    """
    lo, hi = 1.0, max_scale
    best = None
    # quick iterations to keep latency low
    for _ in range(18):
        mid = (lo + hi) / 2.0
        plan = [{"event_type": x["event_type"], "industry": x["industry"], "reachouts": int(round(x["reachouts"]*mid))} for x in baseline_plan]
        res = simulate_shows(plan, seg_table, iters=4000, seed=seed)
        pm = probability_metrics(res["totals"], target)
        if pm["p_hit"] >= conf:
            best = (mid, plan, res, pm)
            hi = mid
        else:
            lo = mid
    if best is None:
        mid = hi
        plan = [{"event_type": x["event_type"], "industry": x["industry"], "reachouts": int(round(x["reachouts"]*mid))} for x in baseline_plan]
        res = simulate_shows(plan, seg_table, iters=4000, seed=seed+1)
        pm = probability_metrics(res["totals"], target)
        best = (mid, plan, res, pm)
    scale, plan, res, pm = best
    return {
        "scale": scale,
        "plan": plan,
        "validation": {
            "expected": res["expected"],
            "p10": res["p10"],
            "p50": res["p50"],
            "p90": res["p90"],
            "p_hit": pm["p_hit"],
            "p_overfill": pm["p_overfill"]
        }
    }
