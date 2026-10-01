# CLAUDE.md — mcd_cucea

Context for Claude Code when working in this repository.

## What this repo is
Monorepo for the Maestría en Ciencias de los Datos (MCD) at UdeG CUCEA.
Contains all coursework organized by semester and subject.

## Owner
Carlos Pulido Rosas (carpuro) — 3rd semester, ciclo 2026B (grupo 2, modalidad ejecutiva).

## Location
Repo lives at `C:\Users\carlo\GitHub\mcd_cucea` (moved OUT of OneDrive on 2026-09-03 —
OneDrive sync froze Explorer and risks corrupting `.git`). Backup = `git push`, never OneDrive.

## Repo structure
- `_recursos/` — shared assets: report template, logos, official program PDFs, study plan
- `1er-semestre/` — 4 subjects (completed)
- `2do-semestre/` — 4 subjects (completed)
- `3er-semestre/` — 4 subjects (active): `econometria`, `visualizacion-grandes-bases-datos`,
  `desarrollo-proyecto-i`, `topicos-selectos-ii`
- `4to-semestre/` — empty, ready for future semester

## 3rd semester — subjects, NRC and professors (ciclo 2026B, grupo 2)
| Materia | NRC | Profesor | Día |
|---|---|---|---|
| Econometría | 176457 | Dr. Andrés Jerson Millán López | Lunes (Q-209) |
| Tópicos Selectos de GBD II | 176456 | Mtro. Iván Alejandro Toledano Juárez | Martes (virtual) |
| Desarrollo de Proyecto I | 176459 | Dra. Ana Rosa Jiménez Meza | Miércoles (virtual) |
| Visualización de GBD | 176458 | Mtro. Carlos Fernando Ruiz Chávez | Jueves (virtual) |

### Visualización de GBD — estado
- Dataset: `visualizacion-grandes-bases-datos/datos/BD_2024_calidad_aire.xlsx` — calidad del
  aire SIMAJ 2024 (hoja `Data` horaria por estación; hoja `Param` con metadatos/coordenadas).
  OJO: la columna `DATE` ya incluye la hora (timestamp completo) — no sumarle `HOUR`.
- Estaciones: **Country (COU)** = la más cercana al domicilio, pero SOLO tiene CO de septiembre
  y NO mide NO2 → sirve para análisis puntual (tareas 1.0–1.2). **Centro (CEN)** = año completo,
  mide NO2; usada en tareas 1.3–1.4 (análisis mensual/correlación).
- Tareas entregadas: 1.0 (boxplot+IQR), 1.1 (cuartiles Tukey), 1.2 (histograma+IMECA),
  1.3 (series de tiempo + SMA + boxplots hora/mes), 1.4 (correlación con NO2). Cada una tiene
  su `build_tareaX.py` en `tareas/` que llena la plantilla y exporta PDF con LibreOffice.

## Per-subject structure (standard, applies to all 16 subjects)
```
materia/
├── notebooks/   — Jupyter/Python/R exercises
├── tareas/      — formal deliverables (DOCX + PDF)
├── proyectos/   — partial or final projects
├── datos/       — subject-specific datasets
├── notas/       — slides, readings, professor material
└── README.md
```

## Report template
Location: `_recursos/plantillas/plantilla_informe_MCD.docx`
Style: navy blue (#1F497D) headers, amber (#D48C00) accents, Calibri font.
Generate with python-docx in conda env `MCD`. Convert to PDF with LibreOffice headless.

## Active infrastructure (homelab: 192.168.100.11)

### Hadoop + Hive (2do-semestre/almacenamiento)
- Stack: bde2020 hadoop 3.3.6 + Hive 2.3.2 + PostgreSQL 9.6 metastore
- Config: `~/apps/hadoop/docker-compose.yml` + `hadoop.env`
- HDFS UI: http://192.168.100.11:9870 | YARN: http://192.168.100.11:8088
- HiveServer2: `192.168.100.11:10000` (Tailscale: `100.64.0.11:10000`)
- Connect: `beeline -u "jdbc:hive2://localhost:10000/default"`
- HDFS tables: `empleo` (~25M records), `empleo_enero` (~4.6M records) — IMSS ASG 2025

### SQL Server (2do-semestre/programacion-ii)
- SQL Server 2025 on Docker, port 1433
- DB: `Defunciones_2000` — 10,099,182 records, 81 VARCHAR columns
- User: `readonly` / `MCD_2000` | Tailscale: `100.64.0.11,1433`
- CRITICAL: `NOTIEDER` NULL = WITH coverage. Never filter `IS NOT NULL`.
- All columns are VARCHAR — always CAST before numeric operations.

## Python environment
- Conda env: `MCD` (`~/miniconda3/envs/MCD`) — Python 3.13
- Activate: `conda activate MCD`
- Key packages: pandas, numpy, scipy, statsmodels, sklearn, xgboost, pyodbc, pyspark, jupyter, python-docx, matplotlib, seaborn, plotly

## Git conventions
- Commit messages in English, no Co-Authored-By line
- Never use `pip install` system-wide — use conda or venv
