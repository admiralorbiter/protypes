# Future Work – Can’t Stop Coach

## Quick Wins (High Impact, Low Effort)
- **Per-pairing next-roll bust%**: Show how choosing a pairing changes the bust probability for the *next* roll.
- **Why-this-call panel**: Display top roll outcomes driving the press EV (e.g., “7&7 happens 16/1296 and finishes 7”).
- **Shareable states**: Encode board state and risk profile into the URL.
- **Challenge seeds**: Generate daily “50/50” press/park puzzles.
- **Accessibility improvements**: Keyboard shortcuts, color-blind safe palette.

## Teaching & Explainability
- **Bust heatmap by column**: Bars above each open column showing `P(adv)` next roll.
- **Press threshold curve**: Graph showing bust% break-even points for current state and risk profile.
- **Rule visualizer**: Highlight playable columns before pairing selection.
- **Scenario scripts**: Prebuilt lessons explaining core strategy concepts.

## Strategy & AI Upgrades
- **Exact turn DP solver (risk-neutral)**: Replace MCTS for press/park with a memoized dynamic program over turn states.
- **Opponent-aware value**: Bonus for finishing columns where others are close.
- **Full-game mode**: Extend rollouts to game end with simple opponent models; report win%.
- **Learned policy model**: Train from DP/MCTS data for instant mobile advice.
- **Risk calibration**: Infer user’s risk preference from past choices.

## What-If & Analysis Tools
- **Press-K-times explorer**: Show bust%, finishes, EV for pressing K more rolls.
- **Pairing comparison table**: For current roll, show gains, finish probability, next-roll bust%, EV for each pairing.
- **Indifference map**: Visualize micro-states where press/park is marginal.

## Multiplayer & UX Polish
- **Hot-seat scoreboard**: Player trays, claimed-column crowns.
- **Online real-time**: WebSocket rooms for shared state viewing.
- **Opponent bots**: Greedy, Balanced, Blocker, Gambler.

## Performance & Engineering
- **Zobrist hashing**: Cache odds and search nodes by turn state key.
- **Vectorization / Numba**: Speed up bust probability loops.
- **Chance sampling knob**: Control sample count in MCTS chance nodes.
- **Profile & optimize**: Identify hot paths in `legal_pairings` and state copies.

## Testing & Correctness
- **Property-based tests**: Generate random states and assert invariants.
- **Golden states**: Hand-curated tricky positions with known correct odds.

## Data & Research Features
- **Decision logging**: Export board state, advice, user action, outcome for analysis.
- **Skill rating**: Track user EV vs. optimal turn decisions over time.
- **Explainer notebook**: Auto-generate match reports with plots.

## Nice-to-Haves / Variants
- **Speed round drill**: Timed decision challenges with EV scoring.
- **Mobile layout**: Compact, tap-friendly design.
- **Import real boards**: Form to set permanent markers & claimed columns.

---

### Recommended Next Two Features
1. **Pairing comparison + bust deltas**  
   Backend route: `/api/pairing_eval { roll }` → List of pairings with immediate gain, finish probability, next-roll bust%, and EV.  
   Frontend: Table display under roll info.

2. **Exact turn-DP press/park**  
   Backend: `dp.py` with `value(turn_state) -> EV`, memoized by compact key.  
   Integrate into `/api/coach/recommend` for stable, explainable press/park calls.
