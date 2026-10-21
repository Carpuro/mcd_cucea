# CLAUDE.md: mcd_cucea

Context for Claude Code when working in this repository.

## What this repo is
Monorepo for the Maestría en Ciencias de los Datos (MCD) at UdeG CUCEA.
It contains all coursework, organized by semester and subject.

## Owner
Carlos Pulido Rosas (carpuro). Currently in the 3rd semester, ciclo 2026B (group 2, executive modality).

## Location
The repo lives at `C:\Users\carlo\GitHub\mcd_cucea`. It was moved out of OneDrive on 2026-09-03
because OneDrive sync froze Windows Explorer and risks corrupting `.git`.
Backups are done with `git push`, never with OneDrive.

## Repo structure
- `_recursos/`: shared assets (report template, logos, official program PDFs, study plan)
- `1er-semestre/`: 4 subjects (completed)
- `2do-semestre/`: 4 subjects (completed)
- `3er-semestre/`: 4 subjects (active): `econometria`, `visualizacion-grandes-bases-datos`,
  `desarrollo-proyecto-i`, `topicos-selectos-ii`
- `4to-semestre/`: empty, ready for the next semester

## 3rd semester subjects (ciclo 2026B, group 2)
| Subject | NRC | Professor | Day |
|---|---|---|---|
| Econometría | 176457 | Dr. Andrés Jerson Millán López | Monday (room Q-209) |
| Tópicos Selectos de GBD II | 176456 | Mtro. Iván Alejandro Toledano Juárez | Tuesday (online) |
| Desarrollo de Proyecto I | 176459 | Dra. Ana Rosa Jiménez Meza | Wednesday (online) |
| Visualización de GBD | 176458 | Mtro. Carlos Fernando Ruiz Chávez | Thursday (online) |

### Visualización de GBD: current status
- Dataset: `visualizacion-grandes-bases-datos/datos/BD_2024_calidad_aire.xlsx`, SIMAJ air quality 2024.
  Sheet `Data` holds hourly readings per station; sheet `Param` holds station metadata and coordinates.
- Gotcha: the `DATE` column already includes the hour (full timestamp). Do not add `HOUR` to it.
- Stations:
  - **Country (COU)** is the closest to home, but it only has CO for September and does not measure NO2.
    Use it for single-period analysis (tasks 1.0 to 1.2).
  - **Centro (CEN)** has full-year coverage for O3, CO and PM, but NO2/NO/NOX only from September to December 2024.
    Use it for monthly, correlation and regression analysis (tasks 1.3 onward).
    No SIMAJ station measures NO2 before August 2024.
- Delivered tasks: 1.0 (boxplot and IQR outliers), 1.1 (Tukey quartiles), 1.2 (histogram vs IMECA norm),
  1.3 (time series, moving averages, boxplots by hour and month), 1.4 (correlation with NO2),
  1.5 (homogeneous corpus, Tukey outlier exclusion, regression through the origin, heatmaps),
  1.6 (NO2 imputation from CO with capped model 1.5, multiple regression NO2 ~ PM10 + PM2.5, collinearity),
  1.7 (refined multiple regression through the origin vs 1.6, residuals, PM10-PM2.5 relation with K-means).
- Each task has a `build_tarea*.py` script in `tareas/` (task 1.0 is `build_tarea10.py`) that fills the
  report template and exports the PDF with LibreOffice. Outputs go to `tareas/Tarea1_N/`.
  `build_tarea17.py` imports `build_tarea16.py` for the data preparation.
- Deliverable names: `Tarea1_N_VisualizacionGBD_CarlosPulidoRosas.pdf`. Copy the final PDF to Downloads.

### Tópicos Selectos de GBD II: current status
- Professor material: https://github.com/IvTole/Topicos_Selectos_II_CUCEA (marimo notebooks, one folder per topic).
- Each activity starts from the professor's notebook, keeps his code and questions, and adds answers
  backed by experiments that reuse his functions with fixed settings (the widgets only show one case).
- Deliverables per activity in `tareas/ActividadN/`: `ActividadN_TopicosGBDII_CarlosPulidoRosas.py`
  (marimo, the deliverable), `.ipynb` (exported with outputs, kernelspec set) and `.html`, plus
  `README.md` and `requirements.txt`. Two notebooks in one topic are `ActividadN_1_…` and `ActividadN_2_…`.
- Export: `conda run -n MCD marimo export ipynb <f>.py -o <f>.ipynb --include-outputs -f` and
  `marimo export html`; verify with `marimo check` and `jupyter nbconvert --execute`.
- Use markdown tables (`tabla_md` helper), not `mo.ui.table`, so tables render in Jupyter and GitHub.
- The repo is public; the professor gets the folder link. PyTorch is not installed in the MCD env yet.
- Delivered: 1 (single-neuron regression), 2 (perceptron limits, XOR), 3 (one hidden layer, two
  notebooks), 4 (deep network with `layer_dims`).

### Desarrollo de Proyecto I: current status
- `tareas/Protocolo/`: `build_protocolo.py` fills the official CUCEA template; text in `contenido_protocolo.py`.
  Formatting follows `_recursos/Lineamientos presentación de trabajos MCD Ver 2.0.docx`.
- `tareas/Actividad_Referencias/`: `build_referencias.py` builds the 16-reference analysis and Excel table.
- Thesis data comes only from the thesis repo (`ai-automation-risk-jalisco`); every external datum cited in APA 7.

### Writing style for coursework
- Spanish, first person, natural student voice; no em-dashes; avoid stock AI phrases.
- Every number in the text must match what the script or notebook computes.

## Per-subject structure (standard, applies to all 16 subjects)
```
materia/
├── notebooks/   Jupyter/Python/R exercises
├── tareas/      formal deliverables (DOCX + PDF)
├── proyectos/   partial or final projects
├── datos/       subject-specific datasets
├── notas/       slides, readings, professor material
└── README.md
```

## Report template
- Location: `_recursos/plantillas/plantilla_informe_MCD.docx`
- Style: navy blue (#1F497D) headers, amber (#D48C00) accents, Calibri font.
- Generate with python-docx in conda env `MCD`. Convert to PDF with LibreOffice headless.

## Active infrastructure (homelab: 192.168.100.11)

### Hadoop + Hive (2do-semestre/almacenamiento)
- Stack: bde2020 hadoop 3.3.6, Hive 2.3.2, PostgreSQL 9.6 metastore
- Config: `~/apps/hadoop/docker-compose.yml` and `hadoop.env`
- HDFS UI: http://192.168.100.11:9870 | YARN: http://192.168.100.11:8088
- HiveServer2: `192.168.100.11:10000` (Tailscale: `100.64.0.11:10000`)
- Connect: `beeline -u "jdbc:hive2://localhost:10000/default"`
- HDFS tables: `empleo` (~25M records) and `empleo_enero` (~4.6M records), from IMSS ASG 2025

### SQL Server (2do-semestre/programacion-ii)
- SQL Server 2025 on Docker, port 1433
- DB: `Defunciones_2000`, 10,099,182 records, 81 VARCHAR columns
- User: `readonly` / `MCD_2000` | Tailscale: `100.64.0.11,1433`
- CRITICAL: `NOTIEDER` NULL means WITH coverage. Never filter `IS NOT NULL`.
- All columns are VARCHAR. Always CAST before numeric operations.

## Python environment
- Conda env: `MCD` (`~/miniconda3/envs/MCD`), Python 3.13
- Activate: `conda activate MCD`
- Key packages: pandas, numpy, scipy, statsmodels, sklearn, xgboost, pyodbc, pyspark, jupyter, python-docx, matplotlib, seaborn, plotly

## Git conventions
- Commit messages in English, with no Co-Authored-By line
- Never use `pip install` system-wide. Use conda or a venv.
