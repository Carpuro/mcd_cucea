"""
Generates the final deliverable PDF for TrabajoFinal — Métodos Estadísticos Multivariados.
Uses the MCD report template (python-docx) and converts to PDF via Word (win32com).
"""

import os
import shutil
import copy
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
TEMPLATE     = Path("C:/Users/carlo/GitHub/mcd_cucea/_recursos/plantillas/plantilla_informe_MCD.docx")
LOGO         = Path("C:/Users/carlo/GitHub/mcd_cucea/_recursos/logos/logo_udeg_flat.png")
OUTPUT_DIR   = SCRIPT_DIR / "output"
ENTREGABLES  = SCRIPT_DIR / "entregables"
DOCX_OUT     = ENTREGABLES / "TrabajoFinal_MetodosMultivariados_CarlosPulidoRosas.docx"
PDF_OUT      = ENTREGABLES / "TrabajoFinal_MetodosMultivariados_CarlosPulidoRosas.pdf"

ENTREGABLES.mkdir(exist_ok=True)

# ── Style constants ────────────────────────────────────────────────────────────
NAVY   = RGBColor(0x1A, 0x23, 0x7E)
AMBER  = RGBColor(0xD4, 0x8C, 0x00)
BLACK  = RGBColor(0x00, 0x00, 0x00)
FONT   = "Calibri"


# ── Helpers ───────────────────────────────────────────────────────────────────

def set_run_style(run, bold=False, size=11, color=BLACK, italic=False):
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.name = FONT


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 8)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    size = {1: 13, 2: 11.5, 3: 11}[level]
    set_run_style(run, bold=True, size=size, color=NAVY)
    return p


def add_body(doc, text, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(space_after)
    run = p.add_run(text)
    set_run_style(run, size=11)
    return p


def add_figure(doc, img_path, caption, width_cm=14):
    if not img_path.exists():
        add_body(doc, f"[Figura no encontrada: {img_path.name}]")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run()
    run.add_picture(str(img_path), width=Cm(width_cm))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    r = cap.add_run(caption)
    set_run_style(r, italic=True, size=9.5, color=RGBColor(0x55, 0x55, 0x55))


def add_kv_table(doc, rows_data, col_widths=(4, 11)):
    """rows_data: list of (label, value) tuples."""
    table = doc.add_table(rows=len(rows_data), cols=2)
    table.style = "Table Grid"
    table.autofit = False
    for i, (label, value) in enumerate(rows_data):
        cell_label = table.cell(i, 0)
        cell_value = table.cell(i, 1)
        cell_label.width = Cm(col_widths[0])
        cell_value.width = Cm(col_widths[1])
        r = cell_label.paragraphs[0].add_run(label)
        set_run_style(r, bold=True, size=10, color=NAVY)
        r2 = cell_value.paragraphs[0].add_run(value)
        set_run_style(r2, size=10)
    return table


def add_data_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    # header row
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        _shade_cell(cell, "1A237E")
        r = cell.paragraphs[0].add_run(h)
        set_run_style(r, bold=True, size=9.5, color=RGBColor(0xFF, 0xFF, 0xFF))
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    # data rows
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            if i % 2 == 0:
                _shade_cell(cell, "E8EAF6")
            r = cell.paragraphs[0].add_run(str(val))
            set_run_style(r, size=9.5)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if col_widths:
        for i in range(len(rows) + 1):
            for j, w in enumerate(col_widths):
                table.cell(i, j).width = Cm(w)
    return table


def _shade_cell(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def replace_cell_text(cell, new_text, bold=None):
    for p in cell.paragraphs:
        for run in p.runs:
            if bold is not None:
                run.bold = bold
            run.text = ""
    cell.paragraphs[0].add_run(new_text)


def clear_body_after_tables(doc):
    """Remove everything after the first two tables (logo table + metadata table)."""
    body = doc.element.body
    tables_found = 0
    elements_to_remove = []
    for elem in list(body):
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag == "tbl":
            tables_found += 1
            if tables_found > 2:
                elements_to_remove.append(elem)
        elif tag == "sectPr":
            continue
        elif tables_found >= 1:
            elements_to_remove.append(elem)
    for elem in elements_to_remove:
        body.remove(elem)


# ── Build the document ────────────────────────────────────────────────────────

def build_docx():
    doc = Document(str(TEMPLATE))

    # --- Table 0: header institution info ---
    t0 = doc.tables[0]
    # Cell [0,0]: logo
    cell_logo = t0.cell(0, 0)
    for p in cell_logo.paragraphs:
        for run in p.runs:
            run.text = ""
    cell_logo.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_run = cell_logo.paragraphs[0].add_run()
    logo_run.add_picture(str(LOGO), height=Cm(1.8))

    # Cell [0,1]: institution text — fix the materia line
    cell_info = t0.cell(0, 1)
    for p in cell_info.paragraphs:
        for run in p.runs:
            if "[NOMBRE DE LA MATERIA]" in run.text:
                run.text = run.text.replace(
                    "[NOMBRE DE LA MATERIA]",
                    "Métodos Estadísticos Multivariados"
                )
            if "2º S" in run.text or "2do" in run.text.lower() or "2°" in run.text:
                run.text = run.text.replace("2º Semestre", "2do Semestre")

    # --- Table 1: metadata ---
    t1 = doc.tables[1]
    meta = {
        0: ("Alumno:", "Carlos Pulido Rosas"),
        1: ("Fecha:", "29 de mayo de 2026"),
        2: ("Actividad:", "Trabajo Final — Índice de Marginación Municipal mediante PCA"),
        3: ("Herramienta:", "Python 3.13 · scikit-learn · pandas · geopandas · matplotlib"),
        4: ("Versión:", "sklearn 1.5 · pandas 2.x · numpy 1.26"),
        5: ("Entorno:", "Conda env MCD — katana (Windows 11)"),
        6: ("Dataset:", "IMM_2020.xls — CONAPO, Índice de Marginación Municipal 2020"),
    }
    for i, (label, value) in meta.items():
        row = t1.rows[i]
        # label cell
        for p in row.cells[0].paragraphs:
            for run in p.runs:
                run.text = ""
        row.cells[0].paragraphs[0].add_run(label).bold = True
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = NAVY
        row.cells[0].paragraphs[0].runs[0].font.name = FONT
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(10)
        # value cell
        for p in row.cells[1].paragraphs:
            for run in p.runs:
                run.text = ""
        vrun = row.cells[1].paragraphs[0].add_run(value)
        vrun.font.color.rgb = NAVY
        vrun.font.name = FONT
        vrun.font.size = Pt(10)

    # --- Clear placeholder body paragraphs ---
    clear_body_after_tables(doc)

    # ── 0. Title ──────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(6)
    r = p.add_run("Índice de Marginación Municipal mediante PCA")
    set_run_style(r, bold=True, size=15, color=NAVY)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(16)
    rs = sub.add_run(
        "Construcción de un índice sintético para los 2,469 municipios de México "
        "(Censo 2020), clasificación en cinco grados mediante K-means y comparación "
        "con el índice oficial CONAPO DP2."
    )
    set_run_style(rs, size=10.5, color=RGBColor(0x44, 0x44, 0x44), italic=True)

    # ── 1. Introducción ───────────────────────────────────────────────────────
    add_heading(doc, "1. Introducción")
    add_body(doc,
        "El índice de marginación permite identificar y cuantificar las carencias que "
        "afectan a la población en dimensiones como educación, salud, servicios básicos "
        "e ingresos. El Consejo Nacional de Población (CONAPO) calcula oficialmente este "
        "índice a través de la metodología DP2 (distancia al patrón de desarrollo). "
        "En este trabajo se replica dicho índice mediante Análisis de Componentes "
        "Principales (PCA), utilizando las mismas nueve variables del Censo 2020, y se "
        "clasifica a los municipios en cinco grados de marginación mediante K-means. "
        "Finalmente, se georreferencian los resultados sobre la Zona Metropolitana de "
        "Guadalajara (ZMG) y se evalúa la concordancia con el índice oficial."
    )

    # ── 2. Base de datos ──────────────────────────────────────────────────────
    add_heading(doc, "2. Base de datos")
    add_body(doc,
        "Se utiliza el archivo IMM_2020.xls publicado por CONAPO, que contiene los "
        "indicadores socioeconómicos del Censo de Población y Vivienda 2020 a nivel "
        "municipal (n = 2,469 municipios). La clave geográfica CVEGEO (5 dígitos) se "
        "construye a partir del campo CVE_MUN. No se detectaron valores perdidos en "
        "ninguna de las nueve variables utilizadas para el PCA."
    )

    add_heading(doc, "2.1 Variables de análisis", level=2)
    add_data_table(
        doc,
        headers=["Variable", "Dimensión", "Descripción"],
        rows=[
            ("ANALF",  "Educación",     "% Pob. 15+ analfabeta"),
            ("SBASC",  "Educación",     "% Pob. 15+ sin educación básica"),
            ("OVSDE",  "Servicios",     "% Ocupantes en viv. sin drenaje"),
            ("OVSEE",  "Servicios",     "% Ocupantes en viv. sin electricidad"),
            ("OVSAE",  "Servicios",     "% Ocupantes en viv. sin agua entubada"),
            ("OVPT",   "Vivienda",      "% Ocupantes en viv. con piso de tierra"),
            ("VHAC",   "Hacinamiento",  "% Viviendas con hacinamiento"),
            ("PL5000", "Dispersión",    "% Pob. en localidades < 5,000 hab."),
            ("PO2SM",  "Ingreso",       "% Pob. ocupada con ingresos < 2 sal. mín."),
        ],
        col_widths=[2.2, 2.8, 10],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # ── 3. Análisis exploratorio ───────────────────────────────────────────────
    add_heading(doc, "3. Análisis Exploratorio")

    add_heading(doc, "3.1 Estadísticas descriptivas", level=2)
    add_data_table(
        doc,
        headers=["Estadístico", "ANALF", "SBASC", "OVSDE", "OVSEE", "OVSAE", "OVPT", "VHAC", "PL5000", "PO2SM"],
        rows=[
            ("count", "2469", "2469", "2469", "2469", "2469", "2469", "2469", "2469", "2469"),
            ("mean",  "10.16", "45.85", "3.16", "1.50", "6.12", "7.99", "26.57", "69.90", "82.14"),
            ("std",   "7.63",  "13.98", "5.29", "2.77", "9.25", "8.97", "10.59", "35.27", "11.83"),
            ("min",   "0.35",  "5.54",  "0.00", "0.00", "0.00", "0.00", "3.95",  "0.00",  "28.45"),
            ("25%",   "4.43",  "35.74", "0.65", "0.37", "0.88", "1.65", "18.73", "40.13", "74.62"),
            ("50%",   "8.20",  "46.34", "1.43", "0.83", "2.45", "4.71", "25.00", "100.00","84.64"),
            ("75%",   "13.79", "55.86", "3.34", "1.68", "7.29", "11.03","32.82", "100.00","91.62"),
            ("max",   "53.07", "88.33", "64.45","53.07","81.79","68.15","69.56", "100.00","100.00"),
        ],
        col_widths=[2.2, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.8, 1.8],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    add_heading(doc, "3.2 Distribuciones", level=2)
    add_figure(doc, OUTPUT_DIR / "distributions.png",
               "Figura 1. Distribución de las nueve variables de marginación (2,469 municipios).")

    add_heading(doc, "3.3 Matriz de correlaciones", level=2)
    add_body(doc,
        "Las variables de educación (ANALF, SBASC) y los indicadores de ingreso (PO2SM) "
        "presentan las correlaciones más altas entre sí (|r| > 0.70), lo que sugiere un "
        "factor latente común. Esta estructura multivariada justifica la aplicación de PCA."
    )
    add_figure(doc, OUTPUT_DIR / "correlation_matrix.png",
               "Figura 2. Matriz de correlaciones de Pearson entre las variables de marginación.")

    # ── 4. Pruebas de adecuación ───────────────────────────────────────────────
    add_heading(doc, "4. Pruebas de Adecuación para PCA")
    add_body(doc,
        "Antes de aplicar PCA se verificó la adecuación de los datos con dos pruebas estándar."
    )

    add_heading(doc, "4.1 Prueba KMO (Kaiser-Meyer-Olkin)", level=2)
    add_data_table(
        doc,
        headers=["Variable", "KMO"],
        rows=[
            ("ANALF", "0.8429"), ("SBASC", "0.8179"), ("OVSDE", "0.7088"),
            ("OVSEE", "0.7172"), ("OVSAE", "0.9184"), ("OVPT",  "0.8471"),
            ("VHAC",  "0.8209"), ("PL5000","0.8377"), ("PO2SM", "0.8491"),
            ("KMO Global", "0.8209 — Muy bueno"),
        ],
        col_widths=[4, 11],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_body(doc,
        "Un KMO global de 0.82 (≥ 0.80) confirma que los patrones de correlación son "
        "compactos y el PCA producirá componentes interpretables."
    )

    add_heading(doc, "4.2 Prueba de Esfericidad de Bartlett", level=2)
    add_data_table(
        doc,
        headers=["Estadístico", "Valor"],
        rows=[
            ("Chi-cuadrado", "11,158.03"),
            ("p-valor", "< 0.0001"),
            ("Decisión", "Se rechaza H₀ — datos ADECUADOS para PCA"),
        ],
        col_widths=[5, 10],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ── 5. Índice PCA (1 componente) ──────────────────────────────────────────
    add_heading(doc, "5. Índice de Marginación: Un Componente Principal")
    add_body(doc,
        "Se aplica PCA sobre las nueve variables estandarizadas (µ=0, σ=1). Se retiene "
        "únicamente el primer componente principal (CP1) como índice sintético de "
        "marginación, siguiendo el criterio de parsimonia. El signo del componente se "
        "orienta para que puntajes más altos correspondan a mayor marginación."
    )

    add_heading(doc, "5.1 Eigenvalor y varianza explicada", level=2)
    add_data_table(
        doc,
        headers=["Métrica", "Valor"],
        rows=[
            ("Eigenvalor CP1", "4.4270"),
            ("Varianza explicada", "49.17%"),
        ],
        col_widths=[6, 9],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    add_heading(doc, "5.2 Cargas factoriales CP1", level=2)
    add_data_table(
        doc,
        headers=["Variable", "Carga CP1"],
        rows=[
            ("ANALF",  "0.4111"), ("SBASC",  "0.3947"), ("OVPT",   "0.3715"),
            ("PO2SM",  "0.3669"), ("VHAC",   "0.3632"), ("PL5000", "0.2951"),
            ("OVSEE",  "0.2652"), ("OVSAE",  "0.2384"), ("OVSDE",  "0.2374"),
        ],
        col_widths=[4, 11],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_figure(doc, OUTPUT_DIR / "loadings_pc1.png",
               "Figura 3. Cargas factoriales del primer componente principal.")

    add_heading(doc, "5.3 Municipios extremos", level=2)
    add_data_table(
        doc,
        headers=["Municipio", "Estado", "Índice PCA"],
        rows=[
            ("Batopilas de Manuel Gómez Morín", "Chihuahua",        "+14.117"),
            ("Del Nayar",                        "Nayarit",          "+10.866"),
            ("Mezquital",                        "Durango",          "+10.720"),
            ("Cochoapa el Grande",               "Guerrero",         "+10.284"),
            ("Mezquitic",                        "Jalisco",           "+9.419"),
            ("—",                               "—",                "—"),
            ("Benito Juárez",                    "Ciudad de México",  "−5.463"),
            ("San Pedro Garza García",           "Nuevo León",        "−5.029"),
            ("San Nicolás de los Garza",         "Nuevo León",        "−4.657"),
        ],
        col_widths=[6.5, 4.5, 4],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ── 6. K-means ────────────────────────────────────────────────────────────
    add_heading(doc, "6. Clasificación mediante K-means")
    add_body(doc,
        "Se aplica K-means (k=5, n_init=25) sobre el índice PCA para clasificar los "
        "2,469 municipios en cinco grados de marginación ordenados de menor a mayor. "
        "Los centros resultantes son bien separados y los grupos son coherentes con la "
        "distribución del índice."
    )

    add_heading(doc, "6.1 Distribución de municipios por grado", level=2)
    add_data_table(
        doc,
        headers=["Grado", "Centro del grupo", "Municipios", "% Total"],
        rows=[
            ("Muy bajo", "−2.7178", "473",  "19.16%"),
            ("Bajo",     "−0.9862", "763",  "30.90%"),
            ("Medio",    " 0.6868", "741",  "30.01%"),
            ("Alto",     " 2.5879", "412",  "16.69%"),
            ("Muy alto", " 5.6755",  "80",   "3.24%"),
        ],
        col_widths=[3.5, 3.5, 3.5, 4.5],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_figure(doc, OUTPUT_DIR / "kmeans_results.png",
               "Figura 4. Frecuencia y distribución del índice PCA por grado K-means.")

    # ── 7. Criterio Kaiser ────────────────────────────────────────────────────
    add_heading(doc, "7. PCA con Criterio de Kaiser")
    add_body(doc,
        "Aplicando el criterio de Kaiser (eigenvalor > 1) se retienen dos componentes "
        "principales, que en conjunto explican el 63.45% de la varianza total."
    )

    add_heading(doc, "7.1 Tabla de eigenvalores", level=2)
    add_data_table(
        doc,
        headers=["Componente", "Eigenvalor", "Varianza (%)", "Var. Acumulada (%)", "Decisión"],
        rows=[
            ("CP1", "4.4270", "49.17", "49.17", "✓ Retener"),
            ("CP2", "1.2858", "14.28", "63.45", "✓ Retener"),
            ("CP3", "0.8408",  "9.34", "72.79", "— Descartar"),
            ("CP4", "0.7445",  "8.27", "81.06", "— Descartar"),
            ("CP5", "0.5666",  "6.29", "87.35", "— Descartar"),
            ("CP6", "0.3986",  "4.43", "91.78", "— Descartar"),
            ("CP7", "0.3259",  "3.62", "95.40", "— Descartar"),
            ("CP8", "0.2472",  "2.75", "98.14", "— Descartar"),
            ("CP9", "0.1672",  "1.86", "100.00","— Descartar"),
        ],
        col_widths=[2.5, 2.5, 2.8, 3.5, 3.7],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_figure(doc, OUTPUT_DIR / "pca_kaiser_scree.png",
               "Figura 5. Diagrama de sedimentación (Scree plot) y varianza explicada acumulada.")

    add_heading(doc, "7.2 Cargas factoriales — 2 componentes Kaiser", level=2)
    add_data_table(
        doc,
        headers=["Variable", "CP1", "CP2", "Comunalidad"],
        rows=[
            ("ANALF",  "0.411", "−0.109", "0.181"),
            ("SBASC",  "0.395", "−0.291", "0.241"),
            ("OVSDE",  "0.237",  "0.510", "0.316"),
            ("OVSEE",  "0.265",  "0.561", "0.385"),
            ("OVSAE",  "0.238",  "0.278", "0.134"),
            ("OVPT",   "0.372",  "0.119", "0.152"),
            ("VHAC",   "0.363",  "0.022", "0.132"),
            ("PL5000", "0.295", "−0.332", "0.197"),
            ("PO2SM",  "0.367", "−0.356", "0.261"),
        ],
        col_widths=[3, 3, 3, 6],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_figure(doc, OUTPUT_DIR / "kaiser_loadings_heatmap.png",
               "Figura 6. Mapa de calor de cargas factoriales — 2 componentes Kaiser.")

    # ── 8. Comparación entre procedimientos ───────────────────────────────────
    add_heading(doc, "8. Comparación entre Procedimientos")
    add_body(doc,
        "Se compara el índice de un componente contra el enfoque Kaiser de dos componentes. "
        "La correlación entre INDEX_PCA (CP1 único) y COMP1 (Kaiser) es de r = 1.0, "
        "confirmando que el primer componente es idéntico en ambos enfoques. "
        "La diferencia radica en que Kaiser captura una dimensión adicional (CP2) que "
        "refleja el contraste entre hacinamiento urbano y dispersión rural."
    )
    add_data_table(
        doc,
        headers=["Criterio", "Componentes", "Varianza explicada", "Uso recomendado"],
        rows=[
            ("1 Componente",    "CP1",     "49.17%", "Índice único de marginación, ranking, mapas"),
            ("Kaiser",          "CP1+CP2", "63.45%", "Análisis multidimensional, perfiles municipales"),
        ],
        col_widths=[3, 2.8, 3.5, 5.7],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_figure(doc, OUTPUT_DIR / "comparison_1cp_kaiser.png",
               "Figura 7. Relación entre el índice de 1 CP y los componentes Kaiser.")

    # ── 9. Georreferenciación ZMG ─────────────────────────────────────────────
    add_heading(doc, "9. Georreferenciación — Zona Metropolitana de Guadalajara")
    add_body(doc,
        "Se aplican los índices construidos a los nueve municipios de la ZMG según la "
        "delimitación CONAPO, usando geometrías del Marco Geoestadístico GADM v4.1. "
        "La ZMG concentra municipios de marginación Muy baja, consistente con ser "
        "la segunda área metropolitana más importante de México."
    )

    add_heading(doc, "9.1 Resultados ZMG", level=2)
    add_data_table(
        doc,
        headers=["Municipio", "Índice PCA", "Grado PCA", "Grado CONAPO"],
        rows=[
            ("Tonalá",                          "−0.629", "Bajo",     "Bajo"),
            ("Zapotlanejo",                     "−1.682", "Bajo",     "Muy bajo"),
            ("Ixtlahuacán de los Membrillos",   "−2.304", "Muy bajo", "Muy bajo"),
            ("El Salto",                        "−2.617", "Muy bajo", "Muy bajo"),
            ("Juanacatlán",                     "−3.149", "Muy bajo", "Muy bajo"),
            ("Tlajomulco de Zúñiga",            "−3.555", "Muy bajo", "Muy bajo"),
            ("San Pedro Tlaquepaque",           "−3.676", "Muy bajo", "Muy bajo"),
            ("Guadalajara",                     "−4.126", "Muy bajo", "Muy bajo"),
            ("Zapopan",                         "−4.155", "Muy bajo", "Muy bajo"),
        ],
        col_widths=[5.5, 2.8, 2.8, 3.9],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    add_figure(doc, OUTPUT_DIR / "map_zmg_pca_index.png",
               "Figura 8. Índice PCA continuo — Zona Metropolitana de Guadalajara.", width_cm=12)
    add_figure(doc, OUTPUT_DIR / "map_zmg_kmeans.png",
               "Figura 9. Grado de marginación K-means — ZMG.", width_cm=12)
    add_figure(doc, OUTPUT_DIR / "map_zmg_conapo.png",
               "Figura 10. Grado de marginación CONAPO DP2 — ZMG.", width_cm=12)

    # ── 10. Comparación con CONAPO ────────────────────────────────────────────
    add_heading(doc, "10. Comparación con el Índice Oficial CONAPO")
    add_body(doc,
        "Se evalúa la validez del índice PCA comparándolo con el índice oficial CONAPO DP2 "
        "para los 2,469 municipios."
    )

    add_heading(doc, "10.1 Correlación Pearson", level=2)
    add_data_table(
        doc,
        headers=["Métrica", "Valor"],
        rows=[
            ("Correlación Pearson (Índice PCA vs. IM_2020 CONAPO)", "r = −0.9871"),
            ("Nota", "El signo negativo indica que PCA y DP2 ordenan en sentido inverso — "
                     "al invertir el índice PCA la correlación es +0.9871"),
        ],
        col_widths=[8, 7],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_figure(doc, OUTPUT_DIR / "scatter_pca_vs_conapo.png",
               "Figura 11. Dispersión: Índice PCA vs. Índice CONAPO DP2 (2,469 municipios).")

    add_heading(doc, "10.2 Concordancia por grados", level=2)
    add_data_table(
        doc,
        headers=["Grado PCA \\ CONAPO", "Muy bajo", "Bajo", "Medio", "Alto", "Muy alto", "Total"],
        rows=[
            ("Muy bajo", "473", "0",   "0",   "0",   "0",   "473"),
            ("Bajo",     "182", "507", "74",  "0",   "0",   "763"),
            ("Medio",    "0",   "23",  "420", "298", "0",   "741"),
            ("Alto",     "0",   "0",   "0",   "288", "124", "412"),
            ("Muy alto", "0",   "0",   "0",   "0",   "80",  "80"),
            ("Total",    "655", "530", "494", "586", "204", "2469"),
        ],
        col_widths=[3.5, 2, 2, 2, 2, 2, 1.5],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_body(doc,
        "Coincidencia exacta de grados: 1,768 / 2,469 = 71.6%. "
        "La mayoría de los municipios mal clasificados son casos limítrofes entre dos grados consecutivos."
    )

    # ── 11. Conclusiones ───────────────────────────────────────────────────────
    add_heading(doc, "11. Conclusiones")

    conclusions = [
        ("¿El PCA genera un índice razonable?",
         "Sí. El primer componente principal concentra el 49.17% de la varianza total y sus "
         "cargas positivas en todas las variables son consistentes con un índice de "
         "marginación. Los municipios de regiones reconocidamente marginadas (Oaxaca, "
         "Guerrero, Chiapas) ocupan los primeros lugares del ranking."),

        ("¿Qué tan similares son los resultados a CONAPO?",
         "La correlación de Pearson con el índice oficial DP2 es r = 0.9871 (en valor "
         "absoluto), confirmando que ambos métodos ordenan a los municipios de forma casi "
         "idéntica. La concordancia exacta en la clasificación por grados supera el 71%."),

        ("Ventajas del PCA frente a DP2",
         "El PCA es objetivo, reproducible y no requiere supuestos sobre los pesos de las "
         "variables — los pesos emergen de la estructura de los datos. Además revela la "
         "dimensionalidad latente del fenómeno (Kaiser: 2 componentes)."),

        ("Limitaciones",
         "El PCA es sensible a la escala y a valores atípicos. El signo del componente es "
         "arbitrario (requiere convención). El índice único no captura heterogeneidad "
         "intra-grado. La interpretación es menos directa para tomadores de decisiones "
         "no técnicos."),

        ("¿Qué aporta el criterio Kaiser?",
         "Revela que la marginación en México no es unidimensional. CP2 captura el contraste "
         "entre hacinamiento/vivienda urbana y dispersión rural, evidenciando que la "
         "marginación asume perfiles cualitativamente distintos en contextos urbanos y rurales."),

        ("Aplicación a la ZMG",
         "Los nueve municipios de la Zona Metropolitana de Guadalajara presentan niveles de "
         "marginación Muy bajo o Bajo, consistentes con la naturaleza urbana de la zona. "
         "Tonalá registra el índice más alto dentro de la ZMG, reflejo de su menor "
         "dotación de servicios básicos respecto al resto de los municipios metropolitanos."),
    ]

    for title, body in conclusions:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after  = Pt(2)
        r_title = p.add_run(f"• {title} ")
        set_run_style(r_title, bold=True, size=11, color=NAVY)
        r_body = p.add_run(body)
        set_run_style(r_body, size=11)

    # ── 12. Referencias ────────────────────────────────────────────────────────
    add_heading(doc, "12. Referencias")
    refs = [
        "CONAPO. (2021). Índice de Marginación por Entidad Federativa y Municipio 2020. "
        "Consejo Nacional de Población. Ciudad de México.",
        "Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. "
        "Journal of Machine Learning Research, 12, 2825–2830.",
        "INEGI. (2020). Censo de Población y Vivienda 2020. Instituto Nacional de "
        "Estadística y Geografía. Aguascalientes, México.",
        "GADM. (2023). GADM database of Global Administrative Areas, v4.1. "
        "University of California, Davis.",
        "Pena Trapero, B. (1977). Problemas de la medición del bienestar y conceptos afines. "
        "INE, Madrid.",
    ]
    for ref in refs:
        p = doc.add_paragraph(style="Normal")
        p.paragraph_format.left_indent   = Cm(0.5)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.space_after   = Pt(4)
        r = p.add_run(ref)
        set_run_style(r, size=10)

    doc.save(str(DOCX_OUT))
    print(f"DOCX guardado: {DOCX_OUT}")
    return DOCX_OUT


def convert_to_pdf(docx_path):
    """Convert DOCX to PDF using Microsoft Word via win32com."""
    import win32com.client as win32
    import time

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(docx_path.resolve()))
        time.sleep(1)
        pdf_path = str(PDF_OUT.resolve())
        doc.SaveAs(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
        print(f"PDF guardado: {PDF_OUT}")
    finally:
        word.Quit()


if __name__ == "__main__":
    print("Generando DOCX...")
    docx_path = build_docx()
    print("Convirtiendo a PDF...")
    convert_to_pdf(docx_path)
    print("Listo.")
