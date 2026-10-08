# -*- coding: utf-8 -*-
"""
Desarrollo de Proyecto I - Research protocol filled directly on the official CUCEA template.
Keeps the template cover (UdeG crest, CUCEA and MCD logos), its fonts, numbering and the
footer of the body section (CUCEA logo + page number). Only the guide text is replaced.
All figures come from the thesis repo (ai-automation-risk-jalisco); manufacturing-specific
items that are not yet computed are written as planned work.
"""
import copy
import glob
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = glob.glob(os.path.join(HERE, "plantilla_protocolo_cucea_2026.docx"))[0]
OUT = os.path.join(HERE, "Protocolo_Investigacion_CarlosPulidoRosas.docx")

TITULO = ("Modelo de evaluación del riesgo de sustitución laboral mediante herramientas de ciencia "
          "de datos: inteligencia artificial cognitiva y robótica en la industria manufacturera de "
          "Jalisco")

doc = Document(TEMPLATE)
P = doc.paragraphs
body = doc.element.body

# ---------------- prototypes taken from the template itself -----------------
PROTO = {
    "titulo": copy.deepcopy(P[24]._p),     # centered, bold, 12 pt
    "seccion": copy.deepcopy(P[54]._p),    # numbered section heading (List Paragraph)
    "sub": copy.deepcopy(P[26]._p),        # bold justified subheading
    "cuerpo": copy.deepcopy(P[28]._p),     # justified body, 12 pt, 1.5 spacing
    "sangria": copy.deepcopy(P[55]._p),    # indented body
}

# ---------------- cover: fill only the placeholders --------------------------
def set_text(par, text):
    runs = [r for r in par.runs if r._r.xpath("./w:t")]
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""

set_text(P[10], TITULO)
set_text(P[14], "Carlos Pulido Rosas")
set_text(P[20], "7 de octubre de 2026")
set_text(P[22], "carlos.pulido.rosas@gmail.com")
for r in P[23].runs:                       # keep the anchored CUCEA / MCD logos untouched
    if "Teléfono" in r.text:
        r.text = "Teléfono"

# ---------------- remove the guide, keep the body-section footer ------------
elems = list(body)
cover_break = elems[23]                    # paragraph holding the cover section break
guide_break = elems[35]                    # paragraph holding the body section break (footer2)
final_sect = body.find(qn("w:sectPr"))
body.replace(final_sect, copy.deepcopy(guide_break.find(qn("w:pPr")).find(qn("w:sectPr"))))
for el in elems[24:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)
END = body.find(qn("w:sectPr"))


# ---------------- formatting per "Lineamientos presentación de trabajos MCD Ver 2.0" ----------
# Times New Roman; text 12 / level-1 headings 14; justified; double spacing in text, single in
# tables, 1.5 in references with hanging indent; 1.25 cm first-line indent; level-1 headings
# centered, bold, uppercase, Roman numerals; level-2 left, bold, Arabic numbering.
FONT = "Times New Roman"
INDENT = 709                     # 1.25 cm in twips
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]
_num = {"sec": 0, "sub": 0}


def _p(text, size=12, bold=False, italic=False, align="both", line=480, first=None, left=None,
       hanging=None, before=0, after=0, keep=False):
    p = OxmlElement("w:p"); ppr = OxmlElement("w:pPr")
    if keep:
        ppr.append(OxmlElement("w:keepNext"))
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:before"), str(int(before * 20))); sp.set(qn("w:after"), str(int(after * 20)))
    sp.set(qn("w:line"), str(line)); sp.set(qn("w:lineRule"), "auto"); ppr.append(sp)
    if first or left or hanging:
        ind = OxmlElement("w:ind")
        if left: ind.set(qn("w:left"), str(left))
        if first: ind.set(qn("w:firstLine"), str(first))
        if hanging: ind.set(qn("w:hanging"), str(hanging))
        ppr.append(ind)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), align); ppr.append(jc)
    p.append(ppr)
    r = OxmlElement("w:r"); rp = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    for a in ("ascii", "hAnsi", "cs", "eastAsia"):
        rf.set(qn(f"w:{a}"), FONT)
    rp.append(rf)
    if bold: rp.append(OxmlElement("w:b"))
    if italic: rp.append(OxmlElement("w:i"))
    for tag in ("w:sz", "w:szCs"):
        e = OxmlElement(tag); e.set(qn("w:val"), str(int(size * 2))); rp.append(e)
    r.append(rp)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve")
    r.append(t); p.append(r)
    END.addprevious(p)
    return p


def titulo(t):
    _p(t, size=14, bold=True, align="center", before=0, after=12, keep=True)


def seccion(t):
    _num["sec"] += 1; _num["sub"] = 0
    _p(f"{ROMAN[_num['sec'] - 1]}. {t.upper()}", size=14, bold=True, align="center",
       before=12, after=6, keep=True)


def sub(t):
    _num["sub"] += 1
    _p(f"{_num['sec']}.{_num['sub']}. {t}", bold=True, align="left", before=12, after=0, keep=True)


def par(t):
    _p(t, first=INDENT)


def item(t):
    _p(t, left=INDENT)


def ref(t):
    _p(t, align="left", line=360, left=INDENT, hanging=INDENT)


def caption_table(num, title):
    _p(f"Tabla {num}", bold=True, align="left", line=480, before=12, keep=True)
    _p(title, italic=True, align="left", line=480, keep=True)


def note(t):
    _p(t, size=8, align="left", line=240, before=4, after=8)


def page_break():
    p = OxmlElement("w:p"); r = OxmlElement("w:r"); br = OxmlElement("w:br")
    br.set(qn("w:type"), "page"); r.append(br); p.append(r); END.addprevious(p)


def table(rows, widths_twips):
    tbl = OxmlElement("w:tbl"); tblPr = OxmlElement("w:tblPr")
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); tblPr.append(jc)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "808080"); borders.append(e)
    tblPr.append(borders); tbl.append(tblPr)
    grid = OxmlElement("w:tblGrid")
    for w in widths_twips:
        g = OxmlElement("w:gridCol"); g.set(qn("w:w"), str(w)); grid.append(g)
    tbl.append(grid)
    for ri, row in enumerate(rows):
        tr = OxmlElement("w:tr")
        if ri == 0:
            trPr = OxmlElement("w:trPr"); h = OxmlElement("w:tblHeader"); trPr.append(h); tr.append(trPr)
        for ci, val in enumerate(row):
            tc = OxmlElement("w:tc"); tcPr = OxmlElement("w:tcPr")
            tw = OxmlElement("w:tcW"); tw.set(qn("w:w"), str(widths_twips[ci])); tw.set(qn("w:type"), "dxa")
            tcPr.append(tw)
            if ri == 0:
                shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "D9D9D9")
                tcPr.append(shd)
            tc.append(tcPr)
            p = OxmlElement("w:p"); ppr = OxmlElement("w:pPr")
            spc = OxmlElement("w:spacing"); spc.set(qn("w:before"), "0"); spc.set(qn("w:after"), "0")
            spc.set(qn("w:line"), "240"); spc.set(qn("w:lineRule"), "auto"); ppr.append(spc)
            jc2 = OxmlElement("w:jc"); jc2.set(qn("w:val"), "left" if ci == 0 else "center"); ppr.append(jc2)
            p.append(ppr)
            r = OxmlElement("w:r"); rp = OxmlElement("w:rPr")
            rf = OxmlElement("w:rFonts")
            for a in ("ascii", "hAnsi", "cs", "eastAsia"):
                rf.set(qn(f"w:{a}"), FONT)
            rp.append(rf)
            if ri == 0: rp.append(OxmlElement("w:b"))
            sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "20"); rp.append(sz)
            r.append(rp); t = OxmlElement("w:t"); t.text = val; t.set(qn("xml:space"), "preserve")
            r.append(t); p.append(r); tc.append(p); tr.append(tc)
        tbl.append(tr)
    END.addprevious(tbl)


# =============================================================================
# CONTENT
# =============================================================================
titulo("Protocolo de investigación")

seccion("Datos de identificación y título")
par(f"Título: {TITULO}.")
par("Alumno: Carlos Pulido Rosas. Programa: Maestría en Ciencia de los Datos, Centro Universitario "
    "de Ciencias Económico Administrativas, Universidad de Guadalajara. Generación 2025-2027, "
    "modalidad ejecutiva. Unidad de aprendizaje: Desarrollo de Proyecto I, impartida por la "
    "Dra. Ana Rosa Jiménez Meza. Director de tesis: por designar. Línea de generación y "
    "aplicación del conocimiento: Smart Data (LGAC 2), por el uso de técnicas de aprendizaje "
    "automatizado y analítica de datos.")
par("El título responde a las tres preguntas que pide la guía. Qué se pretende hacer: evaluar el "
    "riesgo de que el trabajo sea sustituido por tecnología. Con qué herramientas: un modelo "
    "construido con métodos de ciencia de datos que integra índices de exposición ocupacional, "
    "modelos estadísticos y escenarios de adopción tecnológica. Dónde se aplicará: en la industria "
    "manufacturera del estado de Jalisco.")

seccion("Planteamiento del problema")
par("El debate sobre la automatización suele tratar a la inteligencia artificial como un riesgo "
    "único que amenaza a todos los empleos por igual. La evidencia acumulada indica otra cosa: la "
    "automatización avanza por dos fronteras tecnológicas distintas. Una es cognitiva y está "
    "encabezada por los modelos de lenguaje, que realizan tareas de redacción, análisis y "
    "procesamiento de información. La otra es física y se materializa en robots industriales y "
    "máquinas autónomas que manipulan objetos y operan equipo. Ambas fronteras tienen costos, "
    "canales de difusión y ocupaciones afectadas diferentes, y los análisis del repositorio de esta "
    "tesis muestran que las ocupaciones más expuestas a una suelen ser las menos expuestas a la otra.")
par("La industria manufacturera de Jalisco concentra las dos fronteras en un mismo sector. Es el "
    "sector con mayor empleo formal del estado, con 627 mil trabajadores registrados en los Censos "
    "Económicos, y en las proyecciones de la tesis aparece entre los de mayor presión de "
    "automatización hacia 2030, con un componente físico dominante. Dentro de sus plantas conviven "
    "los operadores de maquinaria industrial, el grupo ocupacional con la exposición más alta a la "
    "automatización física, y las áreas administrativas, técnicas y de supervisión, expuestas a los "
    "modelos de lenguaje. A esto se suma el nearshoring: la inversión extranjera directa en Jalisco "
    "aumentó 27 % en 2021-2023 respecto a 2015-2019, sobre todo por reinversión de plantas "
    "establecidas, lo que crea empleo en el corto plazo y al mismo tiempo trae consigo la frontera "
    "tecnológica de las empresas matrices.")
par("Los instrumentos disponibles no permiten dimensionar este riesgo. Las medidas clásicas, como la "
    "de Frey y Osborne (2017), son estáticas, se construyeron con juicio experto sobre datos de "
    "Estados Unidos y suponen que el trabajo cognitivo no rutinario está protegido. Las medidas "
    "recientes de exposición a la IA se enfocan en el eje cognitivo y no distinguen el riesgo de "
    "robotización. Ninguna considera si la sustitución es rentable para las empresas de un sector "
    "específico. En consecuencia, se formula la siguiente pregunta de investigación: ¿cómo se "
    "distribuye el riesgo de sustitución laboral por inteligencia artificial cognitiva y por "
    "robótica entre las ocupaciones y ramas de la industria manufacturera de Jalisco, y qué factores "
    "determinan cuál de las dos fronteras domina?")

seccion("Justificación")
par("La relevancia del problema es social y económica. La manufactura es la principal fuente de "
    "empleo formal del estado, y la tesis estima que la automatización física presiona sobre todo a "
    "trabajadores con menor escolaridad, que son también los que tienen menos opciones de "
    "reconversión. Del lado económico, veinte años de Censos Económicos muestran que en Jalisco los "
    "sectores donde automatizar resultaba más rentable profundizaron su capital y redujeron la "
    "participación del trabajo en el valor agregado, con valores p por permutación de 0.013 y 0.004. "
    "Es decir, la sustitución no es solo una posibilidad técnica, sino un comportamiento observado.")
par("El impacto esperado se dirige a quienes toman decisiones en el sector: autoridades estatales de "
    "desarrollo económico y trabajo, cámaras industriales y centros de capacitación. Un diagnóstico "
    "por rama y ocupación permitiría orientar la formación de trabajadores hacia las ocupaciones con "
    "mayor riesgo antes de que el desplazamiento ocurra. La tesis documenta que ese momento todavía "
    "existe: la capacidad de los modelos de lenguaje ya aumentó y las expectativas de desplazamiento "
    "de la población crecieron 12.5 puntos entre 2020 y 2023, pero aún no se detecta un efecto en el "
    "empleo, lo que abre una ventana para la política pública.")
par("La contribución original es metodológica. La tesis construye dos índices propios de exposición "
    "ocupacional: el DBOE, que agrega una dimensión temporal al índice de Felten et al. (2021) a partir "
    "de curvas anuales de desempeño de los modelos de lenguaje y reproduce el índice publicado con "
    "una correlación de 0.94, y el DEOE, un índice de exposición física validado contra la medida de "
    "robots de Webb (2020) con una correlación de 0.76. Frente a las soluciones existentes, el modelo "
    "propuesto mide ambas fronteras con la misma metodología, incorpora la rentabilidad de "
    "automatizar y se ancla en datos mexicanos de empleo, censos e inversión.")

seccion("Objetivos")
sub("Objetivo general")
par("Evaluar el riesgo de sustitución laboral en la industria manufacturera de Jalisco frente a la "
    "inteligencia artificial cognitiva y la robótica, mediante un modelo de ciencia de datos que "
    "integre la exposición ocupacional, la rentabilidad de automatizar y escenarios de adopción "
    "tecnológica para el periodo 2025-2030.")
sub("Objetivos específicos")
item("1. Identificar y caracterizar las ocupaciones y ramas de la industria manufacturera de Jalisco, "
     "así como su composición de empleo, a partir de la ENOE, los Censos Económicos y los registros "
     "del IMSS.")
item("2. Construir y validar dos índices de exposición ocupacional, uno cognitivo (DBOE) y uno físico "
     "(DEOE), y aplicarlos a la estructura ocupacional de la manufactura.")
item("3. Desarrollar modelos que relacionen la exposición con el uso observado de la IA y con la "
     "sustitución de trabajo por capital en función de la rentabilidad de automatizar.")
item("4. Evaluar y comparar el desempeño de los modelos y la robustez de sus resultados mediante "
     "validación externa, validación cruzada e inferencia por permutación.")
item("5. Proyectar la presión de sustitución hacia 2030 en tres escenarios de adopción y presentar los "
     "resultados en un tablero de visualización por rama, ocupación y municipio.")

seccion("Hipótesis")
par("H1. Dentro de la industria manufacturera de Jalisco, la exposición a la IA cognitiva y la "
    "exposición a la robótica recaen en ocupaciones distintas: los operadores y trabajadores de "
    "producción concentran la exposición física, mientras que las ocupaciones administrativas, "
    "técnicas y de supervisión concentran la exposición cognitiva. Se contrastará con análisis "
    "factorial exploratorio y confirmatorio sobre los índices de exposición.")
par("H2. Las ramas manufactureras con mayor rentabilidad de automatizar, medida con el Índice de "
    "Rentabilidad de la Automatización, presentan mayor profundización de capital y menor "
    "participación del trabajo en el valor agregado. Se contrastará con un panel de los Censos "
    "Económicos con efectos fijos e inferencia por permutación.")

seccion("Antecedentes")
par("Los antecedentes se presentan en orden cronológico. Autor, Levy y Murnane (2003) establecieron "
    "el enfoque de tareas: la tecnología sustituye tareas y no ocupaciones completas, y las tareas "
    "rutinarias son las más fáciles de automatizar. Frey y Osborne (2017) estimaron, con un "
    "clasificador de procesos gaussianos aplicado a 702 ocupaciones, que 47 % del empleo de Estados "
    "Unidos enfrentaba un riesgo alto de automatización. Acemoglu y Restrepo (2018) formalizaron el "
    "proceso como una carrera entre el desplazamiento del trabajo y la creación de tareas nuevas, e "
    "incorporaron la condición de que automatizar solo ocurre cuando es más barato que pagar "
    "salarios.")
par("Sobre la robótica, Graetz y Michaels (2018) encontraron, con datos de 17 países entre 1993 y "
    "2007, que los robots industriales elevaron la productividad, el valor agregado y los salarios "
    "sin un efecto significativo en las horas totales trabajadas. Acemoglu y Restrepo (2019) "
    "atribuyeron el menor crecimiento del empleo en Estados Unidos a un desplazamiento más rápido, "
    "sobre todo en la manufactura, y a una creación de tareas nuevas más débil. Acemoglu y Restrepo "
    "(2020) estimaron que cada robot adicional por cada mil trabajadores redujo la razón "
    "empleo-población entre 0.18 y 0.34 puntos porcentuales en las zonas laborales de ese país.")
par("Para México, Artuc, Christiaensen y Winkler (2019) mostraron que un robot adicional por cada mil "
    "trabajadores en Estados Unidos reduce 6.7 % el crecimiento de las exportaciones por trabajador "
    "de México hacia ese país, y que el empleo manufacturero cae en los municipios con ocupaciones "
    "más automatizables. Faber (2020) encontró que los robots instalados en Estados Unidos reducen el "
    "empleo en los mercados laborales mexicanos, con el mayor efecto en operadores de maquinaria de "
    "baja escolaridad de la manufactura. Webb (2020) midió la exposición de las ocupaciones con el "
    "texto de las patentes y mostró que, a diferencia del software y los robots, la IA se dirige a "
    "tareas de alta calificación.")
par("La llegada de los modelos de lenguaje abrió una nueva línea. Brynjolfsson, Rock y Syverson (2021) "
    "explicaron por qué los efectos de las tecnologías de propósito general tardan en aparecer en "
    "las estadísticas. Eloundou et al. (2023) estimaron que cerca de 80 % de los trabajadores de "
    "Estados Unidos tiene al menos 10 % de sus tareas expuestas a estos modelos. Felten, Raj y "
    "Seamans (2023) adaptaron su índice de exposición a la IA a los modelos de lenguaje, y Gmyrek, "
    "Berg y Bescond (2023) concluyeron para la OIT que el efecto dominante será complementar más que "
    "automatizar. En América Latina, Azuara, Ripani y Torres (2024) estimaron que 74 % de los "
    "empleos en México tiene más de 10 % de sus tareas expuestas, y Benítez-Rueda y Parrado (2024) "
    "calcularon que alrededor de 16 millones de empleos mexicanos están muy expuestos en un horizonte "
    "de un año. Finalmente, Handa et al. (2025) midieron por primera vez el uso real de la IA por "
    "ocupación a partir de millones de conversaciones con un asistente.")

seccion("Marco teórico")
par("¿Qué se sabe hasta ahora? El marco de tareas (Autor et al., 2003) y el modelo de desplazamiento "
    "y reinstalación (Acemoglu y Restrepo, 2018, 2019) son la base teórica de la investigación. Según "
    "este enfoque, el efecto de la automatización sobre el empleo depende del balance entre las tareas "
    "que pasan al capital y las tareas nuevas que surgen para el trabajo, y la sustitución se "
    "materializa solo cuando el costo del capital es menor que el salario. La paradoja de Moravec "
    "(Moravec, 1988), según la cual lo que resulta sencillo para las personas es difícil para las "
    "máquinas y viceversa, explica por qué la IA cognitiva y los robots avanzan sobre tareas "
    "distintas, como confirmó empíricamente Webb (2020).")
par("¿Cómo se relaciona el problema con lo que se sabe? La literatura mide la exposición de las "
    "ocupaciones, pero lo hace por separado para cada tecnología y casi siempre con datos de Estados "
    "Unidos (Frey y Osborne, 2017; Eloundou et al., 2023; Felten et al., 2023). Los estudios para "
    "México muestran que la robotización afecta a la manufactura nacional a través del comercio "
    "(Artuc et al., 2019; Faber, 2020), y los trabajos del BID trasladan las medidas cognitivas a la "
    "región (Azuara et al., 2024; Benítez-Rueda y Parrado, 2024). Falta un análisis que combine "
    "ambas fronteras dentro de un mismo sector y que considere la rentabilidad de automatizar. La "
    "teoría de la curva J (Brynjolfsson et al., 2021) ayuda a interpretar por qué el efecto en el "
    "empleo todavía no es visible.")
par("¿Por qué este método? El enfoque es cuantitativo porque el riesgo se expresa en magnitudes "
    "comparables entre ocupaciones, ramas y territorios. Los índices de exposición se construyen a "
    "partir de los descriptores de tareas de O*NET, como en la literatura de referencia, y se validan "
    "contra medidas externas. Los modelos estadísticos permiten contrastar las hipótesis con "
    "inferencia formal, y los modelos de aprendizaje automático aportan capacidad predictiva y "
    "medidas de importancia de variables. La proyección por escenarios, en lugar de un pronóstico, "
    "responde a que no existe un panel histórico de automatización observada para Jalisco.")

seccion("Metodología")
par("Tipo de estudio. Investigación cuantitativa, no experimental, que combina un análisis transversal "
    "de la exposición ocupacional con un análisis longitudinal de la sustitución de trabajo por "
    "capital y una proyección por escenarios.")
par("Población y unidades de análisis. Trabajadores ocupados en la industria manufacturera de Jalisco "
    "(sectores 31-33 del SCIAN). Las unidades de análisis son la ocupación (clasificación SINCO 2011 "
    "y su equivalencia SOC), el trabajador, la rama manufacturera y el municipio.")
par("Fuentes de datos. Todas son públicas y se integran en una base de datos SQL Server que funciona "
    "como fuente única: O*NET 28.3 para el contenido de tareas; el apéndice de Felten et al. (2021) y "
    "la base de capacidades de Epoch AI (doce pruebas de referencia, 2022-2026) para el índice "
    "cognitivo; la ENOE del tercer trimestre de 2024 (6,147 ocupados de Jalisco con ocupación a cuatro "
    "dígitos) y once trimestres consecutivos para el análisis de informalidad; los Censos Económicos "
    "2003 a 2023; el empleo formal mensual del IMSS 2000-2024; la inversión extranjera directa de la "
    "Secretaría de Economía; las estadísticas de robots de la Federación Internacional de Robótica; y "
    "el Índice Económico de Anthropic como medida de uso observado. El cruce entre SINCO y SOC usa las "
    "tablas comparativas oficiales del INEGI.")
par("Procedimiento. El trabajo se organiza en seis pasos, alineados con los objetivos específicos:")
item("1. Integración y depuración de las fuentes, y delimitación de la población manufacturera por rama "
     "y ocupación.")
item("2. Construcción de los índices DBOE y DEOE a partir de O*NET, su validación contra los índices "
     "publicados y contra la medida de robots de Webb (2020), y su traslado a las ocupaciones "
     "manufactureras mediante la cadena de cruce SINCO-SOC.")
item("3. Análisis de la estructura de la exposición con análisis factorial exploratorio y confirmatorio, "
     "para contrastar H1, y descripción del perfil de exposición del sector ponderado por empleo.")
item("4. Modelación de la exposición frente al uso observado de la IA con un modelo de dos partes "
     "(hurdle), complementado con modelos de aprendizaje supervisado (bosques aleatorios y gradient "
     "boosting) con validación cruzada e interpretación mediante valores SHAP.")
item("5. Contraste de H2 con un panel de los Censos Económicos y efectos fijos de periodo, usando el "
     "Índice de Rentabilidad de la Automatización rezagado e inferencia por permutación. Se propone "
     "desagregar este análisis a nivel de rama manufacturera.")
item("6. Proyección 2025-2030 en tres escenarios (conservador, base y acelerado) que combinan la "
     "exposición, la rentabilidad y las curvas de capacidad de la IA y de adopción robótica, para "
     "dimensionar la presión de sustitución en el sector, y elaboración del tablero de "
     "visualización.")
par("Herramientas de análisis. Python (pandas, NumPy, statsmodels, scikit-learn, factor_analyzer y "
    "Matplotlib), SQL Server para la integración de datos y GitHub para el control de versiones y la "
    "reproducibilidad. Cada tabla y figura se genera con un script versionado.")

seccion("Recursos")
par("Recursos humanos. El tesista, responsable del desarrollo del proyecto; el director de tesis, por "
    "designar; y la profesora de la unidad de aprendizaje Desarrollo de Proyecto I, que da "
    "seguimiento al protocolo.")
par("Recursos materiales. Equipo de cómputo personal, un servidor local con SQL Server para la base de "
    "datos del proyecto, software libre para el análisis (Python y sus bibliotecas) y un repositorio en "
    "GitHub. Las fuentes de información son públicas y gratuitas.")
par("Recursos económicos. El proyecto no requiere la compra de datos ni de licencias de software. Los "
    "costos se limitan al uso del equipo propio y a la conexión a internet, cubiertos por el tesista.")

seccion("Cronograma")
par("El cronograma reproduce el plan registrado en el avance de protocolo de la tesis, con la "
    "actividad de reenfoque a la industria manufacturera añadida y el estado de cada etapa a octubre "
    "de 2026.")
caption_table(1, "Cronograma de actividades del proyecto de tesis")
table([
    ["Etapa / actividad", "2025B", "2026A", "2026B", "2027A", "Estado"],
    ["Revisión de literatura y antecedentes", "Ago-Sep", "", "", "", "Concluida"],
    ["Corrección del marco teórico y definición metodológica", "Sep-Oct", "", "", "", "Concluida"],
    ["Obtención y limpieza de datos (INEGI, O*NET)", "Oct-Nov", "", "", "", "Concluida"],
    ["Mapeo y normalización de ocupaciones", "Nov-Dic", "Ene", "", "", "Concluida"],
    ["Cálculo de índices", "", "Feb-Mar", "", "", "Concluida"],
    ["Incorporación de indicadores emergentes de IA", "", "Mar-Abr", "", "", "Concluida"],
    ["Desarrollo y entrenamiento de modelos", "", "May-Jul", "Ago-Sep", "", "Concluida"],
    ["Reenfoque a la industria manufacturera", "", "", "Ago-Oct", "", "En curso"],
    ["Evaluación y validación del modelo", "", "", "Sep-Nov", "", "En curso"],
    ["Visualización y desarrollo del tablero", "", "", "Nov-Dic", "Ene", "Pendiente"],
    ["Redacción de resultados y análisis de impacto", "", "", "Dic", "Feb-Mar", "En curso"],
    ["Escritura y revisión del documento final", "", "", "", "Mar-Jun", "Pendiente"],
    ["Presentación y defensa del trabajo de tesis", "", "", "", "Jul 2027", "Pendiente"],
], [3300, 900, 900, 900, 1000, 1100])
note("Nota. Elaboración propia con base en el plan del avance de protocolo de la tesis.")

seccion("Referencias bibliográficas")
for a in [
 "Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. American Economic Review, 108(6), 1488-1542. https://doi.org/10.1257/aer.20160696",
 "Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. Journal of Economic Perspectives, 33(2), 3-30. https://doi.org/10.1257/jep.33.2.3",
 "Acemoglu, D., & Restrepo, P. (2020). Robots and jobs: Evidence from US labor markets. Journal of Political Economy, 128(6), 2188-2244. https://doi.org/10.1086/705716",
 "Artuc, E., Christiaensen, L., & Winkler, H. (2019). Does automation in rich countries hurt developing ones? Evidence from the U.S. and Mexico (Policy Research Working Paper 8741). Banco Mundial.",
 "Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. The Quarterly Journal of Economics, 118(4), 1279-1333. https://doi.org/10.1162/003355303322552801",
 "Azuara, O., Ripani, L., & Torres, E. (2024). AI and the increase of productivity and labor inequality in Latin America: Potential impact of large language models on Latin American workforce (IDB Discussion Paper 01076). Banco Interamericano de Desarrollo.",
 "Benítez-Rueda, M., & Parrado, E. (2024). “Mirror, mirror on the wall: Which jobs will AI replace after all?”: A new index of occupational exposure (IDB Working Paper 1624). Banco Interamericano de Desarrollo.",
 "Brynjolfsson, E., Rock, D., & Syverson, C. (2021). The productivity J-curve: How intangibles complement general purpose technologies. American Economic Journal: Macroeconomics, 13(1), 333-372. https://doi.org/10.1257/mac.20180386",
 "Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. arXiv. https://arxiv.org/abs/2303.10130",
 "Faber, M. (2020). Robots and reshoring: Evidence from Mexican labor markets. Journal of International Economics, 127, 103384. https://doi.org/10.1016/j.jinteco.2020.103384",
 "Felten, E., Raj, M., & Seamans, R. (2021). Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses. Strategic Management Journal, 42(12), 2195-2217. https://doi.org/10.1002/smj.3286",
 "Felten, E., Raj, M., & Seamans, R. (2023). How will language modelers like ChatGPT affect occupations and industries? arXiv. https://arxiv.org/abs/2303.01157",
 "Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019",
 "Gmyrek, P., Berg, J., & Bescond, D. (2023). Generative AI and jobs: A global analysis of potential effects on job quantity and quality (ILO Working Paper 96). Organización Internacional del Trabajo. https://doi.org/10.54394/FHEM8239",
 "Graetz, G., & Michaels, G. (2018). Robots at work. The Review of Economics and Statistics, 100(5), 753-768. https://doi.org/10.1162/rest_a_00754",
 "Handa, K., Tamkin, A., McCain, M., Huang, S., Durmus, E., Heck, S., Mueller, J., Hong, J., Ritchie, S., Belonax, T., Troy, K. K., Amodei, D., Kaplan, J., Clark, J., & Ganguli, D. (2025). Which economic tasks are performed with AI? Evidence from millions of Claude conversations. arXiv. https://arxiv.org/abs/2503.04761",
 "Moravec, H. (1988). Mind children: The future of robot and human intelligence. Harvard University Press.",
 "Webb, M. (2020). The impact of artificial intelligence on the labor market [Documento de trabajo]. Stanford University. https://www.michaelwebb.co/webb_ai.pdf",
]:
    ref(a)

from docx.shared import Cm
for s_ in doc.sections:
    s_.left_margin, s_.right_margin = Cm(3.0), Cm(2.5)
    s_.top_margin, s_.bottom_margin = Cm(2.5), Cm(2.5)
doc.save(OUT)
print("DOCX:", OUT)
