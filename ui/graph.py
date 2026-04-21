import numpy as np
import plotly.graph_objects as go
from solver.models import Problem, Solution
from solver.geometry import feasible_vertices


def build_graph(problem: Problem, solution: Solution) -> go.Figure:
    constraints = problem.constraints

    # Calcular rango de los ejes
    all_x = [0.0]
    all_y = [0.0]
    for c in constraints:
        if abs(c.b) > 1e-9:
            all_y.append(c.rhs / c.b)
        if abs(c.a) > 1e-9:
            all_x.append(c.rhs / c.a)
    if solution.feasible_vertices:
        all_x += [v[0] for v in solution.feasible_vertices]
        all_y += [v[1] for v in solution.feasible_vertices]
    if solution.x is not None:
        all_x.append(solution.x)
    if solution.y is not None:
        all_y.append(solution.y)

    x_max = max(max(v for v in all_x if np.isfinite(v)) * 1.35, 10.0)
    y_max = max(max(v for v in all_y if np.isfinite(v)) * 1.35, 10.0)

    # Recalcular vértices incluyendo los bordes del gráfico para regiones no acotadas
    vertices = feasible_vertices(problem, x_max=x_max, y_max=y_max)

    fig = go.Figure()

    colors = ["#818CF8", "#34D399", "#F59E0B", "#F87171", "#60A5FA", "#C084FC"]
    x_range = np.linspace(0, x_max, 500)

    for idx, c in enumerate(constraints):
        color = colors[idx % len(colors)]
        label = f"{c.a}x + {c.b}y {c.op} {c.rhs}"

        if abs(c.b) > 1e-9:
            y_line = (c.rhs - c.a * x_range) / c.b
            mask = (y_line >= -y_max * 0.1) & (y_line <= y_max * 1.1)
            fig.add_trace(go.Scatter(
                x=x_range[mask], y=y_line[mask],
                mode="lines",
                name=label,
                line=dict(color=color, width=2),
            ))
        elif abs(c.a) > 1e-9:
            x_val = c.rhs / c.a
            fig.add_trace(go.Scatter(
                x=[x_val, x_val], y=[0, y_max],
                mode="lines",
                name=label,
                line=dict(color=color, width=2),
            ))

    # Región factible
    if len(vertices) >= 3:
        vx = [v[0] for v in vertices] + [vertices[0][0]]
        vy = [v[1] for v in vertices] + [vertices[0][1]]
        fig.add_trace(go.Scatter(
            x=vx, y=vy,
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.15)",
            line=dict(color="rgba(99, 102, 241, 0.4)", width=1),
            name="Región factible",
            hoverinfo="skip",
        ))

        # Vértices "reales" (no son los del borde del gráfico)
        real_verts = [v for v in vertices if v[0] < x_max * 0.99 and v[1] < y_max * 0.99]
        if real_verts:
            fig.add_trace(go.Scatter(
                x=[v[0] for v in real_verts],
                y=[v[1] for v in real_verts],
                mode="markers+text",
                marker=dict(color="#A5B4FC", size=8),
                text=[f"({v[0]:.2f}, {v[1]:.2f})" for v in real_verts],
                textposition="top right",
                name="Vértices",
                hoverinfo="text",
            ))

    # Punto óptimo
    if solution.status == "optimal" and solution.x is not None:
        fig.add_trace(go.Scatter(
            x=[solution.x], y=[solution.y],
            mode="markers+text",
            marker=dict(symbol="star", size=18, color="#FBBF24",
                        line=dict(color="#F59E0B", width=2)),
            text=[f"  Óptimo ({solution.x:.4f}, {solution.y:.4f})"],
            textposition="middle right",
            textfont=dict(size=13, color="#FBBF24"),
            name="Punto óptimo",
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(color="#F1F5F9"),
        xaxis=dict(
            title="x", range=[0, x_max],
            gridcolor="rgba(255,255,255,0.08)",
            zerolinecolor="rgba(255,255,255,0.2)",
        ),
        yaxis=dict(
            title="y", range=[0, y_max],
            gridcolor="rgba(255,255,255,0.08)",
            zerolinecolor="rgba(255,255,255,0.2)",
        ),
        legend=dict(bgcolor="rgba(30,41,59,0.8)", bordercolor="#334155"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
    )
    return fig
