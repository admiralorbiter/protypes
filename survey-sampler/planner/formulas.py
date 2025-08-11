
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import math

Z_MAP = {
    0.80: 1.2816,
    0.85: 1.4395,
    0.90: 1.6449,
    0.95: 1.96,
    0.975: 2.2414,
    0.98: 2.3263,
    0.99: 2.5758,
    0.995: 2.8070,
}

def z_for_conf(conf_level: float) -> float:
    # conf_level like 0.95 -> two-sided z for alpha/2
    # We'll map common values; otherwise approximate using 0.95 baseline
    if conf_level in Z_MAP:
        return Z_MAP[conf_level]
    # linear-ish fallback around 0.95 for nearby values
    return 1.96 + (conf_level - 0.95) * 6.0

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

@dataclass
class OneGroupInput:
    N: Optional[int]  # population size; None or 0 -> infinite
    moe: Optional[float]  # desired margin (0..1). If None, compute MOE given n
    n: Optional[int]      # completes (if provided, compute MOE); else compute n from moe
    conf: float = 0.95
    p_est: float = 0.5
    deff: float = 1.0
    response_rate: float = 1.0  # 0..1

@dataclass
class OneGroupResult:
    n_required: int
    invitations_needed: int
    moe_achieved: float
    fpc_applied: bool
    details: Dict[str, float]

def sample_size_one_group(inp: OneGroupInput) -> OneGroupResult:
    Z = z_for_conf(inp.conf)
    p = clamp01(inp.p_est)
    deff = max(1e-9, inp.deff)
    rr = max(1e-6, min(1.0, inp.response_rate))
    N = inp.N if (inp.N and inp.N > 0) else None

    if inp.moe is not None and (inp.n is None):
        e = max(1e-9, inp.moe)
        n0 = (Z**2 * p * (1-p)) / (e**2)    # infinite population
        n_deff = n0 * deff
        if N is None:
            n = math.ceil(n_deff)
            fpc_used = False
        else:
            n = math.ceil( (n_deff * N) / (n_deff + (N - 1)) )
            fpc_used = True
        invites = math.ceil(n / rr)
        # compute achieved MOE back from integer n
        n_eff = n / deff
        fpc = math.sqrt((N - n)/(N - 1)) if (N and N > 1) else 1.0
        moe_achieved = Z * math.sqrt( (p*(1-p))/max(1.0, n_eff) ) * fpc
        return OneGroupResult(n_required=n, invitations_needed=invites, moe_achieved=moe_achieved, fpc_applied=fpc_used,
                              details={"Z": Z, "p_est": p, "deff": deff, "rr": rr})
    elif inp.n is not None and (inp.moe is None):
        n = max(1, int(inp.n))
        n_eff = n / deff
        fpc = math.sqrt((N - n)/(N - 1)) if (N and N > 1) else 1.0
        moe = Z * math.sqrt( (p*(1-p))/max(1.0, n_eff) ) * fpc
        invites = math.ceil(n / rr)
        return OneGroupResult(n_required=n, invitations_needed=invites, moe_achieved=moe, fpc_applied=(N is not None),
                              details={"Z": Z, "p_est": p, "deff": deff, "rr": rr})
    else:
        raise ValueError("Provide either 'moe' or 'n', but not both.")

@dataclass
class GroupRow:
    name: str
    N: int
    p_est: float = 0.5
    deff: float = 1.0
    response_rate: float = 1.0
    min_n: int = 0

@dataclass
class MultiGroupInput:
    groups: List[GroupRow]
    conf: float = 0.95

@dataclass
class MultiGroupResult:
    per_group: List[Dict]
    overall_moe: float
    total_n: int
    total_invites: int
    allocation: str

def overall_moe_from_allocation(groups: List[GroupRow], n_alloc: List[int], conf: float) -> float:
    Z = z_for_conf(conf)
    N_total = sum(g.N for g in groups)
    if N_total <= 0:
        return float('nan')
    # Weighted stratified estimator variance
    var = 0.0
    for g, n in zip(groups, n_alloc):
        W = g.N / N_total
        p = clamp01(g.p_est)
        deff = max(1e-9, g.deff)
        n_eff = max(1.0, n / deff)
        fpc = (g.N - n) / (g.N - 1) if g.N > 1 else 1.0
        var += (W**2) * (p*(1-p) / n_eff) * fpc
    return Z * math.sqrt(max(var, 0.0))

def allocate(groups: List[GroupRow], total_n: int, style: str = "proportional") -> List[int]:
    # respect min_n floors
    floors = [max(0, g.min_n) for g in groups]
    n_remaining = max(0, total_n - sum(floors))
    alloc = floors[:]
    if n_remaining <= 0:
        return alloc
    if style == "balanced":
        # even split of remaining
        k = len(groups)
        base = n_remaining // k
        rem = n_remaining % k
        for i in range(k):
            alloc[i] += base + (1 if i < rem else 0)
    elif style == "neyman":
        # Neyman: proportional to N_h * S_h (and adjust for deff by sqrt)
        weights = []
        for g in groups:
            S = math.sqrt(clamp01(g.p_est) * (1 - clamp01(g.p_est))) or 0.5
            w = g.N * S * math.sqrt(max(1.0, g.deff))
            weights.append(w)
        total_w = sum(weights) or 1.0
        shares = [w/total_w for w in weights]
        parts = [int(n_remaining * s) for s in shares]
        # distribute residuals
        residual = n_remaining - sum(parts)
        # assign by largest fractional part
        fracs = [n_remaining * s - p for s,p in zip(shares, parts)]
        order = sorted(range(len(groups)), key=lambda i: fracs[i], reverse=True)
        for i in range(residual):
            parts[order[i]] += 1
        alloc = [a + p for a, p in zip(alloc, parts)]
    else:  # proportional
        weights = [g.N for g in groups]
        total_w = sum(weights) or 1.0
        shares = [w/total_w for w in weights]
        parts = [int(n_remaining * s) for s in shares]
        residual = n_remaining - sum(parts)
        fracs = [n_remaining * s - p for s,p in zip(shares, parts)]
        order = sorted(range(len(groups)), key=lambda i: fracs[i], reverse=True)
        for i in range(residual):
            parts[order[i]] += 1
        alloc = [a + p for a, p in zip(alloc, parts)]
    # cap by population if necessary
    for i, g in enumerate(groups):
        if alloc[i] > g.N:
            alloc[i] = g.N
    return alloc

def solve_total_n_for_overall_moe(groups: List[GroupRow], conf: float, target_moe: float, style: str = "proportional") -> Tuple[int, List[int]]:
    # Binary search total n to reach overall_moe <= target_moe
    lo, hi = 1, max(1, sum(g.N for g in groups))
    best_n, best_alloc = None, None
    for _ in range(20):
        mid = (lo + hi) // 2
        alloc = allocate(groups, mid, style=style)
        moe = overall_moe_from_allocation(groups, alloc, conf)
        if moe <= target_moe:
            best_n, best_alloc = sum(alloc), alloc
            hi = mid
        else:
            lo = mid + 1
    if best_alloc is None:
        alloc = allocate(groups, hi, style=style)
        return sum(alloc), alloc
    return best_n, best_alloc

def per_group_moe_targets(groups: List[GroupRow], conf: float, target_moe: float) -> List[int]:
    # Compute n for each group individually (same target per group)
    alloc = []
    for g in groups:
        res = sample_size_one_group(OneGroupInput(N=g.N, moe=target_moe, n=None, conf=conf, p_est=g.p_est, deff=g.deff, response_rate=1.0))
        alloc.append(res.n_required)
    return alloc

def invites_from_alloc(groups: List[GroupRow], alloc: List[int]) -> List[int]:
    invites = []
    for g, n in zip(groups, alloc):
        rr = max(1e-6, min(1.0, g.response_rate))
        invites.append(math.ceil(n / rr))
    return invites

# A/B difference in proportions (power-based sample size; equal n per group)
def z_for_power(power: float) -> float:
    # power = 1 - beta
    # common values: 0.8 -> 0.8416, 0.9 -> 1.2816
    if power >= 0.9: return 1.2816
    if power >= 0.8: return 0.8416
    return 0.5244  # ~70%

def n_diff_proportions(delta: float, conf: float = 0.95, power: float = 0.8, p1: float = 0.5, p2: float = 0.5, deff1: float = 1.0, deff2: float = 1.0, N1: Optional[int] = None, N2: Optional[int] = None) -> Tuple[int, int]:
    # Normal approximation; equal n per group
    Z = z_for_conf(conf)
    Zb = z_for_power(power)
    pbar = (p1 + p2) / 2.0
    num = (Z * math.sqrt(2 * pbar * (1 - pbar)) + Zb * math.sqrt(p1*(1-p1) + p2*(1-p2)))**2
    n0 = num / max(1e-9, delta**2)
    # inflate by design effects
    n1 = n0 * deff1
    n2 = n0 * deff2
    # FPC per group
    def apply_fpc(n, N):
        if N is None or N <= 0: return n
        return (n * N) / (n + (N - 1))
    n1 = apply_fpc(n1, N1)
    n2 = apply_fpc(n2, N2)
    return math.ceil(n1), math.ceil(n2)
