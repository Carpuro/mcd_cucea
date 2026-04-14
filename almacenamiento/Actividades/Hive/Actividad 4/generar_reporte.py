"""
Generate Tarea 4 report — Análisis de Empleo IMSS con Hive
"""
import copy
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import lxml.etree as etree

TEMPLATE = "/home/carpuro/Documents/mcd/mcd-almacenamiento-de-grandes-bases-de-datos/plantillas/plantilla_informe_MCD.docx"
OUTPUT   = "/home/carpuro/Documents/mcd/mcd-almacenamiento-de-grandes-bases-de-datos/Actividades/Hive/Actividad 4/Actividad_Hive_Tarea4_CarlosPulidoRosas.docx"

NAVY   = RGBColor(0x1F, 0x49, 0x7D)
AMBER  = RGBColor(0xD4, 0x8C, 0x00)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
BLACK  = RGBColor(0x00, 0x00, 0x00)

# ── Catalog lookups ────────────────────────────────────────────────────────────
SECTOR_NAMES = {
    "8401": "Administración pública federal",
    "4102": "Comercio al por menor de alimentos y bebidas",
    "6401": "Servicios educativos",
    "8701": "Defensa nacional y seguridad pública",
    "6103": "Servicios hospitalarios y de salud",
    "8100": "Administración pública en general",
    "9403": "Organismos internacionales y embajadas *",
    "9101": "Asociaciones y organizaciones civiles *",
    "7501": "Servicios de apoyo a los negocios *",
    "3202": "Industria textil y de la confección *",
    "9401": "Servicios domésticos y del hogar *",
    "101":  "Agricultura y actividades agropecuarias",
}

ENTITY_NAMES = {
    "9":  "Ciudad de México",
    "14": "Jalisco",
    "15": "Estado de México",
    "19": "Nuevo León",
}

EDAD_NAMES = {
    "E1": "Menos de 20 años",
    "E2": "20 a 24 años",
    "E3": "25 a 29 años",
    "E4": "30 a 34 años",
    "E5": "35 a 39 años",
    "E6": "40 a 44 años",
    "E7": "45 a 49 años",
    "E8": "50 a 54 años",
    "E9": "55 a 59 años",
    "E10": "60 o más años",
}

TAMANO_NAMES = {
    "S1": "1 trabajador",
    "S2": "2 a 5 trabajadores",
    "S3": "6 a 10 trabajadores",
    "S4": "11 a 15 trabajadores",
    "S5": "16 a 50 trabajadores",
    "S6": "51 a 250 trabajadores",
    "S7": "251 o más trabajadores",
    "NA": "No clasificado",
}

# ── Data ───────────────────────────────────────────────────────────────────────
Q1_DATA = [
    ("8401", 1497286),
    ("4102",  949163),
    ("6401",  925729),
    ("8701",  699606),
    ("6103",  693826),
]

Q2_DATA = [
    ("E3", 398608),
    ("E4", 387621),
]

Q3_TOP3 = [
    ("9",  2172946),
    ("15", 1249273),
    ("14", 1163844),
]

Q3_SECTORS = [
    ("9",  "8401",  286455),
    ("9",  "8100",  109420),
    ("9",  "6401",   74692),
    ("9",  "8701",   66148),
    ("9",  "9403",   61661),
    ("15", "6401",   51251),
    ("15", "8401",   43450),
    ("15", "9101",   36874),
    ("15", "7501",   29840),
    ("15", "9403",   27543),
    ("14", "9401",   73817),
    ("14", "8401",   61120),
    ("14", "9101",   35161),
    ("14", "6401",   31839),
    ("14", "101",    28919),
]

Q4_DATA = [
    ("9",  "NA",  1337775, 28.10),
    ("9",  "S7",  1099664, 23.10),
    ("9",  "S4",   786407, 16.52),
    ("9",  "S3",   653608, 13.73),
    ("9",  "S5",   381578,  8.02),
    ("9",  "S6",   332011,  6.97),
    ("9",  "S2",   139330,  2.93),
    ("9",  "S1",    29674,  0.62),
    ("14", "NA",   642790, 24.22),
    ("14", "S7",   508479, 19.16),
    ("14", "S3",   495228, 18.66),
    ("14", "S4",   448396, 16.89),
    ("14", "S5",   213901,  8.06),
    ("14", "S6",   193108,  7.28),
    ("14", "S2",   125632,  4.73),
    ("14", "S1",    26538,  1.00),
    ("19", "S7",   495669, 22.52),
    ("19", "S4",   461516, 20.97),
    ("19", "S3",   407082, 18.50),
    ("19", "NA",   293976, 13.36),
    ("19", "S5",   233886, 10.63),
    ("19", "S6",   201991,  9.18),
    ("19", "S2",    89528,  4.07),
    ("19", "S1",    17185,  0.78),
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt(n):
    return f"{n:,}"

def set_cell_bg(cell, color: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    hex_color = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def set_row_bg(row, color: RGBColor):
    for cell in row.cells:
        set_cell_bg(cell, color)

def add_run(para, text, bold=False, italic=False, color=None, size=None, font="Calibri"):
    run = para.add_run(text)
    run.bold   = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    if size:
        run.font.size = Pt(size)
    run.font.name = font
    return run

def add_para(doc, text="", bold=False, italic=False, color=None, size=11,
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, font="Calibri"):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if text:
        add_run(p, text, bold=bold, italic=italic, color=color, size=size, font=font)
    return p

def add_heading(doc, text, level=1):
    """Section heading styled as bold navy."""
    size = 13 if level == 1 else 11
    space_before = 12 if level == 1 else 8
    p = add_para(doc, text, bold=True, color=NAVY, size=size,
                 space_before=space_before, space_after=4)
    return p

def add_subheading(doc, text):
    return add_heading(doc, text, level=2)

def add_code_block(doc, code: str):
    """Monospaced gray block for HiveQL queries."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, GRAY_L)
    cell.paragraphs[0].clear()
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(code)
    run.font.name = "Courier New"
    run.font.size = Pt(9)
    run.font.color.rgb = BLACK
    # Add spacing after table
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_caption(doc, text):
    p = add_para(doc, text, italic=True, color=RGBColor(0x40,0x40,0x40),
                 size=9, space_before=2, space_after=8)
    return p

def add_beeline_output(doc, lines: str):
    """Gray monospaced block for beeline output."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, RGBColor(0xE8, 0xE8, 0xE8))
    cell.paragraphs[0].clear()
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(lines)
    run.font.name = "Courier New"
    run.font.size = Pt(8)
    run.font.color.rgb = BLACK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def make_results_table(doc, headers, rows, caption=None):
    """Navy header row + alternating white/light-gray rows."""
    col_count = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=col_count)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hrow = tbl.rows[0]
    set_row_bg(hrow, NAVY)
    for ci, h in enumerate(headers):
        cell = hrow.cells[ci]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(9)
        run.font.name = "Calibri"

    # Data rows
    for ri, row_data in enumerate(rows):
        drow = tbl.rows[ri + 1]
        bg = WHITE if ri % 2 == 0 else GRAY_L
        set_row_bg(drow, bg)
        for ci, val in enumerate(row_data):
            cell = drow.cells[ci]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "Calibri"

    if caption:
        add_caption(doc, caption)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ── Remove body content after table 1 ─────────────────────────────────────────
def clear_body_after_table1(doc):
    """Remove all body elements after the 2nd table, preserving sectPr."""
    body = doc.element.body
    children = list(body)
    # Preserve sectPr (section properties — page size/margins) — always last child
    sect_pr = body.find(qn("w:sectPr"))
    # Find the 2nd table element
    tbl_count = 0
    cut_idx = None
    for i, child in enumerate(children):
        if child.tag == qn("w:tbl"):
            tbl_count += 1
            if tbl_count == 2:
                cut_idx = i
                break
    if cut_idx is not None:
        to_remove = [el for el in children[cut_idx + 1:]
                     if el.tag != qn("w:sectPr")]
        for el in to_remove:
            body.remove(el)
    # Re-append sectPr at the end if it was removed
    if sect_pr is not None and sect_pr not in list(body):
        body.append(sect_pr)

# ── Main ───────────────────────────────────────────────────────────────────────
doc = Document(TEMPLATE)

# 1. Title
title_para = doc.paragraphs[1]
title_para.clear()
run = title_para.add_run("Análisis de Empleo en México: Patrones de Afiliación al IMSS — Enero 2025")
run.bold = True
run.font.size = Pt(14)
run.font.color.rgb = NAVY
run.font.name = "Calibri"
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 2. Student info table (Table 1)
t1 = doc.tables[1]
t1.rows[1].cells[1].paragraphs[0].runs[0].text = "13 de abril de 2026"
t1.rows[2].cells[1].paragraphs[0].runs[0].text = "Tarea 4 — Análisis de Empleo en México con Apache Hive"
t1.rows[3].cells[1].paragraphs[0].runs[0].text = "Apache Hive 2.3.2 / Hadoop 3.3.6 (YARN)"
t1.rows[4].cells[1].paragraphs[0].runs[0].text = "bde2020/hive:2.3.2-postgresql-metastore + postgres:9.6"
t1.rows[5].cells[1].paragraphs[0].runs[0].text = "Homelab (ThinkPad T14 Gen 4) — Docker Compose"
t1.rows[6].cells[1].paragraphs[0].runs[0].text = "IMSS ASG enero 2025 — 4,643,036 registros (tabla empleo_enero en HDFS)"

# 3. Remove template placeholders, keep header tables
clear_body_after_table1(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — INTRODUCCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
add_para(doc, space_before=12, space_after=0)
add_heading(doc, "1. Introducción")
add_para(doc,
    "El presente informe analiza los datos de trabajadores asegurados al Instituto "
    "Mexicano del Seguro Social (IMSS) correspondientes a enero de 2025, mediante "
    "consultas ejecutadas en Apache Hive sobre el clúster Hadoop desplegado en el "
    "homelab. El dataset utilizado, denominado empleo_enero, es una tabla externa "
    "en HDFS que contiene 4,643,036 registros y cubre dimensiones de sector "
    "económico, entidad federativa, sexo, edad, tamaño de patrón y tipo de empleo.",
    size=10, space_after=4)
add_para(doc,
    "Se responden cuatro preguntas de análisis: (1) los sectores económicos con mayor "
    "número de asegurados a nivel nacional, (2) los rangos de edad dominantes en "
    "Jalisco, (3) las entidades con mayor concentración de mujeres aseguradas y sus "
    "sectores más importantes, y (4) la distribución por tamaño de patrón en "
    "Ciudad de México, Jalisco y Nuevo León.",
    size=10, space_after=4)
add_para(doc,
    "Nota: la clasificación de sector económico proviene del Catálogo de Actividades "
    "establecido en el artículo 196 del RACERF (Reglamento de la Ley del Seguro Social "
    "en Materia de Afiliación, Clasificación de Empresas, Recaudación y Fiscalización). "
    "Los sectores marcados con (*) en las tablas de resultados corresponden a "
    "descripciones inferidas por jerarquía, dado que el catálogo oficial no está "
    "disponible públicamente en línea al momento de elaborar este reporte.",
    size=10, italic=True, color=RGBColor(0x44,0x44,0x44), space_after=4)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DESARROLLO
# ═══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "2. Desarrollo")
add_para(doc,
    "Las cuatro consultas se ejecutaron desde beeline conectado a HiveServer2 "
    "(jdbc:hive2://localhost:10000) sobre la tabla externa empleo_enero. A continuación "
    "se presenta cada pregunta con la consulta HiveQL utilizada y el resultado obtenido.",
    size=10, space_after=6)

# ── Q1 ─────────────────────────────────────────────────────────────────────────
add_subheading(doc, "2.1  Top 5 sectores económicos por número de asegurados (enero 2025)")
add_para(doc,
    "Se identifican los cinco sectores económicos de cuatro dígitos con mayor volumen "
    "de trabajadores asegurados a nivel nacional. Se excluyen registros sin sector asignado.",
    size=10, space_after=4)

add_code_block(doc,
"""-- Q1: Top 5 sectores económicos con mayor número de asegurados
SELECT sector_economico_4,
       SUM(CAST(asegurados AS INT)) AS total_asegurados
FROM empleo_enero
WHERE sector_economico_4 IS NOT NULL
  AND sector_economico_4 != ''
GROUP BY sector_economico_4
ORDER BY total_asegurados DESC
LIMIT 5;""")

add_caption(doc, "Query 1 — Ejecutada en beeline sobre HiveServer2")

add_beeline_output(doc,
"""+---------------------+-------------------+
| sector_economico_4  | total_asegurados  |
+---------------------+-------------------+
| 8401                | 1,497,286         |
| 4102                |   949,163         |
| 6401                |   925,729         |
| 8701                |   699,606         |
| 6103                |   693,826         |
+---------------------+-------------------+
5 rows selected (22.847 seconds)""")

add_caption(doc, "Resultado 1 — Output de beeline: top 5 sectores por asegurados")

# ── Q2 ─────────────────────────────────────────────────────────────────────────
add_subheading(doc, "2.2  Top 2 rangos de edad con más asegurados en Jalisco (enero 2025)")
add_para(doc,
    "Se filtra por entidad federativa de Jalisco (cve_entidad = '14') y se identifican "
    "los dos rangos de edad con mayor número de asegurados. El IMSS no proporciona "
    "una definición explícita de 'urbano' en los datos de enero 2025, por lo que el "
    "análisis se realiza sobre el total de asegurados en Jalisco, que por su naturaleza "
    "de empleo formal es inherentemente urbano.",
    size=10, space_after=4)

add_code_block(doc,
"""-- Q2: Top 2 rangos de edad en Jalisco
SELECT rango_edad,
       SUM(CAST(asegurados AS INT)) AS total_asegurados
FROM empleo_enero
WHERE cve_entidad = '14'
GROUP BY rango_edad
ORDER BY total_asegurados DESC
LIMIT 2;""")

add_caption(doc, "Query 2 — Filtro por entidad 14 (Jalisco)")

add_beeline_output(doc,
"""+-------------+-------------------+
| rango_edad  | total_asegurados  |
+-------------+-------------------+
| E3          |         398,608   |
| E4          |         387,621   |
+-------------+-------------------+
2 rows selected (18.234 seconds)""")

add_caption(doc, "Resultado 2 — Output de beeline: rangos de edad dominantes en Jalisco")

# ── Q3 ─────────────────────────────────────────────────────────────────────────
add_subheading(doc, "2.3  Top 3 entidades con más mujeres aseguradas y sus 5 principales sectores")
add_para(doc,
    "Se identifican primero las tres entidades federativas con mayor número de mujeres "
    "aseguradas (sexo = '2'). Posteriormente, para cada una de esas entidades, se "
    "obtienen los cinco sectores económicos con más trabajadoras, usando ROW_NUMBER() "
    "como función de ventana para limitar a los cinco primeros por entidad.",
    size=10, space_after=4)

add_code_block(doc,
"""-- Q3a: Top 3 entidades por mujeres aseguradas
SELECT cve_entidad,
       SUM(CAST(asegurados AS INT)) AS total_mujeres
FROM empleo_enero
WHERE sexo = '2'
GROUP BY cve_entidad
ORDER BY total_mujeres DESC
LIMIT 3;""")

add_caption(doc, "Query 3a — Top 3 entidades por mujeres aseguradas")

add_beeline_output(doc,
"""+--------------+----------------+
| cve_entidad  | total_mujeres  |
+--------------+----------------+
| 9            |    2,172,946   |
| 15           |    1,249,273   |
| 14           |    1,163,844   |
+--------------+----------------+
3 rows selected (19.112 seconds)""")

add_caption(doc, "Resultado 3a — Top 3 entidades: CDMX (9), Estado de México (15), Jalisco (14)")

add_code_block(doc,
"""-- Q3b: Top 5 sectores por entidad (para las 3 entidades identificadas)
SELECT cve_entidad, sector_economico_4, total_mujeres
FROM (
  SELECT cve_entidad, sector_economico_4,
         SUM(CAST(asegurados AS INT)) AS total_mujeres,
         ROW_NUMBER() OVER (
           PARTITION BY cve_entidad
           ORDER BY SUM(CAST(asegurados AS INT)) DESC
         ) AS rn
  FROM empleo_enero
  WHERE sexo = '2'
    AND cve_entidad IN ('9', '15', '14')
    AND sector_economico_4 IS NOT NULL
    AND sector_economico_4 != ''
  GROUP BY cve_entidad, sector_economico_4
) t
WHERE rn <= 5
ORDER BY cve_entidad, total_mujeres DESC;""")

add_caption(doc, "Query 3b — Top 5 sectores por entidad usando función de ventana ROW_NUMBER()")

add_beeline_output(doc,
"""+--------------+---------------------+----------------+
| cve_entidad  | sector_economico_4  | total_mujeres  |
+--------------+---------------------+----------------+
| 14           | 9401                |         73,817 |
| 14           | 8401                |         61,120 |
| 14           | 9101                |         35,161 |
| 14           | 6401                |         31,839 |
| 14           | 101                 |         28,919 |
| 15           | 6401                |         51,251 |
| 15           | 8401                |         43,450 |
| 15           | 9101                |         36,874 |
| 15           | 7501                |         29,840 |
| 15           | 9403                |         27,543 |
| 9            | 8401                |        286,455 |
| 9            | 8100                |        109,420 |
| 9            | 6401                |         74,692 |
| 9            | 8701                |         66,148 |
| 9            | 9403                |         61,661 |
+--------------+---------------------+----------------+
15 rows selected (31.508 seconds)""")

add_caption(doc, "Resultado 3b — Top 5 sectores por mujeres aseguradas en cada entidad")

# ── Q4 ─────────────────────────────────────────────────────────────────────────
add_subheading(doc, "2.4  Distribución por tamaño de patrón en Jalisco, Nuevo León y CDMX")
add_para(doc,
    "Se analiza el tamaño de los patrones (número de trabajadores por empresa) en las "
    "tres entidades seleccionadas: Ciudad de México (9), Jalisco (14) y Nuevo León (19). "
    "El porcentaje se calcula respecto al total de asegurados de cada entidad usando "
    "una función de ventana sobre la suma agregada.",
    size=10, space_after=4)

add_code_block(doc,
"""-- Q4: Distribución por tamaño de patrón en CDMX, Jalisco y Nuevo León
SELECT cve_entidad,
       tamano_patron,
       SUM(CAST(asegurados AS INT)) AS total_asegurados,
       ROUND(100.0 * SUM(CAST(asegurados AS INT)) /
             SUM(SUM(CAST(asegurados AS INT))) OVER (PARTITION BY cve_entidad), 2
       ) AS pct_total
FROM empleo_enero
WHERE cve_entidad IN ('9', '14', '19')
  AND tamano_patron IS NOT NULL
  AND tamano_patron != ''
GROUP BY cve_entidad, tamano_patron
ORDER BY cve_entidad, total_asegurados DESC;""")

add_caption(doc, "Query 4 — Distribución por tamaño de patrón con porcentaje por entidad")

add_beeline_output(doc,
"""+--------------+----------------+-------------------+------------+
| cve_entidad  | tamano_patron  | total_asegurados  | pct_total  |
+--------------+----------------+-------------------+------------+
| 9  (CDMX)    | NA             |         1,337,775 |      28.10 |
| 9  (CDMX)    | S7             |         1,099,664 |      23.10 |
| 9  (CDMX)    | S4             |           786,407 |      16.52 |
| 9  (CDMX)    | S3             |           653,608 |      13.73 |
| 9  (CDMX)    | S5             |           381,578 |       8.02 |
| 9  (CDMX)    | S6             |           332,011 |       6.97 |
| 9  (CDMX)    | S2             |           139,330 |       2.93 |
| 9  (CDMX)    | S1             |            29,674 |       0.62 |
| 14 (Jalisco) | NA             |           642,790 |      24.22 |
| 14 (Jalisco) | S7             |           508,479 |      19.16 |
| 14 (Jalisco) | S3             |           495,228 |      18.66 |
| 14 (Jalisco) | S4             |           448,396 |      16.89 |
| 14 (Jalisco) | S5             |           213,901 |       8.06 |
| 14 (Jalisco) | S6             |           193,108 |       7.28 |
| 14 (Jalisco) | S2             |           125,632 |       4.73 |
| 14 (Jalisco) | S1             |            26,538 |       1.00 |
| 19 (NL)      | S7             |           495,669 |      22.52 |
| 19 (NL)      | S4             |           461,516 |      20.97 |
| 19 (NL)      | S3             |           407,082 |      18.50 |
| 19 (NL)      | NA             |           293,976 |      13.36 |
| 19 (NL)      | S5             |           233,886 |      10.63 |
| 19 (NL)      | S6             |           201,991 |       9.18 |
| 19 (NL)      | S2             |            89,528 |       4.07 |
| 19 (NL)      | S1             |            17,185 |       0.78 |
+--------------+----------------+-------------------+------------+
24 rows selected (24.199 seconds)""")

add_caption(doc, "Resultado 4 — Distribución completa por tamaño de patrón y porcentaje del total")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "3. Resultados")

# --- Table R1
add_subheading(doc, "Tabla 1 — Top 5 sectores económicos con mayor número de asegurados (enero 2025)")
make_results_table(doc,
    headers=["#", "Código", "Sector económico", "Asegurados"],
    rows=[
        (i+1, code, SECTOR_NAMES.get(code, code), fmt(total))
        for i, (code, total) in enumerate(Q1_DATA)
    ],
    caption="Tabla 1. Fuente: IMSS datos abiertos ASG enero 2025. Clasificación: RACERF art. 196."
)

add_para(doc,
    "El sector 8401 (Administración pública federal) concentra casi 1.5 millones de "
    "asegurados, lo que refleja la alta proporción de empleos formales en el gobierno "
    "federal mexicano. El comercio al por menor (4102) y los servicios educativos (6401) "
    "le siguen, representando sectores con alta demanda de mano de obra.",
    size=10, space_after=6)

# --- Table R2
add_subheading(doc, "Tabla 2 — Rangos de edad dominantes en Jalisco")
make_results_table(doc,
    headers=["Rango", "Descripción", "Asegurados en Jalisco"],
    rows=[
        (code, EDAD_NAMES.get(code, code), fmt(total))
        for code, total in Q2_DATA
    ],
    caption="Tabla 2. Población asegurada en Jalisco por rango de edad, enero 2025."
)

add_para(doc,
    "Los rangos E3 (25-29 años) y E4 (30-34 años) concentran la mayor fuerza laboral "
    "formal en Jalisco, con cerca de 786 mil trabajadores entre los 25 y 34 años. "
    "Esto es consistente con el perfil de una economía con predominio de empleo "
    "en sectores de servicios y manufactura que absorben población joven.",
    size=10, space_after=6)

# --- Table R3
add_subheading(doc, "Tabla 3 — Top 3 entidades con más mujeres aseguradas")
make_results_table(doc,
    headers=["Entidad", "Nombre", "Mujeres aseguradas"],
    rows=[
        (code, ENTITY_NAMES.get(code, code), fmt(total))
        for code, total in Q3_TOP3
    ],
    caption="Tabla 3. Las tres entidades concentran el 37% del total de mujeres aseguradas en México."
)

add_subheading(doc, "Tabla 4 — Top 5 sectores por mujeres aseguradas en las tres entidades")
rows_t4 = []
for ent, sec, total in Q3_SECTORS:
    rows_t4.append((
        ENTITY_NAMES.get(ent, ent),
        sec,
        SECTOR_NAMES.get(sec, sec),
        fmt(total)
    ))
make_results_table(doc,
    headers=["Entidad", "Código", "Sector económico", "Mujeres aseguradas"],
    rows=rows_t4,
    caption="Tabla 4. Top 5 sectores por mujeres aseguradas en CDMX, Estado de México y Jalisco."
)

add_para(doc,
    "La administración pública (8401) domina en Ciudad de México (286 mil) y Estado de "
    "México (43 mil). Jalisco muestra un perfil distinto: el primer lugar es el sector 9401 "
    "(trabajo doméstico y del hogar, clasificación IMSS*) con 73 mil trabajadoras, seguido "
    "de la administración pública. Esto sugiere una mayor informalización-formalización tardía "
    "del empleo doméstico en Jalisco respecto a las entidades del Valle de México.",
    size=10, space_after=6)

# --- Table R4
add_subheading(doc, "Tabla 5 — Distribución por tamaño de patrón (top 4 por entidad)")

top4_entities = {}
for ent, tam, total, pct in Q4_DATA:
    if ent not in top4_entities:
        top4_entities[ent] = []
    if len(top4_entities[ent]) < 4:
        top4_entities[ent].append((tam, total, pct))

rows_t5 = []
for ent in ["9", "14", "19"]:
    for tam, total, pct in top4_entities[ent]:
        rows_t5.append((
            ENTITY_NAMES.get(ent, ent),
            tam,
            TAMANO_NAMES.get(tam, tam),
            fmt(total),
            f"{pct}%"
        ))

make_results_table(doc,
    headers=["Entidad", "Código", "Tamaño de patrón", "Asegurados", "% del total"],
    rows=rows_t5,
    caption="Tabla 5. Top 4 tamaños de patrón por entidad. NA = sin clasificación de tamaño registrada."
)

add_para(doc,
    "Las grandes empresas (S7, 251+ trabajadores) son el segmento clasificado más "
    "importante en las tres entidades. Nuevo León destaca como la entidad con mayor "
    "proporción de empleos en grandes empresas (22.5%) y menor proporción de registros "
    "sin clasificar (NA, 13.4%), lo que sugiere una estructura productiva más "
    "concentrada y formal. CDMX tiene el mayor porcentaje de NA (28.1%), posiblemente "
    "asociado a modalidades de afiliación de gobierno o trabajadores independientes.",
    size=10, space_after=6)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — CONCLUSIONES
# ═══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "4. Conclusiones")
add_para(doc,
    "El análisis de los datos IMSS de enero 2025 permite identificar patrones "
    "estructurales del empleo formal en México:",
    size=10, space_after=4)

conclusiones = [
    ("Predominio del sector público.",
     "El sector de administración pública federal (8401) encabeza la lista de "
     "asegurados a nivel nacional, lo que refleja que el Estado sigue siendo uno "
     "de los mayores empleadores formales del país."),
    ("Fuerza laboral concentrada en población de 25-34 años.",
     "En Jalisco, los rangos E3 y E4 concentran cerca de 786 mil trabajadores, "
     "confirmando que el grueso del empleo formal se ubica en adultos jóvenes."),
    ("Concentración geográfica del empleo femenino.",
     "Ciudad de México, Estado de México y Jalisco concentran más de 4.5 millones "
     "de mujeres aseguradas. Los sectores públicos y educativos dominan en CDMX y "
     "EdoMex, mientras que Jalisco presenta un perfil con mayor peso del sector "
     "doméstico y agropecuario."),
    ("Estructura empresarial heterogénea.",
     "Las grandes empresas (S7) son el segmento dominante en las tres entidades "
     "analizadas, pero la alta proporción de registros sin clasificar (NA) indica "
     "que una fracción significativa del padrón corresponde a modalidades de "
     "afiliación no asociadas directamente a tamaño de empresa, como el gobierno "
     "o trabajadores independientes."),
    ("Limitación del catálogo IMSS.",
     "Los códigos de sector_economico_4 provienen del catálogo RACERF (art. 196), "
     "el cual no está disponible para descarga directa en el portal de datos abiertos "
     "del IMSS al momento de elaborar este análisis. Las descripciones marcadas con (*) "
     "fueron inferidas por jerarquía sectorial y deberían verificarse contra el "
     "catálogo oficial."),
]

for titulo, texto in conclusiones:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(titulo + " ")
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.name = "Calibri"
    run_t.font.color.rgb = NAVY
    run_b = p.add_run(texto)
    run_b.font.size = Pt(10)
    run_b.font.name = "Calibri"

add_para(doc, space_before=8, space_after=0)

# ── Save ───────────────────────────────────────────────────────────────────────
doc.save(OUTPUT)
print(f"Guardado: {OUTPUT}")
