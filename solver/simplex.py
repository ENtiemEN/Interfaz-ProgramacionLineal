import numpy as np
from .models import Problem, Solution, SimplexStep

_EPS = 1e-9
M = 1e6  # Gran M


def solve(problem: Problem) -> Solution:
    from .geometry import feasible_vertices

    constraints = problem.constraints
    n_con = len(constraints)

    # Contar variables auxiliares
    slack_count = 0
    artificial_count = 0
    for c in constraints:
        if c.op == "<=":
            slack_count += 1
        elif c.op == ">=":
            slack_count += 1      # exceso (-)
            artificial_count += 1
        else:  # "="
            artificial_count += 1

    s_col_start = 2
    a_col_start = 2 + slack_count
    n_vars = 2 + slack_count + artificial_count

    col_labels = ["x", "y"]
    for i in range(slack_count):
        col_labels.append(f"s{i+1}")
    for i in range(artificial_count):
        col_labels.append(f"a{i+1}")
    col_labels.append("RHS")

    # Tableau: n_con filas de restricciones + 1 fila objetivo
    tableau = np.zeros((n_con + 1, n_vars + 1))
    basis = []

    s_ptr = 0
    a_ptr = 0

    for i, c in enumerate(constraints):
        tableau[i, 0] = c.a
        tableau[i, 1] = c.b
        tableau[i, -1] = c.rhs

        if c.op == "<=":
            col = s_col_start + s_ptr
            tableau[i, col] = 1.0
            basis.append(col_labels[col])
            s_ptr += 1
        elif c.op == ">=":
            e_col = s_col_start + s_ptr
            tableau[i, e_col] = -1.0
            s_ptr += 1
            a_col = a_col_start + a_ptr
            tableau[i, a_col] = 1.0
            basis.append(col_labels[a_col])
            a_ptr += 1
        else:  # "="
            a_col = a_col_start + a_ptr
            tableau[i, a_col] = 1.0
            basis.append(col_labels[a_col])
            a_ptr += 1

    # Fila objetivo: coeficientes originales
    sign = -1.0 if problem.objective == "maximize" else 1.0
    tableau[-1, 0] = sign * problem.cx
    tableau[-1, 1] = sign * problem.cy

    # Gran M: colocar M directamente en las columnas artificiales de la fila objetivo
    for a_idx in range(artificial_count):
        a_col = a_col_start + a_idx
        tableau[-1, a_col] = M

    # Eliminación inicial: poner en 0 las columnas de las variables básicas en la fila objetivo
    for i, b in enumerate(basis):
        b_col = col_labels.index(b)
        if abs(tableau[-1, b_col]) > _EPS:
            tableau[-1, :] -= tableau[-1, b_col] * tableau[i, :]

    steps = []
    iteration = 0
    MAX_ITER = 200

    while iteration < MAX_ITER:
        obj_row = tableau[-1, :-1]

        if np.all(obj_row >= -_EPS):
            break

        pivot_col = int(np.argmin(obj_row))
        entering = col_labels[pivot_col]

        col_vals = tableau[:-1, pivot_col]
        rhs_vals = tableau[:-1, -1]

        ratios = np.full(len(col_vals), np.inf)
        for r in range(len(col_vals)):
            if col_vals[r] > _EPS:
                ratios[r] = rhs_vals[r] / col_vals[r]

        if np.all(ratios == np.inf):
            verts = feasible_vertices(problem)
            return Solution(status="unbounded", steps=steps, feasible_vertices=verts)

        pivot_row = int(np.argmin(ratios))
        leaving = basis[pivot_row]

        steps.append(SimplexStep(
            iteration=iteration,
            tableau=tableau[:-1, :].copy(),
            basis=basis.copy(),
            col_labels=col_labels,
            entering=entering,
            leaving=leaving,
            pivot_row=pivot_row,
            pivot_col=pivot_col,
        ))

        pivot_val = tableau[pivot_row, pivot_col]
        tableau[pivot_row, :] /= pivot_val
        for r in range(len(tableau)):
            if r != pivot_row:
                tableau[r, :] -= tableau[r, pivot_col] * tableau[pivot_row, :]

        basis[pivot_row] = entering
        iteration += 1

    # Tableau final
    steps.append(SimplexStep(
        iteration=iteration,
        tableau=tableau[:-1, :].copy(),
        basis=basis.copy(),
        col_labels=col_labels,
    ))

    # Comprobar artificiales en base con valor > 0 → infeasible
    for i, b in enumerate(basis):
        if b.startswith("a") and tableau[i, -1] > _EPS:
            verts = feasible_vertices(problem)
            return Solution(status="infeasible", steps=steps, feasible_vertices=verts)

    x_val = 0.0
    y_val = 0.0
    if "x" in basis:
        x_val = tableau[basis.index("x"), -1]
    if "y" in basis:
        y_val = tableau[basis.index("y"), -1]

    obj_value = problem.cx * x_val + problem.cy * y_val
    verts = feasible_vertices(problem)

    return Solution(
        status="optimal",
        x=round(x_val, 6),
        y=round(y_val, 6),
        value=round(obj_value, 6),
        steps=steps,
        feasible_vertices=verts,
    )
