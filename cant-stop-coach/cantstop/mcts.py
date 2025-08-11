from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List
import math, random

from .constants import COLUMN_HEIGHTS, COLUMNS
from .state import GameState
from .engine import roll_dice, legal_pairings, apply_pairing, compute_turn_gain, finished_columns_this_turn, stop_and_bank
from .odds import bust_prob

# Risk utilities
def utility(gain_steps: float, finished_cols: List[int], risk: str = "neutral") -> float:
    # Finish bonus by rarity (outer columns more valuable)
    finish_bonus = 0.0
    for c in finished_cols:
        if c in (2,12):
            finish_bonus += 4.0
        elif c in (3,11):
            finish_bonus += 3.0
        elif c in (4,10):
            finish_bonus += 2.0
        elif c in (5,9):
            finish_bonus += 1.5
        elif c in (6,8):
            finish_bonus += 1.0
        else: # 7
            finish_bonus += 1.0
    base = gain_steps + finish_bonus
    if risk == "averse":
        return math.sqrt(max(0.0, base))
    elif risk == "seeking":
        return base * base
    else:
        return base

@dataclass
class Node:
    state: GameState
    node_type: str  # 'decision', 'chance', 'pairing'
    parent: Optional['Node'] = None
    action_from_parent: Optional[Tuple] = None
    N: int = 0
    W: float = 0.0
    children: Dict[Tuple, 'Node'] = field(default_factory=dict)
    roll_cache: List[Tuple[int,int,int,int]] = field(default_factory=list)  # for chance nodes

def is_terminal_turn(state: GameState) -> bool:
    # Terminal for the *turn* occurs when we choose to stop (handled in simulate),
    # or when a bust would occur (if no legal pairings after a roll).
    return False  # Non-absorbing; handled explicitly

def uct_select(node: Node, c: float = 1.0) -> Tuple:
    best, best_score = None, -1e9
    for action, child in node.children.items():
        q = 0.0 if child.N == 0 else (child.W / child.N)
        u = c * math.sqrt(math.log(max(1, node.N)) / (1 + child.N))
        score = q + u
        if score > best_score:
            best_score, best = score, action
    return best

def expand_decision(node: Node):
    # Actions at decision node: 'STOP' or 'ROLL'
    if ('STOP',) not in node.children:
        # Create a terminal-ish child representing choosing to stop now
        s2 = node.state.copy()
        child_stop = Node(state=s2, node_type='terminal_stop', parent=node, action_from_parent=('STOP',))
        node.children[('STOP',)] = child_stop
    if ('ROLL',) not in node.children:
        s3 = node.state.copy()
        child_roll = Node(state=s3, node_type='chance', parent=node, action_from_parent=('ROLL',))
        node.children[('ROLL',)] = child_roll

def expand_chance(node: Node, rng: random.Random):
    # Sample a new roll and create a pairing-choice node, or a bust terminal if no legal pairings
    roll = roll_dice(rng)
    node.roll_cache.append(roll)
    s2 = node.state.copy()
    s2.turn.last_roll = roll
    legals = legal_pairings(s2, roll)
    if not legals:
        child = Node(state=s2, node_type='terminal_bust', parent=node, action_from_parent=('BUST', roll))
        node.children[(roll, 'BUST')] = child
    else:
        # 'pairing' node where actions are the legal pairings
        child = Node(state=s2, node_type='pairing', parent=node, action_from_parent=('ROLL_RESULT', roll))
        # bootstrap children as empty; we'll add pairing children lazily in simulate
        node.children[(roll,)] = child

def expand_pairing(node: Node):
    roll = node.state.turn.last_roll
    legals = legal_pairings(node.state, roll)
    for p in legals:
        if ('PAIR', p) not in node.children:
            s2 = node.state.copy()
            apply_pairing(s2, p)
            child = Node(state=s2, node_type='decision', parent=node, action_from_parent=('PAIR', p))
            node.children[('PAIR', p)] = child

def simulate(node: Node, rng: random.Random, risk: str, max_depth: int = 200) -> float:
    depth = 0
    cur = node
    while depth < max_depth:
        depth += 1
        if cur.node_type == 'terminal_bust':
            # Bust => 0 utility (lost all turn gains)
            reward = 0.0
            backpropagate(cur, reward)
            return reward
        if cur.node_type == 'terminal_stop':
            # Stopping now: compute utility of what is already gained
            gain = compute_turn_gain(cur.state)
            fins = finished_columns_this_turn(cur.state)
            reward = utility(gain, fins, risk)
            backpropagate(cur, reward)
            return reward

        if cur.node_type == 'decision':
            # Expand both options if not yet
            if not cur.children:
                expand_decision(cur)
            # UCT select between STOP and ROLL
            action = uct_select(cur, c=1.0)
            child = cur.children[action]
            if action == ('STOP',):
                # Convert to terminal-stop by banking (for downstream consistency)
                # Use a copy to not advance the real game yet
                s2 = child.state.copy()
                # Stopping would bank; we don't advance turn to next player in MCTS
                # but we evaluate current turn gains at this point.
                # The terminal_stop node already handles utility; simply move cursor there.
                cur = child
                continue
            else:
                # ROLL: go to chance node
                cur = child
                continue

        if cur.node_type == 'chance':
            # Chance: sample a roll and create downstream node lazily
            expand_chance(cur, rng)
            # Pick the just-sampled outcome to descend
            # Prefer the newest child to avoid bias
            action = list(cur.children.keys())[-1]
            cur = cur.children[action]
            continue

        if cur.node_type == 'pairing':
            # Ensure pairing children exist
            if not cur.children:
                expand_pairing(cur)
            # Select a pairing with UCT
            action = uct_select(cur, c=1.0)
            cur = cur.children[action]
            continue

    # Depth cutoff: treat as stop now
    gain = compute_turn_gain(cur.state)
    fins = finished_columns_this_turn(cur.state)
    reward = utility(gain, fins, risk)
    backpropagate(cur, reward)
    return reward

def backpropagate(node: Node, reward: float):
    cur = node
    while cur is not None:
        cur.N += 1
        cur.W += reward
        cur = cur.parent

def recommend_press_or_park(state: GameState, iters: int = 2000, seed: int = 0, risk: str = "neutral"):
    rng = random.Random(seed)
    root = Node(state=state.copy(), node_type='decision')
    # Pre-create children so we can read Q-values afterwards
    expand_decision(root)

    for _ in range(iters):
        simulate(root, rng, risk)

    def q_of(action_key):
        child = root.children[action_key]
        return 0.0 if child.N == 0 else child.W / child.N

    q_stop = q_of(('STOP',))
    q_roll = q_of(('ROLL',))
    action = 'press' if q_roll > q_stop else 'park'
    # Also compute exact bust probability for UI
    p_bust = bust_prob(state.copy())

    return {
        "action": action,
        "q_stop": q_stop,
        "q_press": q_roll,
        "p_bust": p_bust
    }

def recommend_pairing_after_roll(state: GameState, roll: Tuple[int,int,int,int], iters: int = 2000, seed: int = 0, risk: str = "neutral"):
    rng = random.Random(seed)
    s2 = state.copy()
    s2.turn.last_roll = roll
    legals = legal_pairings(s2, roll)
    if not legals:
        return {"pairing": None, "note": "No legal pairings; bust."}
    root = Node(state=s2, node_type='pairing')
    expand_pairing(root)

    for _ in range(iters):
        simulate(root, rng, risk)

    # Choose child with highest Q
    best_p, best_q = None, -1e9
    for k, child in root.children.items():
        q = 0.0 if child.N == 0 else child.W / child.N
        if q > best_q:
            best_q = q
            best_p = k[1]  # ('PAIR', p)
    return {
        "pairing": best_p,
        "q": best_q
    }
