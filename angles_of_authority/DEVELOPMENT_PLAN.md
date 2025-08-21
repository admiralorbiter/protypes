# Angles of Authority - Development Plan

**Project:** Top-down tactical breach & clear game with moral/legitimacy systems  
**Engine:** Pygame 2.x (Python 3.11+)  
**Scope:** Horizontal slice - 1 apartment, 2 operators, 2 suspects, 2 civilians, 1 press observer  
**Target Timeline:** 2-3 weeks (evenings/weekends)

---

## Phase 0: Project Setup & Infrastructure (Day 1 - 2-3 hours)

### 0.1 Environment Setup
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Install dependencies: `pip install pygame>=2.5`
- [ ] Create requirements.txt
- [ ] Set up project structure per folder plan
- [ ] Create main.py entry point

### 0.2 Project Structure
```
angles_of_authority/
├── main.py              # Entry point
├── core/                # Core systems
│   ├── __init__.py
│   ├── game_loop.py     # Main game loop, clock, pause
│   ├── input_handler.py # Input mapping and processing
│   ├── camera.py        # Viewport management
│   └── scene_manager.py # Scene stack (Game, AAR)
├── ecs/                 # Entity Component System
│   ├── __init__.py
│   ├── entity.py        # Entity base class
│   ├── component.py     # Component base classes
│   └── system.py        # System base classes
├── data/                # Configuration files
│   ├── roe.json         # Rules of Engagement config
│   ├── actors.json      # Actor stats and properties
│   ├── actions.json     # Action definitions
│   └── scoring.json     # Legitimacy scoring rules
├── maps/                # Level data
│   ├── apartment.csv    # Tilemap
│   ├── spawns.json      # Entity spawn points
│   └── doors.json       # Door locations and states
├── ui/                  # User interface
│   ├── __init__.py
│   ├── widgets.py       # UI components
│   ├── hud.py          # In-game HUD
│   └── aar_ui.py       # After-Action Review interface
├── assets/              # Game assets
│   ├── fonts/           # Font files
│   ├── sounds/          # Sound effects
│   └── sprites/         # Simple shapes/placeholders
└── tests/               # Test files
    └── __init__.py
```

### 0.3 Core Infrastructure
- [ ] Implement basic game loop with delta time
- [ ] Create scene management system
- [ ] Set up input handling framework
- [ ] Create basic entity and component system

---

## Phase 1: Core Systems & Basic Movement (Days 2-3 - 4-6 hours)

### 1.1 Entity Component System Foundation
- [ ] Implement Transform component (position, rotation)
- [ ] Implement Hitbox component (collision detection)
- [ ] Implement Team component (operator, suspect, civilian, press)
- [ ] Implement basic System class for processing components

### 1.2 Map System
- [ ] Create tilemap loader for CSV files
- [ ] Implement basic collision detection
- [ ] Create door system with states (closed, open, kicked)
- [ ] Add cover objects and spawn points

### 1.3 Basic Movement & Controls
- [ ] Implement operator movement with WASD
- [ ] Add operator selection (1/2 keys)
- [ ] Create basic pathfinding (simple A* or greedy steering)
- [ ] Add collision detection for walls and doors
- [ ] Implement pause/unpause functionality (Space)

### 1.4 Basic Rendering
- [ ] Create simple shape renderer for entities
- [ ] Implement basic camera system
- [ ] Add minimap rendering
- [ ] Create simple UI framework

---

## Phase 2: Vision & Witness System (Days 4-5 - 4-6 hours)

### 2.1 Field of View System
- [ ] Implement cone-based FOV calculation
- [ ] Add raycasting for line-of-sight
- [ ] Create FOV component with configurable parameters
- [ ] Optimize with visibility caching

### 2.2 Witness System
- [ ] Implement witness detection for events
- [ ] Create viewer weight system (civilian=1.0, press=1.5, officer=0.8)
- [ ] Add bodycam system for operators
- [ ] Create event visibility querying

### 2.3 Event Logging
- [ ] Design event log data structure
- [ ] Implement LoggerSystem for recording events
- [ ] Add event replay capability for AAR
- [ ] Create keyframe selection system

---

## Phase 3: Actions & Rules of Engagement (Days 6-7 - 4-6 hours)

### 3.1 Action System
- [ ] Implement basic actions: Move, Aim, Shout, Fire
- [ ] Add advanced actions: Kick Door, Flashbang, Cuff, Secure Evidence
- [ ] Create action validation system
- [ ] Implement action queuing for real-time gameplay

### 3.2 Rules of Engagement
- [ ] Create ROE configuration system
- [ ] Implement ROE slider UI (R key to cycle)
- [ ] Add ROE validation gates for actions
- [ ] Create tooltip system for blocked actions

### 3.3 Threat & Compliance Model
- [ ] Implement suspect threat states
- [ ] Add compliance calculation for Shout action
- [ ] Create surrender and fleeing logic
- [ ] Implement weapon drawing and aiming mechanics

---

## Phase 4: AI & Gameplay Logic (Days 8-9 - 4-6 hours)

### 4.1 AI Behavior System
- [ ] Implement suspect AI (idle → investigate → draw weapon → aim/shoot/flee)
- [ ] Add civilian AI (wander → freeze → flee)
- [ ] Create press AI (wander route, maintain line-of-sight)
- [ ] Implement basic decision trees for AI actions

### 4.2 Combat & Interaction
- [ ] Implement hitscan shooting system
- [ ] Add flashbang effects and stun mechanics
- [ ] Create door kicking and breach mechanics
- [ ] Implement evidence collection system

### 4.3 Mission Logic
- [ ] Create win/lose/partial condition checking
- [ ] Implement mission completion flow
- [ ] Add evidence linking system
- [ ] Create mission restart functionality

---

## Phase 5: After-Action Review & UI (Days 10-11 - 4-6 hours)

### 5.1 AAR System
- [ ] Implement timeline scrubber
- [ ] Create keyframe replay system
- [ ] Add witness perspective overlays
- [ ] Implement Legitimacy recalculation

### 5.2 Legitimacy Scoring
- [ ] Create scoring table implementation
- [ ] Add viewer-weighted score calculation
- [ ] Implement evidence-based penalty reduction
- [ ] Create final score display and grading

### 5.3 UI Polish
- [ ] Complete HUD with Legitimacy meter
- [ ] Add action bar with hotkeys
- [ ] Implement tooltips and help system
- [ ] Create pause menu and settings

---

## Phase 6: Audio, Effects & Polish (Days 12-13 - 3-4 hours)

### 6.1 Audio System
- [ ] Add basic sound effects (footsteps, shouts, gunshots)
- [ ] Implement flashbang audio and visual effects
- [ ] Add door kick and breach sounds
- [ ] Create simple audio manager

### 6.2 Visual Effects
- [ ] Add screen shake for breaches
- [ ] Implement flashbang white flash overlay
- [ ] Create simple particle effects for impacts
- [ ] Add visual feedback for actions

### 6.3 Game Feel
- [ ] Tune movement speeds and responsiveness
- [ ] Balance AI behavior and timing
- [ ] Adjust scoring weights and thresholds
- [ ] Test and refine user experience

---

## Phase 7: Testing & Final Integration (Days 14-15 - 3-4 hours)

### 7.1 Acceptance Testing
- [ ] Test ROE gate functionality
- [ ] Verify witness system accuracy
- [ ] Test event logging and replay
- [ ] Validate AAR scoring recalculation
- [ ] Test evidence linking system
- [ ] Verify all win/lose/partial conditions

### 7.2 Bug Fixes & Polish
- [ ] Fix any discovered issues
- [ ] Optimize performance bottlenecks
- [ ] Add final UI polish
- [ ] Create demo scenario

### 7.3 Documentation & Packaging
- [ ] Update README with controls and setup
- [ ] Create one-click run script
- [ ] Document configuration options
- [ ] Prepare for potential distribution

---

## Development Priorities & Dependencies

### Critical Path (Must Complete First)
1. **Phase 0-1**: Core infrastructure and basic movement
2. **Phase 2**: Vision system (required for witness mechanics)
3. **Phase 3**: Actions and ROE (core gameplay)
4. **Phase 4**: AI and mission logic (completable gameplay)

### Secondary Path (Can Be Simplified Initially)
1. **Phase 5**: AAR system (can start with basic replay)
2. **Phase 6**: Audio and effects (can use placeholders)
3. **Phase 7**: Polish and optimization

### Risk Mitigation
- **Start Simple**: Begin with basic shapes and simple mechanics
- **Test Early**: Validate core systems before adding complexity
- **Modular Design**: Keep systems loosely coupled for easier debugging
- **Incremental Features**: Add one major system at a time

---

## Success Criteria

### Minimum Viable Product (End of Phase 4)
- [ ] Basic movement and controls work
- [ ] Vision and witness system functional
- [ ] Actions and ROE gates working
- [ ] Simple AI behavior implemented
- [ ] Mission can be completed

### Complete Slice (End of Phase 7)
- [ ] All acceptance tests pass
- [ ] AAR system fully functional
- [ ] Legitimacy scoring accurate
- [ ] Audio and visual effects implemented
- [ ] Game feels polished and responsive

---

## Getting Started

1. **Clone/Setup**: Ensure you have Python 3.11+ and Pygame 2.5+
2. **Phase 0**: Set up project structure and basic infrastructure
3. **Phase 1**: Implement basic movement and map system
4. **Iterate**: Test each phase before moving to the next
5. **Document**: Keep notes on any design changes or discoveries

This plan provides a structured approach to building your game while maintaining focus on the core mechanics that make it unique. Each phase builds upon the previous one, ensuring a solid foundation for the more complex systems.
