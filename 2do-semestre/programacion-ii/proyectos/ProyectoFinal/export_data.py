"""
export_data.py
Exporta las tablas del proyecto desde SQL Server (katana) a CSV
para incluir en la carpeta data/ del entregable.

Tablas exportadas:
  - ocupaciones_onet  → data/ocupaciones_onet.csv   (O*NET + Block 3 scores)
  - trabajadores      → data/trabajadores_enoe.csv  (muestra ENOE Q3 2024 Jalisco)
  - vista_riesgo_jalisco → data/vista_riesgo_jalisco.csv (dataset final del modelo)
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os

# ── Conexion ──────────────────────────────────────────────────────────────────
# Cambia SERVER si conectas directo a katana (ej: 192.168.100.11,1433 o 100.64.0.11,1433)
SERVER = "localhost,1433"
DB     = "ai_automation_risk_jalisco"

engine = create_engine(
    f"mssql+pyodbc://{SERVER}/{DB}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)

OUT = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT, exist_ok=True)

exports = {
    "ocupaciones_onet":     "data/ocupaciones_onet.csv",
    "trabajadores":         "data/trabajadores_enoe.csv",
    "vista_riesgo_jalisco": "data/vista_riesgo_jalisco.csv",
}

with engine.connect() as conn:
    for table, filename in exports.items():
        print(f"Exportando {table}...", end=" ")
        df = pd.read_sql(text(f"SELECT * FROM dbo.{table}"), conn)
        out_path = os.path.join(os.path.dirname(__file__), filename)
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"{len(df):,} filas → {filename}")

print("\nExportacion completada.")
