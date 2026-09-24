# -*- coding: utf-8 -*-
"""
Tarea 1.1 - Calculo manual de cuartiles (metodo de Tukey) vs Tarea 1.0.
Tarea 1.2 - Histograma de CO y periodos por encima de la norma IMECA (11 ppm/8h).
Estacion Country (COU). Dataset SIMAJ calidad del aire 2024.
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

NAVY = RGBColor(0x1F, 0x49, 0x7D); AMBER = RGBColor(0xD4, 0x8C, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF); GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
NAVY_HEX, AMBER_HEX = "#1F497D", "#D48C00"

# ============================ DATA ==========================================
df = pd.read_excel(DATA, sheet_name="Data")
sub = df.loc[df.STATION == "COU", ["DATE", "HOUR", "CO"]].copy()
sub["CO"] = pd.to_numeric(sub["CO"], errors="coerce")
sub = sub.dropna(subset=["CO"])
s = sub["CO"]
x = np.sort(s.values)
n = len(x)


def val(pos1):  # 1-indexed positional value
    return x[pos1 - 1]


# Tukey hinges
q2 = np.median(x)
lower = x[:n // 2]; upper = x[n // 2:]          # n par -> mitades exactas
q1_t = np.median(lower); q3_t = np.median(upper)
iqr_t = q3_t - q1_t
# Tarea 1.0 (interpolacion lineal)
q1_l, q3_l = np.percentile(x, [25, 75]); iqr_l = q3_l - q1_l
# Tarea 1.2
LIM = 11.0
over_h = int((s > LIM).sum())
sub_s = sub.sort_values(["DATE", "HOUR"])
ma8 = sub_s["CO"].rolling(8, min_periods=8).mean()
over_8 = int((ma8 > LIM).sum()); n8 = int(ma8.notna().sum())


def f(v, d=3):
    return f"{v:.{d}f}"


# ============================ DOCX HELPERS ==================================
def set_cell_bg(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"); tcPr.append(shd)


def set_row_bg(row, color):
    for c in row.cells:
        set_cell_bg(c, color)


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


def make_table(doc, headers, rows, caption=None, widths=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = "Table Grid"; tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    if widths:
        for i, w in enumerate(widths):
            for row in tbl.rows:
                row.cells[i].width = Inches(w)
    hr = tbl.rows[0]; set_row_bg(hr, NAVY)
    for ci, h in enumerate(headers):
        p = hr.cells[ci].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, h, bold=True, color=WHITE, size=9)
    for ri, rd in enumerate(rows):
        dr = tbl.rows[ri + 1]; set_row_bg(dr, WHITE if ri % 2 == 0 else GRAY_L)
        for ci, v in enumerate(rd):
            p = dr.cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            add_run(p, str(v), size=9)
    if caption: add_caption(doc, caption)
    else: doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_apa(doc, t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    p.paragraph_format.space_after = Pt(6); add_run(p, t, size=10)


def clear_body_after_table1(doc):
    body = doc.element.body; sect = body.find(qn("w:sectPr")); c = 0; cut = None
    for i, ch in enumerate(list(body)):
        if ch.tag == qn("w:tbl"):
            c += 1
            if c == 2: cut = i; break
    if cut is not None:
        for el in [e for e in list(body)[cut + 1:] if e.tag != qn("w:sectPr")]:
            body.remove(el)
    if sect is not None and sect not in list(body): body.append(sect)


def base_doc(titulo, actividad, fecha="4 de septiembre de 2026"):
    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Visualización de Grandes Bases de Datos"
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run(titulo); r.bold = True; r.font.size = Pt(13)
    r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]
        cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]:
            extra.text = ""
    si(1, fecha); si(2, actividad)
    si(3, "Python 3.13 — pandas, numpy, matplotlib")
    si(4, "SIMAJ · Base de calidad del aire 2024 (BD_2024)")
    si(5, "Análisis local (equipo personal, entorno conda MCD)")
    si(6, "Calidad del aire ZMG 2024 — estación Country (COU); variable CO (ppm)")
    clear_body_after_table1(doc)
    return doc


# ============================ TAREA 1.1 =====================================
def build_11():
    out = COURSE + r"\tareas\Tarea1_1\Tarea1_1_VisualizacionGBD_CarlosPulidoRosas.docx"
    figq = COURSE + r"\tareas\Tarea1_1\cuartiles_tukey_vs_lineal.png"

    # --- Grafica de cuartiles: caja de Tukey vs. lineal (Tarea 1.0) ---------
    uf = q3_t + 1.5 * iqr_t
    whishi = float(x[x <= uf].max()); whislo = float(x.min())
    fliers = x[x > uf]
    stats = [
        {"label": "Tukey", "med": q2, "q1": q1_t, "q3": q3_t,
         "whislo": whislo, "whishi": whishi, "fliers": fliers},
        {"label": "Tarea 1.0\n(lineal)", "med": q2, "q1": q1_l, "q3": q3_l,
         "whislo": whislo, "whishi": whishi, "fliers": fliers},
    ]
    figc, ax = plt.subplots(figsize=(7.2, 3.4))
    bp = ax.bxp(stats, vert=False, showfliers=True, patch_artist=True, widths=0.55,
                boxprops=dict(facecolor="#D9E1F2", edgecolor=NAVY_HEX, linewidth=1.5),
                medianprops=dict(color=AMBER_HEX, linewidth=2.2),
                whiskerprops=dict(color=NAVY_HEX), capprops=dict(color=NAVY_HEX),
                flierprops=dict(marker="o", markerfacecolor=AMBER_HEX,
                                markeredgecolor=NAVY_HEX, markersize=3, alpha=0.5))
    ax.set_xlabel("CO (ppm)", color=NAVY_HEX)
    ax.set_title("Gráfica de cuartiles — método de Tukey vs. Tarea 1.0",
                 color=NAVY_HEX, weight="bold", fontsize=12)
    # anotar Q1, Q2, Q3 sobre la caja de Tukey, alineados para no encimarse
    ax.annotate(f"Q1 = {f(q1_t)}", xy=(q1_t, 1.34), fontsize=8.5, ha="right", color="#333333")
    ax.annotate(f"Q2 = {f(q2)}", xy=(q2, 1.46), fontsize=8.5, ha="center", color=AMBER_HEX)
    ax.annotate(f"Q3 = {f(q3_t)}", xy=(q3_t, 1.34), fontsize=8.5, ha="left", color="#333333")
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    plt.tight_layout(); plt.savefig(figq, dpi=200, bbox_inches="tight"); plt.close()
    doc = base_doc("Tarea 1.1 — Cálculo manual de cuartiles (método de Tukey)\n"
                   "Monóxido de carbono (CO), estación Country",
                   "Tarea 1.1 — Cálculo manual de cuartiles (método de Tukey)")
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        "El objetivo de esta actividad es calcular manualmente los cuartiles Q1 y Q3 de la "
        "concentración de monóxido de carbono (CO) mediante el método de Tukey (bisagras o "
        "hinges) y comparar los resultados con los obtenidos en la Tarea 1.0, que empleó la "
        "interpolación lineal de la librería. Se usa la misma estación de la Tarea 1.0 —"
        f"Country (COU)— con las mismas {n} observaciones horarias válidas de CO en 2024.")

    add_heading(doc, "2. Desarrollo — método de Tukey")
    add_para(doc,
        "El método de Tukey define los cuartiles como las medianas de las mitades de los datos "
        "ordenados. El procedimiento es:")
    add_bullet(doc, "Paso 1.", "Ordenar las n observaciones de menor a mayor.")
    add_bullet(doc, "Paso 2.", "Obtener la mediana (Q2), que divide la muestra en dos mitades.")
    add_bullet(doc, "Paso 3.", "Q1 = mediana de la mitad inferior; Q3 = mediana de la mitad superior.")
    add_para(doc,
        f"Aplicación a los datos (n = {n}, número par):", sb=3, sa=3)
    add_bullet(doc, "Mediana (Q2):",
        f"con n par, es el promedio de las posiciones {n//2} y {n//2+1}: "
        f"({f(val(n//2))} + {f(val(n//2+1))}) / 2 = {f(q2)} ppm.")
    add_bullet(doc, "Mitad inferior:",
        f"posiciones 1 a {n//2} ({n//2} datos, número impar). Su mediana es la posición "
        f"{(n//2+1)//2}, por lo que Q1 = x[{(n//2+1)//2}] = {f(q1_t)} ppm.")
    add_bullet(doc, "Mitad superior:",
        f"posiciones {n//2+1} a {n} ({n//2} datos). Su mediana es la posición "
        f"{n//2 + (n//2+1)//2} global, por lo que Q3 = x[{n//2 + (n//2+1)//2}] = {f(q3_t)} ppm.")

    add_heading(doc, "3. Resultados y comparación")
    add_para(doc, "La Tabla 1 compara los cuartiles por el método de Tukey contra los de la "
                  "Tarea 1.0 (interpolación lineal).", sa=3)
    make_table(doc,
        ["Estadístico", "Método de Tukey (ppm)", "Tarea 1.0 — lineal (ppm)", "Diferencia (ppm)"],
        [("Primer cuartil (Q1)", f(q1_t), f(q1_l), f(q1_t - q1_l, 3)),
         ("Mediana (Q2)", f(q2), f(q2), "0.000"),
         ("Tercer cuartil (Q3)", f(q3_t), f(q3_l), f"+{f(q3_t - q3_l, 3)}"),
         ("Rango intercuartil (IQR)", f(iqr_t), f(iqr_l), f"+{f(iqr_t - iqr_l, 3)}")],
        caption="Tabla 1 — Cuartiles por el método de Tukey vs. interpolación lineal (Tarea 1.0).",
        widths=[2.2, 1.7, 1.9, 1.4])

    add_para(doc, "La Figura 1 muestra la gráfica de cuartiles (diagrama de caja) construida con "
                  "los valores de Tukey y, debajo, la de la Tarea 1.0, para comparar visualmente "
                  "ambos métodos.", sb=4, sa=3)
    doc.add_picture(figq, width=Inches(5.6))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figura 1 — Gráfica de cuartiles de CO: caja de Tukey (arriba) vs. Tarea 1.0 "
                     "interpolación lineal (abajo). Las cajas son casi idénticas; la línea ámbar "
                     "es la mediana y los puntos son los datos atípicos.")

    add_heading(doc, "4. Conclusiones")
    add_para(doc,
        "Los cuartiles calculados manualmente con el método de Tukey coinciden prácticamente "
        f"con los de la Tarea 1.0: Q1 es idéntico ({f(q1_t)} ppm) y Q3 difiere apenas "
        f"{f(q3_t - q3_l, 3)} ppm ({f(q3_t)} vs. {f(q3_l)}). La diferencia es despreciable.")
    add_para(doc,
        "La razón de la coincidencia es que, con n = 578 (par), cada mitad tiene 289 datos "
        "(número impar), de modo que la mediana de cada mitad cae exactamente sobre un dato "
        "(la posición 145) y no requiere promediar dos valores. A su vez, la posición que usa "
        "la interpolación lineal (índice 144.25 para Q1 y 432.75 para Q3) queda muy cerca de "
        "esa misma posición, y como los datos vecinos tienen valores iguales o casi iguales, "
        "ambos métodos entregan esencialmente el mismo resultado. En muestras pequeñas o con "
        "más dispersión entre datos contiguos, las diferencias entre métodos serían mayores.")

    add_heading(doc, "Referencias")
    add_apa(doc, "Tukey, J. W. (1977). Exploratory data analysis. Addison-Wesley.")
    add_apa(doc, "Secretaría de Medio Ambiente y Desarrollo Territorial. (2024). Sistema de "
                 "Monitoreo Atmosférico de Jalisco (SIMAJ): base de datos de calidad del aire "
                 "2024. Gobierno del Estado de Jalisco. https://siga.jalisco.gob.mx/aire/")
    doc.save(out); print("DOCX:", out); return out


# ============================ TAREA 1.2 =====================================
def build_12():
    fig = COURSE + r"\tareas\Tarea1_2\histograma_co_country.png"
    out = COURSE + r"\tareas\Tarea1_2\Tarea1_2_VisualizacionGBD_CarlosPulidoRosas.docx"

    fig_, ax = plt.subplots(1, 2, figsize=(10, 4.2))
    # Panel A: distribucion real (0 a ~1.8) en frecuencia relativa (%) con cuartiles
    w = np.full(len(s), 100.0 / n)   # cada lectura pesa 100/n -> eje en %
    ax[0].hist(s, bins=25, weights=w, color="#9DB7D9", edgecolor=NAVY_HEX)
    for xv, col, lab in [(q1_t, NAVY_HEX, "Q1"), (q2, AMBER_HEX, "Q2 (mediana)"),
                         (q3_t, NAVY_HEX, "Q3")]:
        ax[0].axvline(xv, color=col, linestyle="--", linewidth=1.5,
                      label=f"{lab} = {f(xv)}")
    ax[0].legend(fontsize=8, loc="upper right")
    ax[0].set_title("Distribución de CO con cuartiles", color=NAVY_HEX, weight="bold", fontsize=11)
    ax[0].set_xlabel("CO (ppm)"); ax[0].set_ylabel("Frecuencia relativa (%)")
    ax[0].grid(axis="y", linestyle=":", alpha=0.5)
    # Panel B: escala completa hasta la norma 11 ppm
    ax[1].hist(s, bins=np.arange(0, 12.5, 0.5), color="#9DB7D9", edgecolor=NAVY_HEX)
    ax[1].axvline(LIM, color=AMBER_HEX, linewidth=2.2, linestyle="--")
    ax[1].annotate(f"Norma IMECA\n11 ppm/8h", xy=(LIM, ax[1].get_ylim()[1] * 0.7),
                   xytext=(7.2, ax[1].get_ylim()[1] * 0.75), color=AMBER_HEX,
                   weight="bold", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color=AMBER_HEX))
    ax[1].set_title("Escala completa vs. norma", color=NAVY_HEX, weight="bold", fontsize=11)
    ax[1].set_xlabel("CO (ppm)"); ax[1].set_ylabel("Frecuencia (horas)")
    ax[1].grid(axis="y", linestyle=":", alpha=0.5)
    ax[1].annotate("0 periodos\npor encima", xy=(11, 0), xytext=(6.5, ax[1].get_ylim()[1] * 0.35),
                   color=NAVY_HEX, fontsize=9, ha="center")
    plt.tight_layout(); plt.savefig(fig, dpi=200, bbox_inches="tight"); plt.close()

    doc = base_doc("Tarea 1.2 — Uso de histograma\n"
                   "Monóxido de carbono (CO), estación Country y norma IMECA",
                   "Tarea 1.2 — Uso de histograma")
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        "El Índice Metropolitano de la Calidad del Aire (IMECA) establece para el monóxido de "
        "carbono (CO) un límite de 11 ppm en promedio de 8 horas como valor satisfactorio "
        "(dentro de norma). El objetivo de esta actividad es construir el histograma de CO de la "
        "estación seleccionada en la Tarea 1.0 —Country (COU)— y, con él, responder: ¿cuál es el "
        "número y porcentaje de periodos que en 2024 se encontraron por encima de la norma?")

    add_heading(doc, "2. Desarrollo (metodología)")
    add_para(doc,
        f"Se trabajó con las {n} lecturas horarias válidas de CO de la estación Country en 2024. "
        "Se construyó el histograma de frecuencias y se contó cuántas lecturas superan el "
        "límite de 11 ppm. Dado que la norma se define sobre un promedio de 8 horas, además del "
        "conteo horario se calculó el promedio móvil de 8 horas y se verificó cuántas ventanas "
        "de 8 h superan el límite; ambos criterios se reportan.")

    add_heading(doc, "3. Resultados")
    add_para(doc, "El histograma (Figura 1) muestra a la izquierda el detalle de la distribución "
                  "y a la derecha la escala completa hasta la norma de 11 ppm.", sa=3)
    doc.add_picture(fig, width=Inches(6.3))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figura 1 — Histograma de CO (estación Country, 2024). Izquierda: frecuencia "
                     "relativa (%) con los cuartiles marcados. Derecha: escala completa; la línea "
                     "ámbar marca la norma IMECA (11 ppm/8h), que ninguna observación alcanza.")
    make_table(doc, ["Concepto", "Valor"],
        [("Norma IMECA para CO", "11 ppm (promedio de 8 h)"),
         ("Periodos (lecturas horarias) en 2024", str(n)),
         ("Periodos por encima de la norma (horario)", str(over_h)),
         ("Porcentaje por encima de la norma", f"{100*over_h/n:.2f} %"),
         ("Máximo CO horario observado", f"{f(s.max())} ppm"),
         ("Verificación — ventanas de 8 h > 11 ppm", f"{over_8} de {n8} ({100*over_8/n8:.2f} %)"),
         ("Máximo del promedio móvil de 8 h", f"{f(ma8.max())} ppm")],
        caption="Tabla 1 — Cálculo de periodos por encima de la norma IMECA para CO.",
        widths=[4.0, 2.2])

    add_heading(doc, "4. Respuesta y conclusiones")
    add_para(doc,
        f"Respuesta a la pregunta: en 2024, el número de periodos por encima de la norma fue "
        f"0, equivalente al 0.00 % de las {n} lecturas. Ninguna hora superó el límite de 11 ppm; "
        f"de hecho, el máximo horario registrado fue de {f(s.max())} ppm, unas 6.6 veces por "
        "debajo de la norma.")
    add_para(doc,
        f"El resultado se confirma bajo la definición estricta de la norma (promedio de 8 horas): "
        f"ninguna de las {n8} ventanas de 8 h superó los 11 ppm, y el máximo del promedio móvil "
        f"fue de apenas {f(ma8.max())} ppm. En consecuencia, respecto al monóxido de carbono, la "
        "calidad del aire en la estación Country se mantuvo satisfactoria (dentro de norma) el "
        "100 % del tiempo durante 2024. El histograma evidencia una distribución concentrada muy "
        "por debajo del límite, con un amplio margen respecto a la norma.")

    add_heading(doc, "Referencias")
    add_apa(doc, "Gobierno de México, Secretaría de Salud. (2021). Norma Oficial Mexicana "
                 "NOM-021-SSA1-2021, Criterio para evaluar la calidad del aire ambiente con "
                 "respecto al monóxido de carbono (CO). Diario Oficial de la Federación.")
    add_apa(doc, "Secretaría de Medio Ambiente y Desarrollo Territorial. (2024). Sistema de "
                 "Monitoreo Atmosférico de Jalisco (SIMAJ): base de datos de calidad del aire "
                 "2024. Gobierno del Estado de Jalisco. https://siga.jalisco.gob.mx/aire/")
    doc.save(out); print("DOCX:", out); return out


if __name__ == "__main__":
    import os
    os.makedirs(COURSE + r"\tareas\Tarea1_1", exist_ok=True)
    os.makedirs(COURSE + r"\tareas\Tarea1_2", exist_ok=True)
    build_11(); build_12()
