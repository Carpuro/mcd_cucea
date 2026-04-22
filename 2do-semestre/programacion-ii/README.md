# Programación II
**Semestre:** 2do | **Departamento:** DSI | **Créditos:** 7 | **Prerrequisito:** Programación I | **Estado:** 🔄 En curso

Programación avanzada en Python para análisis de bases de datos. Enfoque en conectividad con SQL Server, procedimientos almacenados, tablas materializadas y pipelines de machine learning sobre datasets de gran escala.

## Notebooks (`notebooks/`)

| Notebook | Contenido | Estado |
|----------|-----------|--------|
| `Actividad_Defunciones_SQL.ipynb` | Pipeline completo de análisis — `Defunciones_2000` (10M+ registros) vía SQL Server | ✅ Hecho |
| `practica1.ipynb` | Práctica SQL — procedimientos almacenados y vistas | ✅ Hecho |

## Entregables (`tareas/`)

| Archivo | Contenido | Estado |
|---------|-----------|--------|
| `SP_Defunciones_CarlosPulidoRosas.docx/.pdf` | Reporte de procedimientos almacenados | ✅ Entregado |

## Dataset: Defunciones_2000

- **BD:** SQL Server 2025 en Docker — `192.168.100.11:1433`
- **Tabla:** `defunciones` — 10,099,182 registros · 81 columnas VARCHAR
- **Conexión:** pyodbc vía Tailscale (`100.64.0.11,1433`)
- **Usuario:** `readonly` / `MCD_2000`

### Tablas materializadas
`tbl_kpis` · `tbl_acceso_resumen` · `tbl_estados_resumen` · `tbl_urbano_resumen` · `tbl_escolaridad_resumen` · `tbl_indigena_resumen` · `tbl_grupos_edad_resumen` · `tbl_metricas_modelos` · `tbl_importancia_variables` · `tbl_coeficientes_ols`

### Procedimientos almacenados
`sp_muertes_*` (6 procedimientos) · `sp_top10_padecimientos_*` — 13 vistas SQL en total

### Resultados de modelos
| Modelo | Resultado |
|--------|-----------|
| OLS — efecto de derechohabiencia en esperanza de vida | +3.46 años (p < 0.0001), R² = 0.028 |
| Random Forest — predicción de edad al fallecimiento | R² = 0.2696, RMSE = 14.61 años |
| Árbol de decisión — clasificación de cobertura | Accuracy = 71.45% |
| Distribución de la variable objetivo | 65.3% sin cobertura / 34.7% con cobertura (8,896,028 registros tras limpieza) |
| Variable predictora dominante | Nivel educativo (77–81% de importancia) |

### Reglas críticas de datos
- **`NOTIEDER`**: `NULL` = CON cobertura. **Nunca** filtrar `AND NOTIEDER IS NOT NULL` — elimina toda la clase positiva
- Todas las columnas son `VARCHAR` — siempre `CAST` o `pd.to_numeric` antes de operaciones numéricas
- `999` / `9999` = no especificado en la mayoría de columnas
- SQL Server limitado a 4 GB RAM — usar tablas materializadas, nunca queries sin filtros sobre la tabla completa
- **`NIVELACAD`**: códigos INEGI de 2 dígitos (00, 10, 20…) — usar `dim_nivelacad` para joins, no `dim_nivel_educativo`

```python
import pyodbc
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=100.64.0.11,1433;'
    'DATABASE=Defunciones_2000;'
    'UID=readonly;PWD=MCD_2000'
)
```

## Herramientas
Python · Jupyter · pyodbc · pandas · scikit-learn · SQL Server 2025 · T-SQL
