
# Math Playground (Flask)

An educational, interactive web app showcasing classic probability and statistics concepts with sleek, minimal UI.

## Demos Included
- **Birthday Paradox** — theoretical vs simulated probability of a shared birthday.
- **Monty Hall** — switch vs stay win rates.
- **Central Limit Theorem (CLT)** — histogram of sample means with a normal curve overlay.
- **Benford’s Law** — first-digit frequencies vs Benford’s expected distribution.
- **Law of Large Numbers (LLN)** — running average of biased coin flips.
- **Conway’s Game of Life** — classic cellular automaton (client-side).

## Quickstart

```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
python app.py

# 4) Open in your browser
# Visit http://127.0.0.1:5000
```

## Dependencies
- Python 3.9+
- Flask

## Notes
- No external CDNs; everything is self-contained.
- The charts are lightweight custom canvas drawings — no heavy charting libraries.
- The server endpoints limit sample sizes to keep the app responsive.
