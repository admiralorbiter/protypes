from dataclasses import dataclass, field
import numpy as np

GRID_W, GRID_H = 48, 36  # Small, readable
TILE = 16

@dataclass
class GameState:
    # Time
    seconds_per_month: float = 2.0
    month_time: float = 0.0
    month: int = 0
    year: int = 1
    # Economy/politics
    budget: float = 1_000_000.0
    legitimacy: float = 60.0  # 0-100
    majority: str = "Neutral"
    # Grids
    zone: np.ndarray = field(default_factory=lambda: np.zeros((GRID_H, GRID_W), dtype=np.int32))
    btype: np.ndarray = field(default_factory=lambda: np.zeros((GRID_H, GRID_W), dtype=np.int32))
    pop: np.ndarray = field(default_factory=lambda: np.random.poisson(3, (GRID_H, GRID_W)).astype('int32'))
    jobs: np.ndarray = field(default_factory=lambda: np.random.poisson(2, (GRID_H, GRID_W)).astype('int32'))
    district: np.ndarray = field(default_factory=lambda: np.zeros((GRID_H, GRID_W), dtype=np.int32))
    # Externality fields
    N: np.ndarray = field(default_factory=lambda: np.zeros((GRID_H, GRID_W), dtype=np.float32))
    P: np.ndarray = field(default_factory=lambda: np.zeros((GRID_H, GRID_W), dtype=np.float32))
    T: np.ndarray = field(default_factory=lambda: np.zeros((GRID_H, GRID_W), dtype=np.float32))
    # Toggles
    show_field: int = 1  # 1:N, 2:P, 3:T
    # RNG
    seed: int = 42

    def __post_init__(self):
        np.random.seed(self.seed)
        # Seed simple downtown industry
        self.btype[14:20, 22:28] = 2  # factories
        self.btype[10:15, 10:18] = 1  # housing
        self.district[:, :GRID_W//2] = 1
        self.district[:, GRID_W//2:] = 2
