# Programación II
**Semester:** 2nd | **Department:** DSI | **Credits:** 7 | **Pre-req:** Programación I

Advanced Python programming applied to database analysis. Focus on SQL Server connectivity, stored procedures, and data analysis pipelines over large datasets.

## Notebooks (`notebooks/`)

### Python
- `Actividad_Defunciones_SQL.ipynb` — Analysis of the `Defunciones_2000` dataset (10M+ records) via SQL Server

### SQL
- `practica1.ipynb` — SQL practice notebook
- `SP_Defunciones_CarlosPulidoRosas.docx/.pdf` — Stored procedures report

## Dataset: Defunciones_2000
- **DB:** SQL Server 2025 on Docker (homelab `192.168.100.11:1433`)
- **Table:** `defunciones` — 10,099,182 records, 81 VARCHAR columns
- **Connection:** pyodbc via Tailscale (`100.64.0.11,1433`)
- **User:** `readonly` / `MCD_2000`

### Critical Data Rules
- `NOTIEDER` NULL = WITH coverage (not missing). Never filter `IS NOT NULL` — removes the entire positive class
- All columns are VARCHAR — always `CAST` or `pd.to_numeric` before numeric operations
- `999`/`9999` = unspecified in most columns

## Tools
Python · Jupyter · pyodbc · pandas · SQL Server 2025 · T-SQL
