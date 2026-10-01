# -*- coding: utf-8 -*-
"""
Tarea 1.4 - Contaminante con mayor correlacion lineal con NO2.
Estacion Centro (CEN): es la que mide NO2 (Country/COU no registra NO2).
Dispersion + recta de regresion + coeficiente de Pearson.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"C:\Users\carlo\GitHub\mcd_cucea"
TEMPLATE = BASE + r"\_recursos\plantillas\plantilla_informe_MCD.docx"
COURSE = BASE + r"\3er-semestre\visualizacion-grandes-bases-datos"
DATA = COURSE + r"\datos\BD_2024_calidad_aire.xlsx"
OUT = COURSE + r"\tareas\Tarea1_4"
NAVY = RGBColor(0x1F, 0x49, 0x7D); AMBER = RGBColor(0xD4, 0x8C, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF); GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
NAVY_HEX, AMBER_HEX = "#1F497D", "#D48C00"

NAMES = {"O3": "O₃ (ozono)", "NO": "NO (mon. de nitrógeno)", "NOX": "NOx (óxidos de N)",
         "CO": "CO (mon. de carbono)", "PM10": "PM10", "PM2.5": "PM2.5"}
UNID = {"O3": "ppm", "NO": "ppm", "NOX": "ppm", "CO": "ppm", "PM10": "µg/m³", "PM2.5": "µg/m³"}

# ============================ DATA + STATS ==================================
df = pd.read_excel(DATA, sheet_name="Data")
d = df[df.STATION == "CEN"].copy()
CAND = ["O3", "NO", "NOX", "CO", "PM10", "PM2.5"]
for c in CAND + ["NO2"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")

rows = []
for c in CAND:
    sub = d[["NO2", c]].dropna()
    r = sub["NO2"].corr(sub[c])
    b, a = np.polyfit(sub[c], sub["NO2"], 1)   # NO2 = a + b*c
    rows.append({"var": c, "r": r, "r2": r**2, "n": len(sub), "slope": b, "intercept": a})
stats = pd.DataFrame(rows).sort_values("r", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)
winner = stats.iloc[0]                                   # mayor |r| (NOX, estructural)
indep = stats[~stats["var"].isin(["NOX", "NO"])].iloc[0]  # mayor entre independientes (CO)


def f(v, dd=3):
    return f"{v:.{dd}f}"


# ============================ FIGURE: scatter grid ==========================
def fig_scatter():
    p = OUT + r"\dispersion_regresion_no2.png"
    fig, ax = plt.subplots(2, 3, figsize=(10.5, 6.6))
    order = stats["var"].tolist()
    for axx, c in zip(ax.ravel(), order):
        sub = d[["NO2", c]].dropna()
        row = stats[stats["var"] == c].iloc[0]
        axx.scatter(sub[c], sub["NO2"], s=5, alpha=0.18, color=NAVY_HEX, edgecolors="none")
        xs = np.linspace(sub[c].min(), sub[c].max(), 50)
        axx.plot(xs, row["intercept"] + row["slope"] * xs, color=AMBER_HEX, linewidth=2)
        is_top = c == winner["var"]
        axx.set_title(f"NO₂ vs {c}   r = {row['r']:+.3f}",
                      color=(AMBER_HEX if is_top else NAVY_HEX), weight="bold", fontsize=10)
        axx.set_xlabel(f"{c} ({UNID[c]})", fontsize=8)
        axx.set_ylabel("NO₂ (ppm)", fontsize=8)
        axx.grid(linestyle=":", alpha=0.4)
        if is_top:
            for s in axx.spines.values():
                s.set_edgecolor(AMBER_HEX); s.set_linewidth(2)
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


# ============================ DOCX HELPERS ==================================
def set_cell_bg(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"); tcPr.append(shd)


def add_run(p, t, bold=False, italic=False, color=None, size=None, font="Calibri"):
    r = p.add_run(t); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = color
    if size: r.font.size = Pt(size)
    r.font.name = font; return r


def add_para(doc, t="", bold=False, italic=False, color=None, size=10,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=5):
    p = doc.add_paragraph(); p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if t: add_run(p, t, bold, italic, color, size)
    return p


def add_heading(doc, t, level=1):
    return add_para(doc, t, bold=True, color=NAVY, size=(13 if level == 1 else 11),
                    align=WD_ALIGN_PARAGRAPH.LEFT, sb=(10 if level == 1 else 7), sa=3)


def add_caption(doc, t):
    return add_para(doc, t, italic=True, color=RGBColor(0x40, 0x40, 0x40), size=9,
                    align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=6)


def add_bullet(doc, titulo, texto):
    p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = Pt(4)
    add_run(p, titulo + " ", bold=True, color=NAVY, size=10); add_run(p, texto, size=10)


def make_table(doc, headers, rows_, caption=None, widths=None, hl=None):
    tbl = doc.add_table(rows=1 + len(rows_), cols=len(headers))
    tbl.style = "Table Grid"; tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    if widths:
        for i, w in enumerate(widths):
            for row in tbl.rows:
                row.cells[i].width = Inches(w)
    hr = tbl.rows[0]
    for c in hr.cells: set_cell_bg(c, NAVY)
    for ci, h in enumerate(headers):
        pp = hr.cells[ci].paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(pp, h, bold=True, color=WHITE, size=9)
    for ri, rd in enumerate(rows_):
        dr = tbl.rows[ri + 1]
        bg = RGBColor(0xFC, 0xE4, 0xB8) if hl == ri else (WHITE if ri % 2 == 0 else GRAY_L)
        for c in dr.cells: set_cell_bg(c, bg)
        for ci, v in enumerate(rd):
            pp = dr.cells[ci].paragraphs[0]
            pp.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            add_run(pp, str(v), size=9, bold=(hl == ri))
    if caption: add_caption(doc, caption)
    else: doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_apa(doc, t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.5); p.paragraph_format.first_line_indent = Inches(-0.5)
    p.paragraph_format.space_after = Pt(6); add_run(p, t, size=10)


def clear_body_after_table1(doc):
    body = doc.element.body; sect = body.find(qn("w:sectPr")); c = 0; cut = None
    for i, ch in enumerate(list(body)):
        if ch.tag == qn("w:tbl"):
            c += 1
            if c == 2: cut = i; break
    if cut is not None:
        for el in [e for e in list(body)[cut + 1:] if e.tag != qn("w:sectPr")]: body.remove(el)
    if sect is not None and sect not in list(body): body.append(sect)


# ============================ BUILD =========================================
def build():
    import os
    os.makedirs(OUT, exist_ok=True)
    p_fig = fig_scatter()

    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Visualización de Grandes Bases de Datos"
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Tarea 1.4 — Correlación de contaminantes con NO₂\n"
                   "Dispersión y regresión lineal — estación Centro")
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]; cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]: extra.text = ""
    si(1, "4 de septiembre de 2026")
    si(2, "Tarea 1.4 — Correlación con NO₂")
    si(3, "Python 3.13 — pandas, numpy, matplotlib")
    si(4, "SIMAJ · Base de calidad del aire 2024 (BD_2024)")
    si(5, "Análisis local (equipo personal, entorno conda MCD)")
    si(6, "Calidad del aire ZMG 2024 — estación Centro (CEN); contaminantes (ppm, µg/m³)")
    clear_body_after_table1(doc)

    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        "El objetivo de esta actividad es identificar el contaminante que presenta el mayor "
        "coeficiente de correlación lineal con el dióxido de nitrógeno (NO₂), apoyando la "
        "respuesta con gráficas de dispersión y rectas de regresión. Se emplea la base de "
        "calidad del aire 2024 de la Zona Metropolitana de Guadalajara (SIMAJ).")
    add_heading(doc, "1.1 Estación utilizada", level=2)
    add_para(doc,
        "Esta actividad requiere datos de NO₂. Al revisar la base se encontró que la estación "
        "Country (COU) —usada en las tareas 1.0 a 1.2— no registra NO₂ en 2024 (0 lecturas). "
        "Por ello se utiliza la estación Centro (CEN), que sí mide NO₂ (2,706 lecturas horarias) "
        "junto con O₃, NO, NOx, CO, PM10 y PM2.5, y que ya se empleó en la Tarea 1.3. El SO₂ no "
        "se registra en Centro, por lo que se excluye del análisis.")

    add_heading(doc, "2. Desarrollo (metodología)")
    add_para(doc,
        "Para cada contaminante se calculó el coeficiente de correlación lineal de Pearson (r) "
        "contra el NO₂, usando únicamente las horas con lectura válida en ambas variables "
        "(pares completos). El coeficiente r mide la fuerza y el sentido de la relación lineal "
        "(de −1 a +1). Adicionalmente se ajustó una recta de regresión por mínimos cuadrados "
        "(NO₂ = a + b·X) y se reporta el coeficiente de determinación R² = r². La exploración se "
        "apoya en las gráficas de dispersión con su recta de regresión.")

    add_heading(doc, "3. Resultados")
    add_para(doc, "La Tabla 1 ordena los contaminantes por su correlación con el NO₂.", sa=3)
    trows = [[NAMES[rr["var"]], f"{rr['r']:+.3f}", f(rr["r2"], 3), f"{int(rr['n'])}"]
             for _, rr in stats.iterrows()]
    make_table(doc, ["Contaminante (vs NO₂)", "r de Pearson", "R²", "n (pares)"], trows,
               caption="Tabla 1 — Correlación lineal de cada contaminante con el NO₂ (Centro, 2024).",
               widths=[2.7, 1.5, 1.2, 1.2], hl=0)

    add_para(doc, "La Figura 1 muestra las gráficas de dispersión de NO₂ contra cada contaminante "
                  "con su recta de regresión; en ámbar se resalta la mayor correlación.", sb=4, sa=3)
    doc.add_picture(p_fig, width=Inches(6.4))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figura 1 — Dispersión y recta de regresión de NO₂ frente a cada contaminante "
                     "(estación Centro, 2024). La pendiente positiva/negativa indica el sentido de la relación.")

    add_heading(doc, "4. Respuesta y conclusiones")
    add_para(doc,
        f"¿Cuál contaminante tiene la mayor correlación lineal con el NO₂? El coeficiente más "
        f"alto corresponde a los NOx (r = {f(winner['r'])}, R² = {f(winner['r2'],3)}). No "
        "obstante, debe interpretarse con cautela: los NOx se definen como la suma de NO y NO₂ "
        "(NOx = NO + NO₂), por lo que el NO₂ está contenido en los NOx y la correlación es, en "
        "parte, estructural y esperada.")
    add_para(doc,
        f"Entre los contaminantes de origen independiente, la mayor correlación con el NO₂ es la "
        f"del monóxido de carbono (CO, r = {f(indep['r'])}, R² = {f(indep['r2'],3)}), con recta "
        f"de regresión NO₂ = {f(indep['intercept'])} + {f(indep['slope'])}·CO. Esta asociación "
        "tiene sentido físico: tanto el NO₂ como el CO se producen principalmente por la "
        "combustión vehicular, de modo que aumentan y disminuyen juntos (horas pico, inversiones "
        "térmicas). Por ello, el CO es el mejor predictor lineal 'real' del NO₂.")
    add_para(doc,
        "En sentido inverso, el O₃ es el único con correlación negativa (r = "
        f"{f(stats[stats['var']=='O3'].iloc[0]['r'])}): el ozono se forma fotoquímicamente "
        "durante el día, cuando el NO₂ se consume, lo que explica su relación opuesta. Las "
        "partículas (PM10, PM2.5) muestran correlación positiva moderada, consistente con "
        "fuentes de combustión compartidas.")
    add_para(doc,
        "Conclusión: el contaminante con mayor coeficiente de correlación lineal con el NO₂ son "
        f"los NOx ({f(winner['r'])}) por su relación de definición; descartando esa dependencia "
        f"estructural, el contaminante más correlacionado es el CO ({f(indep['r'])}), reflejo de "
        "su origen común en la combustión vehicular.")

    add_heading(doc, "Referencias")
    add_apa(doc, "Ruiz Chávez, C. (2024). Visualización de Grandes Bases de Datos — Sesión 4: "
                 "combinación de gráficos, series de tiempo y correlación [material de clase]. "
                 "Maestría en Ciencia de los Datos, CUCEA, Universidad de Guadalajara.")
    add_apa(doc, "Secretaría de Medio Ambiente y Desarrollo Territorial. (2024). Sistema de "
                 "Monitoreo Atmosférico de Jalisco (SIMAJ): base de datos de calidad del aire "
                 "2024. Gobierno del Estado de Jalisco. https://siga.jalisco.gob.mx/aire/")
    out = OUT + r"\Tarea1_4_VisualizacionGBD_CarlosPulidoRosas.docx"
    doc.save(out); print("DOCX:", out); return out


if __name__ == "__main__":
    build()
