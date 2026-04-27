import streamlit as st
from datetime import datetime

from solver.models import Problem, Constraint
from solver.simplex import solve
from ui.graph import build_graph
from ui.steps import show_steps
from ui.latex_helpers import constraint_to_latex, objective_to_latex

st.set_page_config(
    page_title="Solver PL 2 Variables",
    page_icon="📐",
    layout="wide",
)

# 🔥 PEGA AQUÍ
st.markdown("""
<style>

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
    status = "🟢 Resuelto" if st.session_state.solution else "🟡 En espera"
    st.markdown(f"<div style='text-align:right;padding-top:20px'><b>{status}</b></div>", unsafe_allow_html=True)

st.divider()

# ── LAYOUT ───────────────────────────────────────
left, right = st.columns([1, 2.3], gap="large")

# ── PANEL IZQUIERDO ──────────────────────────────
with left:
    with st.container(border=True):

        st.subheader("⚡ Configurar problema")

        description = st.text_area("📝 Descripción", placeholder="Ej: Maximizar ganancia...")

        objective = st.radio(
            "🎯 Optimización",
            ["maximize", "minimize"],
            format_func=lambda x: "▲ Maximizar" if x=="maximize" else "▼ Minimizar",
            horizontal=True
        )

        st.markdown("🧾 **Función objetivo**")
        c1, c2 = st.columns(2)
        cx = c1.number_input("cx", value=3.0)
        cy = c2.number_input("cy", value=5.0)
        st.latex(objective_to_latex(cx, cy, objective))

        st.divider()
        st.markdown("📦 **Restricciones**")

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
            if st.button("💾 Guardar", use_container_width=True):
                st.session_state.history.append({
                    "description": description,
                    "problem": st.session_state.problem,
                    "solution": st.session_state.solution,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.success("✅ Guardado")
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

        # RESULTADO
        with st.container(border=True):
            st.subheader("📊 Resultado")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📍 x*", sol.x)
            m2.metric("📍 y*", sol.y)
            m3.metric("💰 f*", sol.value)
            m4.metric("📦 Restricciones", len(prob.constraints))

        # GRÁFICA
        with st.container(border=True):
            st.subheader("📈 Región factible")
            st.plotly_chart(build_graph(prob, sol), use_container_width=True)

        # ITERACIONES
        with st.container(border=True):
            st.subheader("🧮 Iteraciones del Método Simplex")
            show_steps(sol)