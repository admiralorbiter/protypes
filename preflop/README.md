
# Preflop Poker Trainer (Flask)

A tiny educational app focused on **opening two hole cards**. It estimates **preflop equity** via Monte Carlo vs N random opponents and shows **combinatorial flop odds** (pair/two pair/set, flush draws, etc.). It then makes a **simple raise/call/fold** suggestion using a breakeven equity threshold.

> ⚠️ This is a teaching toy. It **ignores position, stack sizes, bet sizes, rake, and opponent ranges**. Use it to learn intuition, not as a real strategy chart.

## Features
- Pick or deal two hole cards; choose number of opponents.
- Monte Carlo equity estimate (configurable iterations).
- Combinatorial flop odds:
  - Pocket pair: P(set), P(quads), P(set or better)
  - Unpaired: P(pair or better), P(two pair), P(trips)
  - Suited: P(flush on flop), P(flush draw), P(backdoor flush), P(flush by river)
  - Connectors: approx P(open-ended straight draw on flop)
- Recommendation: **Raise / Call / Fold** using equity thresholds around **1/(players)** baseline.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install flask
python app.py
# open http://127.0.0.1:5000/
```

## How recommendations work
- Break-even all-in equity vs *n* opponents is roughly **1/(n+1)**.
- We add a margin (+6% for raise, -2% for call) to produce conservative suggestions.
- Example: vs one opponent, breakeven ~50%. So **Raise ≥56%**, **Call 48–56%**, **Fold <48%**.

## Implementation notes
- Equity: simple Monte Carlo using a 7-card evaluator (best 5 of 7).
- Flop odds: exact hypergeometric calculations where feasible.
- OESD probability is an approximation for true connectors; exact values vary by ranks.

## Ideas to extend
- Position/range presets (e.g., “Button vs BB”, “UTG open vs MP”). 
- Real preflop charts by position and stack depth.
- Hand history “quiz mode” with scoring.
- Faster C-based evaluator or precomputed 169-hand equity table.
