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

## 9) Implementation & Development

**For detailed implementation planning and task breakdown, see [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)**

The development is organized into 7 phases:
- **Phase 0-1**: Core infrastructure and basic movement
- **Phase 2**: Vision and witness system  
- **Phase 3**: Actions and Rules of Engagement
- **Phase 4**: AI and mission logic
- **Phase 5**: After-Action Review system
- **Phase 6**: Audio, effects, and polish
- **Phase 7**: Testing and final integration

Each phase builds upon the previous one, with clear deliverables and acceptance criteria.

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

## 12) Development Timeline

**Target:** 2-3 weeks (evenings/weekends)  
**Approach:** 7 development phases with clear deliverables

**For detailed phase-by-phase breakdown, see [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)**

**Quick Overview:**
- **Week 1**: Core systems, movement, vision (Phases 0-2)
- **Week 2**: Actions, AI, mission logic (Phases 3-4)  
- **Week 3**: AAR, polish, testing (Phases 5-7)

---

## 13) Definition of Done (Slice)

- All acceptance tests pass.  
- Win/Fail/Partial endings reachable.  
- AAR shows at least 4 key frames with differing viewer sets.  
- Legitimacy score visibly changes with different tactics/ROE.  
- Code structured per folder plan with JSON-configured ROE and actors.

---

**End of Document**