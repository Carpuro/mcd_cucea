# Programación I
**Semester:** 1st | **Department:** DSI | **Credits:** 7

Python programming fundamentals applied to data science, from core language features to web scraping, database connectivity, and graphical interfaces. Sessions run in a Dockerized environment.

## Sessions (`notebooks/sessions/`)

| # | Topic |
|---|-------|
| 01 | Python architecture |
| 02 | Python fundamentals |
| 03 | String functions |
| 04 | File handling |
| 05 | Data structures |
| 06 | Regular expressions |
| 07 | External files (Excel, CSV, JSON) |
| 08 | Sockets and web services |
| 09 | Web scraping |
| 10 | Graphical interfaces |
| 11 | SQL in Python (Part 1) |
| 12 | SQL in Python (Part 2) |
| 13 | MySQL in Python |
| 14 | Combining GUIs and databases |

## Quick Start (Docker)
```bash
docker build -t mcd_prog1:latest .
docker run --rm \
  -v "${PWD}/datos/data:/app/data" \
  -v "${PWD}/tareas/output:/app/output" \
  mcd_prog1:latest \
  python sessions/01_python_architecture/<script>.py
```

## Structure
- `notebooks/sessions/` — one folder per session with exercises
- `notebooks/common/` — shared helper functions
- `datos/data/` — input CSV files
- `tareas/output/` — generated plots and results
- `notas/presentation/` — slides (Selenium, Graphical Interfaces)

## Tools
Python 3.11 · Docker · pandas · matplotlib · Selenium · MySQL
