# Future Work — Preflop Poker Trainer

A structured checklist of improvements, features, and refinements for the app.

---

## 1. Core Functionality

- [ ] **Equity Engine**
  - [ ] Add faster evaluator (C, Numba, or precomputed tables)
  - [ ] Cache 169-hand × opponent-count equity values
  - [ ] Allow custom opponent range definitions (not just random)

- [ ] **Combinatorial Odds**
  - [ ] Add exact OESD probability per rank combo (no approximations)
  - [ ] Add top pair probability (unpaired hands)
  - [ ] Include overpair probability (pocket pairs vs board)

- [ ] **Recommendation Engine**
  - [ ] Make thresholds adjustable via UI sliders
  - [ ] Support multiple strategies (loose, tight, GTO-inspired)
  - [ ] Add bankroll/stack size consideration

---

## 2. User Interface / UX

- [ ] **Card Picker**
  - [ ] Drag-and-drop card selection
  - [ ] Highlight invalid duplicates dynamically
  - [ ] “Hand Rank” badge for quick recognition (e.g., AKs, 99, T8o)

- [ ] **Results Display**
  - [ ] Equity & odds chart with visual bars
  - [ ] Color-coded recommendation (green = raise, yellow = call, red = fold)
  - [ ] Tooltips explaining each probability

- [ ] **Interactivity**
  - [ ] Quick “Random Hand” hotkey
  - [ ] “Lock” a card to practice specific ranges
  - [ ] History of last 10 hands with results

---

## 3. Training & Learning Modes

- [ ] **Quiz Mode**
  - [ ] Show random hand → user picks Raise/Call/Fold → score vs model
  - [ ] Streak tracker for correct answers
  - [ ] Difficulty settings (opponent count changes, random)

- [ ] **Scenario Mode**
  - [ ] Preset contexts (Heads-up, 6-max, Full ring)
  - [ ] Include position presets (UTG, MP, CO, BTN, SB, BB)
  - [ ] Simulate common preflop spots

- [ ] **Learning Aids**
  - [ ] Range heatmaps showing which hands are profitable
  - [ ] Explain “why” behind recommendation (equity + odds + hand type)
  - [ ] Links to external learning resources

---

## 4. Data & Analytics

- [ ] **Session Tracking**
  - [ ] Store hands and results in local storage
  - [ ] Export CSV of played/trained hands
  - [ ] Aggregate stats: % raise/call/fold, EV diff from model

- [ ] **Performance Metrics**
  - [ ] Track accuracy improvement over time
  - [ ] Compare user’s play vs GTO ranges

---

## 5. Technical & Deployment

- [ ] **Performance**
  - [ ] Optimize Monte Carlo loop (vectorize or multi-thread)
  - [ ] Async equity calculation to avoid UI freezing
  - [ ] Preload data tables for instant lookup

- [ ] **Deployment**
  - [ ] Dockerize app for easy sharing
  - [ ] Deploy demo on Render/Heroku/Fly.io
  - [ ] Add offline PWA mode

---

## 6. Nice-to-Have Features

- [ ] **Customization**
  - [ ] Theme switcher (dark/light)
  - [ ] Card back styles
  - [ ] Custom bet size slider (for non-all-in equity calc)

- [ ] **Advanced Features**
  - [ ] Multi-way equity breakdown (graph equity vs # of opponents)
  - [ ] Postflop extension (basic flop texture awareness)
  - [ ] Integrate with real hand histories for review

---
