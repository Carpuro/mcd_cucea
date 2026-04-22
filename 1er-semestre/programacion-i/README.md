# Programación I
**Semester:** 1st | **Department:** DSI | **Credits:** 7 | **Status:** ✅ Completed

Python programming fundamentals for data science: core language, file handling, web scraping, database connectivity, and graphical interfaces. Sessions run in a Dockerized environment.

## Sessions (`notebooks/sessions/`)

| # | Topic | Status |
|---|-------|--------|
| 01 | Python architecture | ✅ Done |
| 02 | Python fundamentals | ✅ Done |
| 03 | String functions | ✅ Done |
| 04 | File handling | ✅ Done |
| 05 | Data structures | ✅ Done |
| 06 | Regular expressions | ✅ Done |
| 07 | External files (Excel, CSV, JSON) | ✅ Done |
| 08 | Sockets and web services | ✅ Done |
| 09 | Web scraping (Selenium) | ✅ Done |
| 10 | Graphical interfaces (tkinter) | ✅ Done |
| 11 | SQL in Python (Part 1) | ✅ Done |
| 12 | SQL in Python (Part 2) | ✅ Done |
| 13 | MySQL in Python | ✅ Done |
| 14 | Combining GUIs and databases | ✅ Done |

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
