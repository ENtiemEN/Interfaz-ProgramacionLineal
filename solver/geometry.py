import numpy as np
from .models import Problem

_EPS = 1e-9


def _satisfies_all(x, y, constraints) -> bool:
    for c in constraints:
        val = c.a * x + c.b * y
        if c.op == "<=" and val > c.rhs + _EPS:
            return False
        if c.op == ">=" and val < c.rhs - _EPS:
            return False
        if c.op == "=" and abs(val - c.rhs) > _EPS:
            return False
    if x < -_EPS or y < -_EPS:
        return False
    return True


def _intersect(a1, b1, r1, a2, b2, r2):
    det = a1 * b2 - a2 * b1
    if abs(det) < _EPS:
        return None
    x = (r1 * b2 - r2 * b1) / det
    y = (a1 * r2 - a2 * r1) / det
    return x, y


def feasible_vertices(problem: Problem, x_max: float = None, y_max: float = None) -> list:
    constraints = problem.constraints

    lines = [(c.a, c.b, c.rhs) for c in constraints]
    lines.append((1, 0, 0))  # x = 0
    lines.append((0, 1, 0))  # y = 0

    candidates = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            pt = _intersect(*lines[i], *lines[j])
            if pt is not None:
                candidates.append(pt)

    # Si hay límites de gráfico, añadir puntos en los bordes para regiones no acotadas
    if x_max is not None and y_max is not None:
        boundary_points = [
            (x_max, 0), (0, y_max), (x_max, y_max),
        ]
        for c in constraints:
            if abs(c.b) > _EPS:
                # intersección con x = x_max
                y_at_xmax = (c.rhs - c.a * x_max) / c.b
                candidates.append((x_max, y_at_xmax))
            if abs(c.a) > _EPS:
                # intersección con y = y_max
                x_at_ymax = (c.rhs - c.b * y_max) / c.a
                candidates.append((x_at_ymax, y_max))
        candidates.extend(boundary_points)

    vertices = [
        (round(x, 8), round(y, 8))
        for x, y in candidates
        if _satisfies_all(x, y, constraints)
    ]

    unique = []
    for v in vertices:
        if not any(abs(v[0] - u[0]) < _EPS and abs(v[1] - u[1]) < _EPS for u in unique):
            unique.append(v)

    if len(unique) < 2:
        return unique

    cx = sum(v[0] for v in unique) / len(unique)
    cy = sum(v[1] for v in unique) / len(unique)
    unique.sort(key=lambda v: np.arctan2(v[1] - cy, v[0] - cx))

    return unique
