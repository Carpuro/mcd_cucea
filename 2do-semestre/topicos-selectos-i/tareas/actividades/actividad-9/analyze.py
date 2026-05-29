import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

BASE = r"C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\2do-semestre\topicos-selectos-i\tareas\actividades\actividad-9"

# ── Load core tables ──────────────────────────────────────────────────────────
ai = pd.read_excel(f"{BASE}/13._FACT_AI_RECOMENDATION.xlsx", sheet_name="AI_ENRICHED")
fp = pd.read_excel(f"{BASE}/11._Forecast_PLANEACION.xlsx", sheet_name="FORECAST_PLANEACION")
cls = pd.read_excel(f"{BASE}/7.CLASIFICACION_DE_PRODUCTOS_iluminacion.xlsx", sheet_name="SKU")
cls.columns = ["CLASIFICACION", "ITEM"]

stock = pd.read_excel(f"{BASE}/3._Stock_MB52.xlsx", sheet_name="Sheet1")
stock = stock[["Material", "Libre utilización"]].copy()
stock.columns = ["ITEM", "STOCK_TOTAL"]
stock = stock.groupby("ITEM", as_index=False)["STOCK_TOTAL"].sum()

sales_h = pd.read_excel(f"{BASE}/2._HISTORIC_SALES.xlsx", sheet_name="Historic_sales",
                        usecols=["CODIGO REAL", "Cantidad", "YEAR", "MES NUMERO"])
sales_h.columns = ["ITEM", "QTY", "YEAR", "MONTH"]
sales_h = sales_h[sales_h["YEAR"].isin([2024, 2025])]

# ── Select 5 diverse SKUs ─────────────────────────────────────────────────────
# Goal: variety in urgency, ABC class, trend, and urgency score
target_combos = [
    {"URGENCY_STATUS": "CRITICAL", "ABC_CLASS": "A"},   # SKU 1: crítico clase A
    {"URGENCY_STATUS": "HIGH",     "ABC_CLASS": "A"},   # SKU 2: alto clase A
    {"URGENCY_STATUS": "HIGH",     "ABC_CLASS": "B"},   # SKU 3: alto clase B
    {"URGENCY_STATUS": "MEDIUM",   "ABC_CLASS": "C"},   # SKU 4: medio clase C
    {"URGENCY_STATUS": "LOW"},                           # SKU 5: bajo cualquier clase
]

selected = []
used = set()

for combo in target_combos:
    mask = pd.Series([True] * len(ai), index=ai.index)
    for col, val in combo.items():
        mask &= (ai[col] == val)
    candidates = ai[mask & ~ai["ITEM"].isin(used)]
    if candidates.empty:
        mask2 = ~ai["ITEM"].isin(used)
        for col, val in combo.items():
            if col == "URGENCY_STATUS":
                mask2 &= (ai[col] == val)
        candidates = ai[mask2]
    if not candidates.empty:
        row = candidates.sort_values("URGENCY_SCORE", ascending=False).iloc[0]
        selected.append(row)
        used.add(row["ITEM"])

skus_df = pd.DataFrame(selected).reset_index(drop=True)

# ── My own recommendation logic ───────────────────────────────────────────────
# Key insight: stock in supply chain is NOT immediately available.
# Stockout is driven by physical stock on hand vs lead time to receive SC inventory.
# Therefore risk is primarily driven by MONTHS_IN_STOCK and SC_DAYS_UNTIL_STOCKOUT,
# not by the sum of stock + SC.
def my_recommendation(row):
    months_stock    = row["MONTHS_IN_STOCK"]
    months_sc       = row["MONTHS_IN_SUPPLY_CHAIN"]
    total_cover     = months_stock + months_sc
    trend           = row["SALES_TREND_STATUS"]
    abc             = row["ABC_CLASS"]
    stockout_days   = row["SC_DAYS_UNTIL_STOCKOUT"]
    purchase_prop   = row["PURCHASE_PROPOSAL"]
    purchase_months = row["PURCHASE_PROPOSAL_MONTHS"]
    lead_days       = row["SC_LEAD_TIME_TOTAL_DAYS"]

    # Risk = stock on hand vs lead time to replenish from SC
    # If stockout_days < lead_time_days, a gap will occur
    gap_days = stockout_days - lead_days  # negative = stockout before replenishment arrives

    if stockout_days <= 30 or gap_days < -30:
        risk = "CRITICAL"
    elif stockout_days <= 60 or gap_days < 0:
        risk = "HIGH"
    elif months_stock < 2 or (trend in ["GROWING", "STRONG GROWTH"] and months_stock < 3):
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Adjust upward for high-value ABC A SKUs
    if abc == "A" and risk == "LOW":
        risk = "MEDIUM"

    # Action
    if risk == "CRITICAL":
        action = (f"Compra inmediata de {int(purchase_prop):,} pzas ({purchase_months:.1f} meses). "
                  f"Stock en mano: {months_stock:.2f} meses. Stockout en {stockout_days:.0f} días "
                  f"(lead time: {int(lead_days)} días). Activar booking y anticipo urgente.")
    elif risk == "HIGH":
        action = (f"Emitir OC por {int(purchase_prop):,} pzas ({purchase_months:.1f} meses) esta semana. "
                  f"Stock en mano: {months_stock:.2f} meses. Stockout proyectado: {stockout_days:.0f} días. "
                  f"Clase {abc}, tendencia {trend}.")
    elif risk == "MEDIUM":
        action = (f"Planear compra de {int(purchase_prop):,} pzas en los próximos 30 días. "
                  f"Cobertura en mano: {months_stock:.2f} meses. Monitorear tendencia ({trend}).")
    else:
        action = (f"Sin acción inmediata. Stock en mano: {months_stock:.2f} meses + "
                  f"{months_sc:.2f} meses en SC = {total_cover:.2f} meses de cobertura total. "
                  f"Revisar en siguiente ciclo de planeación.")

    return pd.Series({"MY_RISK": risk, "MY_ACTION": action, "TOTAL_COVER_MONTHS": round(total_cover, 2)})

my_recs = skus_df.apply(my_recommendation, axis=1)
skus_df = pd.concat([skus_df, my_recs], axis=1)

# ── Print comparison ──────────────────────────────────────────────────────────
cols_display = [
    "ITEM", "ABC_CLASS", "SALES_TREND_STATUS", "URGENCY_STATUS",
    "MONTHS_IN_STOCK", "MONTHS_IN_SUPPLY_CHAIN", "TOTAL_COVER_MONTHS",
    "SC_DAYS_UNTIL_STOCKOUT", "PURCHASE_PROPOSAL", "PURCHASE_PROPOSAL_MONTHS",
    "YOY_SALES_GROWTH", "DEMAND_MOMENTUM_SCORE",
]

print("\n" + "=" * 80)
print("SELECTED 5 SKUs — KEY METRICS")
print("=" * 80)
print(skus_df[cols_display].to_string(index=False))

print("\n" + "=" * 80)
print("COMPARISON: MY RECOMMENDATION vs AI RECOMMENDATION")
print("=" * 80)

for _, row in skus_df.iterrows():
    print(f"\nSKU: {row['ITEM']}  |  ABC: {row['ABC_CLASS']}  |  Trend: {row['SALES_TREND_STATUS']}")
    print(f"  Stock actual:     {row['MONTHS_IN_STOCK']:.2f} meses  |  SC: {row['MONTHS_IN_SUPPLY_CHAIN']:.2f} meses  |  Total: {row['TOTAL_COVER_MONTHS']:.2f} meses")
    print(f"  Stockout en:      {row['SC_DAYS_UNTIL_STOCKOUT']:.0f} días")
    print(f"  YoY growth:       {row['YOY_SALES_GROWTH']:.1%}")
    print(f"  Propuesta compra: {int(row['PURCHASE_PROPOSAL']):,} pzas ({row['PURCHASE_PROPOSAL_MONTHS']:.1f} meses)")
    print(f"\n  [MI RECOMENDACIÓN — {row['MY_RISK']}]")
    print(f"  {row['MY_ACTION']}")
    print(f"\n  [IA RECOMENDACIÓN — {row['URGENCY_STATUS']}]")
    print(f"  {row['AI_EXECUTIVE_ACTION']}")
    print("-" * 80)

# ── Save comparison to Excel ──────────────────────────────────────────────────
out_cols = [
    "ITEM", "ABC_CLASS", "SALES_TREND_STATUS", "URGENCY_STATUS",
    "MONTHS_IN_STOCK", "MONTHS_IN_SUPPLY_CHAIN", "TOTAL_COVER_MONTHS",
    "SC_DAYS_UNTIL_STOCKOUT", "PURCHASE_PROPOSAL", "PURCHASE_PROPOSAL_MONTHS",
    "YOY_SALES_GROWTH", "DEMAND_MOMENTUM_SCORE",
    "MY_RISK", "MY_ACTION", "AI_EXECUTIVE_ACTION",
]
out = skus_df[out_cols].copy()
out.to_excel(f"{BASE}/sku_analysis_output.xlsx", index=False)
print(f"\nSaved: sku_analysis_output.xlsx")
