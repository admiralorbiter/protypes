# Tri‑Civics (Starter)

A PyGame prototype scaffold that combines **Micro‑City Externalities**, **Bureaucracy**, and **Districting** into one interlocking sim.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## Controls (MVP)
- `1/2/3`: Toggle heatmaps (Noise/Pollution/Traffic)
- `D`: Cycle district brush ID
- `Space`: Pause/Resume

## Structure
- `src/game/systems/city_externalities.py`
- `src/game/systems/districting.py`
- `src/game/systems/bureaucracy.py`
- `src/game/systems/elections.py`
- `src/game/utils/*` helpers
- `src/game/data/scenario_default.json`

See `docs/Tri-Civics_GDD.md` for full design.
