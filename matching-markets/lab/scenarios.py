from __future__ import annotations
from typing import List, Dict
import random
from .model import World, Scenario

def apply_scenario(world: World, scenario: Scenario, seed: int = 0):
    rng = random.Random(seed)
    # Reset dynamic policy fields per college from scenario defaults
    # 1) Legacy
    for c in world.colleges:
        if c.is_public:
            c.legacy_enabled = False
        else:
            c.legacy_enabled = scenario.legacy_on_private

    # 2) Test policy
    # Start with all optional
    for c in world.colleges:
        c.test_policy = "optional"
    if scenario.test_required_private_elite:
        # Mark top-N private colleges (by capacity as proxy for selectivity? here random) as test-required
        private = [c for c in world.colleges if not c.is_public]
        rng.shuffle(private)
        elites = private[:scenario.num_private_elites_test_required]
        for c in elites:
            c.test_policy = "required"

    # 3) Reserves
    for c in world.colleges:
        if c.is_public:
            c.reserve_in_state = scenario.public_in_state_share
        c.reserve_first_gen = scenario.reserve_first_gen
        c.reserve_rural = scenario.reserve_rural
        c.reserve_pell = scenario.reserve_pell
