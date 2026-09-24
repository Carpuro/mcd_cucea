"""
Actividad 11 — Instalacion de paquetes bigmemory y ff en R
Almacenamiento de Grandes Bases de Datos — MCD CUCEA
"""
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os, sys
from docx.shared import Inches

# Adjust template path for Windows vs Linux
if sys.platform == "win32":
    TEMPLATE    = r"C:\Users\carlo\GitHub\mcd_cucea\_recursos\plantillas\plantilla_informe_MCD.docx"
    OUTPUT      = r"C:\Users\carlo\GitHub\mcd_cucea\2do-semestre\almacenamiento\tareas\Actividad 11\Actividad11_AlmacenamientoGBD_CarlosPulidoRosas.docx"
    SS_DIR      = r"C:\Users\carlo\GitHub\mcd_cucea\2do-semestre\almacenamiento\tareas\Actividad 11\screenshots"
else:
    TEMPLATE    = "/home/carpuro/Documents/mcd/mcd_cucea/_recursos/plantillas/plantilla_informe_MCD.docx"
    OUTPUT      = "/home/carpuro/Documents/mcd/mcd_cucea/2do-semestre/almacenamiento/tareas/Actividad 11/Actividad11_AlmacenamientoGBD_CarlosPulidoRosas.docx"
    SS_DIR      = "/home/carpuro/Documents/mcd/mcd_cucea/2do-semestre/almacenamiento/tareas/Actividad 11/screenshots"

NAVY   = RGBColor(0x1F, 0x49, 0x7D)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
BLACK  = RGBColor(0x00, 0x00, 0x00)

# ── Helpers ──────────────────────────────────────────────────────────────────

def set_cell_bg(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), f"{color[0]:02X}{color[1]:02X}{color[2]:02X}")
    tcPr.append(shd)

def set_row_bg(row, color):
    for cell in row.cells:
        set_cell_bg(cell, color)

def add_run(para, text, bold=False, italic=False, color=None, size=None, font="Calibri"):
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    if color: run.font.color.rgb = color
    if size:  run.font.size = Pt(size)
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
    sb   = 10 if level == 1 else 7
    return add_para(doc, text, bold=True, color=NAVY, size=size, space_before=sb, space_after=3)

def add_subheading(doc, text):
    return add_heading(doc, text, level=2)

def add_code_block(doc, code):
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

def add_output_block(doc, text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, RGBColor(0xE8, 0xE8, 0xE8))
    cell.paragraphs[0].clear()
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(8)
    run.font.color.rgb = BLACK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_caption(doc, text):
    return add_para(doc, text, italic=True, color=RGBColor(0x40, 0x40, 0x40),
                    size=9, space_before=2, space_after=6)

def make_table(doc, headers, rows, caption=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hrow = tbl.rows[0]
    set_row_bg(hrow, NAVY)
    for ci, h in enumerate(headers):
        p = hrow.cells[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True; r.font.color.rgb = WHITE; r.font.size = Pt(9); r.font.name = "Calibri"
    for ri, row_data in enumerate(rows):
        drow = tbl.rows[ri + 1]
        set_row_bg(drow, WHITE if ri % 2 == 0 else GRAY_L)
        for ci, val in enumerate(row_data):
            p = drow.cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.size = Pt(9); r.font.name = "Calibri"
    if caption:
        add_caption(doc, caption)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_image(doc, filename, caption=None, width=Inches(5.8)):
    path = os.path.join(SS_DIR, filename)
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(2)
        run = p.add_run()
        run.add_picture(path, width=width)
    if caption:
        add_caption(doc, caption)

def add_bullet(doc, titulo, texto):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    rt = p.add_run(titulo + " ")
    rt.bold = True; rt.font.size = Pt(10); rt.font.name = "Calibri"; rt.font.color.rgb = NAVY
    rb = p.add_run(texto)
    rb.font.size = Pt(10); rb.font.name = "Calibri"

def clear_body_after_table1(doc):
    body = doc.element.body
    children = list(body)
    sect_pr = body.find(qn("w:sectPr"))
    tbl_count = 0; cut_idx = None
    for i, child in enumerate(children):
        if child.tag == qn("w:tbl"):
            tbl_count += 1
            if tbl_count == 2:
                cut_idx = i; break
    if cut_idx is not None:
        for el in [e for e in children[cut_idx + 1:] if e.tag != qn("w:sectPr")]:
            body.remove(el)
    if sect_pr is not None and sect_pr not in list(body):
        body.append(sect_pr)

# ── Build document ────────────────────────────────────────────────────────────
doc = Document(TEMPLATE)

doc.tables[0].rows[0].cells[1].paragraphs[3].runs[0].text = \
    "Materia: Almacenamiento de Grandes Bases de Datos"

title_para = doc.paragraphs[1]
title_para.clear()
run = title_para.add_run(
    "Instalacion de Paquetes para Grandes Bases de Datos en R:\n"
    "bigmemory y ff"
)
run.bold = True; run.font.size = Pt(13); run.font.color.rgb = NAVY; run.font.name = "Calibri"
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

t1 = doc.tables[1]
t1.rows[1].cells[1].paragraphs[0].runs[0].text = "10 de mayo de 2026"
t1.rows[2].cells[1].paragraphs[0].runs[0].text = "Tarea 7 — Instalacion de paquetes bigmemory y ff en R"
t1.rows[3].cells[1].paragraphs[0].runs[0].text = "R 4.5.3 (2026-03-11 ucrt)"
t1.rows[4].cells[1].paragraphs[0].runs[0].text = "bigmemory 4.6.4 | ff 4.5.2"
t1.rows[5].cells[1].paragraphs[0].runs[0].text = "Windows 11 — ThinkPad T14 Gen 4"
t1.rows[6].cells[1].paragraphs[0].runs[0].text = "CRAN — Repositorio oficial de R"

clear_body_after_table1(doc)

# ── 1. INTRODUCCION ──────────────────────────────────────────────────────────
add_para(doc, space_before=10, space_after=0)
add_heading(doc, "1. Introduccion")
add_para(doc,
    "El ecosistema de R ofrece herramientas especializadas para trabajar con conjuntos "
    "de datos que superan la capacidad de la memoria RAM disponible. Dos de los paquetes "
    "mas utilizados para este proposito son bigmemory y ff, cada uno con un enfoque "
    "diferente para gestionar grandes volumenes de datos de forma eficiente.",
    space_after=4)
add_para(doc,
    "bigmemory implementa la estrategia de memoria compartida: crea matrices en una "
    "region de memoria que puede ser accedida simultaneamente por multiples procesos de R, "
    "lo que lo hace ideal para computo paralelo en un mismo equipo. ff, por su parte, "
    "utiliza archivos de mapa de memoria (memory-mapped files): los datos residen en disco "
    "pero se acceden como si estuvieran en RAM, gracias al mecanismo de paginacion del "
    "sistema operativo.",
    space_after=4)
add_para(doc,
    "En esta actividad se documenta la instalacion de ambos paquetes en R 4.5.3 sobre "
    "Windows 11, la verificacion de su funcionamiento mediante ejemplos basicos, y una "
    "comparacion de las estrategias que cada uno implementa.",
    space_after=4)

# ── 2. INSTALACION ───────────────────────────────────────────────────────────
add_heading(doc, "2. Instalacion de Paquetes")
add_para(doc,
    "La instalacion se realiza desde el repositorio oficial CRAN mediante la funcion "
    "install.packages(). Ademas de bigmemory y ff, el gestor de dependencias instala "
    "automaticamente los paquetes requeridos por cada uno:",
    space_after=4)

add_subheading(doc, "2.1  Comando de instalacion")
add_code_block(doc,
"""install.packages(c("bigmemory", "ff"),
                 repos = "https://cran.rstudio.com/")""")
add_caption(doc, "Instalacion de ambos paquetes desde CRAN en una sola instruccion.")

add_para(doc,
    "Las dependencias instaladas automaticamente fueron:",
    space_after=3)

make_table(doc,
    headers=["Paquete", "Version", "Requerido por", "Proposito"],
    rows=[
        ("bigmemory.sri", "0.1.8", "bigmemory", "Indice compartido para big.matrix"),
        ("Rcpp",          "1.1.1", "bigmemory", "Interfaz C++ para R"),
        ("uuid",          "1.2-2", "bigmemory", "Generacion de identificadores unicos"),
        ("BH",            "1.90.0","bigmemory", "Cabeceras Boost para C++"),
        ("bit",           "4.6.0", "ff",        "Vectores de bits de alta eficiencia"),
    ],
    caption="Tabla 1. Dependencias instaladas automaticamente junto con bigmemory y ff."
)

add_subheading(doc, "2.2  Verificacion de versiones instaladas")
add_code_block(doc,
"""packageVersion("bigmemory")   # Verificar version
packageVersion("ff")""")
add_output_block(doc,
"""=== Verificacion de paquetes ===
bigmemory:  4.6.4
ff:         4.5.2""")
add_caption(doc, "Salida real de R 4.5.3 — ambos paquetes instalados correctamente.")

add_image(doc, "ss1_instalacion.png",
    caption="Figura 1. Consola de RStudio 2025.05.0 — instalacion completa de bigmemory 4.6.4 y ff 4.5.2 con todas sus dependencias.")

# ── 3. BIGMEMORY ─────────────────────────────────────────────────────────────
add_heading(doc, "3. Paquete bigmemory — Memoria Compartida")
add_para(doc,
    "bigmemory permite crear matrices de gran tamano almacenadas fuera del heap de R, "
    "en una region de memoria compartida del sistema operativo (shared memory). "
    "Multiples sesiones o procesos de R pueden acceder y modificar la misma matriz "
    "de forma concurrente, lo que lo hace especialmente util para procesamiento paralelo "
    "con los paquetes foreach o parallel.",
    space_after=4)

add_subheading(doc, "3.1  Ejemplo: creacion y acceso a una big.matrix")
add_code_block(doc,
"""library(bigmemory)

# Crear matriz de 1,000 filas x 5 columnas en memoria compartida
bm <- big.matrix(nrow = 1000, ncol = 5, type = "double", init = 0)

# Asignar valores a un subconjunto
bm[1:3, 1:3] <- matrix(1:9, 3, 3)

cat("Clase:", class(bm))
cat("Dimensiones:", nrow(bm), "x", ncol(bm))
print(bm[1:3, 1:3])

# Obtener el descriptor para compartir con otros procesos
desc <- describe(bm)""")
add_output_block(doc,
"""Clase: big.matrix
Dimensiones: 1000 x 5
Primeras 3 filas:
     [,1] [,2] [,3]
[1,]    1    4    7
[2,]    2    5    8
[3,]    3    6    9""")
add_caption(doc, "big.matrix de 1,000 x 5 en memoria compartida. Los datos persisten fuera del heap de R.")

add_image(doc, "ss2_ejecucion.png",
    caption="Figura 2. Ejecucion en RStudio — ejemplo de ff: vector de 10,000 enteros, longitud, primeros elementos, suma y tamano en disco (40,000 bytes). Panel Environment muestra bm (big.matrix) y ffv activos.")

add_para(doc,
    "La funcion describe() genera un objeto que puede pasarse a otros procesos de R "
    "para que accedan a la misma region de memoria mediante attach.big.matrix(), "
    "sin necesidad de copiar los datos.",
    space_after=4)

# ── 4. FF ────────────────────────────────────────────────────────────────────
add_heading(doc, "4. Paquete ff — Archivos de Mapa de Memoria")
add_para(doc,
    "ff implementa la estrategia de memory-mapped files: los datos se almacenan en un "
    "archivo binario en disco y el sistema operativo los mapea al espacio de direcciones "
    "del proceso. Desde el punto de vista del programador, el acceso es identico al de "
    "un vector o arreglo en RAM, pero el consumo real de memoria es minimo porque el SO "
    "carga en RAM unicamente las paginas que se estan usando en cada momento.",
    space_after=4)

add_subheading(doc, "4.1  Ejemplo: creacion y acceso a un vector ff")
add_code_block(doc,
"""library(ff)

# Crear un vector ff de 10,000 enteros mapeado a disco
tmp <- tempfile(fileext = ".ff")
ffv <- ff(1:10000, filename = tmp, vmode = "integer")

cat("Clase:", class(ffv))
cat("Longitud:", length(ffv))
cat("Primeros 5 elementos:", ffv[1:5])
cat("Suma de todos los elementos:", sum(ffv[]))
cat("Tamano en disco (bytes):", file.info(filename(ffv))$size)

close(ffv)   # Liberar el mapa de memoria""")
add_output_block(doc,
"""=== ff: Archivos de mapa de memoria ===
Clase: ff_vector ff
Longitud: 10000
Primeros 5 elementos: 1 2 3 4 5
Suma de todos los elementos: 50005000
Tamano en disco (bytes): 40000""")
add_caption(doc, "Vector ff de 10,000 enteros. Los 40,000 bytes corresponden a 4 bytes por entero (vmode='integer').")

add_para(doc,
    "El parametro vmode controla el tipo de dato a nivel binario. Con vmode='integer' "
    "cada elemento ocupa exactamente 4 bytes, de ahi los 40,000 bytes en disco para "
    "10,000 elementos. ff soporta tipos enteros de 1, 2, 4 y 8 bytes, reales de 4 y 8 "
    "bytes, y valores logicos y categoricos.",
    space_after=4)

# ── 5. COMPARACION ───────────────────────────────────────────────────────────
add_heading(doc, "5. Comparacion de Estrategias")
make_table(doc,
    headers=["Caracteristica", "bigmemory", "ff"],
    rows=[
        ("Estrategia",            "Memoria compartida (shared memory)", "Archivos de mapa de memoria (mmap)"),
        ("Ubicacion de datos",    "RAM / shared memory del SO",         "Archivo binario en disco"),
        ("Acceso concurrente",    "Si — multiples procesos R",          "Limitado (un proceso por defecto)"),
        ("Persistencia",          "Opcional (backing file)",            "Si — el archivo persiste en disco"),
        ("Estructura soportada",  "Matrices (big.matrix)",              "Vectores, matrices, data frames (ffdf)"),
        ("Tipo de datos",         "numeric, integer, short, char",      "integer, double, logical, factor y mas"),
        ("Uso tipico",            "Computo paralelo en un equipo",      "Datasets que no caben en RAM"),
        ("Version instalada",     "4.6.4",                             "4.5.2"),
    ],
    caption="Tabla 2. Comparacion de bigmemory y ff segun sus caracteristicas principales."
)

# ── 6. CONCLUSIONES ───────────────────────────────────────────────────────────
add_heading(doc, "6. Conclusiones")
add_para(doc,
    "Ambos paquetes fueron instalados y verificados correctamente en R 4.5.3 sobre "
    "Windows 11. Los ejemplos de uso confirman que las estructuras de datos creadas "
    "operan como se espera: big.matrix almacena y recupera valores desde memoria "
    "compartida, y el vector ff mapea correctamente 10,000 enteros a un archivo de "
    "40,000 bytes en disco.",
    space_after=4)

conclusiones = [
    ("Complementariedad.",
     "bigmemory y ff no son competidores sino complementarios: bigmemory es la "
     "eleccion natural cuando se necesita paralelismo en un mismo equipo, mientras "
     "que ff es preferible cuando el dataset supera la RAM disponible y no se requiere "
     "acceso concurrente."),
    ("Transparencia de acceso.",
     "Ambos paquetes exponen una interfaz de subindice identica a la de los objetos "
     "nativos de R (vectores y matrices), lo que minimiza la curva de aprendizaje."),
    ("Relevancia para grandes bases de datos.",
     "En el contexto de la materia, estas estrategias son el equivalente en R a lo "
     "que HDFS y el particionado representan en Hive: mecanismos para procesar datos "
     "que rebasan la capacidad de la memoria principal del equipo local."),
    ("Preparacion para la siguiente sesion.",
     "Con bigmemory y ff instalados y verificados, el entorno local esta listo para "
     "aplicar tecnicas de analisis estadistico sobre datasets de gran escala directamente "
     "en R, sin requerir infraestructura distribuida adicional."),
]
for titulo, texto in conclusiones:
    add_bullet(doc, titulo, texto)

add_para(doc, space_before=6, space_after=0)

doc.save(OUTPUT)
print(f"Guardado: {OUTPUT}")
