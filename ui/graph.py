import numpy as np
import plotly.graph_objects as go
from solver.models import Problem, Solution
from solver.geometry import feasible_vertices

_REF_LINE = "#94A3B8"
_REF_FILL = "rgba(148, 163, 184, 0.10)"
_REF_REGION_BORDER = "rgba(148, 163, 184, 0.30)"


def build_graph(
    problem: Problem,
    solution: Solution,
    ref_problem: Problem = None,
    ref_solution: Solution = None,
) -> go.Figure:
    constraints = problem.constraints

    # Calcular rango de los ejes considerando ambos problemas
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

    if ref_problem:
        for c in ref_problem.constraints:
            if abs(c.b) > 1e-9:
                all_y.append(c.rhs / c.b)
            if abs(c.a) > 1e-9:
                all_x.append(c.rhs / c.a)
        if ref_solution and ref_solution.x is not None:
            all_x.append(ref_solution.x)
        if ref_solution and ref_solution.y is not None:
            all_y.append(ref_solution.y)

    x_max = max(max(v for v in all_x if np.isfinite(v)) * 1.35, 10.0)
    y_max = max(max(v for v in all_y if np.isfinite(v)) * 1.35, 10.0)

    vertices = feasible_vertices(problem, x_max=x_max, y_max=y_max)

    fig = go.Figure()
    x_range = np.linspace(0, x_max, 500)

    # ── REFERENCIA (detrás, colores apagados) ──────────────────────────────
    if ref_problem:
        ref_verts = feasible_vertices(ref_problem, x_max=x_max, y_max=y_max)

        for c in ref_problem.constraints:
            label = f"[Ref] {c.a}x + {c.b}y {c.op} {c.rhs}"
            if abs(c.b) > 1e-9:
                y_line = (c.rhs - c.a * x_range) / c.b
                mask = (y_line >= -y_max * 0.1) & (y_line <= y_max * 1.1)
                fig.add_trace(go.Scatter(
                    x=x_range[mask], y=y_line[mask],
                    mode="lines", name=label,
                    line=dict(color=_REF_LINE, width=1.5, dash="dot"),
                    legendgroup="ref", legendgrouptitle_text="Referencia",
                ))
            elif abs(c.a) > 1e-9:
                x_val = c.rhs / c.a
                fig.add_trace(go.Scatter(
                    x=[x_val, x_val], y=[0, y_max],
                    mode="lines", name=label,
                    line=dict(color=_REF_LINE, width=1.5, dash="dot"),
                    legendgroup="ref",
                ))

        if len(ref_verts) >= 3:
            rvx = [v[0] for v in ref_verts] + [ref_verts[0][0]]
            rvy = [v[1] for v in ref_verts] + [ref_verts[0][1]]
            fig.add_trace(go.Scatter(
                x=rvx, y=rvy,
                fill="toself",
                fillcolor=_REF_FILL,
                line=dict(color=_REF_REGION_BORDER, width=1),
                name="Región factible (Ref)",
                hoverinfo="skip",
                legendgroup="ref",
            ))

        if ref_solution and ref_solution.status == "optimal" and ref_solution.x is not None:
            fig.add_trace(go.Scatter(
                x=[ref_solution.x], y=[ref_solution.y],
                mode="markers",
                marker=dict(symbol="star", size=16, color=_REF_LINE,
                            line=dict(color="#64748B", width=1.5)),
                name="Óptimo (Ref)",
                legendgroup="ref",
            ))
            fig.add_annotation(
                x=ref_solution.x, y=ref_solution.y,
                text=(
                    f"<b>[Ref] ({ref_solution.x:.4g}, {ref_solution.y:.4g})</b><br>"
                    f"f* = {ref_solution.value:.4g}"
                ),
                showarrow=True, arrowhead=2,
                arrowcolor=_REF_LINE, arrowsize=1.1, arrowwidth=1.5,
                ax=-60, ay=50,
                bgcolor="rgba(20, 30, 50, 0.85)",
                bordercolor=_REF_LINE, borderwidth=1.2, borderpad=7,
                font=dict(color="#CBD5E1", size=11),
                align="center",
            )

    # ── PROBLEMA ACTUAL ────────────────────────────────────────────────────
    colors = ["#818CF8", "#34D399", "#F59E0B", "#F87171", "#60A5FA", "#C084FC"]

    for idx, c in enumerate(constraints):
        color = colors[idx % len(colors)]
        label = f"{c.a}x + {c.b}y {c.op} {c.rhs}"

        if abs(c.b) > 1e-9:
            y_line = (c.rhs - c.a * x_range) / c.b
            mask = (y_line >= -y_max * 0.1) & (y_line <= y_max * 1.1)
            fig.add_trace(go.Scatter(
                x=x_range[mask], y=y_line[mask],
                mode="lines", name=label,
                line=dict(color=color, width=2),
                legendgroup="actual", legendgrouptitle_text="Actual" if ref_problem else None,
            ))
        elif abs(c.a) > 1e-9:
            x_val = c.rhs / c.a
            fig.add_trace(go.Scatter(
                x=[x_val, x_val], y=[0, y_max],
                mode="lines", name=label,
                line=dict(color=color, width=2),
                legendgroup="actual",
            ))

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
            legendgroup="actual",
        ))

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
                legendgroup="actual",
            ))

    if solution.status == "optimal" and solution.x is not None:
        fig.add_trace(go.Scatter(
            x=[solution.x], y=[solution.y],
            mode="markers",
            marker=dict(symbol="star", size=20, color="#FBBF24",
                        line=dict(color="#F59E0B", width=2)),
            name="Punto óptimo",
            legendgroup="actual",
        ))
        fig.add_annotation(
            x=solution.x, y=solution.y,
            text=(
                f"<b>({solution.x:.4g},  {solution.y:.4g})</b><br>"
                f"f* = {solution.value:.4g}"
            ),
            showarrow=True, arrowhead=2,
            arrowcolor="#FBBF24", arrowsize=1.2, arrowwidth=2,
            ax=55, ay=-55,
            bgcolor="rgba(20, 30, 50, 0.88)",
            bordercolor="#FBBF24", borderwidth=1.5, borderpad=8,
            font=dict(color="#FDE68A", size=12),
            align="center",
        )

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
        legend=dict(bgcolor="rgba(30,41,59,0.8)", bordercolor="#334155", groupclick="toggleitem"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
    )
    return fig
