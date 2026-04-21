import streamlit as st
from solver.models import Problem, Solution


def show_result(problem: Problem, solution: Solution):
    status = solution.status

    if status == "infeasible":
        st.error("No factible: las restricciones no tienen solución en común.")
        return

    if status == "unbounded":
        st.warning("No acotado: la función objetivo puede crecer/decrecer indefinidamente.")
        return

    obj_type = "Máximo" if problem.objective == "maximize" else "Mínimo"

    col1, col2, col3 = st.columns(3)
    col1.metric("x*", f"{solution.x:.6g}")
    col2.metric("y*", f"{solution.y:.6g}")
    col3.metric(f"f(x*, y*) — {obj_type}", f"{solution.value:.6g}")

    st.markdown(
        f"**Función objetivo:** `f(x, y) = {problem.cx}x + {problem.cy}y`  \n"
        f"**Tipo:** {obj_type}  \n"
        f"**Valor óptimo:** `{solution.value:.6g}` en `({solution.x:.6g}, {solution.y:.6g})`"
    )
