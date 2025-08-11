from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Set, List, Tuple, Optional
from .constants import COLUMN_HEIGHTS, COLUMNS

@dataclass
class PlayerState:
    permanent_pos: Dict[int, int] = field(default_factory=lambda: {c: 0 for c in COLUMNS})
    claimed: Set[int] = field(default_factory=set)

    def copy(self) -> 'PlayerState':
        return PlayerState(permanent_pos=dict(self.permanent_pos), claimed=set(self.claimed))

@dataclass
class TurnState:
    active_runners: Dict[int, int] = field(default_factory=dict)  # absolute step positions
    last_roll: Optional[Tuple[int, int, int, int]] = None

    @property
    def free_runners(self) -> int:
        return 3 - len(self.active_runners)

    def copy(self) -> 'TurnState':
        return TurnState(active_runners=dict(self.active_runners), last_roll=self.last_roll)

@dataclass
class GameState:
    players: List[PlayerState]
    claimed_by: Dict[int, Optional[int]] = field(default_factory=lambda: {c: None for c in COLUMNS})
    current: int = 0
    num_players: int = 2
    winner: Optional[int] = None
    turn: TurnState = field(default_factory=TurnState)

    def copy(self) -> 'GameState':
        return GameState(
            players=[p.copy() for p in self.players],
            claimed_by=dict(self.claimed_by),
            current=self.current,
            num_players=self.num_players,
            winner=self.winner,
            turn=self.turn.copy(),
        )

    def to_dict(self) -> dict:
        return {
            "players": [
                {"permanent_pos": dict(p.permanent_pos), "claimed": sorted(list(p.claimed))}
                for p in self.players
            ],
            "claimed_by": {str(c): self.claimed_by[c] for c in COLUMNS},
            "current": self.current,
            "num_players": self.num_players,
            "winner": self.winner,
            "turn": {
                "active_runners": {str(c): step for c, step in self.turn.active_runners.items()},
                "free_runners": self.turn.free_runners,
                "last_roll": list(self.turn.last_roll) if self.turn.last_roll else None
            }
        }

def new_game(num_players: int = 2) -> GameState:
    players = [PlayerState() for _ in range(num_players)]
    return GameState(players=players, num_players=num_players)
