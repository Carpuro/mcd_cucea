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
    'con esquema relacional de dos tablas, Orange Data Mining 3 para exploracion visual, '
    'y Python con scikit-learn para modelado predictivo. El hallazgo principal es que el '
    'perfil sociolaboral del trabajador (educacion, ingreso, sector, formalidad e IRA) '
    'explica el 36% de la varianza en el riesgo de automatizacion (R²=0.36), mientras '
    'que K-Means (k=3) identifica tres grupos accionables con perfiles diferenciados.')
body_text(
    'El Indice de Rentabilidad de la Automatizacion (IRA = salario_anual / '
    'activo_fijo_amortizado_5_anios) revela la paradoja de la agricultura en Jalisco: '
    'es el sector con mayor riesgo tecnico (0.758) Y mayor incentivo economico (IRA=5.07), '
    'pero permanece manual debido a factores geograficos e institucionales — confirmando '
    'la hipotesis H2 de la tesis (Acemoglu & Restrepo, 2018).')

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

t1 = table_header('Variable', 'Tabla', 'Tipo', 'Descripcion')
for v, tb, tp, d in [
    ('sinco_code',         'ocupaciones_onet', 'INT PK',          'Grupo SINCO (1-9)'),
    ('frey_osborne_score', 'ocupaciones_onet', 'FLOAT',           'Score base O*NET'),
    ('rti',                'ocupaciones_onet', 'FLOAT',           'Indice de rutinizacion'),
    ('cognitive_demand',   'ocupaciones_onet', 'FLOAT',           'Demanda cognitiva (0-100)'),
    ('social_interaction', 'ocupaciones_onet', 'FLOAT',           'Interaccion social (0-100)'),
    ('automation_risk',    'ocupaciones_onet', 'FLOAT',           'Riesgo base (0-1)'),
    ('id_trabajador',      'trabajadores',     'INT PK IDENTITY', 'Llave primaria'),
    ('sinco_code',         'trabajadores',     'INT FK',          'Referencia a ocupaciones_onet'),
    ('escoacum',           'trabajadores',     'INT CHECK(1-6)',   'Nivel educativo (ENOE)'),
    ('ingocup',            'trabajadores',     'FLOAT',           'Ingreso mensual MXN (ENOE)'),
    ('scian_sector',       'trabajadores',     'NVARCHAR',        'Sector economico SCIAN'),
    ('formalidad',         'trabajadores',     'NVARCHAR',        'Formal/Informal (seg_soc)'),
    ('edad',               'trabajadores',     'INT CHECK(15-70)', 'Edad del trabajador'),
    ('ira',                'trabajadores',     'FLOAT',           'Indice Rentabilidad Automatizacion'),
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
    'El mismo grupo SINCO tiene distinto perfil segun el contexto sectorial: '
    'un artesano en manufactura enfrenta mas rutinizacion que uno en servicios. '
    'Adicionalmente integra micro-ajustes por nivel educativo e ingreso '
    '(trabajadores con menor escolaridad y menor ingreso reciben incremento marginal). '
    'Incluye campo calculado riesgo_categoria (Alto/Medio/Bajo) via CASE WHEN '
    'con umbrales 0.70 y 0.40, e IRA como indicador de incentivo economico.')

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
    ('rti',                '+0.85', 'Mayor rutinizacion = mayor riesgo (teorico y empirico)'),
    ('cognitive_demand',   '-0.77', 'Mayor demanda cognitiva = menor riesgo'),
    ('social_interaction', '-0.76', 'Mayor interaccion social = menor riesgo'),
    ('nivel_educativo',    '-0.35', 'Escolaridad como factor protector parcial'),
    ('ingreso_mensual',    '-0.21', 'Mayor ingreso asociado a menor riesgo'),
    ('ira',                '-0.40', 'IRA modera: alto incentivo en sectores manuales'),
]:
    table_row(t3, v, r, interp)

doc.add_paragraph()
bullet('Mosaic Display formalidad × riesgo_categoria: informales concentran riesgo Alto.')
body_text('[Insertar capturas: mapa de correlaciones y Mosaic Display formalidad-riesgo]')

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
    'Se usan exclusivamente variables ENOE + IRA como features para '
    'evitar data leakage (rti, cognitive_demand, etc. forman parte del calculo del target). '
    'Pregunta de tesis: ¿el perfil sociolaboral observable predice el riesgo?')
body_text('Preprocesamiento: StandardScaler (obligatorio para interpretar coeficientes). '
         'Division 70/30, random_state=42.')

t4 = table_header('Metrica', 'Valor', 'Interpretacion')
for m, v, i in [
    ('R² Score',  '0.3618', 'El perfil ENOE explica el 36% de la varianza del riesgo'),
    ('RMSE',      '0.1186', 'Error medio de 0.12 en escala 0-1'),
    ('Particion', '70/30',  '1,400 entrenamiento / 600 prueba'),
    ('CV',        '5-fold', 'Curva de aprendizaje sin overfitting'),
]:
    table_row(t4, m, v, i)

doc.add_paragraph()
body_text(
    'El coeficiente mas influyente es sector_enc (el sector determina el contexto '
    'de rutinizacion), seguido de nivel_educativo (negativo — factor protector) '
    'e ira (negativo — mayor incentivo economico correlaciona con sectores manuales '
    'que invierten menos en capital humano). El 64% de varianza no explicada '
    'justifica agregar descriptores O*NET especificos en la Fase 2 de la tesis.')

figure(os.path.join(PLOTS_DIR, 'regresion_lineal_resultados.png'),
       'Figura 1. Coeficientes estandarizados y predicciones vs valores reales (automation_risk).')
figure(os.path.join(PLOTS_DIR, 'curva_aprendizaje.png'),
       'Figura 2. Curva de aprendizaje con validacion cruzada 5-fold — sin overfitting.')

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

heading('5.4 Algoritmo No Supervisado — K-Means (U4)', level=2)
body_text(
    'Justificacion: K-Means segmenta trabajadores por perfil completo de riesgo '
    'sin etiquetas previas. Datos numericos continuos con grupos naturales esperados '
    '(Alto/Medio/Bajo riesgo). Escala obligatoria con StandardScaler.')

figure(os.path.join(PLOTS_DIR, 'kmeans_elbow.png'),
       'Figura 4. Diagrama de Codo — k=3 confirmado como numero optimo de clusters.')

t5 = table_header('Cluster', 'N', 'Riesgo Prom', 'Ingreso Prom', 'Educacion Prom', 'IRA Prom')
for cl, n, r, ing, edu, ira in [
    ('Riesgo Alto',  '521',  '0.650', '$9,168', '3.4', '2.43'),
    ('Riesgo Medio', '1,264','0.454', '$8,606', '2.7', '3.64'),
    ('Riesgo Bajo',  '215',  '0.180', '$12,249','4.6', '4.91'),
]:
    table_row(t5, cl, n, r, ing, edu, ira)

doc.add_paragraph()
body_text(
    'Hallazgo critico: el Cluster Riesgo Medio concentra el 63% de los trabajadores '
    '(1,264 personas) con perfil administrativo/tecnico de Jalisco. '
    'Frey & Osborne (2017) clasificaba estos perfiles como "seguros" por su componente '
    'cognitivo moderado. Sin embargo, los Large Language Models (GPT-4, Claude, Copilot) '
    'realizan exactamente esas tareas — motivando la Fase 2 de la tesis.')

figure(os.path.join(PLOTS_DIR, 'kmeans_clusters_pca.png'),
       'Figura 5. Proyeccion PCA de los 3 clusters (68.2% varianza explicada). '
       'Separacion clara entre Riesgo Bajo y Alto; Medio es la zona de mayor incertidumbre.')

doc.add_page_break()

# ------------------------------------------------------------------
# 7. DISCUSION INTEGRADA
# ------------------------------------------------------------------
heading('6. Discusion Integrada')
body_text('Cada etapa del pipeline responde una dimension distinta de la pregunta de investigacion:')

t6 = table_header('Etapa', 'Pregunta', 'Hallazgo clave')
for etapa, preg, hall in [
    ('SQL INNER JOIN',   'Cobertura O*NET',         '2,000 trab. mapeados; 18% informal sin crosswalk completo'),
    ('SQL LEFT JOIN',    'Brechas de datos',         'Agropecuarios e informales sub-representados en O*NET'),
    ('SQL GROUP BY',     'Riesgo por sector',        'Agri 0.758 > Manuf 0.666 > ... > Salud 0.235'),
    ('Orange Flujo 1',   'Distribucion y patrones',  'Bimodal; informalidad amplifica riesgo en todos los sectores'),
    ('Orange Flujo 2',   'Correlaciones',            'RTI r=+0.85 | cognitivo r=-0.77 | social r=-0.76'),
    ('Orange Flujo 3',   'Clasificacion visual',     'Random Forest clasifica Alto/Medio/Bajo con mayor precision'),
    ('Reg. Lineal',      'Cuantificacion lineal',    'R²=0.36; sector y educacion son los predictores principales'),
    ('K-Means',          'Segmentacion natural',     'Cluster Medio (63%) = nueva zona de riesgo por LLMs'),
    ('IRA',              'Incentivo economico',      'Paradoja agricola: IRA=5.07 + riesgo=0.758, pero sigue manual'),
]:
    table_row(t6, etapa, preg, hall)

doc.add_paragraph()
body_text(
    'Los resultados convergen en tres conclusiones transversales: '
    '(1) el riesgo esta determinado principalmente por el tipo de tareas (RTI, '
    'demanda cognitiva), no solo por el sector economico; '
    '(2) la informalidad actua como amplificador del riesgo — los trabajadores informales '
    'tienen menor acceso a formacion y menor proteccion ante la sustitucion tecnologica; '
    '(3) la brecha entre riesgo tecnico e incentivo economico (IRA) explica por que '
    'sectores teoricamente automatizables siguen siendo manuales en Jalisco.')

doc.add_page_break()

# ------------------------------------------------------------------
# 8. CONCLUSIONES
# ------------------------------------------------------------------
heading('7. Conclusiones y Trabajo Futuro')

heading('7.1 Que demuestra este proyecto', level=2)
bullet('El pipeline SQL → Orange → Python es completamente funcional con datos reales de Jalisco.')
bullet('La Regresion Lineal (R²=0.36) con variables ENOE establece el baseline del modelo M1 de la tesis.')
bullet('K-Means identifica 3 grupos accionables: el Cluster Medio (63%) es la nueva zona de riesgo ante LLMs.')
bullet('El IRA revela la paradoja agricola: maxima exposicion tecnica y economica, minima adopcion real.')
bullet('O*NET 28.3 y ENOE Q3 2024 son integrables via crosswalk SINCO-ISCO-08 para politica laboral en Mexico.')

heading('7.2 Fase 2 de la tesis (trabajo futuro)', level=2)
bullet('Bloque 3 — LLM Exposure: agregar gpt_exposure_score (Eloundou et al., 2023), LTII y AIOE. '
       'Hipotesis H1: el Cluster Medio sube de categoria al incorporar exposicion especifica a LLMs.')
bullet('Bloque 4 — IRA completo: integrar Censos Economicos INEGI 2019 con activo fijo real por sector. '
       'Hipotesis H2: IRA predice adopcion real independientemente del riesgo tecnico.')
bullet('Regresion jerarquica por bloques (M1→M4) con F-test incremental y SHAP values para '
       'comparar importancia de variables entre fases.')
bullet('Validacion estadistica: Ramsey RESET, VIF para multicolinealidad, GAM para relacion no lineal IRA-riesgo.')

doc.add_page_break()

# ------------------------------------------------------------------
# 9. REFERENCIAS
# ------------------------------------------------------------------
heading('8. Referencias')

refs = [
    'Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: '
    'Implications of technology for growth, factor shares, and employment. '
    'American Economic Review, 108(6), 1488-1542. https://doi.org/10.1257/aer.20160696',

    'Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent '
    'technological change: An empirical exploration. Quarterly Journal of Economics, '
    '118(4), 1279-1333. https://doi.org/10.1162/003355303322552801',

    'Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An '
    'early look at the labor market impact potential of large language models. '
    'arXiv preprint arXiv:2303.10130.',

    'Felten, E. W., Raj, M., & Seamans, R. (2023). How will language modelers like '
    'ChatGPT affect occupations and industries? SSRN Working Paper. '
    'https://doi.org/10.2139/ssrn.4375268',

    'Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible '
    'are jobs to computerisation? Technological Forecasting and Social Change, 114, '
    '254-280. https://doi.org/10.1016/j.techfore.2016.08.019',

    'INEGI. (2024). Encuesta Nacional de Ocupacion y Empleo (ENOE), tercer trimestre '
    '2024. Instituto Nacional de Estadistica y Geografia. '
    'https://www.inegi.org.mx/programas/enoe/15ymas/',

    'U.S. Department of Labor. (2024). O*NET Database 28.3. National Center for '
    'O*NET Development. https://www.onetcenter.org/database.html',
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
