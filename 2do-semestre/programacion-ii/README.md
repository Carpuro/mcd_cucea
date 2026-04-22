# Programación II
**Semester:** 2nd | **Department:** DSI | **Credits:** 7 | **Pre-req:** Programación I | **Status:** 🔄 Active

Advanced Python programming for database analysis. Focus on SQL Server connectivity, stored procedures, materialized tables, and machine learning pipelines over large datasets.

## Notebooks (`notebooks/`)

| Notebook | Content | Status |
|----------|---------|--------|
| `Actividad_Defunciones_SQL.ipynb` | Full analysis pipeline — `Defunciones_2000` (10M+ records) via SQL Server | ✅ Done |
| `practica1.ipynb` | SQL practice — stored procedures and views | ✅ Done |

## Deliverables (`tareas/`)

| File | Content | Status |
|------|---------|--------|
| `SP_Defunciones_CarlosPulidoRosas.docx/.pdf` | Stored procedures report | ✅ Done |

## Dataset: Defunciones_2000

- **DB:** SQL Server 2025 on Docker — `192.168.100.11:1433`
- **Table:** `defunciones` — 10,099,182 records · 81 VARCHAR columns
- **Connection:** pyodbc via Tailscale (`100.64.0.11,1433`)
- **User:** `readonly` / `MCD_2000`

### Materialized Tables
`tbl_kpis` · `tbl_acceso_resumen` · `tbl_estados_resumen` · `tbl_urbano_resumen` · `tbl_escolaridad_resumen` · `tbl_indigena_resumen` · `tbl_grupos_edad_resumen` · `tbl_metricas_modelos` · `tbl_importancia_variables` · `tbl_coeficientes_ols`

### Stored Procedures
`sp_muertes_*` (6 procedures) · `sp_top10_padecimientos_*` (6 procedures) — 13 SQL views total

### Key Model Results
| Model | Result |
|-------|--------|
| OLS — healthcare coverage effect on lifespan | +3.46 years (p < 0.0001), R² = 0.028 |
| Random Forest — age at death prediction | R² = 0.2696, RMSE = 14.61 years |
| Decision Tree — coverage classification | Accuracy = 71.45% |
| Target variable distribution | 65.3% without coverage / 34.7% with coverage (8,896,028 records after cleaning) |
| Top predictor | Education level (77–81% feature importance) |

### Critical Data Rules
- **`NOTIEDER`**: `NULL` = WITH coverage. **Never** filter `AND NOTIEDER IS NOT NULL` — removes the entire positive class
- All columns are `VARCHAR` — always `CAST` or `pd.to_numeric` before numeric operations
- `999` / `9999` = unspecified in most columns
- SQL Server limited to 4 GB RAM — use materialized tables, never full-table queries without filters
- **`NIVELACAD`**: INEGI 2-digit codes (00, 10, 20…) — use `dim_nivelacad`, not `dim_nivel_educativo` for joins

```python
import pyodbc
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=100.64.0.11,1433;'
    'DATABASE=Defunciones_2000;'
    'UID=readonly;PWD=MCD_2000'
)
```

## Tools
Python · Jupyter · pyodbc · pandas · scikit-learn · SQL Server 2025 · T-SQL
