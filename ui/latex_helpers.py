def constraint_to_latex(a: float, b: float, op: str, rhs: float) -> str:
    op_map = {"<=": r"\leq", ">=": r"\geq", "=": "="}
    op_latex = op_map.get(op, op)

    def _fmt(coef, var, is_first):
        abs_c = abs(coef)
        abs_s = str(int(abs_c)) if abs_c == int(abs_c) else f"{abs_c:g}"
        coef_str = var if abs_c == 1 else f"{abs_s}{var}"
        if is_first:
            return coef_str if coef > 0 else f"-{coef_str}"
        return f"+ {coef_str}" if coef > 0 else f"- {coef_str}"

    terms = []
    if a != 0:
        terms.append(_fmt(a, "x", True))
    if b != 0:
        terms.append(_fmt(b, "y", len(terms) == 0))

    lhs = " ".join(terms) if terms else "0"
    rhs_s = str(int(rhs)) if rhs == int(rhs) else f"{rhs:g}"
    return f"{lhs} {op_latex} {rhs_s}"


def objective_to_latex(cx: float, cy: float, objective: str) -> str:
    obj = r"\max" if objective == "maximize" else r"\min"

    def _fmt(coef, var, is_first):
        abs_c = abs(coef)
        abs_s = str(int(abs_c)) if abs_c == int(abs_c) else f"{abs_c:g}"
        coef_str = var if abs_c == 1 else f"{abs_s}{var}"
        if is_first:
            return coef_str if coef >= 0 else f"-{coef_str}"
        return f"+ {coef_str}" if coef >= 0 else f"- {coef_str}"

    terms = []
    if cx != 0:
        terms.append(_fmt(cx, "x", True))
    if cy != 0:
        terms.append(_fmt(cy, "y", len(terms) == 0))

    expr = " ".join(terms) if terms else "0"
    return rf"{obj} \; f(x,y) = {expr}"
