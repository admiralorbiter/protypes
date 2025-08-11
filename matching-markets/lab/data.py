from __future__ import annotations
import random
from typing import List, Tuple, Dict, Set
from .model import Student, College, World

US_STATES = ['CA','NY','TX','VA','MA','IL','FL','WA','PA','OH']

def _rand_bool(p: float, rng: random.Random) -> bool:
    return rng.random() < p

def _clip(x, a, b):
    return max(a, min(b, x))

def generate_students(N: int, rng: random.Random) -> List[Student]:
    students = []
    for sid in range(N):
        state = rng.choice(US_STATES)
        income_q = rng.choices([1,2,3,4,5], weights=[0.12,0.18,0.28,0.24,0.18])[0]
        first_gen = _rand_bool(0.28 if income_q <= 3 else 0.12, rng)
        pell = _rand_bool(0.32 if income_q <= 3 else 0.08, rng)
        rural = _rand_bool(0.25 if state in ['TX','OH','PA','FL'] else 0.10, rng)
        # GPA ~ N(3.2, 0.5), bounded [1.8, 4.0]; correlate with income modestly
        gpa = _clip(rng.gauss(3.2 + 0.08*(income_q-3), 0.4), 1.8, 4.0)
        rigor = _clip(rng.random()*0.7 + 0.2 + 0.05*(income_q-3), 0.0, 1.0)
        # Test availability depends on school context/income
        took_test = _rand_bool(0.65 + 0.07*(income_q-3), rng)
        test_score = None
        if took_test:
            base = 1050 + 60*(income_q-3)
            test_score = int(_clip(rng.gauss(base, 120), 400, 1600))
        # HS context (school quality) correlated with income
        hs_context = _clip(rng.gauss(0.08*(income_q-3), 0.4), -1.0, 1.0)
        students.append(Student(
            sid=sid, gpa=gpa, rigor=rigor, test_score=test_score, hs_context=hs_context,
            income_quintile=income_q, first_gen=first_gen, pell=pell, rural=rural,
            state=state, preferences=[]
        ))
    return students

def generate_colleges(M: int, rng: random.Random) -> List[College]:
    colleges = []
    # Split roughly half public, half private
    pub_count = M//2
    for cid in range(M):
        is_public = (cid < pub_count)
        state = rng.choice(US_STATES)
        capacity = rng.randint(220, 520) if is_public else rng.randint(180, 420)
        name = (state + (" State" if is_public else " College") + f" #{cid+1}")
        # defaults
        test_policy = "optional"
        legacy_enabled = (not is_public)
        reserve_in_state = 0.7 if is_public else 0.0
        colleges.append(College(
            cid=cid, name=name, state=state, is_public=is_public, capacity=capacity,
            test_policy=test_policy, legacy_enabled=legacy_enabled, reserve_in_state=reserve_in_state
        ))
    return colleges

def assign_legacy(world: World, rng: random.Random, private_fraction: float = 0.06):
    # A small share of students are legacy for one random private college
    legacy_map: Dict[int, Set[int]] = {c.cid: set() for c in world.colleges if not c.is_public}
    private_ids = [c.cid for c in world.colleges if not c.is_public]
    for s in world.students:
        if rng.random() < private_fraction:
            cid = rng.choice(private_ids)
            legacy_map.setdefault(cid, set()).add(s.sid)
    world.legacy_map = legacy_map

def build_preferences(world: World, rng: random.Random, K: int = 8):
    # Students prefer in-state somewhat; and 'prestige' index
    prestige: Dict[int, float] = {}
    for c in world.colleges:
        # simple proxy: private colleges slightly more prestigious on average
        prestige[c.cid] = (1.0 if not c.is_public else 0.8) + rng.random()*0.4
    for s in world.students:
        # Fit score = prestige + in-state bonus + noise, plus match to student's income (aspiration)
        scores = []
        for c in world.colleges:
            in_state_bonus = 0.35 if (s.state == c.state and c.is_public) else 0.0
            aspiration = 0.1 * (s.income_quintile - 3)  # higher-income slightly tilt to prestige
            noise = rng.random()*0.3
            score = prestige[c.cid] + in_state_bonus + aspiration + noise
            scores.append((score, c.cid))
        scores.sort(reverse=True)
        s.preferences = [cid for _, cid in scores[:K]]

def generate_world(N: int = 8000, M: int = 24, seed: int = 42) -> World:
    rng = random.Random(seed)
    students = generate_students(N, rng)
    colleges = generate_colleges(M, rng)
    world = World(students=students, colleges=colleges)
    world.index()
    assign_legacy(world, rng)
    build_preferences(world, rng)
    return world
