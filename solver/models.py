from dataclasses import dataclass, field
import numpy as np


@dataclass
class Constraint:
    a: float
    b: float
    op: str       # "<=", ">=", "="
    rhs: float


@dataclass
class Problem:
    cx: float
    cy: float
    objective: str           # "maximize" | "minimize"
    constraints: list
    description: str = ""


@dataclass
class SimplexStep:
    iteration: int
    tableau: np.ndarray
    basis: list
    col_labels: list
    entering: str | None = None
    leaving: str | None = None
    pivot_row: int | None = None
    pivot_col: int | None = None
    is_decisive: bool = False


@dataclass
class Solution:
    status: str              # "optimal" | "infeasible" | "unbounded"
    x: float | None = None
    y: float | None = None
    value: float | None = None
    steps: list = field(default_factory=list)
    feasible_vertices: list = field(default_factory=list)
