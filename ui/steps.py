import streamlit as st
import pandas as pd
import numpy as np
from solver.models import Solution


def show_steps(solution: Solution):
    if not solution.steps:
        st.info("No hay pasos disponibles.")
        return

    st.subheader("Iteraciones del Método Simplex")

    for step in solution.steps:
        is_final = step.entering is None
        label = f"Iteración {step.iteration}" if not is_final else f"Tableau final (iteración {step.iteration})"

        with st.expander(label, expanded=(step.iteration == 0)):
            if step.entering:
                st.markdown(
                    f"**Variable entrante:** `{step.entering}` &nbsp;|&nbsp; "
                    f"**Variable saliente:** `{step.leaving}`"
                )

            n_rows = step.tableau.shape[0]
            col_labels = step.col_labels  # incluye "RHS" al final

            df = pd.DataFrame(
                step.tableau,
                index=[f"R{i+1} ({step.basis[i]})" for i in range(n_rows)],
                columns=col_labels,
            )

            # Formatear valores numéricos
            df = df.map(lambda v: round(float(v), 4) if isinstance(v, (int, float, np.floating)) else v)

            def highlight(data):
                styles = pd.DataFrame("", index=data.index, columns=data.columns)
                if step.pivot_col is not None and step.pivot_col < len(col_labels) - 1:
                    styles.iloc[:, step.pivot_col] = "background-color: rgba(99,102,241,0.25)"
                if step.pivot_row is not None:
                    styles.iloc[step.pivot_row, :] = "background-color: rgba(52,211,153,0.2)"
                if step.pivot_row is not None and step.pivot_col is not None:
                    styles.iloc[step.pivot_row, step.pivot_col] = "background-color: rgba(251,191,36,0.5); font-weight: bold"
                return styles

            st.dataframe(df.style.apply(highlight, axis=None), width="stretch")

            if is_final:
                st.success("Solución óptima alcanzada.")
