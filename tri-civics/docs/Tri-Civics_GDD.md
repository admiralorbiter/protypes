# Tri‑Civics: Bureaucracy × Districts × Externalities
**Version:** 0.1  
**Date:** 2025-08-23  
**Author:** Auto-drafted with your prompts

## High Concept
A civic strategy-sim where three layers **interlock**:
1) **Micro‑City Externalities** — Buildings emit Noise/Pollution/Traffic fields. You shape zoning, mitigation, and **Pigouvian taxes** to internalize harms while sustaining growth.
2) **Bureaucracy Simulator** — Every action creates paperwork flowing through a **process graph**. Rules reduce risk but increase delay and rework. You manage staffing, automation, triage, and SLAs.
3) **Gerrymander Puzzlebox** — Redraw districts on a voter grid. In “Governance” mode you must pass court tests (contiguity, equal pop, compactness) while navigating politics and legitimacy.

These subsystems **feed each other**:
- Externalities → voter happiness & neighborhood swing → **election outcomes**.
- District boundaries → policy levers & budget priorities → **bureaucratic rules** and city taxes.
- Bureaucratic throughput → permit timing & enforcement → **land use pattern**, emissions, complaints.

Target vibe: **teach-through-play** with crunchy systems and readable math. Single‑player, session 30–90 minutes, scenario‑driven.

## Player Fantasy & Pillars
- **Steer a living city** using rules, districts, and taxes—not God‑mode zoning alone.
- **Tradeoffs are the game**: throughput vs risk, growth vs harm, winning seats vs fairness.
- **Explainable outcomes**: always show why a metric changed (fields, queues, districts).

**Design Pillars**
- *Transparency*: in‑UI formulas, tooltips, and causal highlighting.
- *Interlocking loops*: each move nudges the other layers within 1–3 minutes.
- *Small, legible maps*: single-screen play first; expand later.

## Core Loop (Monthly Tick)
1) **Plan** (pause): adjust taxes, rules, and district seeds; queue capital projects (parks/barriers).  
2) **Simulate** (run month):  
   - Externality fields diffuse/decay; developers invest/redevelop.  
   - Bureaucratic queues process permits, inspections, benefits.  
   - Residents & firms update satisfaction; voter intentions shift.  
3) **Report**: KPIs, court/legal checks, election/legitimacy drift.  
4) **React**: events (audit, scandal, disaster, boom).  
5) Repeat until scenario goal or failure.

---

## Systems Overview
### A) Micro‑City Externalities
**Grid**: W×H tiles. Each tile `i` has `{zone, btype, pop, jobs, eN,eP,eT}` and receives fields `N,P,T`.

**Field Update** (per day):  
\[ F^{{t+1}} = F^t + D \nabla^2 F^t - \delta F^t + S^t - K^t \]  
- `D`: diffusion, `δ`: decay, `S`: sources (buildings/traffic), `K`: sinks (parks/barriers).  
- Optional advection for pollution: \( F^{{t+1}} += \vec v \cdot \nabla F^t \).

**Developer Decision** (monthly): profit at tile `i` for building `b`  
\[ \pi_i(b) = R_b - C_b - Tax_b - w_{{MEC}} \cdot Impact_i(b, N,P,T) \]  
If \( \pi_i(b) - \pi_i(current) > \theta \), redevelop w.p. `p`.  
**Teaching**: Pigouvian tax suggestion ≈ estimated marginal external cost.

**KPIs**: Welfare (resident utility + firm profit − harm), Budget, Equity (exposure gap), Growth.

### B) Bureaucracy Simulator
**Process Graph** G = (Nodes, Edges). Tokens = “cases” with `{{type, risk in [0,1], age, state}}`.

- **Service Node**: `servers c`, service time ~ Lognormal(μ,σ), cost/hr, optional `rework_to`.  
- **Rule/Check Node**: adds deterministic wait `d` and test with `tp/fp`:
  - For case risk `r`: `P(catch risky) ≈ tp · r`.  
  - `P(false positive) ≈ fp · (1 − r)` → rework.  
- **Incidents**: risky case exiting uncaught causes event with `p_incident = k·r` (cost + legitimacy hit).

**Little’s Law surfaced**: `WIP ≈ Throughput × LeadTime`. Utilization ρ highlights bottlenecks.

**Levers**: staffing, triage (fast lane vs strict lane), automation (reduces `d` but may raise `fp`), mandatory checks (policy cards).

**KPIs**: Throughput, Lead Time, WIP, Incident rate, Cost, Public Satisfaction.

### C) Gerrymander/Districting
**Tiles**: `{{pop, pA in [0,1], turnout w}}`. K districts must be contiguous (4‑connected) and near‑equal population.

**Metrics** (live):  
- **Seats**: expected winner per district.  
- **Efficiency Gap (EG)**:  
  \[ EG = \frac{{\sum (wasted_A) - \sum (wasted_B)}}{{\sum votes}} \]  
- **Compactness (Polsby–Popper)**: \( 4πA / P^2 \) per district (grid area/perimeter).  
- **Mean–Median Bias** (optional).  
- **Community splits** penalty for cutting tagged blocks.

**Modes**: Fairness (minimize bias, pass court) vs Governance (hit seat target within legal bounds to pass reforms).

---

## Interlocks (The Fun Part)
- **Permits ↔ Development**: Bureaucracy throughput gates building starts → changes emission sources S.  
- **Harm → Politics**: High N/P/T harms reduce satisfaction; voters swing; **district seats** and **council composition** update policy levers (tax caps, mandatory checks).  
- **District Law ↔ Bureaucracy**: Court thresholds (compactness, EG band) alter what reforms you can implement; scandals from incidents trigger oversight (mandatory rule nodes).  
- **Budget**: Taxes (including Pigouvian) and staffing costs feed a single budget. Seat control changes **budget priorities** via policy cards.

**Example Loop**: You tighten compliance after a scandal → permits slow → fewer factories → pollution down → happier downtown voters → district flips → council allows higher Pigouvian cap → you fund parks → traffic noise cools → property values shift → developers infill housing.

---

## Game Modes & Progression
- **Scenario Pack** (recommended start): 5 maps with unique winds, geographies, and political constraints.  
- **Sandbox**: start with neutral council, free redraw every 2 years, random events on.  
- **Challenge Puzzles**: fixed community blocks + objective (e.g., “Balance EG within ±0.05 while delivering 4 seats”).

**Victory** (per scenario): reach targets by Year 5–8 (Welfare ≥ X, Equity gap ≤ Y, Budget ≥ 0, Court approval).  
**Loss**: insolvency, catastrophic incident, court injunction, or legitimacy below floor.

---

## UI/UX
- **Top Bar**: Month/Year, Budget, Legitimacy, Majority control.  
- **Left Panel (Tools)**: Zoning brush, District brush (seed/grow), Process editor (add/remove nodes), Build mitigation (parks/barriers).  
- **Right Panel (Levers)**: Tax sliders per type, staffing & automation, triage toggles, policy cards.  
- **Center**: Map (heatmap toggle N/P/T), district overlay, process graph (tab), queue bars.  
- **Explainability**: hover any cell/node shows formula deltas; click district to see compactness/EG and legal status.

---

## Data & Algorithms (MVP)
- **Grids**: numpy int/float arrays for types, fields, districts.  
- **Diffusion**: 2D convolution with Laplacian kernel each day; clamp to [0, max].  
- **District contiguity**: BFS per district; reject edits that break contiguity unless “unsafe edits” mode is on with warnings.  
- **Perimeter**: count boundary edges between different district IDs or map edges.  
- **EG**: compute expected votes via `pop * w * pA`; wasted votes formula as standard.  
- **Queues**: per-node FIFO lists; service progress tracked per server.  
- **Incidents**: Bernoulli by `k·r` on exit; severity distribution (light/moderate/severe).

**Update Order (per month)**  
1. Externalities daily loop (30 steps): diffuse/decay, apply sources/sinks.  
2. Bureaucracy daily loop: process arrivals, services, rules, incidents.  
3. Developer decisions (monthly): redevelopment based on `pi`.  
4. Election model tick (monthly): satisfaction → swing; apply event modifiers.  
5. KPIs & budgets, events.

---

## AI/Agents
- **Developers**: myopic profit seekers with stickiness; heterogeneity via green vs dirty types.  
- **Voters**: base lean + issue weightings (N,P,T, affordability, jobs). Update intention via weighted harms/benefits.  
- **Clerks**: throughput affected by morale; high utilization lowers morale → breakdown chance.  
- **Council**: composition driven by district seats; majority unlocks/locks policies.

---

## Balancing & Difficulty
- Sliders in scenario JSON: `D, δ, wind, emission rates, tp/fp/delay, k, budget caps, EG/compactness thresholds`.  
- Difficulty presets modify: arrivals lambda, incident penalties, election volatility, redevelopment stickiness.

---

## Content & Modding
- **Scenario JSON**: map size, seeds for voters/population, winds, initial districts, process graph layout, policy thresholds.  
- **Tuning tables (YAML)**: building type params, emission rates, tax limits, rule node stats.  
- **Localization**: strings in `i18n/*.json` (later).

---

## Tech & Architecture
- **Language**: Python 3.11+, PyGame, NumPy.  
- **Determinism**: seeded RNG per scenario; record of player actions for replay.  
- **Filesystem**: `saves/` records scenarios and replays (JSONL).  
- **Modules**: `systems.city`, `systems.bureaucracy`, `systems.districting`, `systems.elections`, `utils.*`  
- **Performance**: grids up to 64×64, fixed time step; avoid per-tile Python loops where possible (vectorize).

**Serialization**: dataclasses → JSON via custom encoder.  
**Testing**: metric functions unit tested (EG, compactness, contiguity).

---

## Milestones (suggested)
1) **Foundation (week 1–2)**: Render grid & heatmaps; fixed-step loop; district paint + live EG/compactness; minimal queue sim.  
2) **Interlocks (week 3–4)**: Tie permits → sources; election swing from harms; policy cards affecting rules/taxes.  
3) **Scenarios & UX (week 5–6)**: 2 scenarios, court screen, explainability overlays, save/load.  
4) **Polish (week 7+)**: audio, animations, tutorials, balance.

---

## Glossary
- **Externality**: cost/benefit not priced in private transactions.  
- **Pigouvian Tax**: tax equal to marginal external cost to align incentives.  
- **Efficiency Gap**: asymmetry in wasted votes across parties.  
- **Polsby–Popper**: compactness measure using area & perimeter.  
- **Little’s Law**: WIP = Throughput × Lead Time.

---

## Appendix: Pseudocode Sketches

**Diffusion (one step)**
```
F = F + D * laplacian(F) - δ * F + sources - sinks
F = clip(F, 0, Fmax)
```

**EG (expected votes)**
```
votesA = sum(pop * w * pA over tiles in district)
votesB = sum(pop * w * (1 - pA))
wasted_A = votesA - floor(total/2 + 1) if A wins else votesA
EG = (sum(wasted_A) - sum(wasted_B)) / sum(total_votes)
```

**Queue tick**
```
for node in nodes:
  while node.has_idle_server() and node.queue:
    start_service(next_item)
  advance_services(dt)
  if node.type == 'rule':
    wait d then route pass→next, fail→rework
```

— End of GDD —