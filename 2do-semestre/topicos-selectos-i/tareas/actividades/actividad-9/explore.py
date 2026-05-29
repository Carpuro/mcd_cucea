import pandas as pd
import os

BASE = os.path.dirname(os.path.abspath(__file__))

files = {
    "forecast_2026":        "1._Forecast_2026.xlsx",
    "historic_sales":       "2._HISTORIC_SALES.xlsx",
    "stock_mb52":           "3._Stock_MB52.xlsx",
    "trafico":              "4._Trafico_(Reporte_excel_compartida).xlsx",
    "current_sales":        "5._Current_month_sales_(ZSDR04).xlsx",
    "produccion":           "6._Produccion_(Excel_compras_internacionales).xlsx",
    "clasificacion":        "7.CLASIFICACION_DE_PRODUCTOS_iluminacion.xlsx",
    "master_box":           "8._FACT_MASTER_BOX.xlsx",
    "requirements":         "9._FACT_REQUIREMENTS.xlsx",
    "almacen_fiscal":       "10._FACT_ALMACEN_FISCAL.xlsx",
    "forecast_planeacion":  "11._Forecast_PLANEACION.xlsx",
    "stock_in_past":        "12.STOCK_IN_PAST.xlsx",
    "ai_recommendation":    "13._FACT_AI_RECOMENDATION.xlsx",
    "dim_cedis":            "DIM_CEDIS.xlsx",
}

for key, fname in files.items():
    path = os.path.join(BASE, fname)
    try:
        xl = pd.ExcelFile(path)
        sheets = xl.sheet_names
        print(f"\n{'='*60}")
        print(f"{key}  |  sheets: {sheets}")
        for sheet in sheets:
            df = xl.parse(sheet)
            print(f"  [{sheet}]  shape: {df.shape}")
            print(f"  columns: {list(df.columns)}")
            print(df.head(3).to_string(index=False))
    except Exception as e:
        print(f"\n{key}: ERROR -> {e}")
