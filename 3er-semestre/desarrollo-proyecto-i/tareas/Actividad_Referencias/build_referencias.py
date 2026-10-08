# -*- coding: utf-8 -*-
"""
Desarrollo de Proyecto I - Busqueda y analisis de referencias para el trabajo recepcional.
Builds the reference analysis report (DOCX/PDF from the MCD template) and an XLSX copy.
Downloaded PDFs live in ./referencias, renamed to match the chronological order of the table.
"""
import os
import glob
import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"C:\Users\carlo\GitHub\mcd_cucea"
TEMPLATE = BASE + r"\_recursos\plantillas\plantilla_informe_MCD.docx"
HERE = os.path.dirname(os.path.abspath(__file__))
REFDIR = os.path.join(HERE, "referencias")
OUT_DOCX = os.path.join(HERE, "Analisis_Referencias_DesarrolloProyectoI_CarlosPulidoRosas.docx")
OUT_XLSX = os.path.join(HERE, "Tabla_Referencias_CarlosPulidoRosas.xlsx")
NAVY = RGBColor(0x1F, 0x49, 0x7D); WHITE = RGBColor(0xFF, 0xFF, 0xFF); GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)

TITULO_TESIS = ("Modelo de evaluación del riesgo de sustitución laboral mediante herramientas de "
                "ciencia de datos: inteligencia artificial cognitiva y robótica en la industria "
                "manufacturera de Jalisco")

# (source pdf stem, record). Order = chronological order of the table.
REFS = [
 ("01_Autor_Levy_Murnane_2003", dict(
  titulo="The skill content of recent technological change: An empirical exploration",
  web="https://doi.org/10.1162/003355303322552801 (versión NBER w8337)",
  autores="David H. Autor, Frank Levy y Richard J. Murnane", anio=2003,
  journal="The Quarterly Journal of Economics, 118(4), 1279-1333. MIT Press",
  aporte="Propone el enfoque de tareas: separa el trabajo en tareas rutinarias y no rutinarias, "
         "cognitivas y manuales, y demuestra que la computarización sustituye a las rutinarias y "
         "complementa a las analíticas e interactivas.",
  desc="Explica por qué la computadora cambió la demanda de habilidades en Estados Unidos entre "
       "1960 y 1998. La idea de fondo es que la tecnología no elimina ocupaciones completas, sino "
       "tareas concretas, y que las más fáciles de programar son las que siguen reglas explícitas. "
       "De aquí sale el marco de tareas con el que la tesis mide la exposición de las "
       "ocupaciones de Jalisco.")),
 ("02_Frey_Osborne_2017", dict(
  titulo="The future of employment: How susceptible are jobs to computerisation?",
  web="https://doi.org/10.1016/j.techfore.2016.08.019 (versión Oxford Martin School, 2013)",
  autores="Carl Benedikt Frey y Michael A. Osborne", anio=2017,
  journal="Technological Forecasting and Social Change, 114, 254-280. Elsevier",
  aporte="Estima la probabilidad de automatización de 702 ocupaciones con un clasificador de "
         "procesos gaussianos entrenado con juicio experto y concluye que 47 % del empleo de "
         "Estados Unidos está en riesgo alto.",
  desc="Es el estudio que instaló en el debate público la pregunta de cuántos empleos pueden "
       "automatizarse. Identifica tres cuellos de botella técnicos (percepción y manipulación, "
       "creatividad e inteligencia social) y los extrapola con O*NET. En la tesis funciona como "
       "punto de partida y como contraste, porque su medida es estática, depende del juicio de "
       "expertos y supone que el trabajo cognitivo no rutinario está a salvo.")),
 ("03_Acemoglu_Restrepo_2018_race", dict(
  titulo="The race between man and machine: Implications of technology for growth, factor shares, and employment",
  web="https://doi.org/10.1257/aer.20160696 (versión NBER w22252)",
  autores="Daron Acemoglu y Pascual Restrepo", anio=2018,
  journal="American Economic Review, 108(6), 1488-1542. American Economic Association",
  aporte="Formaliza la automatización como una carrera entre el desplazamiento del trabajo en "
         "tareas existentes y la creación de tareas nuevas, e incorpora la condición de que "
         "automatizar solo ocurre cuando es más barato que pagar salarios.",
  desc="Las máquinas ocupan tareas que antes hacían personas, pero al mismo tiempo aparecen tareas "
       "nuevas en las que el trabajo humano tiene ventaja; el saldo entre ambas fuerzas define qué "
       "pasa con el empleo. La condición de rentabilidad es la base del Índice de Rentabilidad de "
       "la Automatización que la tesis calcula por sector económico con los Censos Económicos.")),
 ("06_Graetz_Michaels_2018", dict(
  titulo="Robots at work",
  web="https://doi.org/10.1162/rest_a_00754 (versión CEP DP1335)",
  autores="Georg Graetz y Guy Michaels", anio=2018,
  journal="The Review of Economics and Statistics, 100(5), 753-768. MIT Press",
  aporte="Con datos de 17 países entre 1993 y 2007 muestra que los robots industriales "
         "elevaron la productividad laboral, el valor agregado y los salarios, y añadieron cerca de "
         "0.37 puntos porcentuales al crecimiento anual, sin un efecto significativo en las horas "
         "totales trabajadas, aunque con indicios de menos horas para la mano de obra de baja y media "
         "calificación.",
  desc="Es una de las primeras evaluaciones del efecto de los robots industriales entre países, "
       "construida con los datos de la Federación Internacional de Robótica. Es antecedente "
       "del eje físico de la automatización y del uso del acervo de robots de la IFR, que la tesis "
       "emplea para construir la curva de adopción robótica de la proyección 2025-2030.")),
 ("16_Artuc_Christiaensen_Winkler_2019_BM", dict(
  titulo="Does automation in rich countries hurt developing ones? Evidence from the U.S. and Mexico",
  web="https://documents.worldbank.org/curated/en/221101550152344701",
  autores="Erhan Artuc, Luc Christiaensen y Hernan Winkler", anio=2019,
  journal="Policy Research Working Paper 8741. Banco Mundial",
  aporte="Un robot adicional por cada mil trabajadores en Estados Unidos reduce 6.7 % el "
         "crecimiento de las exportaciones por trabajador de México hacia ese país, y la "
         "automatización reduce el empleo manufacturero en los municipios con ocupaciones más "
         "automatizables.",
  desc="Con datos de exportaciones por municipio, sector y destino entre 2004 y 2014, analiza cómo "
       "la automatización en Estados Unidos llega a México a través del comercio. El efecto "
       "agregado sobre el empleo manufacturero es nulo porque combina pérdidas en unas zonas y "
       "ganancias en otras. Es clave para la tesis porque muestra que la presión robótica sobre la "
       "manufactura mexicana depende de la composición ocupacional de cada territorio.")),
 ("04_Acemoglu_Restrepo_2019_new_tasks", dict(
  titulo="Automation and new tasks: How technology displaces and reinstates labor",
  web="https://doi.org/10.1257/jep.33.2.3 (versión NBER w25684)",
  autores="Daron Acemoglu y Pascual Restrepo", anio=2019,
  journal="Journal of Economic Perspectives, 33(2), 3-30. American Economic Association",
  aporte="Descompone el cambio en la demanda de trabajo en efectos de desplazamiento, "
         "productividad y reinstalación, y concluye que el menor crecimiento del empleo en "
         "Estados Unidos durante tres décadas se explica por un desplazamiento más rápido, sobre "
         "todo en la manufactura, y por una reinstalación más débil.",
  desc="Presenta de forma accesible el marco teórico de los mismos autores y lo aplica a datos "
       "sectoriales. Explica por qué el empleo puede estancarse aunque la productividad crezca, "
       "cuando se automatiza mucho y se crean pocas tareas nuevas. La tesis lo usa para "
       "interpretar la prueba de la hipótesis H4, en la que los sectores con mayor incentivo a "
       "automatizar profundizaron su capital y perdieron participación laboral.")),
 ("05_Acemoglu_Restrepo_2020_robots", dict(
  titulo="Robots and jobs: Evidence from US labor markets",
  web="https://doi.org/10.1086/705716 (versión NBER w23285)",
  autores="Daron Acemoglu y Pascual Restrepo", anio=2020,
  journal="Journal of Political Economy, 128(6), 2188-2244. University of Chicago Press",
  aporte="Estima que cada robot adicional por cada mil trabajadores redujo la razón "
         "empleo/población entre 0.18 y 0.34 puntos porcentuales y los salarios entre 0.25 y 0.5 % "
         "en las zonas laborales de Estados Unidos entre 1990 y 2007 (versión de trabajo).",
  desc="A diferencia de Graetz y Michaels, encuentra efectos negativos y significativos de los "
       "robots sobre el empleo local. Mide la exposición de cada zona según su composición "
       "industrial, una lógica similar a la del mapa municipal de la tesis, que combina la "
       "composición sectorial de los 125 municipios de Jalisco con la exposición de cada sector.")),
 ("15_Faber_2020_robots_Mexico", dict(
  titulo="Robots and reshoring: Evidence from Mexican labor markets",
  web="https://doi.org/10.1016/j.jinteco.2020.103384",
  autores="Marius Faber", anio=2020,
  journal="Journal of International Economics, 127, 103384. Elsevier",
  aporte="Muestra que los robots instalados en Estados Unidos reducen de forma considerable el "
         "empleo en los mercados laborales mexicanos, con mayor efecto en hombres y en operadores "
         "de maquinaria de baja escolaridad de la manufactura.",
  desc="Analiza el canal de la relocalización: si producir con robots en Estados Unidos resulta "
       "más barato, disminuye la demanda de importaciones mexicanas. Con datos de 1990 a 2015 "
       "encuentra caídas en el empleo, en las exportaciones y en el número de plantas "
       "exportadoras. Es la referencia más directa para el enfoque manufacturero, porque estudia a "
       "los operadores de maquinaria, el grupo ocupacional con mayor exposición a la automatización "
       "física en los resultados de la tesis.")),
 ("07_Webb_2020", dict(
  titulo="The impact of artificial intelligence on the labor market",
  web="https://www.michaelwebb.co/webb_ai.pdf",
  autores="Michael Webb", anio=2020,
  journal="Documento de trabajo. Stanford University",
  aporte="Mide la exposición de las ocupaciones a robots, software e inteligencia artificial a "
         "partir del traslape textual entre patentes y descripciones de tareas, y muestra que, a "
         "diferencia del software y los robots, la IA se dirige a tareas de alta calificación.",
  desc="Compara el lenguaje de las patentes con el de las tareas para saber qué trabajos puede "
       "tocar cada tecnología. Su resultado de que la IA y los robots apuntan a ocupaciones "
       "distintas respalda la estructura bipolar, cognitiva frente a física, que obtuvo el análisis "
       "factorial de la tesis, y su índice de robots se usa para validar el índice físico (DEOE), "
       "con una correlación de 0.76.")),
 ("11_Brynjolfsson_Rock_Syverson_2021", dict(
  titulo="The productivity J-curve: How intangibles complement general purpose technologies",
  web="https://doi.org/10.1257/mac.20180386 (versión NBER w25148)",
  autores="Erik Brynjolfsson, Daniel Rock y Chad Syverson", anio=2021,
  journal="American Economic Journal: Macroeconomics, 13(1), 333-372. American Economic Association",
  aporte="Demuestra que las tecnologías de propósito general exigen inversiones intangibles que "
         "no se registran, por lo que la productividad primero se subestima y después se "
         "sobreestima, formando una curva en J.",
  desc="Explica por qué los efectos de una tecnología como la IA tardan en verse en las "
       "estadísticas: las empresas tienen que reorganizar procesos y capacitar a su personal antes "
       "de obtener beneficios. En la tesis uso esta idea para interpretar que todavía no se observe "
       "un efecto en el empleo como una ventana de tiempo para la política pública.")),
 ("08_Eloundou_2023", dict(
  titulo="GPTs are GPTs: An early look at the labor market impact potential of large language models",
  web="https://arxiv.org/abs/2303.10130",
  autores="Tyna Eloundou, Sam Manning, Pamela Mishkin y Daniel Rock", anio=2023,
  journal="arXiv (preprint, 2303.10130); versión publicada en Science, 384(6702), 2024",
  aporte="Con una rúbrica aplicada por anotadores humanos y por GPT-4 estima que cerca de 80 % de "
         "los trabajadores de Estados Unidos tiene al menos 10 % de sus tareas expuestas a los "
         "modelos de lenguaje, y que la exposición crece con el ingreso.",
  desc="Es la primera medición amplia de la exposición ocupacional a los modelos de lenguaje y "
       "plantea que estos son tecnologías de propósito general. Su índice es uno de los "
       "rivales con los que la tesis compara su índice cognitivo, y en la validación externa resultó "
       "el mejor predictor individual del uso observado de IA.")),
 ("09_Felten_Raj_Seamans_2023", dict(
  titulo="How will language modelers like ChatGPT affect occupations and industries?",
  web="https://arxiv.org/abs/2303.01157",
  autores="Edward Felten, Manav Raj y Robert Seamans", anio=2023,
  journal="arXiv (preprint, 2303.01157)",
  aporte="Ajusta su índice de exposición ocupacional a la IA (AIOE) al avance de los modelos de "
         "lenguaje Las ocupaciones más expuestas son los operadores de telemarketing y varios grupos de "
         "docentes universitarios, y las industrias más expuestas son los servicios legales y los "
         "de valores e inversiones.",
  desc="Los autores relacionan aplicaciones de IA con 52 habilidades de O*NET para calcular la "
       "exposición de cada ocupación y luego recalculan el índice para los modelos de lenguaje. El "
       "índice cognitivo de la tesis (DBOE) parte del AIOE de estos autores, pero sustituye la "
       "capacidad fija de la IA por curvas anuales de desempeño en pruebas de referencia.")),
 ("10_Gmyrek_Berg_Bescond_2023_OIT", dict(
  titulo="Generative AI and jobs: A global analysis of potential effects on job quantity and quality",
  web="https://doi.org/10.54394/FHEM8239",
  autores="Paweł Gmyrek, Janine Berg y David Bescond", anio=2023,
  journal="ILO Working Paper 96. Organización Internacional del Trabajo",
  aporte="Concluye que la IA generativa tiene más potencial para complementar que para "
         "automatizar el trabajo, ya que solo el trabajo administrativo resulta muy expuesto, con "
         "24 % de sus tareas en exposición alta.",
  desc="Desde la OIT, califica con GPT-4 las tareas de la clasificación internacional ISCO y "
       "estima la exposición de cada país según su estructura ocupacional. Es útil para la tesis "
       "porque enfrenta el mismo problema que la tesis, trasladar medidas construidas con "
       "datos de Estados Unidos a países con otra estructura productiva.")),
 ("13_Azuara_Ripani_Torres_2024_BID", dict(
  titulo="AI and the increase of productivity and labor inequality in Latin America: Potential impact of large language models on Latin American workforce",
  web="https://publications.iadb.org (Discussion Paper IDB-DP-01076)",
  autores="Oliver Azuara, Laura Ripani y Eric Torres", anio=2024,
  journal="IDB Discussion Paper 01076. Banco Interamericano de Desarrollo",
  aporte="Adapta la metodología de Eloundou et al. a Chile, México y Perú mediante un cruce entre "
         "O*NET, SINCO-2011 e ISCO-08, y estima que 74 % de los empleos en México tiene más de "
         "10 % de sus tareas expuestas a los modelos de lenguaje.",
  desc="Es el antecedente regional más cercano. Construye una correspondencia entre O*NET y el "
       "SINCO y ajusta la exposición según la capacidad de adopción de cada país. La tesis construye "
       "su propia cadena de cruce con las tablas comparativas oficiales del INEGI, por lo que este "
       "trabajo sirve como punto de comparación para los niveles de exposición en México.")),
 ("14_Benitez-Rueda_Parrado_2024_BID", dict(
  titulo="\u201cMirror, mirror on the wall: Which jobs will AI replace after all?\u201d: A new index of occupational exposure",
  web="https://publications.iadb.org (Working Paper IDB-WP-1624)",
  autores="Miguel Benítez-Rueda y Eric Parrado", anio=2024,
  journal="IDB Working Paper 1624. Banco Interamericano de Desarrollo",
  aporte="Propone el índice GENOE, construido con encuestas sintéticas a modelos de lenguaje, y "
         "estima que alrededor de 16 millones de empleos en México están muy expuestos a la IA en "
         "un horizonte de un año.",
  desc="Usa los propios modelos de lenguaje como evaluadores expertos para estimar la "
       "probabilidad de reemplazo de cada ocupación en horizontes de uno, cinco y diez años, "
       "considerando también factores sociales y regulatorios. Aporta una cifra para México y un "
       "enfoque temporal comparable con la capa dinámica del índice cognitivo de la tesis.")),
 ("12_Handa_2025_Anthropic_Economic_Index", dict(
  titulo="Which economic tasks are performed with AI? Evidence from millions of Claude conversations",
  web="https://arxiv.org/abs/2503.04761",
  autores="Kunal Handa, Alex Tamkin, Miles McCain y colaboradores", anio=2025,
  journal="arXiv (preprint, 2503.04761). Anthropic",
  aporte="Asocia millones de conversaciones con un asistente de IA a tareas de O*NET y encuentra "
         "que el uso se concentra en programación y escritura, que 36 % de las ocupaciones usa IA "
         "en al menos una cuarta parte de sus tareas y que 57 % del uso es de complemento.",
  desc="Es la primera medición del uso real de la IA por ocupación, no de su exposición "
       "potencial. La tesis lo utiliza como variable de validación externa de sus índices, ya que "
       "permite contrastar lo que la IA podría hacer con lo que las personas ya hacen con ella.")),
]

APA = [
 "Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. American Economic Review, 108(6), 1488-1542. https://doi.org/10.1257/aer.20160696",
 "Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. Journal of Economic Perspectives, 33(2), 3-30. https://doi.org/10.1257/jep.33.2.3",
 "Acemoglu, D., & Restrepo, P. (2020). Robots and jobs: Evidence from US labor markets. Journal of Political Economy, 128(6), 2188-2244. https://doi.org/10.1086/705716",
 "Artuc, E., Christiaensen, L., & Winkler, H. (2019). Does automation in rich countries hurt developing ones? Evidence from the U.S. and Mexico (Policy Research Working Paper 8741). Banco Mundial.",
 "Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. The Quarterly Journal of Economics, 118(4), 1279-1333. https://doi.org/10.1162/003355303322552801",
 "Azuara, O., Ripani, L., & Torres, E. (2024). AI and the increase of productivity and labor inequality in Latin America: Potential impact of large language models on Latin American workforce (IDB Discussion Paper 01076). Banco Interamericano de Desarrollo.",
 "Benítez-Rueda, M., & Parrado, E. (2024). \u201cMirror, mirror on the wall: Which jobs will AI replace after all?\u201d: A new index of occupational exposure (IDB Working Paper 1624). Banco Interamericano de Desarrollo.",
 "Brynjolfsson, E., Rock, D., & Syverson, C. (2021). The productivity J-curve: How intangibles complement general purpose technologies. American Economic Journal: Macroeconomics, 13(1), 333-372. https://doi.org/10.1257/mac.20180386",
 "Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. arXiv. https://arxiv.org/abs/2303.10130",
 "Faber, M. (2020). Robots and reshoring: Evidence from Mexican labor markets. Journal of International Economics, 127, 103384. https://doi.org/10.1016/j.jinteco.2020.103384",
 "Felten, E., Raj, M., & Seamans, R. (2023). How will language modelers like ChatGPT affect occupations and industries? arXiv. https://arxiv.org/abs/2303.01157",
 "Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019",
 "Gmyrek, P., Berg, J., & Bescond, D. (2023). Generative AI and jobs: A global analysis of potential effects on job quantity and quality (ILO Working Paper 96). Organización Internacional del Trabajo. https://doi.org/10.54394/FHEM8239",
 "Graetz, G., & Michaels, G. (2018). Robots at work. The Review of Economics and Statistics, 100(5), 753-768. https://doi.org/10.1162/rest_a_00754",
 "Handa, K., Tamkin, A., McCain, M., Huang, S., Durmus, E., Heck, S., Mueller, J., Hong, J., Ritchie, S., Belonax, T., Troy, K. K., Amodei, D., Kaplan, J., Clark, J., & Ganguli, D. (2025). Which economic tasks are performed with AI? Evidence from millions of Claude conversations. arXiv. https://arxiv.org/abs/2503.04761",
 "Webb, M. (2020). The impact of artificial intelligence on the labor market [Documento de trabajo]. Stanford University. https://www.michaelwebb.co/webb_ai.pdf",
]


# ============================ helpers =======================================
def set_cell_bg(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"); tcPr.append(shd)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr(); el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true"); trPr.append(el)


def no_split(row):
    trPr = row._tr.get_or_add_trPr(); el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true"); trPr.append(el)


FONT = "Times New Roman"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
_sec = [0]


def add_run(p, t, bold=False, italic=False, color=None, size=None):
    r = p.add_run(t); r.bold = bold; r.italic = italic; r.font.name = FONT
    rpr = r._r.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("ascii", "hAnsi", "cs", "eastAsia"):
        rf.set(qn(f"w:{a}"), FONT)
    if size: r.font.size = Pt(size)
    return r


def add_para(doc, t="", bold=False, italic=False, color=None, size=12,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=0, keep=False, line=2.0):
    p = doc.add_paragraph(); p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.keep_with_next = keep
    p.paragraph_format.line_spacing = line
    if align == WD_ALIGN_PARAGRAPH.JUSTIFY and not bold:
        p.paragraph_format.first_line_indent = Cm(1.25)
    if t: add_run(p, t, bold, italic, color, size)
    return p


def add_heading(doc, t, level=1):
    t = t.split(". ", 1)[1] if t[:1].isdigit() else t
    if level == 1:
        _sec[0] += 1
        return add_para(doc, f"{ROMAN[_sec[0] - 1]}. {t.upper()}", bold=True, size=14,
                        align=WD_ALIGN_PARAGRAPH.CENTER, sb=12, sa=6, keep=True)
    return add_para(doc, t, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, sb=12, keep=True)


def add_apa(doc, t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(1.25); p.paragraph_format.first_line_indent = Cm(-1.25)
    p.paragraph_format.line_spacing = 1.5; p.paragraph_format.space_after = Pt(0)
    add_run(p, t, size=12)


def clear_body_after_table1(doc):
    body = doc.element.body; sect = body.find(qn("w:sectPr")); c = 0; cut = None
    for i, ch in enumerate(list(body)):
        if ch.tag == qn("w:tbl"):
            c += 1
            if c == 2: cut = i; break
    if cut is not None:
        for el in [e for e in list(body)[cut + 1:] if e.tag != qn("w:sectPr")]: body.remove(el)
    if sect is not None and sect not in list(body): body.append(sect)


def set_orientation(section, landscape):
    w, h = section.page_width, section.page_height
    if landscape and w < h or (not landscape) and w > h:
        section.page_width, section.page_height = h, w
    section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT


# ============================ files =========================================
def rename_pdfs():
    for i, (stem, rec) in enumerate(REFS, 1):
        rest = stem.split("_", 1)[1]
        new = os.path.join(REFDIR, f"{i:02d}_{rest}.pdf")
        cur = glob.glob(os.path.join(REFDIR, f"??_{rest}.pdf"))
        if cur and os.path.abspath(cur[0]) != os.path.abspath(new):
            os.replace(cur[0], new)
        rec["archivo"] = os.path.basename(new)


# ============================ build =========================================
def build():
    rename_pdfs()
    recs = [r for _, r in REFS]

    pd.DataFrame([{"No.": i, "Nombre del artículo o libro": r["titulo"], "Autor o autores": r["autores"],
                   "Año de publicación": r["anio"], "Editorial o journal": r["journal"],
                   "Página web": r["web"], "Principal aportación": r["aporte"],
                   "Descripción del tema": r["desc"], "Archivo PDF": r["archivo"]}
                  for i, r in enumerate(recs, 1)]).to_excel(OUT_XLSX, index=False)

    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Desarrollo de Proyecto I"
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Búsqueda y análisis de referencias para el trabajo recepcional")
    r.bold = True; r.font.size = Pt(14); r.font.name = "Times New Roman"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    info = doc.tables[1]
    labels = ["Alumno:", "Fecha:", "Actividad:", "Fuentes:", "Título tentativo:", "Profesora:", "Material:"]
    values = ["Carlos Pulido Rosas", "7 de octubre de 2026",
              "Búsqueda, selección y análisis de referencias",
              "Google Académico y repositorios institucionales (NBER, arXiv, BID, Banco Mundial, OIT)",
              TITULO_TESIS, "Dra. Ana Rosa Jiménez Meza",
              f"{len(recs)} documentos en PDF (carpeta referencias)"]
    for i, (lab, val) in enumerate(zip(labels, values)):
        cl, cv = info.rows[i].cells[0], info.rows[i].cells[1]
        cl.paragraphs[0].runs[0].text = lab
        for extra in cl.paragraphs[0].runs[1:]: extra.text = ""
        cv.paragraphs[0].runs[0].text = val
        for extra in cv.paragraphs[0].runs[1:]: extra.text = ""
    clear_body_after_table1(doc)

    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Propósito")
    add_para(doc,
        "Este documento reúne la revisión bibliográfica inicial del trabajo recepcional, cuyo objeto "
        "es evaluar el riesgo de sustitución laboral que enfrenta la industria manufacturera de "
        "Jalisco ante dos tecnologías distintas: la inteligencia artificial de tipo cognitivo, en "
        "particular los modelos de lenguaje, y la robótica industrial. Se seleccionaron "
        f"{len(recs)} referencias, se descargó el documento completo de cada una y se analizaron en "
        "una tabla que registra su título, sitio web, autores, año, principal aportación, "
        "descripción del tema y editorial o revista.")

    add_heading(doc, "2. Criterios de búsqueda y selección")
    add_para(doc,
        "La búsqueda se realizó en Google Académico y en los repositorios de origen de cada documento. "
        "Se privilegiaron artículos publicados en revistas arbitradas y, en el caso de los temas más "
        "recientes, documentos de trabajo de organismos internacionales y preprints de amplia "
        "citación. Las referencias se organizaron en tres bloques que corresponden a los componentes "
        "de la tesis:")
    for t, d in [("Marco teórico de la automatización.",
                  "Enfoque de tareas y condiciones bajo las cuales la tecnología desplaza o complementa "
                  "al trabajo (Autor et al., 2003; Acemoglu y Restrepo, 2018, 2019)."),
                 ("Robótica y manufactura.",
                  "Evidencia sobre el efecto de los robots industriales en el empleo, con énfasis en "
                  "México y en el canal del comercio con Estados Unidos (Graetz y Michaels, 2018; "
                  "Artuc et al., 2019; Acemoglu y Restrepo, 2020; Faber, 2020)."),
                 ("Medición de la exposición a la inteligencia artificial.",
                  "Índices ocupacionales para la IA cognitiva y los modelos de lenguaje, incluidas "
                  "sus adaptaciones a América Latina y la primera medición de uso real (Frey y "
                  "Osborne, 2017; Webb, 2020; Eloundou et al., 2023; Azuara et al., 2024; Handa et "
                  "al., 2025).")]:
        p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 2.0; add_run(p, t + " ", bold=True, size=12); add_run(p, d, size=12)
    add_para(doc,
        "La tabla presenta las referencias en orden cronológico para mostrar cómo ha evolucionado el "
        "estudio del tema, desde la computarización de las tareas rutinarias hasta la medición del "
        "uso de los modelos de lenguaje.", sb=3)

    # ---------- landscape section with the table
    sec = doc.add_section(WD_SECTION.NEW_PAGE); set_orientation(sec, True)
    for m in ("left_margin", "right_margin"): setattr(sec, m, Inches(0.55))
    sec.top_margin = Inches(0.6); sec.bottom_margin = Inches(0.6)
    add_heading(doc, "3. Tabla de análisis de referencias")
    add_para(doc, "Tabla 1", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True)
    add_para(doc, "Análisis de las referencias seleccionadas, en orden cronológico", italic=True,
             align=WD_ALIGN_PARAGRAPH.LEFT, keep=True)
    heads = ["No.", "Nombre del artículo o libro", "Autor o autores", "Año", "Editorial o journal",
             "Página web", "Principal aportación", "Descripción del tema (elaboración propia)"]
    widths = [0.32, 1.45, 1.05, 0.42, 1.25, 1.2, 1.95, 2.25]
    tbl = doc.add_table(rows=1 + len(recs), cols=len(heads))
    tbl.style = "Table Grid"; tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
    tblPr = tbl._tbl.tblPr; lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    for i, w in enumerate(widths):
        tbl.columns[i].width = Inches(w)          # grid width (what LibreOffice honors)
    for row in tbl.rows:
        for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    repeat_header(tbl.rows[0])
    for ci, h in enumerate(heads):
        c = tbl.rows[0].cells[ci]; set_cell_bg(c, RGBColor(0xD9, 0xD9, 0xD9))
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0; add_run(p, h, bold=True, size=8)
    for ri, rec in enumerate(recs):
        row = tbl.rows[ri + 1]; no_split(row)
        vals = [str(ri + 1), rec["titulo"], rec["autores"], str(rec["anio"]), rec["journal"],
                rec["web"], rec["aporte"], rec["desc"]]
        for ci, v in enumerate(vals):
            c = row.cells[ci]; set_cell_bg(c, WHITE if ri % 2 == 0 else GRAY_L)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci in (0, 3) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.0; add_run(p, v, size=8, italic=(ci == 1))
    add_para(doc, "Nota. Elaboración propia con base en los documentos consultados.", size=8,
             align=WD_ALIGN_PARAGRAPH.LEFT, sb=4, line=1.0)

    # ---------- back to portrait for synthesis and references
    sec2 = doc.add_section(WD_SECTION.NEW_PAGE); set_orientation(sec2, False)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec2, m, Inches(1))
    add_heading(doc, "4. Análisis de los materiales")
    add_para(doc,
        "La revisión muestra que la literatura ha avanzado en tres etapas. La primera, iniciada por "
        "Autor, Levy y Murnane (2003), estableció que la tecnología sustituye tareas y no ocupaciones "
        "completas, y que las tareas rutinarias son las más vulnerables. Sobre esa base, Frey y "
        "Osborne (2017) estimaron por primera vez la probabilidad de automatización de cada ocupación, "
        "aunque con una medida estática que dependía del juicio de expertos y que consideraba al "
        "trabajo cognitivo no rutinario como protegido.")
    add_para(doc,
        "La segunda etapa incorporó el razonamiento económico y la evidencia causal. Acemoglu y "
        "Restrepo (2018, 2019) mostraron que el efecto neto de la automatización depende del balance "
        "entre el desplazamiento y la creación de tareas nuevas, y que la sustitución solo ocurre "
        "cuando es rentable. Los estudios empíricos sobre robots no son concluyentes en su signo: "
        "Graetz y Michaels (2018) encuentran ganancias de productividad sin pérdida agregada de horas, "
        "mientras que Acemoglu y Restrepo (2020) encuentran efectos negativos en el empleo local. Para "
        "México, Artuc et al. (2019) y Faber (2020) agregan un canal que es central para la tesis: la "
        "automatización en Estados Unidos afecta a la manufactura mexicana a través de la demanda de "
        "exportaciones, y el efecto recae sobre todo en operadores de maquinaria de baja escolaridad.")
    add_para(doc,
        "La tercera etapa responde a la llegada de los modelos de lenguaje. Webb (2020) documentó que "
        "la IA y los robots apuntan a ocupaciones distintas, y los trabajos de Eloundou et al. (2023), "
        "Felten et al. (2023) y Gmyrek et al. (2023) midieron una exposición que se concentra en "
        "ocupaciones administrativas y profesionales. Azuara et al. (2024) y Benítez-Rueda y Parrado "
        "(2024) trasladaron estas medidas a América Latina, y Handa et al. (2025) aportaron por primera "
        "vez datos de uso real. Brynjolfsson et al. (2021) ofrecen la clave para interpretar por qué "
        "estos efectos todavía no se reflejan con claridad en las estadísticas de empleo.")
    add_para(doc,
        "De la revisión se desprenden dos vacíos que la tesis busca atender. En primer lugar, la "
        "mayoría de los estudios analiza la robótica o la IA cognitiva por separado, aunque ambas "
        "pueden afectar a una misma rama manufacturera a través de ocupaciones distintas. En "
        "segundo lugar, en la revisión realizada no se identificó un análisis específico para la manufactura de Jalisco que combine la exposición de las "
        "ocupaciones con la rentabilidad de automatizar y con el contexto del nearshoring. La tesis "
        "propone un modelo que integra ambas fronteras tecnológicas para este sector.")

    add_heading(doc, "Referencias")
    for a in APA:
        add_apa(doc, a)
    for s_ in doc.sections:
        s_.left_margin, s_.right_margin = Cm(3.0), Cm(2.5)
        s_.top_margin, s_.bottom_margin = Cm(2.5), Cm(2.5)
    doc.save(OUT_DOCX)
    print("DOCX:", OUT_DOCX); print("XLSX:", OUT_XLSX)


if __name__ == "__main__":
    build()
