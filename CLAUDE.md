# CLAUDE.md — mcd_cucea

Context for Claude Code when working in this repository.

## What this repo is
Monorepo for the Maestría en Ciencias de los Datos (MCD) at UdeG CUCEA.
Contains all coursework organized by semester and subject.

## Owner
Carlos Pulido Rosas (carpuro) — 2nd semester, 2026.

## Repo structure
- `_recursos/` — shared assets: report template, logos, official program PDFs, study plan
- `1er-semestre/` — 4 subjects (completed)
- `2do-semestre/` — 4 subjects (active)
- `3er-semestre/` and `4to-semestre/` — empty, ready for future semesters

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
