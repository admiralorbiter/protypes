
from __future__ import annotations
from typing import Dict
def recommend_action(equity: float, n_opponents: int) -> Dict[str, str]:
    # Baseline all-in break-even equity ~ 1/(n+1).
    thresh = 1.0 / (n_opponents + 1)
    # Add margins since we're not modeling position/stack/bets; give 5% cushion
    raise_cut = thresh + 0.06
    call_cut = thresh - 0.02
    if equity >= raise_cut:
        action = "RAISE"
        note = f"Equity {equity:.1%} ≥ raise-cut {raise_cut:.1%} vs {n_opponents} opponents"
    elif equity >= call_cut:
        action = "CALL"
        note = f"Equity {equity:.1%} is near threshold {thresh:.1%}; borderline call"
    else:
        action = "FOLD"
        note = f"Equity {equity:.1%} < call-cut {call_cut:.1%} vs {n_opponents} opponents"
    return {"action": action, "explanation": note, "threshold": f"{thresh:.1%}"}
