# Future Work — Matching Markets Lab

A roadmap for extending the proof-of-concept school choice / matching market demo.

---

## 1. Core Matching Logic

- [ ] **Algorithm Options**
  - [ ] Implement both student-proposing and school-proposing Gale–Shapley
  - [ ] Add Boston mechanism as alternative
  - [ ] Support tie-breaking rules (single lottery vs school-specific lotteries)

- [ ] **Priorities**
  - [ ] Sibling priority
  - [ ] Geographic priority (e.g., in-zone vs out-of-zone)
  - [ ] Program-specific priority (STEM, language immersion, etc.)

- [ ] **Diversity Constraints**
  - [ ] Capacity by demographic categories
  - [ ] Minimum/maximum proportions
  - [ ] Enforce via constrained matching or iterative repair

---

## 2. Data Model & Input

- [ ] **Flexible Data Upload**
  - [ ] CSV/Excel import for students, schools, and preferences
  - [ ] Random data generator for quick demos
  - [ ] Support reproducible seeds for testing

- [ ] **School Attributes**
  - [ ] Capacity
  - [ ] Priority categories
  - [ ] Demographic targets

- [ ] **Student Attributes**
  - [ ] Ranked preferences
  - [ ] Eligibility flags (special programs, geographic)
  - [ ] Demographics (for diversity constraints)

---

## 3. Simulation & Scenarios

- [ ] **Scenario Presets**
  - [ ] “No priorities” baseline
  - [ ] Geographic priority only
  - [ ] Diversity quotas enabled

- [ ] **Parameter Controls**
  - [ ] Sliders for school capacities
  - [ ] Toggle priorities on/off
  - [ ] Adjust % of students in each demographic

- [ ] **Batch Experiments**
  - [ ] Run same input through multiple algorithms
  - [ ] Compare efficiency, stability, and diversity metrics

---

## 4. Outputs & Visualization

- [ ] **Matching Table**
  - [ ] Student → assigned school
  - [ ] School → assigned students

- [ ] **Summary Statistics**
  - [ ] % of students assigned to 1st / 2nd / 3rd choice
  - [ ] Stability violations count (if any)
  - [ ] Diversity metrics vs. targets

- [ ] **Visualizations**
  - [ ] Bar chart of choice satisfaction
  - [ ] Map view of assignments (if geographic data provided)
  - [ ] Sankey diagram of preference flows

---

## 5. User Interface

- [ ] **Interactive Controls**
  - [ ] Drag-and-drop for reordering student preferences
  - [ ] Real-time re-run of matching on parameter changes

- [ ] **Comparison Mode**
  - [ ] Side-by-side results from two algorithms
  - [ ] Highlight differences in assignments

- [ ] **Explanatory Text**
  - [ ] Step-through animation of Gale–Shapley rounds
  - [ ] Tooltips for “Why this student got this school”

---

## 6. Learning & Exploration Mode

- [ ] **Teaching Mode**
  - [ ] Toggle to slower “turn-based” match to see proposals/rejections
  - [ ] Color-coded highlighting of active matches and pending proposals

- [ ] **What-If Analysis**
  - [ ] Change one student’s preferences and re-run
  - [ ] Change school capacities mid-process
  - [ ] Show how small changes ripple through matches

---

## 7. Technical Improvements

- [ ] **Performance**
  - [ ] Optimize matching for large inputs (10k+ students)
  - [ ] Add caching for repeated runs with small changes
  - [ ] Move core algorithm to a separate module for testability

- [ ] **Testing**
  - [ ] Unit tests for algorithm correctness
  - [ ] Regression tests for known edge cases (ties, over/under capacity)

- [ ] **Deployment**
  - [ ] Dockerize app
  - [ ] Deploy public demo (Heroku/Fly.io/Render)
  - [ ] Add dataset save/load endpoints

---

## 8. Extensions & Research Directions

- [ ] **Other Matching Markets**
  - [ ] Residency match (hospital ↔ med students)
  - [ ] College admissions with quotas
  - [ ] Labor market matching

- [ ] **Policy Experiments**
  - [ ] Vary diversity quota stringency
  - [ ] Study trade-offs between efficiency, stability, and diversity
  - [ ] Simulate manipulation incentives (strategic ranking)

---
