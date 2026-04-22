# MCD CUCEA — Maestría en Ciencias de los Datos

**Universidad de Guadalajara · Centro Universitario de Ciencias Económico Administrativas**
**Alumno:** Carlos Pulido Rosas · **Generación:** 2025–2027

Repositorio central con todo el material de trabajo del programa MCD — organizado por semestre y materia. Incluye notebooks, tareas, proyectos, datasets e infraestructura de análisis.

---

## Programa

La Maestría en Ciencias de los Datos (MCD) forma profesionistas capaces de diseñar soluciones basadas en datos a gran escala. El programa combina fundamentos estadísticos y matemáticos con herramientas modernas de Big Data, programación y visualización, con orientación hacia proyectos de investigación aplicada.

- **Duración:** 4 semestres
- **Créditos totales:** 112
- **Modalidad:** Presencial — CUCEA, Zapopan, Jalisco
- **Plan completo:** [plan-de-estudios.md](_recursos/plan-de-estudios.md)

---

## Tesis

**Automatización Laboral por Inteligencia Artificial en Jalisco (2025–2030)**

Investigación que predice el riesgo de automatización de ocupaciones en Jalisco usando datos ENOE y O\*NET, metodología Frey-Osborne y modelos de Machine Learning.

| Elemento | Detalle |
|----------|---------|
| **Repositorio** | [ai-automation-risk-jalisco](https://github.com/Carpuro/ai-automation-risk-jalisco) |
| **Datos** | O\*NET · ENOE (INEGI) |
| **Método** | Random Forest · Frey-Osborne variables |
| **Resultado Fase 1** | R² ≈ 0.75 — alto riesgo en agricultura; educación como factor protector |
| **Fase 2 (pendiente)** | Indicadores específicos de LLMs |

---

## Estructura del repositorio

```
mcd_cucea/
├── _recursos/
│   ├── programas/          ← PDFs oficiales de los 16 programas de materia
│   ├── plantillas/         ← plantilla_informe_MCD.docx (navy/amber)
│   ├── logos/              ← logos UdeG
│   └── plan-de-estudios.md ← plan completo con créditos y pre-requisitos
├── 1er-semestre/
├── 2do-semestre/
├── 3er-semestre/
└── 4to-semestre/
```

Cada materia sigue la misma estructura interna:

```
materia/
├── notebooks/   ← ejercicios y notebooks (Jupyter / R / Python)
├── tareas/      ← entregas formales con PDF
├── proyectos/   ← proyectos parciales o finales
├── datos/       ← datasets específicos de la materia
├── notas/       ← slides, lecturas, material del profesor
└── README.md    ← descripción, contenido y herramientas de la materia
```

---

## Primer Semestre

| Materia | Depto | Herramientas | Contenido | Repositorio |
|---------|-------|--------------|-----------|-------------|
| [Métodos Estadísticos Básicos](1er-semestre/metodos-estadisticos-basicos/) | DMC | Python · scipy · sklearn | Estadística descriptiva, regresión lineal, clustering, probabilidad, distribuciones, pruebas de hipótesis | — |
| [Métodos Matemáticos para el Análisis de Datos](1er-semestre/metodos-matematicos-analisis-datos/) | DMC | Python · OpenCV | Álgebra lineal, optimización, visión computacional, algoritmos evolutivos | — |
| [Procesamiento de Grandes Bases de Datos](1er-semestre/procesamiento-grandes-bases-datos/) | DSI | PySpark · Koalas | Apache Spark, DataFrames, Spark ML, Spark Streaming — 8 tareas progresivas | — |
| [Programación I](1er-semestre/programacion-i/) | DSI | Python · Docker · MySQL | Fundamentos Python, web scraping, manejo de archivos, SQL en Python, interfaces gráficas — 14 sesiones en Docker | — |

## Segundo Semestre

| Materia | Depto | Herramientas | Contenido | Repositorio |
|---------|-------|--------------|-----------|-------------|
| [Almacenamiento de Grandes Bases de Datos](2do-semestre/almacenamiento/) | DSI | Hadoop · Hive · HiveQL · beeline | MapReduce, HDFS, Hive 2.3.2, análisis de datos IMSS ASG 2025 (~27M registros) | — |
| [Métodos Estadísticos Multivariados](2do-semestre/metodos-estadisticos-multivariados/) | DMC | Python / R · statsmodels · Orange3 | Análisis multivariado, reducción de dimensionalidad, MANOVA, análisis discriminante | — |
| [Programación II](2do-semestre/programacion-ii/) | DSI | Python · pyodbc · SQL Server · Power BI | Python avanzado, procedimientos almacenados, análisis del dataset Defunciones_2000 (10M registros) | [censo-salud-mexico-2000](https://github.com/Carpuro/censo-salud-mexico-2000) |
| [Tópicos Selectos de GBD I](2do-semestre/topicos-selectos-i/) | DSI | Python · NumPy · python-docx | Diseño y análisis de agentes de IA; árboles de decisión, simulación Monte Carlo, viabilidad de inversión | — |

## Tercer Semestre *(próximo)*

| Materia | Depto | Herramientas (esperadas) |
|---------|-------|--------------------------|
| Econometría | DPE | R · statsmodels · series de tiempo |
| Visualización de Grandes Bases de Datos | DSI | Power BI · Grafana · D3.js |
| Desarrollo de Proyecto I | DSI | Python · Spark · SQL |
| Tópicos Selectos de GBD II | DMC | — |

## Cuarto Semestre *(próximo)*

| Materia | Depto | Herramientas (esperadas) |
|---------|-------|--------------------------|
| Seminario de Tesis | DCSJ | — |
| Tópicos Complementarios de Gestión de Datos | DSI | — |
| Desarrollo de Proyecto II | DSI | — |
| Tópicos Selectos de GBD III | DPE | — |

---

## Infraestructura de análisis

Todo el trabajo corre en un homelab local (ThinkPad T14 Gen 4, 32GB RAM, Ubuntu 24.04) con acceso remoto vía Tailscale.

| Servicio | Descripción | Acceso |
|----------|-------------|--------|
| **Hadoop + HDFS** | Clúster bde2020, Hadoop 3.3.6 | UI: `http://192.168.100.11:9870` |
| **YARN** | Administrador de recursos del clúster | UI: `http://192.168.100.11:8088` |
| **HiveServer2** | Hive 2.3.2 + metastore PostgreSQL | `100.64.0.11:10000` (Tailscale) |
| **SQL Server 2025** | Dataset Defunciones_2000 (10M registros) | `100.64.0.11,1433` · `readonly/MCD_2000` |

**Acceso remoto para compañeros:** instalar [Tailscale](https://tailscale.com/download), compartir IP y solicitar acceso. Conectarse a HiveServer2 con beeline o DBeaver.

```bash
# Hive desde beeline
beeline -u "jdbc:hive2://100.64.0.11:10000/default" -n "" -p ""

# SQL Server desde Python
import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=100.64.0.11,1433;DATABASE=Defunciones_2000;UID=readonly;PWD=MCD_2000')
```

### Entorno Python
```bash
conda activate MCD   # Python 3.13
# pandas · numpy · scipy · statsmodels · sklearn · xgboost
# pyodbc · pyspark · jupyter · python-docx · matplotlib · seaborn · plotly
# Orange3: python -m Orange.canvas
```

---

## Datasets disponibles

| Dataset | Materia | Ubicación | Registros | Fuente |
|---------|---------|-----------|-----------|--------|
| IMSS ASG 2025 — semestre completo | Almacenamiento | HDFS `/user/oem/empleo/` | ~25M | IMSS |
| IMSS ASG enero 2025 | Almacenamiento | HDFS `/user/oem/empleo_enero/` | 4.6M | IMSS |
| Defunciones México 2000 | Programación II | SQL Server `Defunciones_2000` | 10.1M | INEGI |
| ENOE — Jalisco | Tesis | `ai-automation-risk-jalisco` | — | INEGI |
| O\*NET Occupational Data | Tesis | `ai-automation-risk-jalisco` | 873 ocupaciones | O\*NET / DOL |

---

## Recursos

- [Plan de estudios completo](_recursos/plan-de-estudios.md)
- [Programas oficiales de materia](_recursos/programas/)
- [Plantilla de informes (navy/amber)](_recursos/plantillas/plantilla_informe_MCD.docx)
