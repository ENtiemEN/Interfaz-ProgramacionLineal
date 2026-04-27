import streamlit as st
from datetime import datetime

from solver.models import Problem, Constraint
from solver.simplex import solve
from ui.graph import build_graph
from ui.steps import show_steps
from ui.latex_helpers import constraint_to_latex, objective_to_latex, problem_to_latex
from ui.pdf_export import generate_pdf

st.set_page_config(
    page_title="Solver PL 2 Variables",
    page_icon="📐",
    layout="wide",
)

def _sec(title: str, color: str = "#00A9F2"):
    st.markdown(
        f"<div style='border-left:3px solid {color};padding:3px 0 3px 11px;"
        f"margin:6px 0 10px 0'><span style='font-size:1rem;font-weight:600'>"
        f"{title}</span></div>",
        unsafe_allow_html=True,
    )


st.markdown("""
<style>

/* Monospace en tablas */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th {
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace !important;
    font-size: 0.82rem !important;
}

/* 🎨 CARDS DE RESULTADO */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #00A9F2, #1883FF);
    border: none;
    border-radius: 14px;
    padding: 16px;
    color: white;
}

/* Texto */
[data-testid="stMetric"] label {
    color: rgba(255,255,255,0.8) !important;
}

[data-testid="stMetric"] div {
    color: white !important;
}

/* Colores por card */
[data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #00E2E0, #00A9F2);
}

[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #1883FF, #3B82F6);
}

[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #9333EA, #C084FC);
}

[data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #F43F5E, #FB7185);
}

</style>
""", unsafe_allow_html=True)

# 🔥 COLOR + GLOW (seguro)
st.markdown("""
<style>

/* Glow métricas */
[data-testid="stMetric"] {
    box-shadow: 0 0 18px rgba(0, 169, 242, 0.25);
    border: 1px solid rgba(0, 226, 224, 0.35);
    border-radius: 12px;
}

/* Botón principal */
button[kind="primary"] {
    background: linear-gradient(135deg, #1883FF, #00A9F2);
    color: white;
    box-shadow: 0 0 20px rgba(24, 131, 255, 0.45);
    border-radius: 10px;
}

/* Hover */
button[kind="primary"]:hover {
    box-shadow: 0 0 30px rgba(0, 226, 224, 0.7);
}

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
    border: 1px solid rgba(0, 169, 242, 0.25);
}

</style>
""", unsafe_allow_html=True)

# ── STATE ─────────────────────────────────────────
for k, v in {
    "history": [],
    "num_constraints": 3,
    "load_idx": None,
    "solution": None,
    "problem": None,
    "ref_solution": None,
    "ref_problem": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── LOAD ─────────────────────────────────────────
loaded_problem = None
if st.session_state.load_idx is not None:
    idx = st.session_state.load_idx
    if 0 <= idx < len(st.session_state.history):
        loaded_problem = st.session_state.history[idx]["problem"]
        st.session_state.num_constraints = len(loaded_problem.constraints)
    st.session_state.load_idx = None

# ── HEADER ───────────────────────────────────────
top_left, top_right = st.columns([2.3, 1])

with top_left:
    st.title("📐 Solver de Programación Lineal")
    st.caption("🚀 2 variables · Método Simplex · Región factible")

with top_right:
    if st.session_state.solution:
        _c, _bg, _bd, _txt = "#22C55E", "rgba(34,197,94,0.12)", "rgba(34,197,94,0.4)", "● Resuelto"
    else:
        _c, _bg, _bd, _txt = "#EAB308", "rgba(234,179,8,0.12)", "rgba(234,179,8,0.4)", "● En espera"
    st.markdown(
        f"<div style='text-align:right;padding-top:22px'>"
        f"<span style='background:{_bg};color:{_c};border:1px solid {_bd};"
        f"border-radius:20px;padding:5px 14px;font-size:0.85rem;font-weight:600'>"
        f"{_txt}</span></div>",
        unsafe_allow_html=True,
    )

st.divider()

# ── LAYOUT ───────────────────────────────────────
left, right = st.columns([1, 2.3], gap="large")

# ── PANEL IZQUIERDO ──────────────────────────────
with left:
    with st.container(border=True):

        _sec("⚡ Configurar problema", "#00A9F2")

        description = st.text_area("📝 Descripción", placeholder="Ej: Maximizar ganancia...")

        objective = st.radio(
            "🎯 Optimización",
            ["maximize", "minimize"],
            format_func=lambda x: "▲ Maximizar" if x=="maximize" else "▼ Minimizar",
            horizontal=True
        )

        _sec("🧾 Función objetivo", "#818CF8")
        c1, c2 = st.columns(2)
        cx = c1.number_input("cx", value=3.0)
        cy = c2.number_input("cy", value=5.0)
        st.latex(objective_to_latex(cx, cy, objective))

        st.divider()
        _sec("📦 Restricciones", "#34D399")

        constraints_input = []
        base = [(1,0,"<=",4),(0,2,"<=",12),(3,2,"<=",18)]

        for i in range(st.session_state.num_constraints):
            a_d, b_d, op_d, rhs_d = base[i] if i < 3 else (1,0,"<=",0)

            with st.expander(f"📌 Restricción {i+1}", expanded=True):
                r1, r2, r3, r4 = st.columns([1,1,0.8,1])
                a = r1.number_input("a", value=a_d, key=f"a{i}")
                b = r2.number_input("b", value=b_d, key=f"b{i}")
                op = r3.selectbox("op", ["<=",">=","="], key=f"op{i}")
                rhs = r4.number_input("rhs", value=rhs_d, key=f"rhs{i}")

                constraints_input.append(Constraint(a=a,b=b,op=op,rhs=rhs))
                st.latex(constraint_to_latex(a, b, op, rhs))

        if constraints_input:
            with st.expander("📋 Formulación completa", expanded=False):
                st.latex(problem_to_latex(cx, cy, objective, constraints_input))

        colA, colB = st.columns(2)
        if colA.button("➕ Agregar", use_container_width=True):
            st.session_state.num_constraints += 1
            st.rerun()

        if colB.button("➖ Quitar", use_container_width=True) and st.session_state.num_constraints > 1:
            st.session_state.num_constraints -= 1
            st.rerun()

        st.divider()

        solve_btn = st.button("🚀 Resolver", type="primary", use_container_width=True)

        if st.session_state.solution:
            save_col, ref_col = st.columns(2)
            if save_col.button("💾 Guardar", use_container_width=True):
                st.session_state.history.append({
                    "description": description,
                    "problem": st.session_state.problem,
                    "solution": st.session_state.solution,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.success("✅ Guardado")
                st.rerun()
            if ref_col.button("📌 Fijar ref.", use_container_width=True):
                st.session_state.ref_solution = st.session_state.solution
                st.session_state.ref_problem = st.session_state.problem
                st.success("✅ Referencia fijada")
                st.rerun()

            if st.session_state.ref_solution:
                ref_f = st.session_state.ref_solution.value
                st.caption(f"📌 Referencia activa: f* = {ref_f:.4g}")
                if st.button("🗑️ Quitar referencia", use_container_width=True):
                    st.session_state.ref_solution = None
                    st.session_state.ref_problem = None
                    st.rerun()

        st.metric("💾 Guardados", len(st.session_state.history))

# ── SOLVER ───────────────────────────────────────
if solve_btn:
    prob = Problem(cx=cx, cy=cy, objective=objective, constraints=constraints_input)
    sol = solve(prob)

    st.session_state.solution = sol
    st.session_state.problem = prob
    st.rerun()

# ── PANEL DERECHO ────────────────────────────────
with right:

    if not st.session_state.solution:
        st.markdown(
            "<h2 style='text-align:center; margin: 8px 0 4px 0'>📐 Solver de Programación Lineal</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color: rgba(160,160,160,0.9); margin-bottom: 20px'>"
            "Optimiza problemas de 2 variables con el Método Simplex</p>",
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown("#### ¿Qué hace esta aplicación?")
            st.markdown(
                "Esta herramienta resuelve problemas de **programación lineal de 2 variables** "
                "usando el **Método Simplex**. Dado un conjunto de restricciones lineales "
                "y una función objetivo, encuentra el punto $(x^*, y^*)$ que maximiza o minimiza "
                "dicha función dentro de la región factible."
            )
            st.latex(r"""
\begin{aligned}
\max / \min \; & f(x, y) = c_x x + c_y y \\
\text{s.a.} \; & a_i x + b_i y \;\leq/\geq/=\; r_i \quad \forall\, i \\
& x,\, y \geq 0
\end{aligned}
""")

        with st.container(border=True):
            st.markdown("#### El Método Simplex — pasos")
            col_steps, col_formula = st.columns([3, 2])
            with col_steps:
                st.markdown("""
1. **Estandarizar**: agregar variables de holgura $s_i \\geq 0$ para convertir desigualdades en igualdades.
2. **Tableau inicial**: construir la tabla con la función objetivo en la última fila.
3. **Variable entrante**: elegir la columna con coeficiente más negativo en la fila objetivo (regla de Dantzig).
4. **Variable saliente**: aplicar la prueba de razón mínima (*min-ratio test*).
5. **Pivoteo**: hacer cero todos los elementos de la columna entrante salvo el pivote.
6. **Iterar** hasta que no haya coeficientes negativos en la fila objetivo.
7. **Leer solución**: los valores en la columna RHS son la solución óptima $x^*, y^*$.
""")
            with col_formula:
                st.markdown("**Forma estándar:**")
                st.latex(r"""
\begin{aligned}
\min \; & c^T x \\
\text{s.a.} \; & Ax = b \\
& x \geq 0
\end{aligned}
""")
                st.markdown("**Tableau:**")
                st.latex(r"""
\begin{array}{c|c}
B^{-1}N & B^{-1}b \\
\hline
c_N^T - c_B^T B^{-1}N & z^*
\end{array}
""")

        with st.container(border=True):
            st.markdown("#### Cómo usar la aplicación")
            st.markdown("""
1. Ingresa los coeficientes $c_x$ y $c_y$ de la función objetivo y elige **Maximizar** o **Minimizar**.
2. Define cada restricción con sus coeficientes $a$, $b$, el operador y el lado derecho $r$.
3. Presiona **🚀 Resolver** — el resultado aparecerá aquí.
4. Explora la **región factible** en la gráfica y cada **iteración del tableau** en los pasos.
5. Guarda el problema en el historial con **💾 Guardar**.
""")

    else:
        sol = st.session_state.solution
        prob = st.session_state.problem
        ref_sol = st.session_state.ref_solution
        ref_prob = st.session_state.ref_problem

        # Tabs: 3 cuando hay referencia, 2 si no
        if ref_sol and ref_prob:
            tab_res, tab_cmp, tab_pdf = st.tabs(["📊 Resultado", "⚖️ Comparación", "📄 PDF"])
        else:
            tab_res, tab_pdf = st.tabs(["📊 Resultado", "📄 PDF"])
            tab_cmp = None

        # ── TAB RESULTADO ──────────────────────────────────────────────────
        with tab_res:
            with st.container(border=True):
                _sec("📊 Resultado", "#00A9F2")

                with st.expander("📋 Problema planteado", expanded=True):
                    st.latex(problem_to_latex(prob.cx, prob.cy, prob.objective, prob.constraints))

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📍 x*", sol.x)
                m2.metric("📍 y*", sol.y)
                m3.metric("💰 f*", sol.value)
                m4.metric("📦 Restricciones", len(prob.constraints))

            with st.container(border=True):
                _sec("📈 Región factible", "#06B6D4")
                st.plotly_chart(build_graph(prob, sol), use_container_width=True)

            with st.container(border=True):
                _sec("🧮 Iteraciones del Método Simplex", "#A855F7")
                show_steps(sol)

        # ── TAB COMPARACIÓN ────────────────────────────────────────────────
        if tab_cmp:
            with tab_cmp:
                _sec("⚖️ Comparación de Problemas", "#F59E0B")

                ca, cb = st.columns(2)
                with ca:
                    st.markdown("**📌 Referencia**")
                    st.latex(problem_to_latex(
                        ref_prob.cx, ref_prob.cy, ref_prob.objective, ref_prob.constraints
                    ))
                with cb:
                    st.markdown("**🔵 Actual**")
                    st.latex(problem_to_latex(
                        prob.cx, prob.cy, prob.objective, prob.constraints
                    ))

                with st.container(border=True):
                    _sec("📈 Regiones factibles superpuestas", "#06B6D4")
                    st.plotly_chart(
                        build_graph(prob, sol, ref_prob, ref_sol),
                        use_container_width=True,
                    )

                with st.container(border=True):
                    _sec("📊 Diferencias", "#00A9F2")
                    ca, cb = st.columns(2)
                    with ca:
                        st.markdown("**📌 Referencia**")
                        r1, r2, r3 = st.columns(3)
                        r1.metric("x*", ref_sol.x)
                        r2.metric("y*", ref_sol.y)
                        r3.metric("f*", ref_sol.value)
                    with cb:
                        st.markdown("**🔵 Actual**")
                        r1, r2, r3 = st.columns(3)
                        dx = round(sol.x - (ref_sol.x or 0), 6)
                        dy = round(sol.y - (ref_sol.y or 0), 6)
                        df = round(sol.value - (ref_sol.value or 0), 6)
                        r1.metric("x*", sol.x, delta=dx)
                        r2.metric("y*", sol.y, delta=dy)
                        r3.metric("f*", sol.value, delta=df)

        # ── TAB PDF ────────────────────────────────────────────────────────
        with tab_pdf:
            _sec("📄 Exportar PDF", "#A855F7")
            st.markdown(
                "El reporte incluye la formulación del problema, la solución óptima "
                "y las tablas de cada iteración del Simplex con el pivote resaltado."
            )
            include_graph = st.checkbox(
                "Incluir gráfica en el PDF (requiere kaleido instalado)", value=False
            )
            fig_export = build_graph(prob, sol) if include_graph else None
            pdf_bytes = generate_pdf(prob, sol, fig_export)
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_bytes,
                file_name=f"reporte_pl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )