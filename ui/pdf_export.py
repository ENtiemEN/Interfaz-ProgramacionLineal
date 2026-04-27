import io
from datetime import datetime
from fpdf import FPDF
from solver.models import Problem, Solution


def _safe(s: str) -> str:
    return s.encode("latin-1", "replace").decode("latin-1")


def _fmt(v) -> str:
    try:
        f = float(v)
        return str(int(f)) if f == int(f) and abs(f) < 1e10 else f"{f:.4g}"
    except Exception:
        return str(v)


def _obj_expr(cx: float, cy: float) -> str:
    parts = []
    if cx != 0:
        abs_c = abs(cx)
        s = str(int(abs_c)) if abs_c == int(abs_c) else f"{abs_c:g}"
        term = "x" if abs_c == 1 else f"{s}x"
        parts.append(term if cx > 0 else f"-{term}")
    if cy != 0:
        abs_c = abs(cy)
        s = str(int(abs_c)) if abs_c == int(abs_c) else f"{abs_c:g}"
        term = "y" if abs_c == 1 else f"{s}y"
        if parts:
            parts.append(f"+ {term}" if cy > 0 else f"- {term}")
        else:
            parts.append(term if cy > 0 else f"-{term}")
    return " ".join(parts) if parts else "0"


def _constraint_expr(a, b, op, rhs) -> str:
    op_map = {"<=": "<=", ">=": ">=", "=": "="}
    parts = []
    if a != 0:
        abs_a = abs(a)
        s = str(int(abs_a)) if abs_a == int(abs_a) else f"{abs_a:g}"
        term = "x" if abs_a == 1 else f"{s}x"
        parts.append(term if a > 0 else f"-{term}")
    if b != 0:
        abs_b = abs(b)
        s = str(int(abs_b)) if abs_b == int(abs_b) else f"{abs_b:g}"
        term = "y" if abs_b == 1 else f"{s}y"
        if parts:
            parts.append(f"+ {term}" if b > 0 else f"- {term}")
        else:
            parts.append(term if b > 0 else f"-{term}")
    lhs = " ".join(parts) if parts else "0"
    rhs_s = str(int(rhs)) if rhs == int(rhs) else f"{rhs:g}"
    return f"{lhs} {op_map.get(op, op)} {rhs_s}"


def generate_pdf(problem: Problem, solution: Solution, fig=None) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    W = pdf.w - 20  # ancho útil en mm

    def hline(color=(0, 169, 242)):
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 10 + W, pdf.get_y())
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.2)
        pdf.ln(3)

    def section(title: str):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, _safe(title), ln=True)
        hline()

    # ── TÍTULO
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 11, "Solver PL - Reporte de Solucion", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _safe(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"), ln=True, align="C")
    hline((180, 180, 180))

    # ── FORMULACIÓN
    section("Formulacion del Problema")

    if problem.description:
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _safe(f"Descripcion: {problem.description}"))
        pdf.ln(2)

    obj_type = "Maximizar" if problem.objective == "maximize" else "Minimizar"
    pdf.set_font("Courier", "B", 11)
    pdf.cell(0, 7, _safe(f"  {obj_type}: f(x,y) = {_obj_expr(problem.cx, problem.cy)}"), ln=True)
    pdf.cell(0, 7, "  Sujeto a:", ln=True)
    pdf.set_font("Courier", "", 11)
    for c in problem.constraints:
        pdf.cell(0, 6, _safe(f"    {_constraint_expr(c.a, c.b, c.op, c.rhs)}"), ln=True)
    pdf.cell(0, 6, "    x, y >= 0", ln=True)

    # ── GRÁFICA (opcional, requiere kaleido)
    if fig is not None:
        try:
            import plotly.io as pio
            img_bytes = pio.to_image(fig, format="png", width=900, height=500, scale=1.5)
            section("Region Factible")
            pdf.image(io.BytesIO(img_bytes), x=10, w=W)
            pdf.ln(2)
        except Exception:
            pass  # kaleido no disponible, se omite la gráfica

    # ── SOLUCIÓN
    section("Solucion Optima")
    pdf.set_font("Helvetica", "", 11)
    if solution.status == "optimal":
        cw = W / 3
        pdf.set_fill_color(230, 245, 255)
        for label, val in [("x* =", solution.x), ("y* =", solution.y), ("f* =", solution.value)]:
            pdf.cell(cw, 9, _safe(f"  {label} {_fmt(val)}"), border=1, fill=True, align="C")
        pdf.ln()
    elif solution.status == "infeasible":
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 8, "Problema no factible: las restricciones no tienen solucion comun.", ln=True)
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 8, "Problema no acotado: la funcion objetivo crece indefinidamente.", ln=True)

    # ── ITERACIONES
    if solution.steps:
        section("Iteraciones del Metodo Simplex")

        for step in solution.steps:
            is_final = step.entering is None
            is_decisive = getattr(step, "is_decisive", False)

            if is_final:
                label = f"Tableau final (Iteracion {step.iteration})"
            elif is_decisive:
                label = f"[DECISIVA] Iteracion {step.iteration}"
            else:
                label = f"Iteracion {step.iteration}"

            pdf.set_font("Helvetica", "B", 10)
            if is_decisive:
                pdf.set_text_color(180, 120, 0)
            pdf.cell(0, 6, _safe(f"  {label}"), ln=True)
            pdf.set_text_color(0, 0, 0)

            if step.entering:
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 5, _safe(f"    Entrante: {step.entering}   |   Saliente: {step.leaving}"), ln=True)

            # Tabla del tableau
            col_labels = step.col_labels
            n_cols = len(col_labels)
            n_rows_t = step.tableau.shape[0]

            idx_w = 24.0
            data_w = max((W - idx_w) / n_cols, 13.0)
            font_sz = max(6, int(7.5 * (W - idx_w) / (data_w * n_cols + 0.001)))
            row_h = 4.5

            pdf.set_font("Courier", "B", font_sz)
            pdf.set_fill_color(210, 230, 255)
            pdf.cell(idx_w, row_h, "Base", border=1, fill=True, align="C")
            for lbl in col_labels:
                pdf.cell(data_w, row_h, _safe(lbl), border=1, fill=True, align="C")
            pdf.ln()

            pdf.set_font("Courier", "", font_sz)
            for r in range(n_rows_t):
                is_prow = (step.pivot_row == r) and not is_final
                pdf.set_fill_color(220, 255, 230) if is_prow else pdf.set_fill_color(255, 255, 255)
                row_label = f"R{r+1}({step.basis[r]})"
                pdf.cell(idx_w, row_h, _safe(row_label), border=1, fill=is_prow, align="C")

                for ci, val in enumerate(step.tableau[r]):
                    is_pcell = is_prow and step.pivot_col == ci
                    if is_pcell:
                        pdf.set_fill_color(255, 230, 100)
                    pdf.cell(data_w, row_h, _safe(_fmt(val)), border=1, fill=(is_prow or is_pcell), align="R")
                    if is_pcell:
                        pdf.set_fill_color(220, 255, 230)
                pdf.ln()

            pdf.ln(3)
            if pdf.get_y() > pdf.h - 55:
                pdf.add_page()

    return bytes(pdf.output())
