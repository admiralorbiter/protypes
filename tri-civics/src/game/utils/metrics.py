import numpy as np

def compute_eg(state):
    """Very rough efficiency gap using expected votes from pop and a synthetic lean field.
    Replace with real per-tile pA and turnout when available."""
    H, W = state.pop.shape
    pA = np.full((H,W), 0.52, dtype=np.float32)
    pA[:, W//2:] = 0.48
    w = 0.9
    eg_num = 0
    total = 0
    dids = np.unique(state.district)
    for did in dids:
        mask = (state.district == did)
        votesA = np.sum(state.pop[mask] * w * pA[mask])
        votesB = np.sum(state.pop[mask] * w * (1 - pA[mask]))
        total_votes = votesA + votesB
        total += total_votes
        if votesA > votesB:
            wastedA = votesA - (total_votes//2 + 1)
            wastedB = votesB
        else:
            wastedA = votesA
            wastedB = votesB - (total_votes//2 + 1)
        eg_num += (wastedA - wastedB)
    if total == 0:
        return 0.0
    return float(eg_num / total)
