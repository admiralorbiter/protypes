
# Survey Sample Size & MOE Planner (Flask)

A practical planner for finding how many **survey completes** you need to achieve a target **margin of error (MOE)** at a chosen confidence level, with **finite population correction (FPC)**. Includes a **multi-group** allocator and a **power-based A/B (difference in proportions)** calculator.

## Features
- **Single group**: compute required completes *or* the MOE you get for a given n.
- **Finite population correction** and **design effect** multiplier.
- **Response rate** adjustment → **invitations needed**.
- **Multi-group planner**:
  - Target an **overall MOE** (with proportional / balanced / Neyman allocation) or
  - Same **per-group MOE** (size each stratum individually).
  - Shows per-group completes and invites.
- **A/B difference in proportions**: power-based n per group (optional FPC).

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install flask
python app.py
# open http://127.0.0.1:5000/
```

## Formulas (overview)
- **Single group, target MOE e**: \( n_0 = Z^2 p(1-p) / e^2 \). Apply **design effect** (`deff`) and **FPC**: \( n = \frac{n_0\cdot deff \cdot N}{n_0\cdot deff + (N-1)} \).
- **MOE from n**: \( e = Z \sqrt{\frac{p(1-p)}{n/deff}} \sqrt{\frac{N-n}{N-1}} \).
- **Overall MOE (stratified)**: \( Var(\hat p) = \sum_h W_h^2 \cdot \frac{p_h(1-p_h)}{n_h/deff_h} \cdot (1 - f_h) \), with \( W_h=N_h/N \), \( f_h = n_h/N_h \); MOE = Z√Var.
- **Neyman allocation** (approx): \( n_h \propto N_h \cdot S_h \cdot \sqrt{deff_h} \) with \( S_h = \sqrt{p_h(1-p_h)} \).

> Defaults to **worst-case p=0.5** if unknown.

## Notes
- Normal approximation is used; for very small n or extreme p, exact methods (Wilson/Clopper-Pearson) differ.
- Design effect (>1) inflates required n to account for clustering/weights.
- Response rate only rescales **invites**; it doesn’t change sampling variance.

## Next steps
- Support MOE for **means** (with sigma estimate).
- Import/export **group rows** via CSV.
- Show **MOE vs n** curve and **invites vs RR** sensitivity.
