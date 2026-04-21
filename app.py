import streamlit as st
from datetime import datetime

from solver.models import Problem, Constraint
from solver.simplex import solve
from ui.graph import build_graph
from ui.result import show_result
from ui.steps import show_steps

st.set_page_config(
    page_title="Solver PL 2 Variables",
    page_icon="📐",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stMetric { background: #1E293B; border-radius: 8px; padding: 0.5rem 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "num_constraints" not in st.session_state:
    st.session_state.num_constraints = 3
if "load_idx" not in st.session_state:
    st.session_state.load_idx = None
if "solution" not in st.session_state:
    st.session_state.solution = None
if "problem" not in st.session_state:
    st.session_state.problem = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📐 Programación Lineal")
    st.caption("Solver de 2 variables — Método Simplex")
    st.divider()

    description = st.text_area(
        "Descripción del problema (opcional)",
        height=80,
        placeholder="Ej: Maximizar la ganancia de productos A y B...",
    )

    objective = st.radio("Tipo de optimización", ["Maximizar", "Minimizar"], horizontal=True)

    st.markdown("**Función objetivo** `f(x, y) = cx·x + cy·y`")
    col_cx, col_cy = st.columns(2)
    cx = col_cx.number_input("cx", value=3.0, step=0.5, format="%.4g")
    cy = col_cy.number_input("cy", value=5.0, step=0.5, format="%.4g")

    st.divider()
    st.markdown("**Restricciones** `a·x + b·y OP rhs`")

    # Precargar valores si el usuario eligió un problema del historial
    defaults = None
    if st.session_state.load_idx is not None:
        idx = st.session_state.load_idx
        loaded = st.session_state.history[idx]
        defaults = loaded["problem"].constraints
        st.session_state.num_constraints = len(defaults)
        st.session_state.load_idx = None

    col_add, col_del = st.columns(2)
    if col_add.button("➕ Agregar", use_container_width=True):
        st.session_state.num_constraints += 1
    if col_del.button("➖ Quitar", use_container_width=True) and st.session_state.num_constraints > 1:
        st.session_state.num_constraints -= 1

    constraints_input = []
    for i in range(st.session_state.num_constraints):
        st.markdown(f"**Restricción {i+1}**")
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1.2])
        default_c = defaults[i] if defaults and i < len(defaults) else None
        a = c1.number_input("a", value=float(default_c.a) if default_c else 1.0,
                            key=f"a_{i}", format="%.4g")
        b = c2.number_input("b", value=float(default_c.b) if default_c else 0.0,
                            key=f"b_{i}", format="%.4g")
        op = c3.selectbox("op", ["<=", ">=", "="],
                          index=["<=", ">=", "="].index(default_c.op) if default_c else 0,
                          key=f"op_{i}")
        rhs = c4.number_input("rhs", value=float(default_c.rhs) if default_c else 0.0,
                              key=f"rhs_{i}", format="%.4g")
        constraints_input.append(Constraint(a=a, b=b, op=op, rhs=rhs))

    st.divider()

    solve_btn = st.button("🔍 Resolver", type="primary", use_container_width=True)

    if st.session_state.solution is not None:
        if st.button("💾 Guardar en historial", use_container_width=True):
            entry = {
                "description": description or f"Problema {len(st.session_state.history)+1}",
                "problem": st.session_state.problem,
                "solution": st.session_state.solution,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.history.append(entry)
            st.success("Guardado en historial.")

    # Historial
    if st.session_state.history:
        st.divider()
        st.markdown("**Historial de la sesión**")
        for i, entry in enumerate(reversed(st.session_state.history)):
            real_idx = len(st.session_state.history) - 1 - i
            with st.expander(f"📋 {entry['description']} — {entry['timestamp']}"):
                p = entry["problem"]
                obj_lbl = "Max" if p.objective == "maximize" else "Min"
                st.markdown(f"`{obj_lbl} f = {p.cx}x + {p.cy}y`")
                for c in p.constraints:
                    st.markdown(f"- `{c.a}x + {c.b}y {c.op} {c.rhs}`")
                sol = entry["solution"]
                if sol.status == "optimal":
                    st.markdown(f"**Resultado:** x*={sol.x}, y*={sol.y}, f*={sol.value}")
                else:
                    st.markdown(f"**Estado:** {sol.status}")
                if st.button("Cargar", key=f"load_{real_idx}"):
                    st.session_state.load_idx = real_idx
                    st.rerun()

# ── Área principal ─────────────────────────────────────────────────────────────
st.title("Solver de Programación Lineal")
st.caption("2 variables · Método Simplex · Región factible interactiva")

if solve_btn:
    problem = Problem(
        cx=cx,
        cy=cy,
        objective="maximize" if objective == "Maximizar" else "minimize",
        constraints=constraints_input,
        description=description,
    )
    with st.spinner("Resolviendo..."):
        solution = solve(problem)
    st.session_state.solution = solution
    st.session_state.problem = problem

if st.session_state.solution is not None:
    solution = st.session_state.solution
    problem = st.session_state.problem

    st.subheader("Resultado")
    show_result(problem, solution)

    st.subheader("Región factible")
    fig = build_graph(problem, solution)
    st.plotly_chart(fig, width="stretch")

    show_steps(solution)
else:
    st.info("Configura el problema en el panel izquierdo y presiona **Resolver**.")
    st.markdown("""
    **Instrucciones:**
    1. Escribe una descripción opcional del problema.
    2. Elige **Maximizar** o **Minimizar**.
    3. Ingresa los coeficientes `cx` y `cy` de la función objetivo.
    4. Agrega tus restricciones (`a·x + b·y ≤/≥/= rhs`).
    5. Presiona **Resolver**.

    > Las restricciones `x ≥ 0` e `y ≥ 0` se asumen siempre.
    """)
