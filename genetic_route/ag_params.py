from dataclasses import dataclass
from typing import Optional


@dataclass
class AGParams:
    pop_size: int = 150
    generations: int = 500
    mutation_rate: float = 0.02
    crossover_rate: float = 0.9
    elite_size: int = 20
    mutation_type: str = "swap"
    patience: int = 0
    min_improvement: float = 1.0
    seed: Optional[int] = None
    log_interval: int = 50
