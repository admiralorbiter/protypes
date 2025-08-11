# Ideas

## Board Games & Game Theory (Interactive + Teach-y)
- **Can’t Stop Coach**: Monte-Carlo/UCT bot that recommends “press or park” in real time. Add sliders for risk tolerance and visualize bust odds per column.
- **Iterated Prisoner’s Dilemma Arena**: Pit classic strategies (Tit-for-Tat, Grim, WSLS) plus user-coded bots; show replicator dynamics over time.
- **Auction Playground**: Run English, Dutch, first-price, second-price auctions; compare revenue/efficiency with human inputs or simulated bidders.
- **Matching Markets Lab**: Demo school choice (Gale–Shapley) + priorities + diversity constraints; let users see who benefits/loses under rule changes.
- **Signaling Game Explorer**: Interactive tree for education-as-signal vs. human-capital models; toggle costs and pool/separate equilibria highlight.
- **Public Goods + Punishment**: Slider for contribution, probability of punishment, and see tragedy-of-the-commons vs. cooperation.
- **Colonel Blotto Visualizer**: Allocate troops across fronts; heatmap of best responses and mixed strategy intuition.
- **Hotelling’s Beach**: Firms choose locations on a line/city grid; add transportation cost and “move” button to converge to equilibrium.

## Education Policy & Budgets
- **District Budget Sandbox**: Simulate cuts across line items (staffing, arts, buses); output class size, achievement proxy, and equity metrics.
- **Teacher Labor Pipeline**: Model attrition, certification lag, pay shocks; show steady-state teacher shortages under different policies.
- **Course Scheduling Pressure Test**: Integer program to assign teachers/rooms given constraints; visualize infeasibility when budgets shrink.
- **Intervention RCT Simulator**: Power, clustering, and peeking; show false-positive risks and what sample you actually need.
- **Attendance → Outcomes Microsim**: Link chronic absenteeism to grade progression; test incentives vs. transportation fixes.
- **“Adjunctification” Explorer (Higher Ed)**: Slider for tenure-track share, funding, research output; see long-run impacts.
- **School Consolidation Tradeoffs**: Bus time vs. per-pupil admin cost; map-based travel time changes when closing a school.

## Tech Talent Gap & Workforce (P-TECH/Bridge Programs)
- **4,000-Openings Pipeline ABM**: Agents = students/employers; knobs for internship slots, bootcamps, and employer screening noise.
- **Skill Taxonomy Recommender**: Map course syllabi → O*NET skills; show “distance” from a role and minimal upskilling path.
- **Apprenticeship Matching**: Stable matching with employer capacity + soft preferences; simulate diversity and retention effects.
- **Stackable Credentials ROI**: Cohort sim of time-to-job and wage lift vs. direct-to-work.
- **Career Mobility Markov Model**: Transition matrix between roles; test how an entry program shifts 5-year outcomes.

## Behavioral Econ Mini-Sims
- **Newsvendor Game**: Demand uncertainty + risk aversion; show service level and cost tradeoffs.
- **Peak-End Grading Bias**: Generate synthetic grading sequences; quantify bias and train a debiasing rule.
- **Schelling Segregation on Graphs**: Local preferences on friendship networks instead of grids.
- **Nudges A/B Pitfalls**: Sequential testing with optional stopping; show inflated “wins.”
- **Prospect Theory Playground**: Loss aversion/weighting sliders; compare to expected value choices.

## Flight Sim & Control (MSFS Side-Quest)
- **Crosswind Landing Trainer**: 2D physics + joystick input capture; visualize flare timing, sink rate, and runway remaining.
- **Energy Management Tutor**: Glide slope + throttle lag sim; color feedback when you’re high/fast vs. low/slow.
- **Stabilized Approach Checker**: Upload telemetry → auto-flag “stable at 500 ft?” with suggestions.
- **IMSAFE + Weather Risk Tool**: Pre-flight human-factors checklist that quantifies go/no-go score.

## AI for Games & Stealth (Teardown Mod Adjacent)
- **Guard Patrol Optimizer**: Graph-based route generation with coverage guarantees; sliders for FOV/hearing radius.
- **Noise Propagation Demo**: 2D map where sound rays bounce/attenuate; teaches stealth mechanics.
- **POMDP Sneak-by-Guard**: Belief-state visualization for line-of-sight + occlusion.
- **Level-of-Alertness State Machine**: Tune thresholds and hysteresis; export JSON for your mod.

## Health/Biotech (Lightweight, Policy-ish)
- **Innovation Diffusion of CRISPR Therapies**: Bass model with reimbursement knobs; view adoption curves under payer policies.
- **Cost-Effectiveness Toy Model**: QALY vs. cost sliders for a hypothetical islet therapy; tornado plot auto-generated.
- **Clinical Trial Enrollment Funnel**: Simulate inclusion criteria strictness vs. recruitment time.

## Methods & Measurement Teaching Tools
- **Difference-in-Differences Gap Plotter**: Parallel trends violations generator; placebo tests.
- **Regression Discontinuity Builder**: Choose running variable and bandwidth; see sensitivity graphs.
- **Test-Score Reliability Lab**: Cronbach’s alpha vs. test length; show SEM and pass/fail instability.
- **Fairness in Algorithms**: Demo equalized odds vs. demographic parity tradeoffs on a toy admissions dataset.
- **Network Centrality Classroom**: Build student interaction graphs; find influencers for peer-tutoring interventions.

## Data-Lite Mini Research Questions
- Do “soft prerequisites” in course catalogs reduce enrollment diversity? (Scrape a few catalogs; logistic models.)
- How much does bus route consolidation increase earliest pickup times? (OpenStreetMap + simple routing.)
- Which auction format do novices overbid in the most? (Your auction playground + small user study.)
- Does explaining bust odds in push-your-luck games reduce risk taking? (Can’t Stop Coach + randomized UI hints.)
- Are attendance improvements or schedule tweaks more cost-effective for raising credit accumulation? (Toy cost model + sensitivity.)
