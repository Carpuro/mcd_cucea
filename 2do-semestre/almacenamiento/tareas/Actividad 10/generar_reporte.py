"""
Actividad 6 — Estrategia de Optimizacion de Data Warehouse
Agencia de Investigacion sobre Calidad de Empleo — Datos IMSS ASG 2025
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEMPLATE = "/home/carpuro/Documents/mcd/mcd_cucea/_recursos/plantillas/plantilla_informe_MCD.docx"
OUTPUT   = "/home/carpuro/Documents/mcd/mcd_cucea/2do-semestre/almacenamiento/tareas/Actividad 10/Actividad_DW_Tarea6_CarlosPulidoRosas.docx"

NAVY   = RGBColor(0x1F, 0x49, 0x7D)
AMBER  = RGBColor(0xD4, 0x8C, 0x00)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
BLACK  = RGBColor(0x00, 0x00, 0x00)

# ── Helpers ──────────────────────────────────────────────────────────────────

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

def add_para(doc, text="", bold=False, italic=False, color=None, size=10,
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=5, font="Calibri"):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if text:
        add_run(p, text, bold=bold, italic=italic, color=color, size=size, font=font)
    return p

def add_heading(doc, text, level=1):
    size = 13 if level == 1 else 11
    space_before = 10 if level == 1 else 7
    return add_para(doc, text, bold=True, color=NAVY, size=size,
                    space_before=space_before, space_after=3)

def add_subheading(doc, text):
    return add_heading(doc, text, level=2)

def add_code_block(doc, code: str):
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
    run.font.size = Pt(8)
    run.font.color.rgb = BLACK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_caption(doc, text):
    return add_para(doc, text, italic=True, color=RGBColor(0x40, 0x40, 0x40),
                    size=9, space_before=2, space_after=6)

def make_results_table(doc, headers, rows, caption=None, col_widths=None):
    col_count = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=col_count)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in tbl.rows:
                row.cells[i].width = Inches(w)

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
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_bullet(doc, titulo, texto, color_titulo=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    ct = color_titulo or NAVY
    run_t = p.add_run(titulo + " ")
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.name = "Calibri"
    run_t.font.color.rgb = ct
    run_b = p.add_run(texto)
    run_b.font.size = Pt(10)
    run_b.font.name = "Calibri"

def clear_body_after_table1(doc):
    body = doc.element.body
    children = list(body)
    sect_pr = body.find(qn("w:sectPr"))
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
    if sect_pr is not None and sect_pr not in list(body):
        body.append(sect_pr)

# ── Main ─────────────────────────────────────────────────────────────────────
doc = Document(TEMPLATE)

# Header
doc.tables[0].rows[0].cells[1].paragraphs[3].runs[0].text = \
    "Materia: Almacenamiento de Grandes Bases de Datos"

# Title
title_para = doc.paragraphs[1]
title_para.clear()
run = title_para.add_run(
    "Estrategia de Optimizacion de Data Warehouse\n"
    "para Analisis de Calidad de Empleo — Datos IMSS ASG 2025"
)
run.bold = True
run.font.size = Pt(13)
run.font.color.rgb = NAVY
run.font.name = "Calibri"
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Info table
t1 = doc.tables[1]
t1.rows[1].cells[1].paragraphs[0].runs[0].text = "4 de mayo de 2026"
t1.rows[2].cells[1].paragraphs[0].runs[0].text = "Tarea 6 — Estrategia de Optimizacion de DW"
t1.rows[3].cells[1].paragraphs[0].runs[0].text = "Apache Hive 2.3.2 / Hadoop 3.3.6 (YARN)"
t1.rows[4].cells[1].paragraphs[0].runs[0].text = "bde2020/hive:2.3.2-postgresql-metastore + postgres:9.6"
t1.rows[5].cells[1].paragraphs[0].runs[0].text = "Homelab (ThinkPad T14 Gen 4) — Docker Compose"
t1.rows[6].cells[1].paragraphs[0].runs[0].text = "IMSS ASG 2025 — Primer semestre (~27.7M registros, 6 archivos mensuales)"

clear_body_after_table1(doc)

# =============================================================================
# SECTION 1 — INTRODUCCION
# =============================================================================
add_para(doc, space_before=10, space_after=0)
add_heading(doc, "1. Introduccion")
add_para(doc,
    "Los datos abiertos de Asegurados al IMSS (ASG 2025) constituyen una de las fuentes "
    "mas ricas para estudiar la calidad del empleo formal en Mexico. Con aproximadamente "
    "27.7 millones de registros por mes y seis archivos del primer semestre de 2025 ya "
    "disponibles en HDFS, una agencia de investigacion especializada requiere una "
    "infraestructura analitica que permita responder preguntas multidimensionales con "
    "tiempos de respuesta razonables.",
    space_after=4)

add_para(doc,
    "Las cuatro dimensiones de analisis prioritarias para la agencia son: entidad "
    "federativa (32 entidades), sector economico a un digito segun el SCIAN (11 sectores), "
    "rango salarial (10 tramos) y sexo (masculino / femenino). Cruzar estas dimensiones "
    "con la evolucion mensual de 2025 exige consultas que hoy implican escanear los "
    "~2.3 GB de archivos TEXTFILE del semestre completo, aun cuando el analisis solo "
    "requiera un subconjunto especifico.",
    space_after=4)

add_para(doc,
    "Este informe propone una estrategia de optimizacion del Data Warehouse basada en "
    "cuatro pilares: (1) migracion al formato columnar ORC con compresion SNAPPY, "
    "(2) particionado primario por mes y clustering secundario por entidad y sector, "
    "(3) tablas de agregacion pre-calculadas que eviten re-escanear datos base, y "
    "(4) configuracion del motor de consultas Tez con ejecucion vectorizada. La "
    "propuesta se sustenta en el comportamiento real de los datos del primer semestre "
    "y es escalable a los seis meses restantes de 2025.",
    space_after=4)

# =============================================================================
# SECTION 2 — DIAGNOSTICO DEL ESTADO ACTUAL
# =============================================================================
add_heading(doc, "2. Diagnostico del Estado Actual")
add_para(doc,
    "Tras la implementacion del particionado por mes (Actividad 9), la tabla empleo "
    "opera como tabla externa TEXTFILE particionada. La estructura actual en HDFS es "
    "funcional pero presenta tres limitaciones para el patron de consultas de la agencia:",
    space_after=3)

add_bullet(doc,
    "Formato TEXTFILE:",
    "cada consulta debe deserializar texto plano caracter a caracter. Para una tabla "
    "de 29 columnas y 27M registros, la lectura de columnas irrelevantes desperdicia "
    "entre el 70% y el 85% del I/O cuando solo se necesitan asegurados, masa_sal_ta, "
    "cve_entidad, sector_economico_1, rango_salarial y sexo.")

add_bullet(doc,
    "Ausencia de clustering intra-particion:",
    "dentro de cada particion mes=NN los datos estan en el orden de insercion del "
    "archivo original. Filtrar por entidad o sector sobre una particion mensual "
    "(~4.6M registros) requiere un full scan de la particion completa.")

add_bullet(doc,
    "Sin agregaciones materializadas:",
    "cada consulta analitica recalcula desde cero los totales de asegurados y masa "
    "salarial. Las consultas mas frecuentes de la agencia (tendencia mensual de un "
    "sector por entidad) ejecutan el mismo GROUP BY repetidamente sobre los mismos datos.")

add_para(doc, space_before=4, space_after=2)
make_results_table(doc,
    headers=["Limitacion", "Impacto estimado", "Solucion propuesta"],
    rows=[
        ("TEXTFILE — lectura completa de filas",   "85% I/O innecesario por columna", "Migrar a ORC + SNAPPY"),
        ("Sin clustering intra-particion",          "Full scan de ~4.6M filas/mes",    "CLUSTERED BY entidad, sector INTO 32 BUCKETS"),
        ("Sin agregaciones pre-calculadas",         "Recalculo repetido de GROUP BY",  "Tablas de agregacion por dimension"),
        ("Motor MapReduce (predeterminado Hive 2)", "Latencia alta en consultas OLAP", "Activar Tez + vectorizacion"),
    ],
    caption="Tabla 1. Diagnostico del estado actual y mapeo a soluciones de optimizacion."
)

# =============================================================================
# SECTION 3 — MODELO DIMENSIONAL PROPUESTO
# =============================================================================
add_heading(doc, "3. Modelo Dimensional Propuesto")
add_para(doc,
    "Se propone un esquema estrella con una tabla de hechos central y cuatro tablas de "
    "dimension. Las dimensiones son de baja cardinalidad (sexo: 2, sector: 11, salario: 10, "
    "entidad: 32) lo que las hace idoneas para broadcast joins en Hive, eliminando shuffles "
    "costosos en las consultas analiticas.",
    space_after=4)

make_results_table(doc,
    headers=["Tabla", "Tipo", "Granularidad", "Columnas clave"],
    rows=[
        ("fact_asegurados",   "Hechos",    "entidad + sector + salario + sexo + mes", "asegurados, masa_sal_ta"),
        ("dim_entidad",       "Dimension", "cve_entidad (32 filas)",                  "cve_entidad, nombre_entidad, region"),
        ("dim_sector",        "Dimension", "codigo SCIAN 1 digito (11 filas)",        "sector_1, nombre_sector"),
        ("dim_salario",       "Dimension", "rango_salarial (10 filas)",               "rango_salarial, desc_salario, salario_min_smg"),
        ("dim_sexo",          "Dimension", "sexo (2 filas)",                          "sexo, desc_sexo"),
        ("dim_tiempo",        "Dimension", "mes (6-12 filas/anio)",                   "mes, nombre_mes, trimestre, anio"),
    ],
    caption="Tabla 2. Esquema estrella propuesto — tabla de hechos y cuatro dimensiones analiticamente relevantes."
)

add_subheading(doc, "3.1  DDL de la tabla de hechos optimizada")
add_code_block(doc,
"""CREATE TABLE fact_asegurados (
  cve_entidad        TINYINT,
  sector_1           TINYINT,
  rango_salarial     TINYINT,
  sexo               TINYINT,
  asegurados         INT,
  masa_sal_ta        BIGINT
)
PARTITIONED BY (mes TINYINT)
CLUSTERED BY (cve_entidad, sector_1) INTO 32 BUCKETS
STORED AS ORC
TBLPROPERTIES (
  'orc.compress'            = 'SNAPPY',
  'orc.stripe.size'         = '67108864',
  'orc.row.index.stride'    = '10000',
  'transactional'           = 'false'
);""")
add_caption(doc, "DDL de fact_asegurados — ORC + SNAPPY, particionado por mes, clustering por entidad y sector.")

# =============================================================================
# SECTION 4 — ESTRATEGIA DE OPTIMIZACION
# =============================================================================
add_heading(doc, "4. Estrategia de Optimizacion")

add_subheading(doc, "4.1  Migracion TEXTFILE → ORC con compresion SNAPPY")
add_para(doc,
    "ORC (Optimized Row Columnar) almacena los datos en columnas contiguas en disco, "
    "permitiendo que una consulta que accede solo a asegurados y masa_sal_ta lea "
    "aproximadamente el 7% del volumen total (2 de 29 columnas) en lugar del 100%. "
    "Adicionalmente, ORC incluye indices de min/max y bloom filters por stripe que "
    "permiten saltar bloques cuando el predicado no puede coincidir. Con SNAPPY la "
    "relacion de compresion tipica para datos numericos repetitivos como los del IMSS "
    "es de 3:1 a 4:1, reduciendo el dataset de ~2.3 GB a aproximadamente 600 MB.",
    space_after=4)

add_code_block(doc,
"""-- Carga incremental mes a mes desde la tabla TEXTFILE existente
SET hive.exec.dynamic.partition       = true;
SET hive.exec.dynamic.partition.mode  = nonstrict;
SET hive.enforce.bucketing            = true;

INSERT INTO fact_asegurados PARTITION (mes)
SELECT
  CAST(cve_entidad        AS TINYINT),
  CAST(sector_economico_1 AS TINYINT),
  CAST(rango_salarial     AS TINYINT),
  CAST(sexo               AS TINYINT),
  CAST(asegurados         AS INT),
  CAST(masa_sal_ta        AS BIGINT),
  CAST(mes                AS TINYINT)
FROM empleo
WHERE mes = '01';   -- repetir para 02..06""")
add_caption(doc, "Carga de la tabla de hechos ORC desde la tabla TEXTFILE particionada existente.")

add_subheading(doc, "4.2  Tablas de Agregacion Pre-calculadas")
add_para(doc,
    "Para los patrones de consulta mas frecuentes de la agencia se proponen tres vistas "
    "materializadas persistidas como tablas Hive regulares. Cada tabla consolida el "
    "semestre completo en un volumen manejable (miles de filas frente a millones), "
    "reduciendo el tiempo de consulta de minutos a segundos:",
    space_after=3)

add_code_block(doc,
"""-- Agregacion 1: tendencia mensual por entidad y sector
CREATE TABLE agg_entidad_sector_mes
STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY') AS
SELECT mes, cve_entidad, sector_1,
       SUM(asegurados) AS total_asegurados,
       SUM(masa_sal_ta) AS masa_salarial
FROM fact_asegurados
GROUP BY mes, cve_entidad, sector_1;

-- Agregacion 2: distribucion salarial por entidad y sexo
CREATE TABLE agg_salario_entidad_sexo
STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY') AS
SELECT mes, cve_entidad, sexo, rango_salarial,
       SUM(asegurados) AS total_asegurados
FROM fact_asegurados
GROUP BY mes, cve_entidad, sexo, rango_salarial;

-- Agregacion 3: resumen nacional por sector (KPI de dashboard)
CREATE TABLE agg_sector_nacional_mes
STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY') AS
SELECT mes, sector_1,
       SUM(asegurados)  AS total_asegurados,
       SUM(masa_sal_ta) AS masa_salarial,
       AVG(CAST(masa_sal_ta AS DOUBLE) /
           NULLIF(asegurados,0)) AS salario_promedio
FROM fact_asegurados
GROUP BY mes, sector_1;""")
add_caption(doc, "Tres tablas de agregacion que cubren los patrones de consulta prioritarios de la agencia.")

add_subheading(doc, "4.3  Motor de Consultas: Tez y Ejecucion Vectorizada")
add_para(doc,
    "Hive 2.3.2 soporta el motor Tez como alternativa a MapReduce. Tez evita "
    "escrituras intermedias a disco al encadenar los operadores en un DAG en memoria, "
    "reduciendo la latencia de consultas OLAP tipicamente entre un 40% y un 70%. "
    "La ejecucion vectorizada procesa bloques de 1,024 filas por operacion en lugar "
    "de fila por fila, aprovechando las instrucciones SIMD del procesador. "
    "Ambas optimizaciones se activan con las siguientes propiedades de sesion:",
    space_after=4)

add_code_block(doc,
"""SET hive.execution.engine                    = tez;
SET hive.vectorized.execution.enabled        = true;
SET hive.vectorized.execution.reduce.enabled = true;
SET hive.auto.convert.join                   = true;
SET hive.auto.convert.join.noconditionaltask.size = 25000000;
-- Broadcast join automatico para dimensiones < 25 MB (todas las dim propuestas)

ANALYZE TABLE fact_asegurados PARTITION(mes) COMPUTE STATISTICS
  FOR COLUMNS cve_entidad, sector_1, rango_salarial, sexo, asegurados, masa_sal_ta;""")
add_caption(doc, "Configuracion de sesion Hive: motor Tez, vectorizacion y estadisticas de columna.")

add_subheading(doc, "4.4  Ingesta de Meses Futuros (07-12 de 2025)")
add_para(doc,
    "La arquitectura propuesta escala sin modificar el esquema. La ingesta de cada "
    "nuevo mes consiste en tres pasos: (1) subir el archivo CSV a HDFS en la particion "
    "correspondiente, (2) ejecutar la carga INSERT INTO sobre fact_asegurados para "
    "la nueva particion, y (3) actualizar las tres tablas de agregacion con "
    "INSERT OVERWRITE sobre el mes nuevo. El proceso completo para un mes "
    "(~4.6M registros) tarda aproximadamente 8-12 minutos en el entorno Docker "
    "del homelab.",
    space_after=3)

# =============================================================================
# SECTION 5 — ESTIMACION DE IMPACTO
# =============================================================================
add_heading(doc, "5. Estimacion de Impacto y Conclusiones")

make_results_table(doc,
    headers=["Metrica", "Estado actual (TEXTFILE)", "Estado objetivo (ORC)", "Mejora estimada"],
    rows=[
        ("Volumen semestral en disco",     "~2.3 GB",          "~600 MB",        "~74% reduccion"),
        ("I/O por consulta analitica",     "100% de columnas", "~7% de columnas","~93% menos I/O"),
        ("Consulta entidad+sector (1 mes)","60-90 seg (MR)",   "5-10 seg (Tez)", "~85% reduccion"),
        ("Consulta KPI nacional",          "120-180 seg",      "<1 seg (agg)",   ">99% reduccion"),
        ("Ingesta mensual nueva",          "5 min (mv+repair)","10 min (ETL ORC)","Comparable"),
    ],
    caption="Tabla 3. Estimacion de impacto de la estrategia de optimizacion sobre las metricas clave."
)

add_para(doc,
    "La estrategia propuesta transforma el Data Warehouse de un repositorio de archivos "
    "planos en una plataforma analitica optimizada para los patrones de consulta de la "
    "agencia. Los cuatro pilares de la estrategia actuan de forma sinergica: ORC reduce "
    "el volumen y el I/O; el clustering dirige las consultas a los buckets relevantes; "
    "las agregaciones pre-calculadas eliminan el recalculo repetitivo; y Tez con "
    "vectorizacion acelera la ejecucion de los planes de consulta restantes.",
    space_after=4)

conclusiones = [
    ("Adecuacion al patron de consultas.",
     "Las cuatro dimensiones de analisis de la agencia (entidad, sector, salario, sexo) "
     "son precisamente las columnas de clustering y particionado propuestos, garantizando "
     "que el partition pruning y el bucket pruning se activen en la gran mayoria de consultas."),
    ("Escalabilidad a 2025 completo.",
     "Agregar los meses 07 a 12 solo requiere repetir el proceso de ingesta por particion, "
     "sin rediseno del esquema ni de las tablas de agregacion."),
    ("Viabilidad en infraestructura existente.",
     "Toda la estrategia es implementable sobre el Docker Compose actual (Hive 2.3.2 + "
     "Hadoop 3.3.6) sin requerir componentes adicionales, ya que ORC, Tez y el bucketing "
     "estan disponibles de forma nativa en esta version."),
    ("Ruta de implementacion sugerida.",
     "Se recomienda migrar primero el mes de mayor volumen (enero: 385 MB) como prueba "
     "de concepto, validar las metricas de compresion y tiempo de consulta, y proceder "
     "despues con los cinco meses restantes en un proceso batch nocturno."),
]

for titulo, texto in conclusiones:
    add_bullet(doc, titulo, texto)

add_para(doc, space_before=6, space_after=0)

doc.save(OUTPUT)
print(f"Guardado: {OUTPUT}")
