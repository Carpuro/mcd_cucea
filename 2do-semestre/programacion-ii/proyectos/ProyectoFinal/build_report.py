"""
Genera 08_reporte_final.docx a partir de la plantilla MCD (navy/amber).
Luego convierte a PDF con LibreOffice si esta disponible, o deja el DOCX.
"""

import os, shutil, subprocess
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

TEMPLATE = r'C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\_recursos\plantillas\plantilla_informe_MCD.docx'
OUT_DIR  = os.path.dirname(__file__)
OUT_DOCX = os.path.join(OUT_DIR, '08_reporte_final.docx')
PLOTS_DIR = OUT_DIR

# Colores MCD: navy #1F497D, amber #D48C00
NAVY  = RGBColor(0x1F, 0x49, 0x7D)
AMBER = RGBColor(0xD4, 0x8C, 0x00)

doc = Document(TEMPLATE)

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = NAVY if level == 1 else AMBER
    return h

def add_body(doc, text):
    p = doc.add_paragraph(text, style='Normal')
    p.paragraph_format.space_after = Pt(6)
    return p

def add_bullet(doc, text):
    p = doc.add_paragraph(text, style='List Bullet')
    return p

def add_table_row(table, cells):
    row = table.add_row()
    for i, val in enumerate(cells):
        row.cells[i].text = str(val)
    return row

def add_figure(doc, path, caption, width_cm=14):
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width_cm))
        cap = doc.add_paragraph(caption, style='Caption')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        add_body(doc, f'[Figura pendiente: {caption}]')

# ------------------------------------------------------------------
# 1. PORTADA
# ------------------------------------------------------------------
doc.add_paragraph()
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('PROYECTO FINAL\nProgramacion II')
run.bold = True
run.font.size = Pt(24)
run.font.color.rgb = NAVY

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.add_run('\nIntegracion de SQL, Mineria de Datos y Machine Learning\naplicado a datos reales de ENOE y O*NET\n').font.size = Pt(14)

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run(
    '\nAutor: Carlos Pulido Rosas\n'
    'Tema de tesis: Riesgo de Automatizacion Laboral en Jalisco por IA\n'
    'Materia: Programacion II — MCD CUCEA, Universidad de Guadalajara\n'
    f'Fecha: {datetime.date.today().strftime("%d de mayo de %Y")}\n'
    'Base de datos: ai_automation_risk_jalisco\n'
    'Fuentes: O*NET 28.3 | ENOE Q3 2024 (entidad 14 Jalisco)'
)

doc.add_page_break()

# ------------------------------------------------------------------
# 2. RESUMEN EJECUTIVO
# ------------------------------------------------------------------
add_heading(doc, '1. Resumen Ejecutivo')
add_body(doc,
    'Este proyecto demuestra un pipeline completo de ciencia de datos aplicado al problema '
    'de investigacion de tesis: predecir el riesgo de automatizacion laboral en Jalisco, Mexico, '
    'utilizando datos reales de la Encuesta Nacional de Ocupacion y Empleo (ENOE Q3 2024) '
    'y los descriptores de tareas por ocupacion de O*NET 28.3 (U.S. Department of Labor).')
add_body(doc,
    'Las tecnologias integradas fueron: SQL Server (base de datos ai_automation_risk_jalisco), '
    'Orange Data Mining 3 para exploracion visual, y Python con scikit-learn para modelado '
    'predictivo. El hallazgo principal es que el perfil sociolaboral del trabajador '
    '(educacion, ingreso, sector, formalidad) explica el 36% de la varianza en el riesgo '
    'de automatizacion (R²=0.36), mientras que K-Means identifica tres grupos accionables '
    'de ocupaciones con perfiles de riesgo diferenciados.')
add_body(doc,
    'El Indice de Rentabilidad de la Automatizacion (IRA) revela la paradoja de la agricultura '
    'en Jalisco: es el sector con mayor riesgo tecnico (0.758) Y mayor incentivo economico '
    '(IRA=5.07), pero sigue siendo predominantemente manual debido a factores geograficos y '
    'sociales no capturados por el modelo de Frey & Osborne (2017).')

doc.add_page_break()

# ------------------------------------------------------------------
# 3. DESCRIPCION DEL CONJUNTO DE DATOS
# ------------------------------------------------------------------
add_heading(doc, '2. Descripcion del Conjunto de Datos')

add_heading(doc, '2.1 Fuentes de datos', level=2)
add_body(doc, 'El proyecto utiliza dos fuentes de datos oficiales complementarias:')
add_bullet(doc, 'O*NET 28.3 (U.S. Department of Labor, 2024): descriptores de tareas para 1,016 '
           'ocupaciones SOC. Variables clave: Work Activities (41 elementos), Abilities (52 '
           'elementos), Job Zones. Se procesaron para calcular RTI, demanda cognitiva, '
           'interaccion social y riesgo de automatizacion por grupo SINCO.')
add_bullet(doc, 'ENOE Q3 2024 — Entidad 14 (Jalisco): 13,839 registros de trabajadores en '
           'Jalisco. Variables: c_ocu11c (codigo ocupacional SINCO), ingocup, anios_esc, '
           'eda, seg_soc (formalidad), emple7c (tamano empresa), rama_est2 (sector SCIAN). '
           'Se extrajo una muestra de 2,000 trabajadores ocupados con ingreso.')

add_heading(doc, '2.2 Variables del esquema relacional', level=2)

# Tabla ocupaciones_onet
add_body(doc, 'Tabla ocupaciones_onet (8 registros — grupos SINCO con scores O*NET reales):')
t1 = doc.add_table(rows=1, cols=3)
t1.style = 'Table Grid'
t1.rows[0].cells[0].text = 'Variable'
t1.rows[0].cells[1].text = 'Tipo'
t1.rows[0].cells[2].text = 'Descripcion'
for var, tipo, desc in [
    ('sinco_code',         'INT PK',  'Codigo SINCO (1-9 grupos principales)'),
    ('occupation_name',    'NVARCHAR','Nombre del grupo ocupacional'),
    ('sector',             'NVARCHAR','Sector economico SCIAN'),
    ('frey_osborne_score', 'FLOAT',   'Score base O*NET (Frey & Osborne 2013)'),
    ('rti',                'FLOAT',   'Indice de rutinizacion de tareas'),
    ('cognitive_demand',   'FLOAT',   'Demanda cognitiva (0-100)'),
    ('social_interaction', 'FLOAT',   'Interaccion social (0-100)'),
    ('creativity',         'FLOAT',   'Creatividad (0-100)'),
    ('manual_dexterity',   'FLOAT',   'Destreza manual (0-100)'),
    ('automation_risk',    'FLOAT',   'Riesgo base de automatizacion (0-1)'),
]:
    add_table_row(t1, [var, tipo, desc])

doc.add_paragraph()

# Tabla trabajadores
add_body(doc, 'Tabla trabajadores (2,000 registros — muestra ENOE Q3 2024 Jalisco):')
t2 = doc.add_table(rows=1, cols=3)
t2.style = 'Table Grid'
t2.rows[0].cells[0].text = 'Variable'
t2.rows[0].cells[1].text = 'Tipo'
t2.rows[0].cells[2].text = 'Descripcion'
for var, tipo, desc in [
    ('id_trabajador',   'INT PK IDENTITY', 'Identificador unico del trabajador'),
    ('sinco_code',      'INT FK',          'Codigo SINCO -> ocupaciones_onet'),
    ('escoacum',        'INT',             'Nivel educativo acumulado (1-6)'),
    ('ingocup',         'FLOAT',           'Ingreso mensual por ocupacion (MXN)'),
    ('scian_sector',    'NVARCHAR',        'Sector economico SCIAN'),
    ('formalidad',      'NVARCHAR',        'Formal/Informal (basado en seg_soc)'),
    ('edad',            'INT',             'Edad del trabajador (15-70 anos)'),
    ('tamanio_empresa', 'INT',             'Tamano del establecimiento (trabajadores)'),
    ('ira',             'FLOAT',           'Indice de Rentabilidad de la Automatizacion'),
]:
    add_table_row(t2, [var, tipo, desc])

doc.add_paragraph()
add_body(doc, 'Diagrama Entidad-Relacion: trabajadores.sinco_code -> ocupaciones_onet.sinco_code (FK). '
         'La vista vista_riesgo_jalisco consolida ambas tablas con ajuste sectorial del riesgo.')

doc.add_page_break()

# ------------------------------------------------------------------
# 4. ETAPA SQL
# ------------------------------------------------------------------
add_heading(doc, '3. Etapa SQL: Esquema, JOINs y Vista Analitica')

add_heading(doc, '3.1 Esquema relacional', level=2)
add_body(doc,
    'El esquema fue implementado en SQL Server (base de datos ai_automation_risk_jalisco) '
    'con dos tablas principales relacionadas mediante clave foranea. Cada tabla incluye '
    'PRIMARY KEY explicita, restricciones CHECK para validar rangos y tipos de datos '
    'correctamente declarados (INT, FLOAT, NVARCHAR).')

add_heading(doc, '3.2 Carga masiva de datos (02_insercion.py)', level=2)
add_body(doc,
    'La carga masiva se realizo mediante Python con pyodbc (Windows Authentication). '
    'El script 02_insercion.py lee los datos procesados de O*NET y ENOE desde archivos '
    'CSV en el repositorio ai-automation-risk-jalisco, computa el IRA por sector y carga '
    '8 ocupaciones y 2,000 trabajadores reales de Jalisco.')

add_heading(doc, '3.3 Consultas JOIN', level=2)

add_body(doc, 'JOIN 1 — INNER JOIN: cobertura de datos O*NET')
add_body(doc,
    'Pregunta de tesis: ¿Que porcentaje de trabajadores en Jalisco tiene datos '
    'de tareas O*NET disponibles? Resultado: 2,000 de 2,000 registros mapeados '
    '(100% en muestra). En el universo completo de SINCO, el 18% de ocupaciones '
    'del sector informal no tienen crosswalk SOC->SINCO completo.')

add_body(doc, 'JOIN 2 — LEFT JOIN: ocupaciones sin cobertura O*NET')
add_body(doc,
    'Pregunta de tesis: ¿Que ocupaciones quedan fuera del analisis? '
    'Los trabajadores informales y agropecuarios con codigos SINCO de nivel 4 '
    'detallado no tienen equivalente SOC en O*NET — precisamente los mas vulnerables.')

add_body(doc, 'JOIN 3 — INNER JOIN + GROUP BY + HAVING: riesgo por sector')

t3 = doc.add_table(rows=1, cols=3)
t3.style = 'Table Grid'
for cell, hdr in zip(t3.rows[0].cells, ['Sector','Riesgo Promedio','n Trabajadores']):
    cell.text = hdr
for sector, riesgo, n in [
    ('Agricultura',  '0.758', '58'),
    ('Manufactura',  '0.666', '215'),
    ('Construccion', '0.563', '181'),
    ('Comercio',     '0.499', '74'),
    ('Servicios',    '0.438', '1,331'),
    ('Educacion',    '0.322', '109'),
    ('Salud',        '0.235', '32'),
]:
    add_table_row(t3, [sector, riesgo, n])

doc.add_paragraph()

add_heading(doc, '3.4 Vista Analitica: vista_riesgo_jalisco', level=2)
add_body(doc,
    'La vista consolida el perfil completo del trabajador en una sola consulta. '
    'Utiliza un CTE (sector_factors) para aplicar ajustes contextuales al riesgo: '
    'el mismo grupo SINCO tiene distinto riesgo segun el sector donde opera '
    '(un artesano en manufactura enfrenta mas rutinizacion que en servicios). '
    'Incluye el campo calculado riesgo_categoria (Alto/Medio/Bajo) via CASE WHEN '
    'y el IRA como indicador economico de la automatizacion (Acemoglu & Restrepo 2018).')

doc.add_page_break()

# ------------------------------------------------------------------
# 5. ETAPA ORANGE
# ------------------------------------------------------------------
add_heading(doc, '4. Etapa Orange Data Mining: 3 Flujos de Visualizacion')
add_body(doc,
    'Orange Data Mining 3 se conecto directamente a la vista vista_riesgo_jalisco '
    'mediante el widget SQL Table. Los tres flujos exploran dimensiones '
    'complementarias de la pregunta de investigacion.')

add_heading(doc, '4.1 Flujo 1 — Analisis Exploratorio y Distribuciones', level=2)
add_body(doc, 'Objetivo: caracterizar estadisticamente los datos y detectar patrones iniciales.')
add_bullet(doc, 'SQL Table -> Data Table -> Feature Statistics -> Distributions -> Box Plot -> Scatter Plot')
add_bullet(doc, 'Hallazgo: distribucion de riesgo aproximadamente bimodal (picos en 0.15-0.30 y 0.60-0.80). '
           'Manufactura y Agricultura concentran scores altos; Educacion y Salud scores bajos.')
add_bullet(doc, 'Box Plot: clara separacion entre trabajadores sin escolaridad (riesgo ~0.65) '
           'y posgrado (riesgo ~0.28). La informalidad amplifica el riesgo en todos los sectores.')
add_body(doc, '[Insertar captura de pantalla del Flujo 1 en Orange]')

add_heading(doc, '4.2 Flujo 2 — Correlaciones y Agrupaciones', level=2)
add_body(doc, 'Objetivo: identificar relaciones entre variables y grupos naturales.')
add_bullet(doc, 'Correlations: mapa de calor ordenado por fuerza de correlacion con automation_risk')
add_bullet(doc, 'RTI: r=+0.85 (mayor rutinizacion = mayor riesgo) — confirmado en datos reales O*NET')
add_bullet(doc, 'cognitive_demand: r=-0.77 (mayor demanda cognitiva = menor riesgo)')
add_bullet(doc, 'social_interaction: r=-0.76 (mayor interaccion social = menor riesgo)')
add_bullet(doc, 'k-Means exploratorio (k=3): segmentacion visual previa al analisis Python')
add_body(doc, '[Insertar captura de pantalla del Flujo 2 con mapa de correlaciones]')

add_heading(doc, '4.3 Flujo 3 — Modelo Predictivo Visual', level=2)
add_body(doc, 'Objetivo: clasificar trabajadores por riesgo_categoria (Alto/Medio/Bajo) visualmente.')
add_bullet(doc, 'Select Rows -> Data Sampler (70/30) -> Random Forest + Logistic Regression')
add_bullet(doc, 'Confusion Matrix: errores concentrados entre categorias Medio y Alto')
add_bullet(doc, 'ROC Analysis: AUC para clase Alto riesgo')
add_bullet(doc, 'Test and Score: comparacion de modelos con metricas Accuracy, F1, Precision, Recall')
add_body(doc, '[Insertar capturas del Flujo 3: confusion matrix y ROC]')

doc.add_page_break()

# ------------------------------------------------------------------
# 6. ETAPA PYTHON ML
# ------------------------------------------------------------------
add_heading(doc, '5. Etapa Python: Machine Learning Supervisado y No Supervisado')

add_heading(doc, '5.1 Fuente de datos', level=2)
add_body(doc,
    'Los datos se cargan directamente desde la vista vista_riesgo_jalisco '
    'mediante SQLAlchemy (Windows Authentication). El DataFrame contiene '
    '2,000 registros y 16 columnas sin valores nulos.')

add_heading(doc, '5.2 Algoritmo Supervisado — Regresion Lineal Multiple (U3)', level=2)
add_body(doc,
    'Justificacion: automation_risk es variable continua (0-1), lo que hace '
    'de la Regresion Lineal Multiple el algoritmo apropiado de U3. Se excluyen '
    'intencionalmente las variables O*NET (rti, cognitive_demand, etc.) para '
    'evitar data leakage — esas variables son parte del calculo del target. '
    'La pregunta de tesis es: ¿el perfil sociolaboral observable predice el riesgo?')
add_body(doc, 'Preprocesamiento: estandarizacion con StandardScaler (obligatoria para '
         'interpretar coeficientes comparativamente). Division 70/30 con random_state=42.')

t4 = doc.add_table(rows=1, cols=2)
t4.style = 'Table Grid'
t4.rows[0].cells[0].text = 'Metrica'
t4.rows[0].cells[1].text = 'Valor'
for m, v in [('R² Score','0.3618'),('RMSE','0.1186'),
             ('Varianza explicada','36.2%'),('Particion','70/30'),
             ('random_state','42')]:
    add_table_row(t4, [m, v])
doc.add_paragraph()

add_body(doc,
    'Interpretacion: el perfil sociolaboral (educacion, ingreso, sector, formalidad, IRA) '
    'explica el 36% de la varianza del riesgo de automatizacion. Las variables con mayor '
    'peso son sector_enc (el sector determina el contexto de rutinizacion), '
    'nivel_educativo (factor protector negativo) e ira (a mayor incentivo economico, '
    'mayor riesgo de sustitucion). El 64% restante corresponde a caracteristicas '
    'especificas de las tareas capturadas en O*NET — justificando la Fase 2 de la tesis.')

add_figure(doc, os.path.join(PLOTS_DIR, 'regresion_lineal_resultados.png'),
           'Figura 1. Coeficientes estandarizados y predicciones vs valores reales.')
add_figure(doc, os.path.join(PLOTS_DIR, 'curva_aprendizaje.png'),
           'Figura 2. Curva de aprendizaje — ausencia de overfitting.')

add_heading(doc, '5.3 Analisis del IRA — Incentivo Economico', level=2)
add_body(doc,
    'El IRA (Indice de Rentabilidad de la Automatizacion) operacionaliza la hipotesis '
    'de Acemoglu & Restrepo (2018): la automatizacion ocurre cuando el salario anual '
    'supera el costo amortizado del equipo sustituto. '
    'IRA = ingocup_anual / activo_fijo_amortizado_5_anios (por sector SCIAN, '
    'referencia: Censos Economicos INEGI 2019).')
add_body(doc,
    'Hallazgo critico — La paradoja de la agricultura en Jalisco: '
    'Agricultura tiene el mayor riesgo tecnico (0.758) Y el mayor IRA (5.07), '
    'pero sigue siendo predominantemente manual. Esto confirma la hipotesis H2 '
    'de la tesis: la viabilidad tecnica no implica adopcion inmediata — '
    'factores geograficos, institucionales y de capital humano moderan la adopcion real.')

add_figure(doc, os.path.join(PLOTS_DIR, 'ira_analisis.png'),
           'Figura 3. IRA por sector y relacion IRA vs Riesgo Tecnico (paradoja agricola).')

add_heading(doc, '5.4 Algoritmo No Supervisado — K-Means (U4)', level=2)
add_body(doc,
    'Justificacion: K-Means permite segmentar ocupaciones por perfil de riesgo '
    'sin etiquetas previas. Los datos son numericos continuos y se buscan grupos '
    'naturales accionables para politica publica. El Diagrama de Codo confirma '
    'k=3 como numero optimo de clusters.')
add_body(doc, 'Preprocesamiento: escala obligatoria con StandardScaler (K-Means es sensible '
         'a magnitud). PCA a 2 componentes para visualizacion (68% varianza explicada).')

t5 = doc.add_table(rows=1, cols=5)
t5.style = 'Table Grid'
for cell, hdr in zip(t5.rows[0].cells, ['Cluster','N','Riesgo','Ingreso Prom','Educacion']):
    cell.text = hdr
for cl, n, r, i, e in [
    ('Riesgo Alto',  '521',  '0.650', '$9,168', '3.4'),
    ('Riesgo Medio', '1,264','0.454', '$8,606', '2.7'),
    ('Riesgo Bajo',  '215',  '0.180', '$12,249','4.6'),
]:
    add_table_row(t5, [cl, n, r, i, e])
doc.add_paragraph()

add_body(doc,
    'Hallazgo critico: El cluster de Riesgo Medio (1,264 trabajadores, 63% de la muestra) '
    'concentra perfiles administrativos y tecnicos que Frey & Osborne (2017) clasificaba '
    'como "seguros". Los Large Language Models (GPT-4, Claude) realizan exactamente esas '
    'tareas — motivando la Fase 2 de la tesis (exposicion especifica a LLMs).')

add_figure(doc, os.path.join(PLOTS_DIR, 'kmeans_elbow.png'),
           'Figura 4. Diagrama de Codo — k=3 confirmado como optimo.')
add_figure(doc, os.path.join(PLOTS_DIR, 'kmeans_clusters_pca.png'),
           'Figura 5. Proyeccion PCA de los 3 clusters (68.2% varianza explicada).')

doc.add_page_break()

# ------------------------------------------------------------------
# 7. DISCUSION INTEGRADA
# ------------------------------------------------------------------
add_heading(doc, '6. Discusion Integrada')
add_body(doc,
    'Cada etapa del pipeline responde una dimension distinta de la pregunta de investigacion:')

t6 = doc.add_table(rows=1, cols=3)
t6.style = 'Table Grid'
for cell, hdr in zip(t6.rows[0].cells, ['Etapa','Pregunta','Hallazgo']):
    cell.text = hdr
for etapa, preg, hall in [
    ('SQL INNER JOIN','Cobertura datos','2,000 trabajadores mapeados; 18% informal sin crosswalk'),
    ('SQL LEFT JOIN','Brechas O*NET','Agropecuarios e informales sub-representados'),
    ('SQL GROUP BY','Riesgo por sector','Agri 0.758 > Manuf 0.666 > ... > Salud 0.235'),
    ('Orange Flujo 1','Distribucion','Bimodal; informalidad amplifica riesgo'),
    ('Orange Flujo 2','Correlaciones','RTI r=+0.85 | cognitivo r=-0.77 | social r=-0.76'),
    ('Orange Flujo 3','Modelo visual','Clasificacion Alto/Medio/Bajo con Random Forest'),
    ('Regresion Lineal','Cuantificacion','R²=0.36; sector y educacion son predictores clave'),
    ('K-Means','Segmentacion','3 grupos; Medio (63%) es la nueva zona de riesgo LLM'),
    ('IRA','Incentivo economico','Paradoja agricola: alto riesgo + alto IRA, pero sigue manual'),
]:
    add_table_row(t6, [etapa, preg, hall])

doc.add_paragraph()
add_body(doc,
    'Los resultados convergen en tres conclusiones transversales: (1) el riesgo de '
    'automatizacion en Jalisco esta determinado principalmente por el tipo de tareas '
    '(RTI, demanda cognitiva), no solo por el sector economico; (2) la informalidad '
    'actua como amplificador del riesgo — los trabajadores informales tienen menor '
    'acceso a formacion continua y menor proteccion ante la sustitucion tecnologica; '
    '(3) la brecha entre riesgo tecnico e incentivo economico (IRA) explica por que '
    'sectores con alta probabilidad de automatizacion teorica siguen siendo manuales.')

doc.add_page_break()

# ------------------------------------------------------------------
# 8. CONCLUSIONES Y TRABAJO FUTURO
# ------------------------------------------------------------------
add_heading(doc, '7. Conclusiones y Trabajo Futuro')

add_heading(doc, '7.1 Lo que este proyecto demuestra', level=2)
add_bullet(doc, 'El pipeline SQL -> Orange -> Python es completamente funcional con datos reales de Jalisco.')
add_bullet(doc, 'La Regresion Lineal logra R²=0.36 usando solo variables ENOE observables (sin O*NET).')
add_bullet(doc, 'K-Means identifica 3 grupos accionables de trabajadores con perfiles de riesgo diferenciados.')
add_bullet(doc, 'El IRA revela la paradoja de la agricultura: maxima exposicion tecnica y economica, pero minima adopcion real.')
add_bullet(doc, 'O*NET 28.3 y ENOE Q3 2024 pueden integrarse via crosswalk SINCO-ISCO-08 para analisis de politica laboral en Mexico.')

add_heading(doc, '7.2 Fase 2 — Pendiente en la tesis', level=2)
add_bullet(doc, 'Bloque 3: agregar gpt_exposure_score (Eloundou et al., 2023), LTII y AIOE '
           'para cuantificar exposicion especifica a LLMs. Hipotesis H1: el cluster Medio sube '
           'de categoria al incorporar exposicion LLM.')
add_bullet(doc, 'Bloque 4: integrar Censos Economicos INEGI 2019 para calcular IRA completo '
           'con activo fijo real por sector. Hipotesis H2: IRA predice adopcion real vs riesgo tecnico.')
add_bullet(doc, 'Regresion jerarquica por bloques (M1-M4) con F-test incremental para '
           'cuantificar la contribucion de cada bloque de variables.')
add_bullet(doc, 'Validacion estadistica: Ramsey RESET, VIF para multicolinealidad, SHAP values.')

doc.add_page_break()

# ------------------------------------------------------------------
# 9. REFERENCIAS
# ------------------------------------------------------------------
add_heading(doc, '8. Referencias')

refs = [
    'Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. *American Economic Review, 108*(6), 1488-1542.',
    'Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. *Quarterly Journal of Economics, 118*(4), 1279-1333.',
    'Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. *arXiv preprint arXiv:2303.10130*.',
    'Felten, E. W., Raj, M., & Seamans, R. (2023). How will language modelers like ChatGPT affect occupations and industries? *SSRN Working Paper*.',
    'Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? *Technological Forecasting and Social Change, 114*, 254-280.',
    'INEGI. (2024). Encuesta Nacional de Ocupacion y Empleo (ENOE), tercer trimestre 2024. Instituto Nacional de Estadistica y Geografia.',
    'U.S. Department of Labor. (2024). O*NET Database 28.3. National Center for O*NET Development.',
]
for ref in refs:
    p = doc.add_paragraph(style='List Paragraph')
    p.add_run(ref)
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.first_line_indent = Cm(-0.5)

# ------------------------------------------------------------------
# GUARDAR
# ------------------------------------------------------------------
doc.save(OUT_DOCX)
print(f'Reporte guardado: {OUT_DOCX}')

# Intentar convertir a PDF con LibreOffice (si disponible en homelab via SSH)
# En Windows local, intentar con soffice si esta instalado
soffice_paths = [
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
    '/usr/bin/soffice',  # homelab Linux
]
soffice = next((p for p in soffice_paths if os.path.exists(p)), None)
if soffice:
    result = subprocess.run(
        [soffice, '--headless', '--convert-to', 'pdf', '--outdir', OUT_DIR, OUT_DOCX],
        capture_output=True, text=True
    )
    pdf_path = OUT_DOCX.replace('.docx', '.pdf')
    if os.path.exists(pdf_path):
        print(f'PDF generado: {pdf_path}')
    else:
        print(f'LibreOffice error: {result.stderr}')
else:
    print('LibreOffice no encontrado. Abre el DOCX y exporta a PDF manualmente.')
    print('O convierte en el homelab: soffice --headless --convert-to pdf 08_reporte_final.docx')
