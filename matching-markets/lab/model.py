from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple

@dataclass
class Student:
    sid: int
    gpa: float
    rigor: float
    test_score: Optional[int]  # SAT-equivalent 400..1600, or None
    hs_context: float  # -1..+1
    income_quintile: int  # 1..5
    first_gen: bool
    pell: bool
    rural: bool
    state: str
    preferences: List[int]  # ranked list of college ids

@dataclass
class College:
    cid: int
    name: str
    state: str
    is_public: bool
    capacity: int
    # policy
    test_policy: str = "optional"  # 'optional' or 'required'
    legacy_enabled: bool = True
    legacy_weight: float = 0.05
    # reserves (shares 0..1)
    reserve_first_gen: float = 0.0
    reserve_pell: float = 0.0
    reserve_rural: float = 0.0
    reserve_in_state: float = 0.0  # for publics

    # scoring weights
    w_gpa: float = 0.55
    w_test: float = 0.25
    w_rigor: float = 0.15
    w_context: float = 0.05

@dataclass
class World:
    students: List[Student]
    colleges: List[College]
    # Map college -> set of legacy student ids (college-specific)
    legacy_map: Dict[int, Set[int]] = field(default_factory=dict)
    # Quick index
    colleges_by_id: Dict[int, College] = field(default_factory=dict)

    def index(self):
        self.colleges_by_id = {c.cid: c for c in self.colleges}

@dataclass
class Scenario:
    # Global toggles (can be refined per-college in future)
    legacy_on_private: bool = True
    test_required_private_elite: bool = False
    reserve_first_gen: float = 0.0
    reserve_rural: float = 0.0
    reserve_pell: float = 0.0
    public_in_state_share: float = 0.7
    # Number of 'elite' private colleges to set test-required under the wave
    num_private_elites_test_required: int = 4
