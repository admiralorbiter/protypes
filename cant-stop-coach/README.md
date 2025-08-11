
# Can't Stop Coach (Flask + MCTS)

A minimal, clean scaffold for a real-time "Press or Park?" coach for the board game *Can't Stop*. It offers:
- Exact **bust odds** (1296 outcomes) for the *next* roll
- **Per-column advance probabilities**
- A simple but extensible **MCTS** that reasons within a single turn (stop vs. roll, plus pairing decisions)
- A neat Flask UI to play with state, ask for a recommendation, and inspect legal pairings

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install flask
python app.py
# open http://127.0.0.1:5000/
```

## Project layout

```
cantstop_coach/
├─ app.py                      # Flask app + API
├─ cantstop/
│  ├─ __init__.py
│  ├─ constants.py             # column heights
│  ├─ state.py                 # dataclasses for game/turn/player
│  ├─ engine.py                # rules, legal pairings, apply, stop
│  ├─ odds.py                  # bust prob + per-column advance prob
│  └─ mcts.py                  # MCTS + risk utility + recommenders
├─ templates/
│  ├─ base.html
│  └─ index.html               # simple UI
├─ static/
│  └─ style.css
└─ tests/
   └─ test_engine.py
```

## Notes

- The MCTS optimizes **turn utility**, not full-game win probability (kept small for clarity). You can extend rollouts to the end of game if you like.
- Risk profile options change the utility function (averse = sqrt, neutral = linear, seeking = square).
- `odds.py` uses exact enumeration for correctness. If you want blazing speed, memoize by a tighter turn-key or pretabulate by active-runner sets.

## Next steps

- Add opponent models + full-game mode (optimize win chance).
- Add explanation pane that lists top-contributing roll outcomes to EV.
- Serialize state in a shareable querystring (permalink your puzzle positions).
- Persist multiple sessions with server-side storage instead of Flask session.
