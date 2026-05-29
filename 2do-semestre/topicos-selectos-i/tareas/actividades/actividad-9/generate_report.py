import pandas as pd
import numpy as np
import warnings
import copy
warnings.filterwarnings("ignore")

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

BASE = r"C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\2do-semestre\topicos-selectos-i\tareas\actividades\actividad-9"
TEMPLATE = r"C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\_recursos\plantillas\plantilla_informe_MCD.docx"
OUTPUT = os.path.join(BASE, "Actividad9_TopicosSelectos_CarlosPulidoRosas.docx")

# ── Reload analysis data ──────────────────────────────────────────────────────
ai = pd.read_excel(f"{BASE}/13._FACT_AI_RECOMENDATION.xlsx", sheet_name="AI_ENRICHED")

target_combos = [
    {"URGENCY_STATUS": "CRITICAL", "ABC_CLASS": "A"},
    {"URGENCY_STATUS": "HIGH",     "ABC_CLASS": "A"},
    {"URGENCY_STATUS": "HIGH",     "ABC_CLASS": "B"},
    {"URGENCY_STATUS": "MEDIUM",   "ABC_CLASS": "B"},
    {"URGENCY_STATUS": "LOW"},
]
selected, used = [], set()
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
        selected.append(row); used.add(row["ITEM"])

skus_df = pd.DataFrame(selected).reset_index(drop=True)

def my_recommendation(row):
    """
    Executive framework: ACCION + MAGNITUD + POR QUE + RIESGO
    Priority: Protect flow > Avoid overstock > Healthy coverage > Reduce SC saturation > Avoid stockout
    Target coverage: 1.5-2.0 months total. Max 2.5 only for Class A + strong growth + positive momentum.
    """
    months_stock    = row["MONTHS_IN_STOCK"]
    months_sc       = row["MONTHS_IN_SUPPLY_CHAIN"]
    total_cover     = months_stock + months_sc
    trend           = row["SALES_TREND_STATUS"]
    abc             = row["ABC_CLASS"]
    yoy             = row["YOY_SALES_GROWTH"]
    stockout_days   = row["SC_DAYS_UNTIL_STOCKOUT"]
    purchase_prop   = row["PURCHASE_PROPOSAL"]
    purchase_months = row["PURCHASE_PROPOSAL_MONTHS"]
    lead_days       = row["SC_LEAD_TIME_TOTAL_DAYS"]
    momentum        = row["DEMAND_MOMENTUM_SCORE"]
    declining       = trend in ["DECLINING", "STRONG DECLINE"]
    accelerating    = trend in ["GROWING", "STRONG GROWTH"]
    yoy_bad         = yoy < -0.20
    yoy_good        = yoy > 0.15
    sc_saturated    = months_sc > 4.0
    sc_elevated     = months_sc > 2.5
    imminent_out    = stockout_days <= 7
    near_out        = stockout_days <= 30
    over_target     = total_cover > 3.0
    above_target    = total_cover > 2.0
    gap_risk        = (stockout_days - lead_days) < -14

    # ── Decision tree ────────────────────────────────────────────────────────
    # CASE 1: SC already saturated (>4 months) — freeze regardless of trend
    if sc_saturated:
        risk = "LOW"
        action = (
            f"Congelar compras y revisar forecast; supply chain acumula {months_sc:.1f} meses"
            f" con tendencia {trend} y YoY {yoy:.0%}."
            f" Consumir tránsito antes de evaluar nueva orden."
            f" Riesgo: capital detenido y posible obsolescencia."
        )

    # CASE 2: Imminent stockout AND SC cannot bridge the gap
    elif imminent_out and gap_risk:
        risk = "CRITICAL"
        action = (
            f"Acelerar arribo de SC existente y emitir OC de emergencia {int(purchase_prop):,} pzas"
            f" ({purchase_months:.1f} meses); stock fisico se agota en {stockout_days:.0f} dias"
            f" vs lead time {int(lead_days)} dias."
            f" Riesgo: quiebre inminente con impacto a clientes."
        )

    # CASE 3: Near stockout but SC already covers — accelerate SC, no new PO
    elif near_out and not gap_risk and above_target:
        risk = "HIGH"
        action = (
            f"Acelerar arribo del inventario en transito ({months_sc:.1f} meses en SC);"
            f" NO emitir nueva OC — cobertura total {total_cover:.1f} meses supera objetivo de 2.0."
            f" Stock fisico se agota en {stockout_days:.0f} dias."
            f" Riesgo: quiebre tecnico si el transito no se adelanta."
        )

    # CASE 4: Near stockout, coverage below target, declining or bad YoY
    elif near_out and not above_target and (declining or yoy_bad):
        risk = "HIGH"
        pzas_1m = int(purchase_prop * 0.5) if purchase_months > 1 else int(purchase_prop)
        action = (
            f"Comprar unicamente {pzas_1m:,} pzas (1 mes) de forma escalonada;"
            f" stockout en {stockout_days:.0f} dias pero tendencia {trend} con YoY {yoy:.0%}."
            f" Evitar sobrecompra con demanda decreciente."
            f" Riesgo: quiebre parcial si se subestima la demanda."
        )

    # CASE 5: Near stockout, coverage below target, growing
    elif near_out and not above_target and accelerating:
        risk = "HIGH"
        action = (
            f"Comprar {int(purchase_prop):,} pzas ({purchase_months:.1f} meses) y dividir en"
            f" dos ordenes mensuales; stockout en {stockout_days:.0f} dias con crecimiento {trend}."
            f" Riesgo: quiebre de stock en segmento con momentum positivo."
        )

    # CASE 6: Overstock + SC elevated + deceleration — liquidate or freeze
    elif over_target and (sc_elevated or declining or yoy_bad):
        risk = "LOW"
        action = (
            f"Frenar nueva OC; cobertura total {total_cover:.1f} meses con SC elevado"
            f" ({months_sc:.1f} meses) y YoY {yoy:.0%}."
            f" Considerar promocion para acelerar rotacion."
            f" Riesgo: sobreinventario y capital detenido."
        )

    # CASE 7: Above target + mixed signals (growth but also elevated SC)
    elif above_target and sc_elevated and accelerating:
        risk = "MEDIUM"
        action = (
            f"Frenar nueva OC y consumir transito existente; pese a tendencia {trend},"
            f" SC de {months_sc:.1f} meses supera objetivo."
            f" Revisar si el forecast es sostenible vs momentum reciente ({momentum} pts)."
            f" Riesgo: sobrecompra si el crecimiento no se consolida."
        )

    # CASE 8: Healthy range — minor adjustment needed
    elif above_target and not sc_elevated:
        risk = "MEDIUM"
        action = (
            f"Planear compra escalonada de {int(purchase_prop):,} pzas en 30 dias;"
            f" cobertura actual {total_cover:.1f} meses dentro de rango objetivo."
            f" Monitorear tendencia {trend} y YoY {yoy:.0%} antes de confirmar volumen."
            f" Riesgo: retraso de OC si la demanda acelera."
        )

    # CASE 9: Below target, no urgency — buy normally
    else:
        risk = "MEDIUM"
        action = (
            f"Emitir OC por {int(purchase_prop):,} pzas ({purchase_months:.1f} meses)"
            f" en proximo ciclo; cobertura total {total_cover:.1f} meses por debajo del objetivo."
            f" Clase {abc}, tendencia {trend}."
            f" Riesgo: reduccion de cobertura si la demanda supera el forecast."
        )

    return pd.Series({"MY_RISK": risk, "MY_ACTION": action, "TOTAL_COVER": round(total_cover, 2)})

my_recs = skus_df.apply(my_recommendation, axis=1)
skus_df = pd.concat([skus_df, my_recs], axis=1)

# ── Helper functions ──────────────────────────────────────────────────────────
NAVY  = (0x1F, 0x35, 0x64)
AMBER = (0xC0, 0x85, 0x00)
WHITE = (0xFF, 0xFF, 0xFF)
GRAY  = (0xF2, 0xF2, 0xF2)

RISK_COLOR = {
    "CRITICAL": (0xC0, 0x00, 0x00),
    "HIGH":     (0xFF, 0x66, 0x00),
    "MEDIUM":   (0xFF, 0xC0, 0x00),
    "LOW":      (0x00, 0x70, 0xC0),
}

def rgb_to_color(t):
    return RGBColor(t[0], t[1], t[2])

def set_cell_bg(cell, rgb_tuple):
    r, g, b = rgb_tuple
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    hex_color = f"{r:02X}{g:02X}{b:02X}"
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def para_fmt(paragraph, bold=False, size=10, color=None, align=None):
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run("")
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if align:
        paragraph.alignment = align

def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.color.rgb = rgb_to_color(NAVY)
    return p

def add_body(doc, text):
    p = doc.add_paragraph(text)
    p.style.font.size = Pt(10)
    return p

# ── Build document ────────────────────────────────────────────────────────────
doc = Document(TEMPLATE)

# --- Fill metadata table (Table 1) ---
# Rows 0-6: Alumno, Fecha, Actividad, Herramienta, Version, Entorno, Dataset
meta = doc.tables[1]

def set_meta_cell(row_idx, text):
    cell = meta.rows[row_idx].cells[1]
    p = cell.paragraphs[0]
    for run in p.runs:
        run.text = ""
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)

set_meta_cell(0, "Carlos Pulido Rosas")
set_meta_cell(1, "26 de mayo de 2026")
set_meta_cell(2, "Actividad 9 - Planeacion con IA")
set_meta_cell(3, "Power BI / Python 3.13 / pandas")
set_meta_cell(4, "Anaconda Python 3.13 / Power BI Desktop")
set_meta_cell(5, "Katana (MSI Katana AI B8V) - Windows")
set_meta_cell(6, "13 archivos xlsx: ventas historicas, forecast, stock, supply chain, recomendacion IA")

# --- Subject in header (Table 0, cell 1, paragraph 3) ---
try:
    cell1 = doc.tables[0].rows[0].cells[1]
    if len(cell1.paragraphs) > 3:
        p = cell1.paragraphs[3]
        if p.runs:
            p.runs[0].text = "Materia: Topicos Selectos I (ASP28)"
        else:
            p.add_run("Materia: Topicos Selectos I (ASP28)")
except Exception:
    pass

# --- Title ---
for p in doc.paragraphs:
    if "[Titulo de la actividad]" in p.text or "Título de la actividad" in p.text:
        for run in p.runs:
            run.text = ""
        p.add_run("Actividad 9 - Planeacion con Inteligencia Artificial").bold = True
        break

# --- Replace placeholder paragraphs ---
replacements = {
    "Describe brevemente el objetivo y contexto de la actividad.":
        ("La planeacion de inventarios en cadenas de suministro complejas requiere integrar "
         "multiples fuentes de informacion: ventas historicas, forecast, stock fisico, "
         "ordenes en transito y tiempos de respuesta de proveedores. Esta actividad replica "
         "el dashboard de planeacion con IA presentado por el profesor, selecciona 5 SKUs "
         "de la categoria de iluminacion y genera recomendaciones de compra propias, "
         "comparandolas con las producidas por el modelo de IA del archivo FACT_AI_RECOMENDATION."),

    "Describe el procedimiento realizado paso a paso. Agrega subsecciones si es necesario.":
        ("Se cargaron 13 bases de datos en Python con pandas. Las fuentes principales para "
         "el analisis fueron: ventas historicas (92,466 registros), forecast 2026, stock MB52 "
         "por CEDIS, stock en supply chain, y el archivo de recomendacion de IA con 172 SKUs "
         "activos enriquecidos con metricas de urgencia, tendencia y propuesta de compra.\n\n"
         "Seleccion de 5 SKUs: se eligieron buscando diversidad en clase ABC, estado de "
         "urgencia (CRITICAL, HIGH, MEDIUM, LOW) y tendencia de ventas (GROWING, STABLE, "
         "STRONG GROWTH, DECLINING).\n\n"
         "Metodologia de recomendacion propia: se calculo el riesgo de desabasto comparando "
         "el stock en mano (dias disponibles) contra el lead time total de la cadena de "
         "suministro (120 dias). Si el stockout ocurre antes de que el inventario en SC pueda "
         "llegar, se clasifica como CRITICAL o HIGH segun la brecha de dias."),

    "Describe los resultados obtenidos.":
        ("Se analizaron 5 SKUs con perfiles de riesgo distintos. La tabla siguiente muestra "
         "las metricas clave y la comparacion entre la recomendacion propia y la de la IA. "
         "Los principales hallazgos se detallan despues de la tabla."),

    "Escribe las conclusiones. ¿Qué aprendiste? ¿Qué observaste en los datos?":
        ("La comparacion entre el modelo propio y la IA revela diferencias metodologicas "
         "relevantes. El modelo propio es mas conservador: clasifica como CRITICAL cualquier "
         "SKU donde el stockout ocurra antes de que el lead time de la SC permita reponer. "
         "La IA, en cambio, integra tres dimensiones adicionales que el analisis manual no "
         "captura facilmente:\n\n"
         "1. Nivel real del forecast: un SKU con forecast cercano a cero (LED06/10W3) "
         "no merece la misma urgencia que uno con alta demanda, aunque ambos tengan stock "
         "minimo. La IA clasifica este caso como HIGH, no CRITICAL.\n\n"
         "2. Timing de llegada del SC: la IA discrimina entre stock en transito vs en "
         "produccion. Si el inventario en SC puede llegar antes del stockout, la urgencia "
         "baja (SUBSOL/60W: HIGH en lugar de CRITICAL).\n\n"
         "3. Tendencia como ponderador: en SKUs con tendencia DECLINING y bajo forecast "
         "(LRD/9W), la IA recomienda compra minima aunque el stock sea limitado, priorizando "
         "otros articulos con mayor dinamismo comercial.\n\n"
         "El dashboard de Power BI permite visualizar estas dimensiones de forma integrada "
         "y tomar decisiones de planeacion con mayor contexto que un analisis tabular."),
}

for p in doc.paragraphs:
    for old, new in replacements.items():
        if old in p.text:
            for run in p.runs:
                run.text = ""
            p.add_run(new)
            break

# Remove template placeholder paragraphs
to_remove = [
    "Ejemplo de comando o query ejecutado:",
    "Captura 1", "Captura 2", "[Insertar captura",
    "-- Query o comando", "SELECT campo",
]
for p in doc.paragraphs:
    if any(x in p.text for x in to_remove):
        p.clear()

# Remove template tables 2 and 3 (query/results placeholders)
for tbl in doc.tables[2:]:
    tbl._element.getparent().remove(tbl._element)

# --- Results table: 5 SKUs ───────────────────────────────────────────────────
results_section = None
for p in doc.paragraphs:
    if "3. Resultados" in p.text or "Resultados" in p.text:
        results_section = p
        break

# Find insertion point (after "Resultados" content paragraph)
insert_after = None
found = False
for p in doc.paragraphs:
    if found and p.text.strip() and "4. Conclusiones" not in p.text:
        insert_after = p
    if "3. Resultados" in p.text:
        found = True

# Build the SKU comparison table
headers = [
    "SKU", "Clase\nABC", "Tendencia", "Stock\n(meses)", "SC\n(meses)",
    "Cobertura\nTotal", "Stockout\n(dias)", "Propuesta\nCompra (pzas)",
    "MI\nRiesgo", "Mi Recomendacion", "IA\nRiesgo", "Recomendacion IA"
]

tbl = doc.add_table(rows=1 + len(skus_df), cols=len(headers))
tbl.style = "Table Grid"

# Header row
hrow = tbl.rows[0]
for j, h in enumerate(headers):
    cell = hrow.cells[j]
    cell.text = h
    set_cell_bg(cell, NAVY)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.bold = True
        run.font.size = Pt(8)
        run.font.color.rgb = rgb_to_color(WHITE)

# Data rows
for i, row in skus_df.iterrows():
    drow = tbl.rows[i + 1]
    vals = [
        row["ITEM"],
        row["ABC_CLASS"],
        row["SALES_TREND_STATUS"],
        f"{row['MONTHS_IN_STOCK']:.2f}",
        f"{row['MONTHS_IN_SUPPLY_CHAIN']:.2f}",
        f"{row['TOTAL_COVER']:.2f}",
        f"{row['SC_DAYS_UNTIL_STOCKOUT']:.0f}",
        f"{int(row['PURCHASE_PROPOSAL']):,}",
        row["MY_RISK"],
        row["MY_ACTION"],
        row["URGENCY_STATUS"],
        row["AI_EXECUTIVE_ACTION"],
    ]
    for j, val in enumerate(vals):
        cell = drow.cells[j]
        cell.text = str(val)
        p = cell.paragraphs[0]
        for run in p.runs:
            run.font.size = Pt(7)
        if i % 2 == 0:
            set_cell_bg(cell, GRAY)
        # Color risk cells
        if j == 8:  # MY_RISK
            color = RISK_COLOR.get(str(val), NAVY)
            set_cell_bg(cell, color)
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = rgb_to_color(WHITE)
                run.font.size = Pt(7)
        if j == 10:  # AI RISK
            color = RISK_COLOR.get(str(val), NAVY)
            set_cell_bg(cell, color)
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = rgb_to_color(WHITE)
                run.font.size = Pt(7)

# Set column widths
col_widths = [Cm(2.0), Cm(1.0), Cm(2.2), Cm(1.2), Cm(1.2), Cm(1.4),
              Cm(1.3), Cm(1.8), Cm(1.3), Cm(5.5), Cm(1.3), Cm(5.5)]
for row in tbl.rows:
    for j, cell in enumerate(row.cells):
        cell.width = col_widths[j]

# Move the table to after results paragraph
if results_section:
    results_section._element.addnext(tbl._element)

# --- Divergence analysis paragraph ──────────────────────────────────────────
div_text = (
    "\nAnalisis de divergencias entre modelo propio e IA:\n\n"
    "Ambos modelos usan el marco ACCION + MAGNITUD + POR QUE + RIESGO con prioridad en "
    "proteger flujo y evitar sobreinventario. Las divergencias surgen de matices en la "
    "ponderacion de variables:\n\n"
    "- LED06/10W. (HIGH propio / CRITICAL IA): Acuerdo en urgencia, diferencia en magnitud. "
    "Mi modelo detecta que el SC ya cubre 3.5 meses y recomienda acelerar arribo en lugar "
    "de emitir nueva OC; la IA ordena compra adicional de 578,100 pzas ignorando que la "
    "cobertura total de 4.2 meses ya supera el objetivo operativo de 2 meses.\n\n"
    "- SUBSOL/60W (LOW propio / HIGH IA): Divergencia por horizonte de analisis. "
    "Mi modelo prioriza el YoY de -59% y el SC de 2.1 meses como senales de freno; "
    "la IA responde al stockout en 44 dias sin ponderar suficientemente la desaceleracion "
    "comercial sostenida. Un Director de Supply Chain priorizaria proteger el flujo.\n\n"
    "- LED06/10W3 (HIGH propio / HIGH IA): Acuerdo en accion urgente. Mi modelo aplica "
    "compra escalonada (1 mes primero) por la tendencia STABLE y YoY negativo; "
    "la IA recomienda 26,160 pzas directas (2 meses) sin considerar la moderacion de demanda.\n\n"
    "- ADAPTADOR/E40 (LOW propio / MEDIUM IA): Divergencia por saturacion de SC. "
    "Mi modelo frena la compra porque total cover de 3.5 meses supera el objetivo y "
    "el YoY es negativo pese a momentum positivo reciente. La IA recomienda compra normal "
    "de 500 pzas que mantiene el volumen objetivo. La postura conservadora es preferible "
    "ante senales mixtas.\n\n"
    "- LRD/9W (LOW propio / LOW IA): Acuerdo total. SC de 5.4 meses, tendencia DECLINING "
    "y YoY -57% justifican congelar compras y evaluar promocion para liberar capital. "
    "Unico SKU donde ambos modelos convergen en decision y racional."
)

for p in doc.paragraphs:
    if "Los principales hallazgos" in p.text:
        new_p = doc.add_paragraph(div_text)
        p._element.addnext(new_p._element)
        break

doc.save(OUTPUT)
print(f"Report saved: {OUTPUT}")
