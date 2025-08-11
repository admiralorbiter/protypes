
# Volunteer Waitlist & Yield Forecaster (Flask)

Plan **how many volunteers to reach out to today** so you hit event capacity, using your historical **response** and **show** rates by **event type** and **industry**.

- **Model:** Beta–Binomial posteriors for response rate (commitments/outreach) and show rate (shows/commitments) per segment.
- **Forecast:** Monte Carlo (default 10k runs) simulates shows for your plan.
- **UI:** Build a multi-row plan (event type + industry + reachouts), set a target, and see:
  - Expected shows and P10/P50/P90
  - P(hit target), P(overfill)
  - A **Suggested Plan** that scales your rows to reach an 80% (configurable) chance of hitting target.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install flask pandas numpy
python app.py
# open http://127.0.0.1:5000/
```

## Bring your own data
Upload a CSV with columns (lower/upper case ok):
- `date` (YYYY-MM-DD),
- `event_type` (string), 
- `industry` (string),
- `outreach` (int), 
- `commitments` (int ≤ outreach),
- `shows` (int ≤ commitments).

The app recomputes segment posteriors after upload.

## Notes
- If an industry is unseen for an event type, we fall back to the **event-level pooled** posterior.
- Suggestion uses a uniform scale on your plan rows, found by binary search to meet your confidence.
- This is a planning tool. Reality will vary—use it to guide **batches** of outreach, not one massive blast.

## Next ideas
- Recency weighting (downweight older months).
- Per-row upper bounds (contact list sizes).
- Costs per outreach and objective function (minimize cost for target).
- Calendar mode (simulate multiple outreach waves).
