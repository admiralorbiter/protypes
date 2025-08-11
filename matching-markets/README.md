
# Matching Markets Lab — College Edition (PoC)

A small, policy-aware simulator of college admissions using **student-proposing Deferred Acceptance (Gale–Shapley)** with **priorities** and **reserve seats** (first-gen, Pell, rural, in-state). Includes toggles for **legacy** and **test-required waves** to reflect recent policy shifts.

## Features
- Synthetic cohort (≈8k students, 24 colleges) with realistic attributes.
- College choice functions with **reserve seats** and **test policy** filtering.
- Student-proposing **Deferred Acceptance** (stable under priorities).
- Scenario runner: compare **Baseline** vs **Your Scenario** and view winners/losers by group.
- Minimal Flask UI with instant tables and deltas.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install flask
python app.py
# open http://127.0.0.1:5000/
```

## Scenarios
Baseline hard-coded as: legacy on at privates, test-optional for all, no reserves, publics with 70% in-state. You control:
- `legacy_on_private` (bool)
- `test_required_private_elite` (bool) + `num_private_elites_test_required` (int)
- `reserve_first_gen`, `reserve_rural`, `reserve_pell` (shares 0..1, applied to all colleges)
- `public_in_state_share` (share 0..1 for publics)

## Code layout
```
lab/
  model.py       # dataclasses: Student, College, World, Scenario
  data.py        # synthetic data generator + preferences + legacy assignment
  choice.py      # scoring & college choice with reserves + test policy
  da.py          # deferred acceptance engine
  metrics.py     # summary & delta metrics
  scenarios.py   # apply scenario settings to colleges
templates/
  base.html, index.html
static/
  style.css
app.py          # Flask app + /api/run
```

## Notes & next steps
- This PoC **does not** implement Erdil–Ergin tie improvements yet; random tie-breaks are used.
- The reserve implementation uses a fixed order (in-state → first-gen → Pell → rural) and fills general seats next. This mirrors common policy priorities but can be refined.
- Add a CSV export endpoint and an audit log to list variables used in each decision.
- Add per-college overrides (e.g., different reserve mixes, varying legacy weights).
