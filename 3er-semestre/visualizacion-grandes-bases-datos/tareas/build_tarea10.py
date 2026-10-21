# -*- coding: utf-8 -*-
"""
Tarea 1.0 - Box-plot de Tukey e identificacion de datos atipicos (metodo IQR).
Variable: Monoxido de Carbono (CO). Estacion mas cercana al domicilio: Country (COU).
Dataset: Calidad del aire ZMG 2024 (SIMAJ).
"""
import math
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
OUTDIR = COURSE + r"\tareas\Tarea1_0"
FIG = OUTDIR + r"\boxplot_co_country.png"
DOCX = OUTDIR + r"\Tarea1_0_VisualizacionGBD_CarlosPulidoRosas.docx"

NAVY = RGBColor(0x1F, 0x49, 0x7D)
AMBER = RGBColor(0xD4, 0x8C, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
NAVY_HEX, AMBER_HEX = "#1F497D", "#D48C00"

# ============================ 1. DATA + STATISTICS ===========================
STATION, STATION_NAME, DIST_KM = "COU", "Country (Mezquitan)", 1.05
df = pd.read_excel(DATA, sheet_name="Data")
sub = df.loc[df.STATION == STATION, ["DATE", "HOUR", "CO"]].copy()
sub["CO"] = pd.to_numeric(sub["CO"], errors="coerce")
sub = sub.dropna(subset=["CO"])
s = sub["CO"]

n = int(s.size)
vmin, vmax = float(s.min()), float(s.max())
q1, q2, q3 = [float(x) for x in np.percentile(s, [25, 50, 75])]
mean = float(s.mean())
iqr = q3 - q1
lf, uf = q1 - 1.5 * iqr, q3 + 1.5 * iqr
whis_lo = float(s[s >= lf].min())
whis_hi = float(s[s <= uf].max())
out_mask = (s < lf) | (s > uf)
outliers = sub.loc[out_mask].sort_values("CO", ascending=False)
n_low = int((s < lf).sum())
n_high = int((s > uf).sum())


def f(x):
    return f"{x:.3f}"


# --- Distancia del domicilio a cada estacion que mide CO --------------------
import math
HOME = (20.7075, -103.3578)  # Ley Iglesias 230, Quintas del Federalismo, Zapopan
CO_STATIONS = {  # clave: (nombre, lat, lon)
    "COU": ("Country (Mezquitán)", 20.6980712, -103.35811881),
    "CEN": ("Centro", 20.673844, -103.333243),
    "SMT": ("Santa Margarita", 20.723836, -103.431768),
    "MIR": ("Miravalle", 20.614511, -103.343352),
    "LDO": ("Loma Dorada", 20.631665, -103.256809),
    "PIN": ("Las Pintas", 20.576708, -103.326533),
    "SAN": ("Santa Anita", 20.5519704, -103.447256),
}


def haversine(a, b):
    R = 6371.0
    p = math.pi / 180
    dlat = (b[0] - a[0]) * p
    dlon = (b[1] - a[1]) * p
    h = (math.sin(dlat / 2) ** 2 +
         math.cos(a[0] * p) * math.cos(b[0] * p) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))


dist_rows = sorted(
    ((haversine(HOME, (la, lo)), k, nm) for k, (nm, la, lo) in CO_STATIONS.items()))


# ============================ 2. BOX PLOT FIGURE =============================
plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(6.2, 6.4))
bp = ax.boxplot(
    s, vert=True, widths=0.45, whis=1.5, patch_artist=True,
    showmeans=True, meanline=False,
    boxprops=dict(facecolor="#D9E1F2", edgecolor=NAVY_HEX, linewidth=1.6),
    medianprops=dict(color=AMBER_HEX, linewidth=2.2),
    whiskerprops=dict(color=NAVY_HEX, linewidth=1.4),
    capprops=dict(color=NAVY_HEX, linewidth=1.4),
    flierprops=dict(marker="o", markerfacecolor=AMBER_HEX, markeredgecolor=NAVY_HEX,
                    markersize=4, alpha=0.6),
    meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor=NAVY_HEX,
                   markersize=7),
)
ax.set_xticks([1]); ax.set_xticklabels([f"CO — Estación {STATION}"])
ax.set_ylabel("Monóxido de carbono (ppm)", fontsize=11, color=NAVY_HEX)
ax.set_title("Gráfica de caja de Tukey — CO (2024)", fontsize=13, color=NAVY_HEX, weight="bold")
ax.grid(axis="y", linestyle=":", alpha=0.5)

# (y_data, y_label_offset, text) — offsets separate the near-equal fence/whisker labels
ann = [(q1, 0.0, f"Q1 = {f(q1)}"), (q2, 0.0, f"Mediana = {f(q2)}"),
       (q3, 0.0, f"Q3 = {f(q3)}"), (uf, 0.045, f"Cerca sup. = {f(uf)}"),
       (whis_hi, -0.055, f"Bigote sup. = {f(whis_hi)}"),
       (vmin, 0.0, f"Mínimo = {f(vmin)}")]
for y, off, txt in ann:
    ax.annotate(txt, xy=(1.28, y + off), fontsize=8.5, va="center", color="#333333")
ax.annotate(f"Media = {f(mean)}", xy=(0.62, mean), fontsize=8.5, va="center",
            color=NAVY_HEX, ha="right")
ax.annotate(f"{n_high} datos\natípicos", xy=(1.0, uf), xytext=(0.60, uf + 0.25),
            fontsize=9, color=AMBER_HEX, weight="bold", ha="center",
            arrowprops=dict(arrowstyle="->", color=AMBER_HEX))
ax.set_xlim(0.4, 2.0)
plt.tight_layout()
plt.savefig(FIG, dpi=200, bbox_inches="tight")
plt.close()
print("Figura:", FIG)

# ============================ 3. DOCX HELPERS ================================
def set_cell_bg(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), f"{color[0]:02X}{color[1]:02X}{color[2]:02X}")
    tcPr.append(shd)


def set_row_bg(row, color):
    for c in row.cells:
        set_cell_bg(c, color)


def add_run(p, text, bold=False, italic=False, color=None, size=None, font="Calibri"):
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = color
    if size: r.font.size = Pt(size)
    r.font.name = font
    return r


def add_para(doc, text="", bold=False, italic=False, color=None, size=10,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=5):
    p = doc.add_paragraph(); p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if text: add_run(p, text, bold, italic, color, size)
    return p


def add_heading(doc, text, level=1):
    size = 13 if level == 1 else 11
    return add_para(doc, text, bold=True, color=NAVY, size=size,
                    align=WD_ALIGN_PARAGRAPH.LEFT, sb=(10 if level == 1 else 7), sa=3)


def add_caption(doc, text):
    return add_para(doc, text, italic=True, color=RGBColor(0x40, 0x40, 0x40),
                    size=9, align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=6)


def add_bullet(doc, titulo, texto):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    add_run(p, titulo + " ", bold=True, color=NAVY, size=10)
    add_run(p, texto, size=10)


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
        for ci, val in enumerate(rd):
            p = dr.cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            add_run(p, str(val), size=9)
    if caption: add_caption(doc, caption)
    else: doc.add_paragraph().paragraph_format.space_after = Pt(4)


def clear_body_after_table1(doc):
    body = doc.element.body
    sect = body.find(qn("w:sectPr"))
    tbl_count = 0; cut = None
    for i, ch in enumerate(list(body)):
        if ch.tag == qn("w:tbl"):
            tbl_count += 1
            if tbl_count == 2:
                cut = i; break
    if cut is not None:
        for el in [e for e in list(body)[cut + 1:] if e.tag != qn("w:sectPr")]:
            body.remove(el)
    if sect is not None and sect not in list(body):
        body.append(sect)


# ============================ 4. BUILD DOCX =================================
doc = Document(TEMPLATE)

hdr = doc.tables[0].rows[0].cells[1]
hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
hdr.paragraphs[3].runs[0].text = "Materia: Visualización de Grandes Bases de Datos"

title = doc.paragraphs[1]; title.clear()
r = title.add_run("Tarea 1.0 — Gráfica de caja e identificación de datos atípicos\n"
                  "Monóxido de carbono (CO), estación Country")
r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
title.alignment = WD_ALIGN_PARAGRAPH.CENTER


def set_info(row_idx, text):
    cell = doc.tables[1].rows[row_idx].cells[1]
    cell.paragraphs[0].runs[0].text = text
    for extra in cell.paragraphs[0].runs[1:]:
        extra.text = ""


set_info(1, "2 de septiembre de 2026")
set_info(2, "Tarea 1.0 — Gráfica de caja e identificación de datos atípicos")
set_info(3, "Python 3.13 — pandas, numpy, matplotlib")
set_info(4, "SIMAJ · Base de calidad del aire 2024 (BD_2024)")
set_info(5, "Análisis local (equipo personal, entorno conda MCD)")
set_info(6, "Calidad del aire ZMG 2024 — estación Country (COU); variable CO (ppm)")

clear_body_after_table1(doc)

# --- 1. Introduccion --------------------------------------------------------
add_para(doc, sb=8, sa=0)
add_heading(doc, "1. Introducción")
add_para(doc,
    "El objetivo de esta actividad es describir la distribución de la concentración de "
    "monóxido de carbono (CO) mediante la gráfica de caja de Tukey y detectar los valores "
    "atípicos con el método del rango intercuartil (IQR). Se emplea el conjunto de datos de "
    "calidad del aire 2024 de la Zona Metropolitana de Guadalajara (SIMAJ), que contiene "
    "registros horarios de contaminantes y variables meteorológicas por estación de monitoreo.")
add_para(doc,
    "Conforme a la instrucción, la variable de análisis es el monóxido de carbono (CO), "
    "medido en partes por millón (ppm), y elegí la estación de monitoreo por su cercanía a "
    "mi domicilio, según se justifica en la sección 2.1.")

# --- 2. Desarrollo ----------------------------------------------------------
add_heading(doc, "2. Desarrollo (metodología)")

add_heading(doc, "2.1 Selección de la estación de monitoreo", level=2)
add_para(doc,
    "Mi domicilio es Calle Ley Iglesias 230, colonia Quintas del Federalismo, "
    "Zapopan, Jalisco (coordenadas aproximadas 20.7075, −103.3578). La instrucción pide "
    "trabajar con la estación de monitoreo más cercana a mi domicilio. Es importante señalar "
    "que no todas las estaciones de la red SIMAJ miden monóxido de carbono; por ejemplo, las "
    "estaciones geográficamente más próximas al domicilio (Águilas y Atemajac) NO registran "
    "CO, por lo que quedan descartadas para esta variable. La Tabla 1 muestra la distancia "
    "de mi domicilio a cada estación que sí mide CO, calculada con la fórmula de Haversine "
    "sobre las coordenadas de la hoja de parámetros del conjunto de datos.", sa=3)

make_table(doc,
    ["Estación (clave)", "Distancia al domicilio (km)"],
    [(f"{nm} ({k})", f"{d:.2f}") for d, k, nm in dist_rows],
    caption="Tabla 1 — Distancia de mi domicilio (Quintas del Federalismo, Zapopan) a las "
            "estaciones SIMAJ que miden CO. La estación Country (COU) es la más cercana.",
    widths=[3.4, 2.0])

add_para(doc,
    f"La estación más cercana que mide CO es Country (clave COU), a solo {DIST_KM} km de "
    "mi domicilio —frente a 4.53 km de la siguiente—, por lo que es la estación válida para "
    f"esta tarea. De ella analizo {n} observaciones horarias de CO con lectura válida "
    "durante 2024 (descarté los registros sin dato).", sb=2)

add_heading(doc, "2.2 Estadísticos del box-plot y método IQR", level=2)
add_para(doc,
    "La gráfica de caja de Tukey resume la distribución de una variable con base en el "
    "resumen de cinco números y el rango intercuartil. Los estadísticos que la componen son:")
add_bullet(doc, "Mínimo y máximo:", "los valores extremos observados de la variable.")
add_bullet(doc, "Primer cuartil (Q1):", "valor que deja por debajo el 25 % de los datos.")
add_bullet(doc, "Mediana (Q2):", "valor central que divide la muestra en dos mitades (50 %).")
add_bullet(doc, "Tercer cuartil (Q3):", "valor que deja por debajo el 75 % de los datos.")
add_bullet(doc, "Rango intercuartil (IQR):", "IQR = Q3 − Q1; mide la dispersión del 50 % central "
           "y define la altura de la caja.")
add_bullet(doc, "Cercas (límites) de Tukey:", "cerca inferior = Q1 − 1.5·IQR y "
           "cerca superior = Q3 + 1.5·IQR; delimitan el rango de valores considerados normales.")
add_bullet(doc, "Bigotes:", "se extienden hasta el dato observado más extremo que aún cae "
           "dentro de las cercas (valores adyacentes), no hasta las cercas mismas.")
add_para(doc,
    "Método del rango intercuartil (IQR) para datos atípicos. Un dato se considera atípico "
    "(outlier) cuando se ubica fuera de las cercas de Tukey, es decir, cuando es menor que "
    "Q1 − 1.5·IQR o mayor que Q3 + 1.5·IQR. El factor 1.5 es el criterio estándar propuesto "
    "por Tukey; los valores que superan Q3 + 3·IQR suelen denominarse atípicos extremos. En "
    "la gráfica de caja, los datos atípicos se representan como puntos individuales más allá "
    "de los bigotes.", sb=2)

# --- 3. Resultados ----------------------------------------------------------
add_heading(doc, "3. Resultados")
add_para(doc, "La Tabla 2 presenta todos los estadísticos que integran la gráfica de caja de "
              "Tukey para la variable CO en la estación Country.", sa=3)
make_table(doc,
    ["Estadístico", "Valor (ppm)"],
    [("Número de observaciones válidas (n)", n),
     ("Mínimo", f(vmin)),
     ("Primer cuartil (Q1)", f(q1)),
     ("Mediana (Q2)", f(q2)),
     ("Tercer cuartil (Q3)", f(q3)),
     ("Máximo", f(vmax)),
     ("Media", f(mean)),
     ("Rango intercuartil (IQR = Q3 − Q1)", f(iqr)),
     ("Cerca inferior (Q1 − 1.5·IQR)", f(lf)),
     ("Cerca superior (Q3 + 1.5·IQR)", f(uf)),
     ("Bigote inferior (valor adyacente)", f(whis_lo)),
     ("Bigote superior (valor adyacente)", f(whis_hi)),
     ("Datos atípicos (inferiores / superiores)", f"{n_low} / {n_high}")],
    caption="Tabla 2 — Estadísticos de la gráfica de caja de Tukey para CO (estación Country, 2024).",
    widths=[3.6, 1.6])

add_para(doc, "La Figura 1 muestra la gráfica de caja correspondiente.", sb=4, sa=3)
doc.add_picture(FIG, width=Inches(3.9))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
add_caption(doc, "Figura 1 — Gráfica de caja de Tukey de la concentración de CO (ppm), "
                 "estación Country. Los puntos ámbar son los datos atípicos.")

add_para(doc,
    f"Aplicando el criterio IQR, se identificaron {n_high} datos atípicos, todos por encima "
    f"de la cerca superior ({f(uf)} ppm); no se detectaron atípicos por debajo, ya que la "
    f"cerca inferior ({f(lf)} ppm) es negativa y el CO no toma valores negativos. La Tabla 3 "
    "lista los datos atípicos con su fecha y hora de registro.", sb=2, sa=3)

out_rows = []
for i, (_, r_) in enumerate(outliers.iterrows(), 1):
    fecha = pd.to_datetime(r_["DATE"]).strftime("%Y-%m-%d")
    out_rows.append((i, fecha, f"{int(r_['HOUR']):02d}:00", f(r_["CO"])))
make_table(doc, ["#", "Fecha", "Hora", "CO (ppm)"], out_rows,
           caption=f"Tabla 3 — Datos atípicos de CO detectados por el método IQR ({n_high} valores).",
           widths=[0.5, 1.5, 1.0, 1.2])

# --- 4. Conclusiones --------------------------------------------------------
add_heading(doc, "4. Conclusiones")
add_para(doc,
    f"La concentración de CO en la estación Country durante 2024 presenta una mediana de "
    f"{f(q2)} ppm y un 50 % central entre {f(q1)} y {f(q3)} ppm (IQR = {f(iqr)}). La "
    "distribución es asimétrica hacia la derecha: la media supera a la mediana y la totalidad "
    "de los datos atípicos se localizan en la cola superior.")
add_para(doc,
    f"El método del rango intercuartil identificó {n_high} observaciones atípicas "
    f"(≈ {100*n_high/n:.1f} % de la muestra), con valores entre {f(outliers['CO'].min())} y "
    f"{f(outliers['CO'].max())} ppm. Estos picos corresponden a episodios puntuales de alta "
    "concentración —típicamente asociados a horas de máximo tráfico o a inversiones térmicas— "
    "y no a errores de medición, por lo que se conservan como observaciones válidas de interés.")
add_para(doc,
    "Aun el valor máximo registrado (" + f(vmax) + " ppm) se mantiene muy por debajo del "
    "límite de la norma mexicana NOM-021-SSA1 para CO (11 ppm en promedio de 8 horas), por lo "
    "que, pese a la presencia de datos atípicos, la calidad del aire respecto a este "
    "contaminante se mantuvo dentro de lo permitido. El ejercicio muestra cómo la gráfica de "
    "caja y el criterio IQR permiten resumir la distribución y aislar valores extremos de "
    "forma objetiva y reproducible.")

# --- Referencias (APA 7) ----------------------------------------------------
add_heading(doc, "Referencias")


def add_apa(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    p.paragraph_format.space_after = Pt(6)
    add_run(p, text, size=10)


add_apa(doc, "Frigge, M., Hoaglin, D. C., & Iglewicz, B. (1989). Some implementations "
             "of the boxplot. The American Statistician, 43(1), 50–54. "
             "https://doi.org/10.1080/00031305.1989.10475612")
add_apa(doc, "Secretaría de Medio Ambiente y Desarrollo Territorial. (2024). Sistema de "
             "Monitoreo Atmosférico de Jalisco (SIMAJ): base de datos de calidad del aire "
             "2024. Gobierno del Estado de Jalisco. https://siga.jalisco.gob.mx/aire/")
add_apa(doc, "Tukey, J. W. (1977). Exploratory data analysis. Addison-Wesley.")

doc.save(DOCX)
print("DOCX:", DOCX)
