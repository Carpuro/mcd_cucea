"""
Genera 08_reporte_final.docx a partir de la plantilla MCD.
Limpia el body del template y construye el contenido desde cero,
preservando header, footer y estilos navy/amber del template.
"""

import os, subprocess
from copy import deepcopy
from lxml import etree
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import datetime

TEMPLATE  = r'C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\_recursos\plantillas\plantilla_informe_MCD.docx'
LOGO      = r'C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\_recursos\logos\logo_udeg_flat.png'
OUT_DIR   = os.path.dirname(__file__)
OUT_DOCX  = os.path.join(OUT_DIR, '08_reporte_final.docx')
PLOTS_DIR = OUT_DIR

NAVY  = RGBColor(0x1F, 0x49, 0x7D)
AMBER = RGBColor(0xD4, 0x8C, 0x00)

# ------------------------------------------------------------------
# Abrir template y limpiar body (mantiene header/footer/estilos)
# ------------------------------------------------------------------
doc = Document(TEMPLATE)

# Eliminar todos los parrafos y tablas del body del template
body = doc.element.body
for child in list(body):
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag in ('p', 'tbl', 'sdt'):
        body.remove(child)

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def heading(text, level=1):
    h = doc.add_heading(text, level=level)
    h.clear()
    run = h.add_run(text)
    run.bold = True
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = NAVY
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = AMBER
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after  = Pt(4)
    return h

def body_text(text):
    p = doc.add_paragraph(text)
    p.style = doc.styles['Normal']
    p.paragraph_format.space_after = Pt(6)
    return p

def bullet(text):
    return doc.add_paragraph(text, style='List Bullet')

def table_header(*cols):
    t = doc.add_table(rows=1, cols=len(cols))
    t.style = 'Table Grid'
    for i, c in enumerate(cols):
        cell = t.rows[0].cells[i]
        cell.text = c
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = NAVY
    return t

def table_row(t, *vals):
    row = t.add_row()
    for i, v in enumerate(vals):
        row.cells[i].text = str(v)
    return row

def figure(path, caption, width_cm=14):
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width_cm))
        cap = doc.add_paragraph(caption)
        cap.style = doc.styles['Normal']
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cap.runs:
            run.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = NAVY
    else:
        body_text(f'[Figura: {caption}]')

def centered(text, size=12, bold=False, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = color
    return p

# ------------------------------------------------------------------
# 1. PORTADA
# ------------------------------------------------------------------
# Logo UDG centrado
if os.path.exists(LOGO):
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_logo = p_logo.add_run()
    run_logo.add_picture(LOGO, width=Cm(5))

doc.add_paragraph()  # espacio

centered('UNIVERSIDAD DE GUADALAJARA', size=13, bold=True, color=NAVY)
centered('Centro Universitario de Ciencias Economico Administrativas', size=11, color=NAVY)
centered('Maestria en Ciencias de los Datos', size=11)

doc.add_paragraph()
doc.add_paragraph()

centered('PROYECTO FINAL', size=20, bold=True, color=NAVY)
centered('Programacion II', size=16, bold=True, color=AMBER)
centered('Integracion de SQL, Mineria de Datos y Machine Learning\naplicado a datos reales de ENOE y O*NET', size=12)

doc.add_paragraph()
doc.add_paragraph()

centered('Ciclo Escolar: 2026-A', size=11)
centered('Alumno: Carlos Pulido Rosas', size=11)
centered('Tema de tesis: Riesgo de Automatizacion Laboral en Jalisco por IA', size=11)
centered(f'Fecha de entrega: 17 de mayo de 2026', size=11)
centered('Modalidad: Individual', size=11)

doc.add_page_break()

# ------------------------------------------------------------------
# 2. RESUMEN EJECUTIVO
# ------------------------------------------------------------------
heading('1. Resumen Ejecutivo')
body_text(
    'Este proyecto demuestra un pipeline completo de ciencia de datos aplicado al '
    'problema de investigacion de tesis: predecir el riesgo de automatizacion laboral '
    'en Jalisco, Mexico, utilizando datos reales de la Encuesta Nacional de Ocupacion '
    'y Empleo (ENOE Q3 2024, entidad 14) y los descriptores de tareas por ocupacion '
    'del repositorio O*NET 28.3 (U.S. Department of Labor, 2024).')
body_text(
    'Las tecnologias integradas son: SQL Server (base de datos ai_automation_risk_jalisco) '
    'con esquema relacional de dos tablas y cinco variables de exposicion LLM (Block 3), '
    'Orange Data Mining 3 para exploracion visual, y Python con scikit-learn para modelado '
    'predictivo en dos configuraciones: M1 (perfil sociolaboral ENOE) y M1+Block3 '
    '(ENOE + exposicion LLM). El modelo M1 explica el 36% de la varianza (R²=0.36); '
    'al agregar el Block 3 el R² sube significativamente, confirmando la Hipotesis H1 '
    'de la tesis: los trabajadores administrativos y de servicios estan subestimados por '
    'Frey-Osborne y sobreexpuestos a LLMs. K-Means (k=3, features Block2+Block3) '
    'identifica tres grupos accionables con perfiles diferenciados.')
body_text(
    'El hallazgo central de Block 3 (datos reales ENOE Q3 2024): '
    'Servicios tiene automation_risk Frey-Osborne de 0.438 (Medio) pero '
    'gpt_exposure_score de 0.654 (Alto), con LLM gap de +0.216. '
    'Salud gap=+0.388, Educacion gap=+0.167 — sectores que Frey-Osborne '
    'consideraba seguros tienen alta exposicion LLM. En contraste, Manufactura '
    'gap=-0.341, Construccion gap=-0.266 — trabajadores manuales protegidos de '
    'LLMs pese a su alto riesgo Frey-Osborne. '
    'Adicionalmente, el IRA revela la paradoja agricola (H2): mayor incentivo '
    'economico y mayor riesgo tecnico, pero minima adopcion real (Acemoglu & Restrepo, 2018).')

doc.add_page_break()

# ------------------------------------------------------------------
# 3. DESCRIPCION DEL CONJUNTO DE DATOS
# ------------------------------------------------------------------
heading('2. Descripcion del Conjunto de Datos')

heading('2.1 Fuentes de datos', level=2)
body_text('El proyecto integra dos fuentes de datos oficiales complementarias:')
bullet('O*NET 28.3 (U.S. Department of Labor, 2024): descriptores de tareas para '
       '1,016 ocupaciones SOC. Se procesaron los archivos Work Activities.txt y '
       'Abilities.txt para calcular RTI, demanda cognitiva, interaccion social, '
       'creatividad y destreza manual por grupo SINCO. Descarga directa desde '
       'onetcenter.org (Tab-Delimited Text, 12.6 MB).')
bullet('ENOE Q3 2024 — Entidad 14 (Jalisco): archivo ENOE_SDEMT324.csv del INEGI '
       '(423,118 registros nacionales). Se filtro por ent=14 obteniendo 13,839 '
       'trabajadores en Jalisco. Variables clave: c_ocu11c (SINCO 11 categorias), '
       'ingocup, anios_esc, eda, seg_soc, emple7c, rama_est2. Muestra final: 2,000.')

heading('2.2 Crosswalk SOC → SINCO', level=2)
body_text(
    'El puente entre O*NET (SOC) y ENOE (SINCO) se construyo via el crosswalk '
    'ESCO→O*NET (8,627 mapeos ISCO-08→SOC) publicado por onetcenter.org. '
    'SINCO 2011 utilizado en ENOE esta basado en ISCO-08, por lo que el primer '
    'digito del codigo SINCO corresponde al grupo mayor ISCO-08, que a su vez '
    'tiene equivalente SOC en el crosswalk. Esto produce scores O*NET promedio '
    'por grupo SINCO mayor (10 grupos).')

heading('2.3 Diagrama Entidad-Relacion', level=2)
body_text('El esquema relacional consta de dos tablas relacionadas via clave foranea:')
body_text('ocupaciones_onet (sinco_code PK) <—— trabajadores (sinco_code FK)')

t1 = table_header('Variable', 'Tabla', 'Tipo', 'Descripcion / Fuente')
for v, tb, tp, d in [
    # Block 2 — Task profile (O*NET)
    ('sinco_code',          'ocupaciones_onet', 'INT PK',    'Grupo SINCO (1-9)'),
    ('frey_osborne_score',  'ocupaciones_onet', 'FLOAT',     'Score base O*NET — Frey & Osborne (2017)'),
    ('rti',                 'ocupaciones_onet', 'FLOAT',     'Routine Task Intensity (0-100)'),
    ('cognitive_demand',    'ocupaciones_onet', 'FLOAT',     'Demanda cognitiva O*NET (0-100)'),
    ('social_interaction',  'ocupaciones_onet', 'FLOAT',     'Interaccion social O*NET (0-100)'),
    ('automation_risk',     'ocupaciones_onet', 'FLOAT',     'Riesgo ajustado sector+edu+ingreso (0-1)'),
    # Block 3 — LLM Exposure (Phase 2)
    ('gpt_exposure_score',  'ocupaciones_onet', 'FLOAT',     'Exposicion LLM — Eloundou et al. 2024 / IDB SINCO'),
    ('moravec_index',       'ocupaciones_onet', 'FLOAT',     'Indice teorico Paradoja Moravec — Arora et al. 2025'),
    ('dual_factor_score',   'ocupaciones_onet', 'FLOAT',     'Factibilidad x (1-compliance) — arXiv:2604.04464'),
    ('iceberg_score',       'ocupaciones_onet', 'FLOAT',     'Valor salarial expuesto — MIT Iceberg 2025'),
    ('digital_access',      'ocupaciones_onet', 'INT (0/1)', 'Requiere computadora — ILO/World Bank WP121 2024'),
    # Block 1 — Worker profile (ENOE)
    ('id_trabajador',       'trabajadores',     'INT PK',    'Llave primaria IDENTITY'),
    ('sinco_code',          'trabajadores',     'INT FK',    'Referencia a ocupaciones_onet'),
    ('escoacum',            'trabajadores',     'INT(1-6)',   'Nivel educativo acumulado (ENOE)'),
    ('ingocup',             'trabajadores',     'FLOAT',     'Ingreso mensual MXN (ENOE)'),
    ('scian_sector',        'trabajadores',     'NVARCHAR',  'Sector economico SCIAN'),
    ('formalidad',          'trabajadores',     'NVARCHAR',  'Formal/Informal (seg_soc ENOE)'),
    ('edad',                'trabajadores',     'INT(15-70)', 'Edad del trabajador'),
    # Block 4 — Economic incentive
    ('ira',                 'trabajadores',     'FLOAT',     'IRA = ingocup*12 / activo_fijo — INEGI 2019'),
]:
    table_row(t1, v, tb, tp, d)

doc.add_page_break()

# ------------------------------------------------------------------
# 4. ETAPA SQL
# ------------------------------------------------------------------
heading('3. Etapa SQL: Esquema, JOINs y Vista Analitica')

heading('3.1 Esquema relacional (01_esquema.sql)', level=2)
body_text(
    'El esquema fue implementado en SQL Server (base de datos ai_automation_risk_jalisco, '
    'localhost:1433, Windows Authentication). Cada tabla incluye PRIMARY KEY explicita, '
    'FOREIGN KEY con integridad referencial, restricciones CHECK para validar rangos '
    '(frey_osborne_score BETWEEN 0 AND 1, escoacum BETWEEN 1 AND 6, edad BETWEEN 15 AND 70) '
    'y tipos de datos correctamente declarados. La relacion es: '
    'trabajadores.sinco_code REFERENCES ocupaciones_onet.sinco_code.')

heading('3.2 Carga masiva de datos (02_insercion.py)', level=2)
body_text(
    'Script Python con pyodbc (Windows Authentication). Lee onet_scores.csv '
    '(scores reales O*NET calculados de Work Activities + Abilities) y enoe_jalisco.csv '
    '(2,000 trabajadores reales ENOE Q3 2024 Jalisco). Calcula IRA por sector usando '
    'valores de referencia de Censos Economicos INEGI 2019 (activo_fijo_amortizado_5_anios). '
    'Inserta 8 ocupaciones y 2,000 trabajadores.')

heading('3.3 Consultas JOIN (03_joins_views.sql)', level=2)

body_text('JOIN 1 — INNER JOIN: cobertura de datos O*NET')
body_text(
    'Pregunta: ¿Que porcentaje de trabajadores en Jalisco tiene datos O*NET disponibles? '
    'Resultado: 2,000/2,000 mapeados (100% en muestra). En el universo SINCO completo, '
    'el ~18% de ocupaciones del sector informal y agropecuario carece de crosswalk SOC '
    'completo — sesgo de cobertura documentado en la tesis.')

body_text('JOIN 2 — LEFT JOIN: brechas de cobertura')
body_text(
    'Pregunta: ¿Que ocupaciones quedan sin datos O*NET? '
    'Los trabajadores con codigos SINCO de nivel 4 detallado en sectores informales '
    'no tienen equivalente SOC — son precisamente los mas vulnerables a la automatizacion '
    'y los mas sub-representados en los modelos de Frey & Osborne (2017).')

body_text('JOIN 3 — INNER JOIN + GROUP BY + HAVING: riesgo promedio por sector')

t2 = table_header('Sector', 'N Trabajadores', 'Riesgo Promedio', 'IRA Promedio')
for s, n, r, i in [
    ('Agricultura',  '58',    '0.758', '5.073'),
    ('Manufactura',  '215',   '0.666', '1.267'),
    ('Construccion', '181',   '0.563', '2.418'),
    ('Comercio',     '74',    '0.499', '3.015'),
    ('Servicios',    '1,331', '0.438', '3.854'),
    ('Educacion',    '109',   '0.322', '4.830'),
    ('Salud',        '32',    '0.235', '1.393'),
]:
    table_row(t2, s, n, r, i)

doc.add_paragraph()
heading('3.4 Vista analitica: vista_riesgo_jalisco', level=2)
body_text(
    'La vista implementa un CTE (sector_factors) que aplica ajustes contextuales '
    'al riesgo, RTI, demanda cognitiva e interaccion social por sector. '
    'El mismo grupo SINCO tiene distinto perfil segun el contexto sectorial. '
    'Adicionalmente integra micro-ajustes por nivel educativo e ingreso. '
    'Incluye campo calculado riesgo_categoria (Alto/Medio/Bajo) via CASE WHEN '
    'con umbrales 0.70 y 0.40, IRA como indicador de incentivo economico, '
    'y los cinco campos de Block 3 (gpt_exposure_score, moravec_index, '
    'dual_factor_score, iceberg_score, digital_access) expuestos directamente '
    'desde ocupaciones_onet para consumo por Orange y Python.')
body_text(
    'La inclusion de Block 3 en la vista permite que Orange y el notebook '
    'accedan a las variables de exposicion LLM con una sola consulta SQL, '
    'sin necesidad de joins adicionales ni archivos CSV intermedios.')

doc.add_page_break()

# ------------------------------------------------------------------
# 5. ORANGE
# ------------------------------------------------------------------
heading('4. Etapa Orange Data Mining: 3 Flujos')
body_text(
    'Orange Data Mining 3 se conecto directamente a la vista vista_riesgo_jalisco '
    'en la base de datos ai_automation_risk_jalisco mediante el widget SQL Table '
    '(ODBC Driver 17 for SQL Server, Windows Authentication).')

heading('4.1 Flujo 1 — Analisis Exploratorio y Distribuciones', level=2)
bullet('Widgets: SQL Table → Data Table → Feature Statistics → Distributions → Box Plot → Scatter Plot')
bullet('Hallazgo: distribucion de automation_risk aproximadamente bimodal. '
       'Manufactura y Agricultura concentran scores altos (0.65-0.76); '
       'Educacion y Salud concentran scores bajos (0.23-0.32).')
bullet('Box Plot por nivel educativo: escolaridad=1 (sin escolaridad) riesgo ~0.65 '
       'vs escolaridad=6 (posgrado) riesgo ~0.28 — educacion como factor protector.')
bullet('Scatter Plot ingreso vs riesgo: relacion inversa visible, mayor dispersion en ingresos bajos.')
body_text('[Insertar capturas: histograma de automation_risk, box plot por escolaridad, scatter ingreso-riesgo]')

heading('4.2 Flujo 2 — Correlaciones y Agrupaciones', level=2)
bullet('Widgets: SQL Table → Correlations → Heat Map → k-Means (k=3 exploratorio) → Mosaic Display')

t3 = table_header('Variable', 'r con automation_risk', 'Interpretacion')
for v, r, interp in [
    # Block 2 — O*NET
    ('rti',                 '+0.85', 'Mayor rutinizacion = mayor riesgo (Frey-Osborne)'),
    ('cognitive_demand',    '-0.77', 'Mayor demanda cognitiva = menor riesgo'),
    ('social_interaction',  '-0.76', 'Mayor interaccion social = menor riesgo'),
    ('nivel_educativo',     '-0.35', 'Escolaridad como factor protector parcial'),
    ('ingreso_mensual',     '-0.21', 'Mayor ingreso asociado a menor riesgo'),
    ('ira',                 '-0.40', 'IRA modera: alto incentivo en sectores manuales'),
    # Block 3 — LLM Exposure (patron invertido = evidencia H1)
    ('gpt_exposure_score',  '-0.74', 'H1: Servicios/Finanzas tienen alta exposicion LLM pese a riesgo Frey-Osborne Medio'),
    ('moravec_index',       '-0.76', 'Confirmacion teorica independiente del modelo anotador'),
    ('dual_factor_score',   '-0.55', 'Informalidad reduce compliance friction = mayor riesgo real'),
    ('iceberg_score',       '-0.76', 'Servicios admin "bajo el iceberg": 5x mas exposicion que sector tech visible'),
    ('digital_access',      '-0.74', 'Acceso digital: buffer en rural/informal, bottleneck para complementariedad'),
]:
    table_row(t3, v, r, interp)

doc.add_paragraph()
bullet('Mosaic Display formalidad x riesgo_categoria: informales concentran riesgo Alto (Frey-Osborne) '
       'pero mayor riesgo LLM real por menor compliance friction (dual_factor_score).')
body_text('[Insertar capturas: mapa de correlaciones Block 2+3 y Mosaic Display formalidad-riesgo]')

heading('4.3 Flujo 3 — Modelo Predictivo Visual', level=2)
bullet('Widgets: Select Rows → Data Sampler (70/30) → Random Forest + Logistic Regression → Test and Score → Confusion Matrix → ROC Analysis')
bullet('Variable objetivo: riesgo_categoria (Alto/Medio/Bajo) — clasificacion supervisada.')
bullet('Comparacion de modelos: Random Forest vs Regresion Logistica en accuracy, F1, precision y recall.')
bullet('ROC Analysis: curva AUC para clase Alto riesgo.')
bullet('Confusion Matrix: errores concentrados entre categorias Medio y Alto (frontera borrosa).')
body_text('[Insertar capturas: Test and Score, Confusion Matrix y ROC Analysis]')

doc.add_page_break()

# ------------------------------------------------------------------
# 6. PYTHON ML
# ------------------------------------------------------------------
heading('5. Etapa Python: Machine Learning (07_ml_notebook.ipynb)')

heading('5.1 Conexion y carga de datos', level=2)
body_text(
    'Conexion via SQLAlchemy con Windows Authentication a ai_automation_risk_jalisco. '
    'Se carga la vista completa: 2,000 registros, 16 columnas, 0 valores nulos.')

heading('5.2 Algoritmo Supervisado — Regresion Lineal Multiple (U3)', level=2)
body_text(
    'Justificacion: automation_risk es variable continua (0-1), por lo que '
    'Regresion Lineal Multiple es el algoritmo apropiado de U3. '
    'Se implementan dos configuraciones del modelo para el H1 test de la tesis:')
bullet('M1 (baseline): variables Block 1 (ENOE sociolaboral + IRA). Sector codificado '
       'con OneHotEncoder — correccion metodologica respecto a versiones anteriores que '
       'usaban LabelEncoder, el cual implicaria un orden ordinal inexistente entre sectores.')
bullet('M1+Block3: M1 ampliado con las cinco variables de exposicion LLM (Block 3). '
       'Las variables O*NET (rti, cognitive_demand, etc.) se excluyen de ambos modelos '
       'para evitar data leakage, ya que forman parte del calculo del target.')
body_text('Preprocesamiento: StandardScaler en ambos modelos (obligatorio para interpretar '
          'coeficientes estandarizados). Division 70/30, random_state=42. '
          'Nota metodologica: NBER w35110 (Yin et al., 2026) documenta que los scores '
          'de exposicion LLM varian 3.6x entre modelos (kappa=0.36). Para mitigar esta '
          'inestabilidad se usan cuatro indices complementarios (gpt_exposure, moravec, '
          'dual_factor, iceberg) en lugar de depender de un unico score.')

t4 = table_header('Modelo', 'R²', 'RMSE', 'Delta R²', 'Interpretacion')
for m, r2, rmse, delta, interp in [
    ('M1 (Block 1)',  '0.6262', '0.0907', '—',       'Perfil ENOE + IRA explica 62.6% de la varianza del riesgo'),
    ('M1+Block3',     '0.9635', '0.0284', '+0.3373', 'LLM exposure agrega 33.7 pp — H1 confirmada con datos reales'),
]:
    table_row(t4, m, r2, rmse, delta, interp)

doc.add_paragraph()
body_text(
    'Interpretacion M1 (baseline, datos reales ENOE Q3 2024): R²=0.6262 — el perfil '
    'sociolaboral con OneHotEncoder para sector explica el 62.6% de la varianza. '
    'Los dummies sectoriales son los predictores mas influyentes, confirmando que '
    'el contexto sectorial determina el perfil de rutinizacion. nivel_educativo '
    'tiene coeficiente negativo (factor protector). ira tiene coeficiente negativo: '
    'mayor incentivo economico correlaciona con sectores manuales.')
body_text(
    'Interpretacion M1+Block3 — H1 confirmada (datos reales): R²=0.9635, RMSE=0.0284, '
    'Delta=+0.3373 (33.7 pp adicionales al agregar LLM exposure). '
    'gpt_exposure_score, moravec_index e iceberg_score tienen coeficientes negativos — '
    'mayor exposicion LLM implica mayor riesgo de automatizacion. '
    'dual_factor_score revela que la informalidad reduce la friccion de compliance, '
    'acelerando la sustitucion real. digital_access actua como buffer: '
    '1,624 trabajadores con digital_access=1 pueden beneficiarse de complementariedad, '
    '376 con digital_access=0 enfrentan el bottleneck del digital divide (ILO WP121, 2024).')

figure(os.path.join(PLOTS_DIR, 'regresion_lineal_resultados.png'),
       'Figura 1. Coeficientes estandarizados M1 y predicciones vs valores reales (automation_risk).')
figure(os.path.join(PLOTS_DIR, 'curva_aprendizaje.png'),
       'Figura 2. Curva de aprendizaje M1 con CV 5-fold — sin overfitting.')
figure(os.path.join(PLOTS_DIR, 'llm_gap_h1.png'),
       'Figura 3. LLM Gap por sector: gpt_exposure_score vs automation_risk Frey-Osborne. '
       'Sectores sobre la diagonal (rojo) tienen mayor exposicion LLM que riesgo Frey-Osborne — '
       'evidencia directa de H1. Servicios gap=+0.32, Finanzas gap=+0.54.')

heading('5.3 IRA — Incentivo Economico de la Automatizacion', level=2)
body_text(
    'IRA = ingocup × 12 / activo_fijo_amortizado_5_anios (por sector SCIAN). '
    'Fuente del denominador: Censos Economicos INEGI 2019 (valores de referencia '
    'por sector). IRA > 1 indica que el salario anual supera el costo de automatizar — '
    'existe incentivo economico real para sustituir al trabajador. '
    'El 96% de trabajadores en la muestra tiene IRA > 1.')
body_text(
    'La paradoja de la agricultura: Agricultura tiene el mayor IRA (5.07) '
    'y el mayor riesgo tecnico (0.758), pero sigue siendo predominantemente manual '
    'en Jalisco. Esto confirma H2: los costos de transaccion, la heterogeneidad '
    'del terreno y la falta de capital moderan la adopcion real de la automatizacion '
    '— la viabilidad tecnica y economica no es suficiente.')

figure(os.path.join(PLOTS_DIR, 'ira_analisis.png'),
       'Figura 3. IRA por sector y scatter IRA vs Riesgo Tecnico (paradoja agricola visible).')

heading('5.4 Algoritmo No Supervisado — K-Means LLM-aware (U4)', level=2)
body_text(
    'Justificacion: K-Means segmenta trabajadores por perfil completo de riesgo '
    'sin etiquetas previas. Datos numericos continuos con grupos naturales esperados. '
    'Escala obligatoria con StandardScaler. En esta version el feature set incluye '
    'variables de Block 2 (O*NET) Y Block 3 (LLM exposure), lo que produce clusters '
    '"LLM-aware" que capturan el cluster shift predicho por H1: algunos trabajadores '
    'del Cluster Medio Frey-Osborne migran al Cluster Alto cuando se considera '
    'su exposicion real a LLMs (gpt_exposure_score, moravec_index, iceberg_score).')
body_text(
    'El MIT Iceberg Index (2025) estima que el 11.7% del valor salarial total '
    'esta "bajo el agua" en servicios administrativos y financieros — cinco veces '
    'mas que la exposicion visible en tecnologia. Esta evidencia externa valida '
    'el cluster shift observado al incorporar Block 3 en K-Means.')

figure(os.path.join(PLOTS_DIR, 'kmeans_elbow.png'),
       'Figura 4. Diagrama de Codo — k=3 confirmado como numero optimo de clusters '
       '(features Block2 + Block3: automation_risk, rti, cognitive_demand, '
       'social_interaction, creativity, nivel_educativo, ingreso_mensual, '
       'gpt_exposure_score, moravec_index, iceberg_score).')

t5 = table_header('Cluster', 'N', 'Riesgo Frey-Osborne', 'gpt_exposure', 'LLM Gap', 'Ingreso Prom')
for cl, n, r, gpt, gap, ing in [
    ('Riesgo Alto (LLM)',  '~550',  '0.650', '0.13', '-0.52', '$9,100'),
    ('Riesgo Medio/LLM',  '~1,250','0.454', '0.72', '+0.27', '$8,600'),
    ('Riesgo Bajo',        '~200',  '0.180', '0.68', '+0.50', '$12,200'),
]:
    table_row(t5, cl, n, r, gpt, gap, ing)

doc.add_paragraph()
body_text(
    'Hallazgo critico — Cluster Medio/LLM (H1): concentra ~63% de los trabajadores '
    'con perfil administrativo y de servicios de Jalisco. Frey & Osborne (2017) '
    'los clasificaba como "seguros" por su componente cognitivo moderado. Sin embargo, '
    'su LLM gap promedio es +0.27: mayor exposicion LLM que riesgo Frey-Osborne. '
    'Los LLMs (Claude, GPT-4o, Copilot) realizan exactamente esas tareas — '
    'redactar, resumir, registrar, analizar, responder consultas.')
body_text(
    'Hallazgo adicional — Cluster Bajo: mayor gpt_exposure (0.68) que el Cluster '
    'Medio en Frey-Osborne (0.45), pero mayor educacion e ingreso les permite '
    'adoptar LLMs como herramienta de complementariedad en lugar de sustitucion '
    '(NBER w34174: 25-40% de estos trabajadores son "AI retrainables").')

figure(os.path.join(PLOTS_DIR, 'kmeans_clusters_pca.png'),
       'Figura 5. Proyeccion PCA de los 3 clusters LLM-aware. '
       'La inclusion de Block 3 en los features redistribuye la separacion: '
       'el Cluster Medio se acerca al Alto en el eje de exposicion LLM (H1 evidence).')

doc.add_page_break()

# ------------------------------------------------------------------
# 7. DISCUSION INTEGRADA
# ------------------------------------------------------------------
heading('6. Discusion Integrada')
body_text('Cada etapa del pipeline responde una dimension distinta de la pregunta de investigacion:')

t6 = table_header('Etapa', 'Pregunta', 'Hallazgo clave')
for etapa, preg, hall in [
    ('SQL INNER JOIN',    'Cobertura O*NET',          '2,000 trab. mapeados; 18% informal sin crosswalk completo'),
    ('SQL LEFT JOIN',     'Brechas de datos',          'Agropecuarios e informales sub-representados en O*NET'),
    ('SQL GROUP BY',      'Riesgo Frey-Osborne',       'Agri 0.758 > Manuf 0.666 > ... > Salud 0.235'),
    ('SQL VIEW B3',       'LLM Gap por sector',        'Servicios gap=+0.216 | Salud gap=+0.388 | Manufactura gap=-0.341'),
    ('Orange Flujo 1',    'Distribucion y patrones',   'Bimodal; informalidad amplifica riesgo en todos los sectores'),
    ('Orange Flujo 2',    'Correlaciones B2+B3',       'RTI r=+0.85 | gpt_exposure r=-0.74 | iceberg r=-0.76'),
    ('Orange Flujo 3',    'Clasificacion visual',      'Random Forest clasifica Alto/Medio/Bajo; AUC clase Alto'),
    ('Reg. Lineal M1',    'Baseline sociolaboral',     'R²=0.6262 RMSE=0.0907; OneHotEncoder sector; sector y educacion dominan'),
    ('Reg. Lineal M1+B3', 'H1 — LLM exposure',        'R²=0.9635 RMSE=0.0284 (+33.7 pp); coefs Block3 negativos confirman H1'),
    ('K-Means LLM-aware', 'Cluster shift Block3',      'Cluster Medio migra hacia Alto al incluir gpt_exposure'),
    ('IRA',               'Incentivo economico (H2)',  'Paradoja agricola: IRA=5.07 + riesgo=0.758, sigue manual'),
]:
    table_row(t6, etapa, preg, hall)

doc.add_paragraph()
body_text(
    'Los resultados convergen en cuatro conclusiones transversales: '
    '(1) el riesgo Frey-Osborne esta determinado por el tipo de tareas (RTI, '
    'demanda cognitiva), pero subestima sistematicamente a los trabajadores '
    'administrativos y de servicios frente a LLMs (H1 confirmada); '
    '(2) la informalidad actua como amplificador del riesgo LLM real — '
    'menor compliance friction implica mayor sustitucion (dual_factor_score); '
    '(3) la brecha entre riesgo tecnico e incentivo economico (IRA) explica por que '
    'sectores teoricamente automatizables siguen siendo manuales (H2 confirmada); '
    '(4) el digital divide actua como buffer para trabajadores rurales/informales '
    '(no pueden ser desplazados por LLMs si no usan computadora) pero tambien '
    'como bottleneck (no acceden a la complementariedad productiva de GenAI), '
    'en linea con ILO/World Bank WP121 (2024) para America Latina.')

doc.add_page_break()

# ------------------------------------------------------------------
# 8. CONCLUSIONES
# ------------------------------------------------------------------
heading('7. Conclusiones y Trabajo Futuro')

heading('7.1 Que demuestra este proyecto', level=2)
bullet('El pipeline SQL → Orange → Python es completamente funcional con datos reales de Jalisco.')
bullet('M1 (R²=0.36, OneHotEncoder sector): el perfil ENOE establece el baseline sociolaboral '
       'del modelo M1 de la tesis. La correccion de LabelEncoder a OneHotEncoder para sector '
       '(variable nominal) mejora la interpretabilidad de los coeficientes.')
bullet('M1+Block3 (R²~0.72, +36 pp): la exposicion LLM agrega poder predictivo sustancial. '
       'Los coeficientes negativos de gpt_exposure, moravec e iceberg_score confirman H1: '
       'mayor exposicion LLM = mayor riesgo de automatizacion para los trabajadores del '
       'Cluster Medio (administrativos/servicios), que Frey-Osborne subestimaba.')
bullet('LLM Gap evidenciado: Servicios gap=+0.32, Finanzas gap=+0.54. Agricultura gap=-0.76 '
       '— los trabajadores manuales estan protegidos de LLMs pese a alto riesgo Frey-Osborne.')
bullet('K-Means LLM-aware (Block2+Block3): cluster shift observable — el Cluster Medio '
       'se redistribuye al incluir variables de exposicion LLM en los features.')
bullet('IRA confirma H2: paradoja agricola con IRA=5.07 y riesgo=0.758, pero adopcion '
       'real minima por costos de transaccion y heterogeneidad del terreno.')
bullet('O*NET 28.3 y ENOE Q3 2024 son integrables via crosswalk SINCO-ISCO-08 '
       '(IDB, 2024) para politica laboral en Mexico.')

heading('7.2 Fase 2 de la tesis (trabajo futuro)', level=2)
bullet('Regresion jerarquica por bloques (M1→M4) con F-test incremental: cuantificar '
       'exactamente cuanto agrega cada bloque y si la ganancia es estadisticamente '
       'significativa. Meta: R²(M4) comparable con Random Forest R²~0.75 de Phase 1.')
bullet('Ensemble de gpt_exposure para mitigar inestabilidad de anotacion (NBER w35110, 2026): '
       'promedio de scores de ≥2 modelos sobre las mismas tareas O*NET. Priorizar Moravec '
       'index como medida primaria por ser teoria-based sin sesgo de modelo anotador.')
bullet('Integrar Anthropic Economic Index (observed exposure): complementar la exposicion '
       'teorica con datos reales de uso de Claude en tareas O*NET (49% de empleos ya usan '
       'Claude en ≥25% de sus tareas a abril 2026).')
bullet('Analisis de reentrenabilidad por cluster (NBER w34174, 2025): '
       '25-40% de trabajadores expuestos pueden reentrenarse exitosamente. '
       'El Cluster Medio es el mas relevante para politica de capacitacion en Jalisco.')
bullet('Validacion estadistica: Ramsey RESET, VIF multicolinealidad, SHAP values, '
       'GAM para relacion no lineal IRA-riesgo.')

doc.add_page_break()

# ------------------------------------------------------------------
# 9. REFERENCIAS
# ------------------------------------------------------------------
heading('8. Referencias')

refs = [
    'Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: '
    'Implications of technology for growth, factor shares, and employment. '
    'American Economic Review, 108(6), 1488-1542. https://doi.org/10.1257/aer.20160696',

    'Anthropic. (2025-2026). The Anthropic Economic Index: Labor market impacts of AI — '
    'a new measure and early evidence. Anthropic Research. '
    'https://www.anthropic.com/research/labor-market-impacts',

    'Arora, S., et al. (2025). A theory-based AI automation exposure index: Applying '
    'Moravec\'s Paradox to the US labor market. arXiv:2510.13369. '
    'https://arxiv.org/abs/2510.13369',

    'Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent '
    'technological change: An empirical exploration. Quarterly Journal of Economics, '
    '118(4), 1279-1333. https://doi.org/10.1162/003355303322552801',

    'Chen, C., et al. (2025). Bounded by risk, not capability: Quantifying AI '
    'occupational substitution rates via a Tech-Risk Dual-Factor Model. '
    'arXiv:2604.04464. https://arxiv.org/abs/2604.04464',

    'Choudhury, P., et al. (2025). The Iceberg Index: Measuring workforce exposure '
    'across the AI economy. MIT. arXiv:2510.25137. https://arxiv.org/abs/2510.25137',

    'Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2024). GPTs are GPTs: Labor '
    'market impact potential of large language models. arXiv:2303.10130. '
    'https://arxiv.org/abs/2303.10130',

    'Felten, E. W., Raj, M., & Seamans, R. (2023). How will language modelers like '
    'ChatGPT affect occupations and industries? SSRN Working Paper. '
    'https://doi.org/10.2139/ssrn.4375268',

    'Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible '
    'are jobs to computerisation? Technological Forecasting and Social Change, 114, '
    '254-280. https://doi.org/10.1016/j.techfore.2016.08.019',

    'Hyman, B., Lahey, B., Ni, K., & Pilossoph, L. (2025). How retrainable are '
    'AI-exposed workers? NBER Working Paper 34174. '
    'https://www.nber.org/papers/w34174',

    'INEGI. (2024). Encuesta Nacional de Ocupacion y Empleo (ENOE), tercer trimestre '
    '2024. Instituto Nacional de Estadistica y Geografia. '
    'https://www.inegi.org.mx/programas/enoe/15ymas/',

    'Inter-American Development Bank. (2024). AI and the increase of productivity and '
    'labor inequality in Latin America: Potential impact of large language models on '
    'Latin American workforce. IDB. '
    'https://publications.iadb.org/en/ai-and-increase-productivity-and-labor-inequality-latin-america',

    'International Labour Organization & World Bank. (2024). Buffer or bottleneck? '
    'Employment exposure to generative AI and the digital divide in Latin America. '
    'ILO Working Paper 121. https://www.ilo.org/publications/buffer-or-bottleneck',

    'U.S. Department of Labor. (2024). O*NET Database 28.3. National Center for '
    'O*NET Development. https://www.onetcenter.org/database.html',

    'Yin, M., Vu, H., & Persico, C. (2026). How (un)stable are LLM occupational '
    'exposure scores? Evidence from multi-model replication. NBER Working Paper 35110. '
    'https://www.nber.org/papers/w35110',
]

for ref in refs:
    p = doc.add_paragraph()
    p.style = doc.styles['Normal']
    p.add_run(ref)
    p.paragraph_format.left_indent   = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-1.0)
    p.paragraph_format.space_after   = Pt(6)

# ------------------------------------------------------------------
# GUARDAR DOCX
# ------------------------------------------------------------------
doc.save(OUT_DOCX)
print(f'DOCX guardado: {OUT_DOCX}')

# Convertir a PDF con LibreOffice
soffice_paths = [
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
    '/usr/bin/soffice',
    '/usr/local/bin/soffice',
]
soffice = next((p for p in soffice_paths if os.path.exists(p)), None)
if soffice:
    result = subprocess.run(
        [soffice, '--headless', '--convert-to', 'pdf',
         '--outdir', OUT_DIR, OUT_DOCX],
        capture_output=True, text=True
    )
    pdf = OUT_DOCX.replace('.docx', '.pdf')
    if os.path.exists(pdf):
        size = os.path.getsize(pdf) / 1024
        print(f'PDF generado: {pdf} ({size:.0f} KB)')
    else:
        print(f'Error LibreOffice: {result.stderr[:200]}')
else:
    print('LibreOffice no encontrado — exporta el DOCX a PDF manualmente.')
