"""
Actividad 6 — Tópicos Selectos de Grandes Bases de Datos
Decisión de inversión en riego para productor de caña de azúcar en Pánuco
Carlos Pulido Rosas
"""

import numpy as np
import copy
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path

# ─────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────
HECTARES       = 100
HORIZON        = 7          # years
INVESTMENT_HA  = 80_000     # MXN/ha (4000 USD × 20)
INVESTMENT     = INVESTMENT_HA * HECTARES  # total

COST_TEMPORAL  = 38_000     # MXN/ha/yr
COST_RIEGO_OP  = 55_000     # MXN/ha/yr (production)
COST_RIEGO_MNT =  8_000     # MXN/ha/yr (maintenance)
COST_RIEGO     = COST_RIEGO_OP + COST_RIEGO_MNT  # 63,000

PRICES = [701.49, 757.16, 755.59, 900.95, 829.39, 897.65]  # MXN/ton

P_STORM = 0.05  # probability of severe storm

# Drought conditions
DROUGHT = {
    "Normal/Anormal seca":   {"prob": 0.40},
    "Sequía moderada":       {"prob": 0.30},
    "Sequía severa":         {"prob": 0.20},
    "Sequía extrema":        {"prob": 0.10},
}

# Yields (ton/ha/yr) — temporal
YIELD_TEMPORAL = {
    "Normal/Anormal seca": 60,
    "Sequía moderada":     50,
    "Sequía severa":       40,
    "Sequía extrema":      25,
}

# Yields (ton/ha/yr) — riego (when no storm)
# Normal/Anormal seca: stochastic sub-distribution
YIELD_RIEGO_NORMAL = [
    {"prob": 0.50, "yield": 90},
    {"prob": 0.30, "yield": 120},
    {"prob": 0.20, "yield": 200},
]
YIELD_RIEGO_FIXED = {
    "Sequía moderada": 90,
    "Sequía severa":   70,
    "Sequía extrema":  40,
}

N_SIM = 10_000
RNG   = np.random.default_rng(42)


# ─────────────────────────────────────────────
# 1. UTILITY FUNCTIONS
# ─────────────────────────────────────────────
def annual_utility(revenue_per_ha, cost_per_ha):
    """Net annual utility for 100 ha."""
    return (revenue_per_ha - cost_per_ha) * HECTARES


def revenue_per_ha(yield_ton, price):
    return yield_ton * price


# ─────────────────────────────────────────────
# 2. SCENARIO ENUMERATION (decision tree)
# ─────────────────────────────────────────────
def build_scenarios():
    """
    Returns list of dicts with:
      scenario, probability, yield_temporal, yield_riego_sub,
      utility_temporal, utility_riego  (at each price)
    Aggregated over prices for expected utility.
    """
    scenarios = []
    E_price = np.mean(PRICES)

    # Storm scenario (same for both)
    storm_prob = P_STORM
    storm = {
        "scenario":        "Tormenta severa",
        "condition":       "Tormenta",
        "sub_condition":   "-",
        "prob":            storm_prob,
        "yield_temporal":  0,
        "yield_riego":     0,
        "util_temporal":   annual_utility(0, COST_TEMPORAL),
        "util_riego":      annual_utility(0, COST_RIEGO),
    }
    scenarios.append(storm)

    no_storm_prob = 1 - P_STORM

    # Non-storm scenarios
    for cond, cinfo in DROUGHT.items():
        p_cond = cinfo["prob"] * no_storm_prob

        # TEMPORAL
        yt = YIELD_TEMPORAL[cond]

        # RIEGO
        if cond == "Normal/Anormal seca":
            for sub in YIELD_RIEGO_NORMAL:
                p_sub = p_cond * sub["prob"]
                yr    = sub["yield"]
                scenarios.append({
                    "scenario":      f"{cond} → {yr} ton/ha (riego)",
                    "condition":     cond,
                    "sub_condition": f"{yr} ton/ha",
                    "prob":          p_sub,
                    "yield_temporal": yt,
                    "yield_riego":    yr,
                    "util_temporal":  annual_utility(revenue_per_ha(yt, E_price), COST_TEMPORAL),
                    "util_riego":     annual_utility(revenue_per_ha(yr, E_price), COST_RIEGO),
                })
        else:
            yr = YIELD_RIEGO_FIXED[cond]
            scenarios.append({
                "scenario":      cond,
                "condition":     cond,
                "sub_condition": "-",
                "prob":          p_cond,
                "yield_temporal": yt,
                "yield_riego":    yr,
                "util_temporal":  annual_utility(revenue_per_ha(yt, E_price), COST_TEMPORAL),
                "util_riego":     annual_utility(revenue_per_ha(yr, E_price), COST_RIEGO),
            })

    return scenarios


# ─────────────────────────────────────────────
# 3. EXPECTED ANNUAL UTILITY
# ─────────────────────────────────────────────
def expected_annual_utility(scenarios):
    """E[annual utility] for temporal and riego (operating, before investment)."""
    E_price = np.mean(PRICES)
    E_ut = 0.0
    E_ur = 0.0

    # Storm
    storm_prob = P_STORM
    E_ut += storm_prob * annual_utility(0, COST_TEMPORAL)
    E_ur += storm_prob * annual_utility(0, COST_RIEGO)

    no_storm_prob = 1 - P_STORM

    for cond, cinfo in DROUGHT.items():
        p_cond = cinfo["prob"] * no_storm_prob
        yt = YIELD_TEMPORAL[cond]
        E_ut += p_cond * annual_utility(revenue_per_ha(yt, E_price), COST_TEMPORAL)

        if cond == "Normal/Anormal seca":
            E_yield_riego_normal = sum(s["prob"] * s["yield"] for s in YIELD_RIEGO_NORMAL)
            E_ur += p_cond * annual_utility(
                revenue_per_ha(E_yield_riego_normal, E_price), COST_RIEGO
            )
        else:
            yr = YIELD_RIEGO_FIXED[cond]
            E_ur += p_cond * annual_utility(revenue_per_ha(yr, E_price), COST_RIEGO)

    return E_ut, E_ur


# ─────────────────────────────────────────────
# 4. SIMULATION
# ─────────────────────────────────────────────
def simulate():
    """
    10,000 scenarios × 7 years.
    Returns arrays of cumulative 7-year utility for temporal and riego.
    """
    prices  = np.array(PRICES)
    drought_probs  = np.array([0.40, 0.30, 0.20, 0.10])
    yield_temporal = np.array([60, 50, 40, 25])

    # Riego expected yield per drought condition (for moderate/severe/extreme it's fixed)
    # For normal: E[yield] = 0.5*90 + 0.3*120 + 0.2*200 = 121
    yield_riego_det = np.array([121.0, 90.0, 70.0, 40.0])  # deterministic E[yield] per condition

    cum_temporal = np.zeros(N_SIM)
    cum_riego    = np.zeros(N_SIM)

    for _ in range(HORIZON):
        # Draw price (uniform over 6 observed)
        p_idx   = RNG.integers(0, 6, size=N_SIM)
        p       = prices[p_idx]

        # Draw drought condition
        d_idx   = RNG.choice(4, size=N_SIM, p=drought_probs)

        # Draw storm
        storm   = RNG.random(size=N_SIM) < P_STORM

        # Yields
        yt      = np.where(storm, 0.0, yield_temporal[d_idx].astype(float))
        yr_base = np.where(storm, 0.0, yield_riego_det[d_idx])

        # For normal/dry with riego: sample the sub-distribution
        is_normal_no_storm = (~storm) & (d_idx == 0)
        sub_rng   = RNG.random(size=N_SIM)
        yr_normal = np.where(sub_rng < 0.50, 90.0,
                    np.where(sub_rng < 0.80, 120.0, 200.0))
        yr        = np.where(is_normal_no_storm, yr_normal, yr_base)

        # Annual utilities
        ut = annual_utility(yt * p, COST_TEMPORAL)   # vectorized: yt*p is revenue/ha (scalar ops)
        # Note: annual_utility does (rev_per_ha - cost)*100, but here revenue_per_ha = yield*price
        # We need element-wise: (yt*p - COST_TEMPORAL)*HECTARES
        ut = (yt * p - COST_TEMPORAL) * HECTARES
        ur = (yr * p - COST_RIEGO)    * HECTARES

        cum_temporal += ut
        cum_riego    += ur

    # Subtract investment from riego
    cum_riego -= INVESTMENT

    return cum_temporal, cum_riego


# ─────────────────────────────────────────────
# 5. REPORT GENERATION
# ─────────────────────────────────────────────
NAVY  = RGBColor(0x1F, 0x35, 0x64)   # #1F3564
AMBER = RGBColor(0xFF, 0xBF, 0x00)   # #FFBF00
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xD9, 0xE1, 0xF2)   # light blue fill


def set_cell_bg(cell, rgb_hex: str):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  rgb_hex)
    tcPr.append(shd)


def set_col_width(table, col_idx, width_cm):
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = NAVY
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = NAVY
    else:
        run.font.size = Pt(11)
        run.font.color.rgb = NAVY
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    return p


def add_body(doc, text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in p.runs:
        run.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_table_header_row(table, headers):
    row = table.rows[0]
    for i, h in enumerate(headers):
        cell = row.cells[i]
        cell.text = h
        set_cell_bg(cell, "1F3564")
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.bold = True
                run.font.color.rgb = WHITE
                run.font.size = Pt(9)


def add_data_row(table, values, shade=False):
    row = table.add_row()
    for i, v in enumerate(values):
        cell = row.cells[i]
        cell.text = str(v)
        if shade:
            set_cell_bg(cell, "D9E1F2")
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.font.size = Pt(9)
    return row


def fmt(n, decimals=2):
    return f"{n:,.{decimals}f}"


def build_report(scenarios, E_ut_annual, E_ur_annual, cum_temporal, cum_riego):
    template_path = Path.home() / "Documents/mcd/mcd_cucea/_recursos/plantillas/plantilla_informe_MCD.docx"
    doc = Document(str(template_path))

    # ── Title block ──────────────────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("Actividad 6 — Decisión de Inversión en Riego\npara Productor de Caña de Azúcar en Pánuco")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = NAVY

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta_p.add_run(
        "Carlos Pulido Rosas\n"
        "ASP28 Tópicos Selectos de Grandes Bases de Datos\n"
        "Maestría en Ciencias de los Datos — UdeG CUCEA · 2026"
    )
    meta_run.font.size = Pt(10)
    meta_run.font.color.rgb = NAVY

    doc.add_paragraph()

    # ── 1. Introducción ──────────────────────────────────────────────────────
    add_heading(doc, "1. Planteamiento del caso", level=1)
    add_body(doc,
        "Un productor de caña de azúcar en Pánuco, Veracruz, cultiva 100 hectáreas bajo condiciones "
        "de temporal y evalúa invertir en un sistema de riego ante la caída progresiva en sus rendimientos. "
        "El análisis se realiza en un horizonte de 7 años, considerando incertidumbre en el precio de la caña, "
        "en la condición hídrica anual y en la ocurrencia de tormentas severas. "
        "La inversión inicial asciende a $8,000,000 MXN (4,000 USD/ha × 100 ha × 20 MXN/USD)."
    )

    # ── 2. Árbol de decisión ─────────────────────────────────────────────────
    add_heading(doc, "2. Árbol de decisión — estructura", level=1)
    add_body(doc,
        "El árbol de decisión tiene dos ramas principales: (A) No invertir en riego (temporal) y "
        "(B) Invertir en sistema de riego. En cada rama, la primera fuente de incertidumbre es la "
        "ocurrencia de una tormenta severa (P = 5%), que destruye la cosecha independientemente de "
        "la alternativa. Si no hay tormenta (P = 95%), se ramifica en cuatro condiciones hídricas. "
        "En la alternativa con riego, bajo condiciones normales o anormalmente secas existe además "
        "una sub-distribución productiva (90/120/200 ton/ha con probabilidades 50%/30%/20%)."
    )

    add_heading(doc, "Parámetros del modelo", level=2)

    # Parameters table
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    add_table_header_row(t, ["Parámetro", "Valor"])
    params = [
        ("Superficie total", "100 ha"),
        ("Horizonte de análisis", "7 años"),
        ("Inversión sistema de riego", "$80,000 MXN/ha  →  $8,000,000 MXN total"),
        ("Costo anual — temporal", "$38,000 MXN/ha/año"),
        ("Costo anual — riego (operación + mantenimiento)", "$55,000 + $8,000 = $63,000 MXN/ha/año"),
        ("Probabilidad de tormenta severa", "5%"),
        ("Precio promedio esperado (E[precio])", f"${np.mean(PRICES):,.2f} MXN/ton"),
        ("Precios históricos observados", "701.49 · 757.16 · 755.59 · 900.95 · 829.39 · 897.65"),
    ]
    for i, (k, v) in enumerate(params):
        add_data_row(t, [k, v], shade=(i % 2 == 0))
    doc.add_paragraph()

    # ── 3. Escenarios y utilidades ───────────────────────────────────────────
    add_heading(doc, "3. Escenarios productivos y utilidad anual por escenario", level=1)
    add_body(doc,
        "La utilidad anual se calcula como: Utilidad = (Rendimiento × Precio − Costo/ha) × 100 ha. "
        f"Se utiliza el precio esperado E[precio] = ${np.mean(PRICES):,.2f} MXN/ton para el cálculo "
        "analítico. Las probabilidades combinadas incorporan la independencia entre condición hídrica "
        "y ocurrencia de tormenta."
    )

    E_price = np.mean(PRICES)
    headers = ["Condición", "Sub-condición", "P(escenario)", "Rend. Temporal\n(ton/ha)",
               "Util. Temporal\n(MXN)", "Rend. Riego\n(ton/ha)", "Util. Riego\n(MXN)"]
    t2 = doc.add_table(rows=1, cols=len(headers))
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2.style = "Table Grid"
    add_table_header_row(t2, headers)

    all_scen = []
    # Storm
    all_scen.append({
        "condition": "Tormenta severa", "sub": "—",
        "prob": P_STORM,
        "yt": 0, "yr": 0,
        "ut": (0 * E_price - COST_TEMPORAL) * HECTARES,
        "ur": (0 * E_price - COST_RIEGO)    * HECTARES,
    })
    for cond, cinfo in DROUGHT.items():
        p = cinfo["prob"] * (1 - P_STORM)
        yt = YIELD_TEMPORAL[cond]
        if cond == "Normal/Anormal seca":
            for sub in YIELD_RIEGO_NORMAL:
                yr = sub["yield"]
                all_scen.append({
                    "condition": cond, "sub": f"Riego: {yr} ton/ha",
                    "prob": p * sub["prob"],
                    "yt": yt, "yr": yr,
                    "ut": (yt * E_price - COST_TEMPORAL) * HECTARES,
                    "ur": (yr * E_price - COST_RIEGO)    * HECTARES,
                })
        else:
            yr = YIELD_RIEGO_FIXED[cond]
            all_scen.append({
                "condition": cond, "sub": "—",
                "prob": p,
                "yt": yt, "yr": yr,
                "ut": (yt * E_price - COST_TEMPORAL) * HECTARES,
                "ur": (yr * E_price - COST_RIEGO)    * HECTARES,
            })

    for i, s in enumerate(all_scen):
        add_data_row(t2, [
            s["condition"], s["sub"],
            f"{s['prob']*100:.1f}%",
            f"{s['yt']:.0f}",
            f"${s['ut']:,.0f}",
            f"{s['yr']:.0f}",
            f"${s['ur']:,.0f}",
        ], shade=(i % 2 == 0))

    doc.add_paragraph()

    # ── 4. Utilidad esperada anual ───────────────────────────────────────────
    add_heading(doc, "4. Utilidad esperada anual", level=1)
    add_body(doc,
        "La utilidad esperada anual se obtiene como la suma ponderada de las utilidades de cada "
        "escenario por su probabilidad de ocurrencia, utilizando el precio esperado."
    )

    # Expected yield breakdown
    E_yt = sum(
        DROUGHT[c]["prob"] * (1-P_STORM) * YIELD_TEMPORAL[c] for c in DROUGHT
    )  # + storm contributes 0
    E_yr_normal = sum(s["prob"] * s["yield"] for s in YIELD_RIEGO_NORMAL)
    E_yr = (
        DROUGHT["Normal/Anormal seca"]["prob"] * (1-P_STORM) * E_yr_normal +
        DROUGHT["Sequía moderada"]["prob"]     * (1-P_STORM) * YIELD_RIEGO_FIXED["Sequía moderada"] +
        DROUGHT["Sequía severa"]["prob"]       * (1-P_STORM) * YIELD_RIEGO_FIXED["Sequía severa"] +
        DROUGHT["Sequía extrema"]["prob"]      * (1-P_STORM) * YIELD_RIEGO_FIXED["Sequía extrema"]
    )

    t3 = doc.add_table(rows=1, cols=3)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3.style = "Table Grid"
    add_table_header_row(t3, ["Concepto", "Sin riego (temporal)", "Con riego"])
    rows3 = [
        ("Rendimiento esperado (ton/ha/año)", f"{E_yt:.3f}", f"{E_yr:.3f}"),
        ("Precio esperado (MXN/ton)", f"${E_price:,.2f}", f"${E_price:,.2f}"),
        ("Ingreso esperado (MXN/año)", f"${E_yt*E_price*HECTARES:,.0f}", f"${E_yr*E_price*HECTARES:,.0f}"),
        ("Costo operación total (MXN/año)", f"${COST_TEMPORAL*HECTARES:,.0f}", f"${COST_RIEGO*HECTARES:,.0f}"),
        ("Utilidad esperada anual (MXN/año)", f"${E_ut_annual:,.0f}", f"${E_ur_annual:,.0f}"),
    ]
    for i, r in enumerate(rows3):
        row = t3.add_row()
        for j, v in enumerate(r):
            row.cells[j].text = v
            if i % 2 == 0:
                set_cell_bg(row.cells[j], "D9E1F2")
            for para in row.cells[j].paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9)
            if j == 4 or (i == len(rows3)-1):
                for para in row.cells[j].paragraphs:
                    for run in para.runs:
                        run.bold = True
    doc.add_paragraph()

    # ── 5. Utilidad acumulada 7 años ─────────────────────────────────────────
    add_heading(doc, "5. Utilidad acumulada esperada — horizonte de 7 años", level=1)

    cum_ut_7 = E_ut_annual * HORIZON
    cum_ur_7 = E_ur_annual * HORIZON - INVESTMENT

    add_body(doc,
        f"Temporal (acumulada 7 años) = ${E_ut_annual:,.0f} × 7 = ${cum_ut_7:,.0f} MXN\n"
        f"Riego (acumulada 7 años)    = ${E_ur_annual:,.0f} × 7 − $8,000,000 = ${cum_ur_7:,.0f} MXN"
    )

    t4 = doc.add_table(rows=1, cols=3)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4.style = "Table Grid"
    add_table_header_row(t4, ["Concepto", "Sin riego (temporal)", "Con riego"])
    rows4 = [
        ("Utilidad esperada anual (MXN)", f"${E_ut_annual:,.0f}", f"${E_ur_annual:,.0f}"),
        ("Utilidad operativa acumulada (×7)", f"${E_ut_annual*7:,.0f}", f"${E_ur_annual*7:,.0f}"),
        ("Inversión inicial (MXN)", "$0", f"−${INVESTMENT:,.0f}"),
        ("Utilidad neta acumulada 7 años (MXN)", f"${cum_ut_7:,.0f}", f"${cum_ur_7:,.0f}"),
    ]
    for i, r in enumerate(rows4):
        row = t4.add_row()
        for j, v in enumerate(r):
            row.cells[j].text = v
            if i == len(rows4)-1:
                set_cell_bg(row.cells[j], "1F3564")
                for para in row.cells[j].paragraphs:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in para.runs:
                        run.bold = True
                        run.font.color.rgb = WHITE
                        run.font.size = Pt(9)
            else:
                if i % 2 == 0:
                    set_cell_bg(row.cells[j], "D9E1F2")
                for para in row.cells[j].paragraphs:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in para.runs:
                        run.font.size = Pt(9)
    doc.add_paragraph()

    # ── 6. Simulación ────────────────────────────────────────────────────────
    add_heading(doc, "6. Simulación de Monte Carlo — 10,000 escenarios", level=1)

    mean_t    = np.mean(cum_temporal)
    mean_r    = np.mean(cum_riego)
    p_riego   = np.mean(cum_riego > cum_temporal)
    median_t  = np.median(cum_temporal)
    median_r  = np.median(cum_riego)
    std_t     = np.std(cum_temporal)
    std_r     = np.std(cum_riego)
    p5_t      = np.percentile(cum_temporal, 5)
    p5_r      = np.percentile(cum_riego,    5)
    p95_t     = np.percentile(cum_temporal, 95)
    p95_r     = np.percentile(cum_riego,    95)

    add_body(doc,
        f"Se simularon {N_SIM:,} escenarios de 7 años. En cada año se sortearon de forma independiente: "
        "el precio (distribución uniforme discreta sobre los 6 precios históricos), la condición hídrica "
        "(multinomial con probabilidades 40%/30%/20%/10%) y la ocurrencia de tormenta (Bernoulli 5%). "
        "Para la alternativa de riego bajo condiciones normales sin tormenta, se sorteó adicionalmente "
        "el sub-escenario productivo (50%/30%/20% → 90/120/200 ton/ha). "
        "La inversión inicial de $8,000,000 MXN se descuenta al total acumulado de la alternativa con riego."
    )

    t5 = doc.add_table(rows=1, cols=3)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    t5.style = "Table Grid"
    add_table_header_row(t5, ["Métrica (7 años)", "Sin riego (temporal)", "Con riego"])
    sim_rows = [
        ("Media (MXN)",        f"${mean_t:,.0f}",   f"${mean_r:,.0f}"),
        ("Mediana (MXN)",      f"${median_t:,.0f}",  f"${median_r:,.0f}"),
        ("Desv. estándar",     f"${std_t:,.0f}",     f"${std_r:,.0f}"),
        ("Percentil 5% (MXN)", f"${p5_t:,.0f}",      f"${p5_r:,.0f}"),
        ("Percentil 95% (MXN)",f"${p95_t:,.0f}",     f"${p95_r:,.0f}"),
        (f"P(riego > temporal) = {p_riego*100:.1f}%", "—", f"{p_riego*100:.1f}%"),
    ]
    for i, r in enumerate(sim_rows):
        row = t5.add_row()
        for j, v in enumerate(r):
            row.cells[j].text = v
            if i % 2 == 0:
                set_cell_bg(row.cells[j], "D9E1F2")
            for para in row.cells[j].paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9)
                    if i == len(sim_rows) - 1:
                        run.bold = True
    doc.add_paragraph()

    # ── 7. Comparación de criterios ──────────────────────────────────────────
    add_heading(doc, "7. Comparación de criterios de decisión", level=1)

    winner_ev   = "Riego" if cum_ur_7 > cum_ut_7 else "Temporal"
    winner_sim  = "Riego" if p_riego > 0.50 else "Temporal"

    t6 = doc.add_table(rows=1, cols=4)
    t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    t6.style = "Table Grid"
    add_table_header_row(t6, ["Criterio", "Temporal", "Riego", "Decisión"])
    crit_rows = [
        ("Mayor utilidad esperada (analítica)",
         f"${cum_ut_7:,.0f}", f"${cum_ur_7:,.0f}", winner_ev),
        ("Mayoría de escenarios favorables (simulación)",
         f"{(1-p_riego)*100:.1f}%", f"{p_riego*100:.1f}%", winner_sim),
        ("Utilidad media simulada (7 años)",
         f"${mean_t:,.0f}", f"${mean_r:,.0f}",
         "Riego" if mean_r > mean_t else "Temporal"),
    ]
    for i, r in enumerate(crit_rows):
        row = t6.add_row()
        for j, v in enumerate(r):
            row.cells[j].text = v
            if i % 2 == 0:
                set_cell_bg(row.cells[j], "D9E1F2")
            if j == 3:  # Decision column
                set_cell_bg(row.cells[j], "1F3564")
                for para in row.cells[j].paragraphs:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in para.runs:
                        run.bold = True
                        run.font.color.rgb = WHITE
                        run.font.size = Pt(9)
            else:
                for para in row.cells[j].paragraphs:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in para.runs:
                        run.font.size = Pt(9)
    doc.add_paragraph()

    # ── 8. Conclusión ────────────────────────────────────────────────────────
    add_heading(doc, "8. Recomendación y conclusión", level=1)

    if cum_ur_7 > cum_ut_7 and p_riego > 0.50:
        recom = "invertir en el sistema de riego"
        justif = (
            f"Ambos criterios coinciden en recomendar la inversión. La utilidad neta esperada acumulada "
            f"con riego (${cum_ur_7:,.0f} MXN) supera a la alternativa temporal (${cum_ut_7:,.0f} MXN) "
            f"en un horizonte de 7 años. Además, la simulación de {N_SIM:,} escenarios indica que "
            f"en el {p_riego*100:.1f}% de los casos el riego es más rentable, lo que confirma la "
            "solidez de la decisión."
        )
    elif cum_ur_7 <= cum_ut_7 and p_riego <= 0.50:
        recom = "no invertir en el sistema de riego"
        justif = (
            f"Ambos criterios coinciden en no recomendar la inversión. La utilidad neta esperada "
            f"con riego (${cum_ur_7:,.0f} MXN) no supera a la alternativa temporal (${cum_ut_7:,.0f} MXN). "
            f"La simulación muestra que solo en el {p_riego*100:.1f}% de los escenarios el riego resulta "
            "más rentable, lo que evidencia que la inversión no se recupera en el horizonte analizado. "
            "Sin embargo, el riego ofrece mayor estabilidad productiva, lo que puede ser relevante si "
            "el productor tiene alta aversión al riesgo o acceso a financiamiento favorable."
        )
    else:
        recom = "evaluar condiciones de financiamiento"
        justif = (
            "Los criterios divergen. Bajo valor esperado analítico una alternativa domina, pero la "
            f"simulación indica que en el {p_riego*100:.1f}% de los escenarios el riego es superior. "
            "Se recomienda considerar la aversión al riesgo del productor y las condiciones de financiamiento."
        )

    add_body(doc,
        f"Con base en el análisis, se recomienda al productor {recom}.\n\n{justif}\n\n"
        "Es importante destacar que el sistema de riego no solo impacta la rentabilidad esperada, "
        "sino también la volatilidad del ingreso. El riego estabiliza la producción ante sequías moderadas "
        "y severas, y abre la posibilidad de rendimientos excepcionales (hasta 200 ton/ha) en años "
        "favorables, lo que representa un beneficio estratégico a largo plazo más allá del horizonte "
        "de 7 años analizado."
    )

    # Save
    out_dir  = Path(__file__).parent
    docx_out = out_dir / "Actividad6_TopicosSelectos_CarlosPulidoRosas.docx"
    doc.save(str(docx_out))
    print(f"Guardado: {docx_out}")
    return docx_out


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Construyendo escenarios...")
    scenarios = build_scenarios()

    print("Calculando utilidad esperada anual...")
    E_ut_annual, E_ur_annual = expected_annual_utility(scenarios)
    print(f"  E[Util anual temporal] = ${E_ut_annual:,.0f} MXN")
    print(f"  E[Util anual riego]    = ${E_ur_annual:,.0f} MXN")

    cum_ut_7 = E_ut_annual * HORIZON
    cum_ur_7 = E_ur_annual * HORIZON - INVESTMENT
    print(f"  Util acumulada temporal (7 años) = ${cum_ut_7:,.0f} MXN")
    print(f"  Util acumulada riego    (7 años) = ${cum_ur_7:,.0f} MXN")

    print(f"\nEjecutando simulación ({N_SIM:,} escenarios × {HORIZON} años)...")
    cum_temporal, cum_riego = simulate()
    p_riego = np.mean(cum_riego > cum_temporal)
    print(f"  Media temporal = ${np.mean(cum_temporal):,.0f} MXN")
    print(f"  Media riego    = ${np.mean(cum_riego):,.0f} MXN")
    print(f"  P(riego > temporal) = {p_riego*100:.1f}%")

    print("\nGenerando reporte DOCX...")
    docx_path = build_report(scenarios, E_ut_annual, E_ur_annual, cum_temporal, cum_riego)
    print("Listo.")
