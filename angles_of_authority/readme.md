# Angles of Authority — Horizontal Slice Proof of Concept (Pygame)

**Version:** 0.1 (Horizontal Slice)  
**Genre:** Top-down tactical breach & clear with moral/legitimacy systems  
**Engine:** Pygame 2.x (Python 3.11+)  
**Target Playtime (slice):** 5–10 minutes per run  
**Scope:** 1 small apartment map, 2 suspects, 2 civilians, 1 press observer, 2 operators

---

## 1) One-Page Summary

**Pitch:** A SWAT-style micro-mission where your success is judged not only by clearing rooms but by how your actions *look* from witness perspectives. Live **Rules of Engagement (ROE)** gate allowable actions; a post-mission **After-Action Review (AAR)** reinterprets the encounter using recorded witness viewpoints to compute **Legitimacy** (your reputation/resource driver).

**Core Pillars**
- **Legitimacy by Perspective:** Morality is simulated via what witnesses saw, not what you intended.
- **Explicit Constraints:** Live ROE slider changes what’s legal *right now*.
- **Receipts, Not Narratives:** AAR replays logged events from cameras to re-score.

**Win/Lose (slice):**
- **Win:** Extract with all suspects neutralized (alive or restrained), no civilian injuries, Legitimacy ≥ 60, and at least 1 evidence token secured.
- **Partial:** Mission cleared but Legitimacy < 60.
- **Fail:** Operator down, hostage harmed, or all suspects flee.

---

## 2) Target Horizontal Slice (What “Done” Looks Like)

- One apartment (3 rooms + corridor), closed doors, 4–6 cover props.
- Two operators (Player-controlled, WEGO or pausable real-time with queued actions). For slice, use **pausable real-time**.
- Entities: **Suspect ×2**, **Civilian ×2**, **Press ×1** (wanders), **Evidence ×2** (gun, phone).
- Actions: **Move, Aim, Shout (Comply), Fire, Kick Door, Flashbang (1), Cuff, Secure Evidence**.
- ROE Modes: **Free, Cautious, Strict** (three positions).
- Witness System: cones + raycast; bodycams on both operators; press has wider FOV.
- AAR: replay 4–6 key frames; compute **Legitimacy** using observer-weighted scoring.
- UI: ROE slider, action bar (hotkeys), Legitimacy meter, small minimap, AAR results panel.

---

## 3) Core Mechanics (Slice Rules)

### 3.1 Rules of Engagement (ROE)
- **Strict:** No shots unless **target_threat_state ≥ AimingWeaponAtSomeone**. Flashbang allowed only after **Shout**. Door-kick only if **NoCivilianBehindDoor** (ray pre-check via peephole window marker).
- **Cautious:** Shots allowed if **WeaponDrawn** and **RefusesCompliance**; flashbang anytime; door-kick allowed.
- **Free:** No restrictions (still scored morally!).

**Gate Check:** `allowed = (target.threat_state.value >= current_roe.min_threat_to_fire)`

### 3.2 Threat & Compliance Model
- States: **Unarmed**, **WeaponHolstered**, **WeaponDrawn**, **AimingWeapon**, **Surrendered**, **Fleeing**.
- `Shout` tests compliance: `P(surrender) = base + distance_factor + flanked_bonus − ally_support − fear_penalty`.

### 3.3 Witness & Camera Model
- Viewers: **Civilian(w=1.0)**, **Press(w=1.5)**, **OfficerCam(w=0.8)**.
- Each viewer has **cone(fov, range)**; events are visible if raycast from viewer to event is clear and within cone.
- **Event Log Row:** `{t, event_type, actor, target, target_state, position, viewers:[ids]}`.

### 3.4 Legitimacy Scoring (per *visible* event)
| Event                                  | Strict | Cautious | Free | Notes |
|----------------------------------------|:-----:|:-------:|:----:|------|
| Fired at Unarmed target                | -20   | -15     | -10  | × sum(viewer weights) |
| Fired at Aiming target                 | +6    | +8      | +10  | × sum(viewer weights) |
| Flashbang with civilian in room        | -8    | -5      | -2   | |
| Shout → Surrender achieved             | +8    | +6      | +4   | |
| Cuffed surrendered suspect             | +5    | +5      | +5   | |
| Secured evidence (weapon/phone)        | +6    | +6      | +6   | |
| Door-kick that reveals armed suspect   | +3    | +2      | +1   | |
| Civilian injured (any cause)           | -25   | -25     | -25  | not mitigated |

> Final **Legitimacy = clamp(0–100, 50 + Σ (viewer_weighted_scores) / scale)`** with 50 as neutral baseline.

### 3.5 Evidence
- Tokens: **RecoveredGun**, **PhoneClip**.
- Each reduces penalties for “Fired at Aiming” disputes in AAR by 20% if the evidence links to the target (simple association by proximity at time of event).

---

## 4) Gameplay Flow

1. **Briefing (10s):** See map silhouette, objectives, starting ROE (Cautious).  
2. **Ingress:** Place operators at two entry points.  
3. **Action (pausable real-time):** Move, shout, kick doors, flashbang, fire, cuff, secure. Toggle ROE.  
4. **Extract:** Reach exit zone with all suspects neutralized & civilians safe.  
5. **AAR:** Timeline scrubber auto-highlights 4–6 events; shows who saw what; recomputes Legitimacy with witness weights; grade & rewards.

---

## 5) Controls (Slice)

- **WASD:** Move selected operator (hold to path-follow).  
- **1/2:** Select operator.  
- **Q/E:** Cycle actions; **Space:** Pause/Unpause.  
- **R:** Toggle ROE (Strict ↔ Cautious ↔ Free).  
- **F:** Flashbang (if equipped).  
- **K:** Kick door.  
- **V:** Shout (Comply).  
- **C:** Cuff.  
- **X:** Secure evidence (context).  
- **Left Click:** Confirm action / target.  
- **Tab (in AAR):** Next key frame. **Shift+Tab:** Previous.

---

## 6) Technical Plan (Pygame)

**Resolution:** 1280×720; **Tile Size:** 32px; **Tick:** 60 FPS (dt-based).  
**Folders:**  
```
/game
  main.py
  /core    # loop, clock, input, camera
  /ecs     # components & systems
  /maps    # CSV tilemaps + door/cover markers
  /data    # json: actors, actions, roe, scores
  /ui      # widgets (slider, meters, timeline)
  /assets  # simple shapes/fonts/placeholders
```
**Key Systems**
- **VisionSystem:** precompute visibility (cone raycasts grid).  
- **ActionSystem:** validates via ROE gate, enqueues atomic steps (aim, resolve).  
- **WitnessSystem:** resolves viewers per event.  
- **LoggerSystem:** appends Event Log rows; supports playback (AAR).  
- **AARSystem:** picks key frames (salience: high penalty/bonus), re-scores.  
- **UISystem:** draws ROE slider, Legitimacy meter, tooltips, AAR timeline.

**Data Schemas (JSON)**
```json
// roe.json
{
  "Strict": {"min_threat_to_fire": 3, "flashbang_requires_shout": true},
  "Cautious": {"min_threat_to_fire": 2, "flashbang_requires_shout": false},
  "Free": {"min_threat_to_fire": 0, "flashbang_requires_shout": false}
}
```
```json
// actors.json (slice excerpt)
{
  "operator": {"hp": 100, "move_speed": 120, "fov_deg": 70, "fov_range": 220},
  "suspect":  {"hp": 80,  "move_speed": 100, "fov_deg": 65, "fov_range": 200},
  "civilian": {"hp": 60,  "move_speed": 90,  "fov_deg": 80, "fov_range": 180},
  "press":    {"hp": 60,  "move_speed": 90,  "fov_deg": 100, "fov_range": 240}
}
```

---

## 7) Tuning Defaults (Slice)

- **Compliance (Shout):** base 35%, +15% if within 3 tiles, +10% if flanked, −15% per armed ally in room.  
- **Surrender → Flee threshold:** If ally_count ≥2 and no operator in cone for 2s → 40% flee each second.  
- **Flashbang:** 1.2s stun; reduces compliance penalty by 20% for the next **Shout**.  
- **Legitimacy scale:** divide Σ by 10 before adding to baseline 50.

---

## 8) Acceptance Tests (Horizontal Slice)

- [ ] **ROE gate works:** Attempting to fire in **Strict** at **Unarmed** target is blocked with tooltip.  
- [ ] **Witness cones:** An event in LOS of press observer marks the event with `viewer_ids` including press.  
- [ ] **Event log:** Contains ≥ 50% of meaningful actions with correct fields (time-ordered).  
- [ ] **AAR recompute:** Changing ROE during play affects post-mission Legitimacy scoring outcomes.  
- [ ] **Evidence link:** Securing weapon near suspect reduces penalty for prior justified fire by 20%.  
- [ ] **End states:** Win/Partial/Fail paths trigger appropriate summary text and restart option.

---

## 9) Implementation Checklists (Task Breakdown)

### 9.1 Project & Infrastructure
- [ ] Create repo, virtualenv, requirements (`pygame>=2.5`).
- [ ] Main loop with `dt`, pause toggling, scene stack (Game, AAR).
- [ ] Input mapper (bind actions & UI hotkeys).

### 9.2 Map & Navigation
- [ ] Load CSV tilemap; mark wall/door/cover tiles.
- [ ] A* or simple greedy-steer to clicked tile with collision.
- [ ] Door object with states (closed, open, kicked).

### 9.3 Entities & Components
- [ ] `Transform`, `Hitbox`, `Team`, `FOV`, `AIState`, `Inventory`, `Camera` (for bodycams), `RoleTag`.
- [ ] Spawner for operators, suspects, civilians, press.

### 9.4 Vision & Witnessing
- [ ] Cone raycast per viewer each tick with cached occluders.
- [ ] Event visibility query `visible_viewers(event_pos)` → ids & weights.

### 9.5 Actions & ROE
- [ ] Implement actions: Move, Aim, Shout, Fire (hitscan), KickDoor, Flashbang, Cuff, SecureEvidence.
- [ ] ROE slider UI; config in `roe.json`.
- [ ] ROE gate: pre-checks per action; deny with reason overlay.

### 9.6 AI Behavior (Slice)
- [ ] Suspect: idle → investigate noise → draw weapon → aim/shoot/flee logic.
- [ ] Civilian: wander → freeze → flee to safe tile if shots nearby.
- [ ] Press: wander route; avoids gunfire but keeps line-of-sight.

### 9.7 Event Logging & AAR
- [ ] `LoggerSystem.append(row)` on significant actions.
- [ ] Keyframe selection (top-|score| deltas or notable states).
- [ ] AAR scene: timeline scrubber, per-viewer overlays, final Legitimacy calc.

### 9.8 UI & Feedback
- [ ] ROE slider (R to cycle), Legitimacy meter (0–100), action bar, minimap.
- [ ] Tooltips for blocked actions with cause (e.g., “Strict ROE blocks Fire”).

### 9.9 Audio & Polish (Minimal)
- [ ] Footstep, shout, door kick, flashbang pop, single gunshot SFX (placeholders).
- [ ] Screen shake on breach, brief white flash for flashbang (alpha overlay).

### 9.10 Packaging
- [ ] Config file for tuning constants.
- [ ] One-click run script; README with controls.

---

## 10) Stretch Goals (Post-Slice)

- **Officer POV selection in AAR** (compare differing angles).  
- **Civil liability mini-summary** (fine/reward modifiers).  
- **No-knock warrant** variant (tighter ROE window).  
- **Stealth ingress** (lockpick + hold-to-commit).  
- **Campaign meta:** Legitimacy affects funding (gadgets, team size).

---

## 11) Risks & Mitigations

- **Too costly vision checks:** Cache visibility and update only when actors or doors move.  
- **Ambiguous scoring:** Keep scoring table visible in AAR; add “why” breakdown.  
- **Unfun ROE blocks:** Provide actionable tooltips and fast toggle; ensure at least one viable action under every mode.

---

## 12) Milestones (2–3 Evenings)

**Day 1:** Map+movement, ROE slider, Move/Shout/Fire, basic FOV, Logger skeleton.  
**Day 2:** Witness checks, AAR replayer & scoring, flashbang/door-kick/cuff/evidence, Legitimacy meter.  
**Day 3 (polish):** AI states, keyframe selection, sound/FX, acceptance tests pass.

---

## 13) Definition of Done (Slice)

- All acceptance tests pass.  
- Win/Fail/Partial endings reachable.  
- AAR shows at least 4 key frames with differing viewer sets.  
- Legitimacy score visibly changes with different tactics/ROE.  
- Code structured per folder plan with JSON-configured ROE and actors.

---

**End of Document**