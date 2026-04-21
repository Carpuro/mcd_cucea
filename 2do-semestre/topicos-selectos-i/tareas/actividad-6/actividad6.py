"""
Actividad 6 — Tópicos Selectos de Grandes Bases de Datos
Decisión de inversión en riego para productor de caña de azúcar en Pánuco
Carlos Pulido Rosas
"""

import numpy as np
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path

TEMPLATE = "/home/carpuro/Documents/mcd/mcd_cucea/_recursos/plantillas/plantilla_informe_MCD.docx"
OUTPUT   = "/home/carpuro/Documents/mcd/mcd_cucea/2do-semestre/topicos-selectos-i/tareas/actividad-6/Actividad6_TopicosSelectos_CarlosPulidoRosas.docx"

NAVY  = RGBColor(0x1F, 0x49, 0x7D)
AMBER = RGBColor(0xD4, 0x8C, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
BLACK  = RGBColor(0x00, 0x00, 0x00)

# ─────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────
HECTARES      = 100
HORIZON       = 7
INVESTMENT_HA = 80_000       # MXN/ha (4000 USD × 20)
INVESTMENT    = INVESTMENT_HA * HECTARES

COST_TEMPORAL = 38_000
COST_RIEGO    = 55_000 + 8_000   # 63,000

PRICES = [701.49, 757.16, 755.59, 900.95, 829.39, 897.65]

P_STORM = 0.05

DROUGHT = {
    "Normal / anormal seca": {"prob": 0.40},
    "Sequía moderada":       {"prob": 0.30},
    "Sequía severa":         {"prob": 0.20},
    "Sequía extrema":        {"prob": 0.10},
}
YIELD_TEMPORAL = {
    "Normal / anormal seca": 60,
    "Sequía moderada":       50,
    "Sequía severa":         40,
    "Sequía extrema":        25,
}
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
# ANALYSIS
# ─────────────────────────────────────────────
def expected_annual_utility():
    E_price = np.mean(PRICES)
    E_ut = P_STORM * (0 * E_price - COST_TEMPORAL) * HECTARES
    E_ur = P_STORM * (0 * E_price - COST_RIEGO)    * HECTARES
    no_storm = 1 - P_STORM
    for cond, cinfo in DROUGHT.items():
        p = cinfo["prob"] * no_storm
        yt = YIELD_TEMPORAL[cond]
        E_ut += p * (yt * E_price - COST_TEMPORAL) * HECTARES
        if cond == "Normal / anormal seca":
            e_yr = sum(s["prob"] * s["yield"] for s in YIELD_RIEGO_NORMAL)
        else:
            e_yr = YIELD_RIEGO_FIXED[cond]
        E_ur += p * (e_yr * E_price - COST_RIEGO) * HECTARES
    return E_ut, E_ur


def build_scenarios():
    E_price = np.mean(PRICES)
    rows = []
    # Storm
    rows.append({
        "cond": "Tormenta severa", "sub": "—", "prob": P_STORM,
        "yt": 0, "yr": 0,
        "ut": (0 - COST_TEMPORAL) * HECTARES,
        "ur": (0 - COST_RIEGO)    * HECTARES,
    })
    no_storm = 1 - P_STORM
    for cond, cinfo in DROUGHT.items():
        p = cinfo["prob"] * no_storm
        yt = YIELD_TEMPORAL[cond]
        if cond == "Normal / anormal seca":
            for sub in YIELD_RIEGO_NORMAL:
                yr = sub["yield"]
                rows.append({
                    "cond": cond, "sub": f"{yr} ton/ha",
                    "prob": p * sub["prob"], "yt": yt, "yr": yr,
                    "ut": (yt * E_price - COST_TEMPORAL) * HECTARES,
                    "ur": (yr * E_price - COST_RIEGO)    * HECTARES,
                })
        else:
            yr = YIELD_RIEGO_FIXED[cond]
            rows.append({
                "cond": cond, "sub": "—", "prob": p, "yt": yt, "yr": yr,
                "ut": (yt * E_price - COST_TEMPORAL) * HECTARES,
                "ur": (yr * E_price - COST_RIEGO)    * HECTARES,
            })
    return rows


def simulate():
    prices         = np.array(PRICES)
    drought_probs  = np.array([0.40, 0.30, 0.20, 0.10])
    yield_t        = np.array([60, 50, 40, 25], dtype=float)
    yield_r_det    = np.array([121.0, 90.0, 70.0, 40.0])

    cum_t = np.zeros(N_SIM)
    cum_r = np.zeros(N_SIM)

    for _ in range(HORIZON):
        p      = prices[RNG.integers(0, 6, N_SIM)]
        d_idx  = RNG.choice(4, N_SIM, p=drought_probs)
        storm  = RNG.random(N_SIM) < P_STORM

        yt = np.where(storm, 0.0, yield_t[d_idx])

        yr_base   = np.where(storm, 0.0, yield_r_det[d_idx])
        sub_rng   = RNG.random(N_SIM)
        yr_normal = np.where(sub_rng < 0.50, 90.0,
                    np.where(sub_rng < 0.80, 120.0, 200.0))
        is_norm   = (~storm) & (d_idx == 0)
        yr        = np.where(is_norm, yr_normal, yr_base)

        cum_t += (yt * p - COST_TEMPORAL) * HECTARES
        cum_r += (yr * p - COST_RIEGO)    * HECTARES

    cum_r -= INVESTMENT
    return cum_t, cum_r


# ─────────────────────────────────────────────
# DOCX HELPERS  (same pattern as Actividad 5)
# ─────────────────────────────────────────────
def set_cell_bg(cell, color: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    hex_c = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_c)
    tcPr.append(shd)


def set_row_bg(row, color: RGBColor):
    for cell in row.cells:
        set_cell_bg(cell, color)


def add_run(para, text, bold=False, italic=False, color=None, size=None, font="Calibri"):
    run = para.add_run(text)
    run.bold   = bold
    run.italic = italic
    if color: run.font.color.rgb = color
    if size:  run.font.size = Pt(size)
    run.font.name = font
    return run


def add_para(doc, text="", bold=False, italic=False, color=None, size=10,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, font="Calibri"):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if text:
        add_run(p, text, bold=bold, italic=italic, color=color, size=size, font=font)
    return p


def add_heading(doc, text, level=1):
    size   = 13 if level == 1 else 11
    before = 12 if level == 1 else 8
    p = add_para(doc, text, bold=True, color=NAVY, size=size,
                 align=WD_ALIGN_PARAGRAPH.LEFT, space_before=before, space_after=4)
    return p


def add_subheading(doc, text):
    return add_heading(doc, text, level=2)


def add_caption(doc, text):
    return add_para(doc, text, italic=True, color=RGBColor(0x40, 0x40, 0x40),
                    size=9, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=2, space_after=8)


def make_table(doc, headers, data_rows, caption=None, col_widths=None):
    tbl = doc.add_table(rows=1 + len(data_rows), cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header
    hrow = tbl.rows[0]
    set_row_bg(hrow, NAVY)
    for ci, h in enumerate(headers):
        p = hrow.cells[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(9)
        run.font.name = "Calibri"

    # Data
    for ri, row_data in enumerate(data_rows):
        drow = tbl.rows[ri + 1]
        bg = WHITE if ri % 2 == 0 else GRAY_L
        set_row_bg(drow, bg)
        for ci, val in enumerate(row_data):
            p = drow.cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "Calibri"

    if caption:
        add_caption(doc, caption)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    return tbl


def make_table_highlight_last(doc, headers, data_rows, caption=None):
    """Same as make_table but last data row has navy background."""
    tbl = make_table(doc, headers, data_rows[:-1], caption=None)
    # add last row manually
    last = data_rows[-1]
    lrow = tbl.add_row()
    set_row_bg(lrow, NAVY)
    for ci, val in enumerate(last):
        p = lrow.cells[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(str(val))
        run.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(9)
        run.font.name = "Calibri"
    if caption:
        add_caption(doc, caption)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl


def clear_body_after_table1(doc):
    """Remove all content after the 2nd table (metadata table), keeping sectPr."""
    body     = doc.element.body
    children = list(body)
    sect_pr  = body.find(qn("w:sectPr"))
    tbl_count = 0
    cut_idx   = None
    for i, child in enumerate(children):
        if child.tag == qn("w:tbl"):
            tbl_count += 1
            if tbl_count == 2:
                cut_idx = i
                break
    if cut_idx is not None:
        to_remove = [el for el in children[cut_idx + 1:] if el.tag != qn("w:sectPr")]
        for el in to_remove:
            body.remove(el)
    if sect_pr is not None and sect_pr not in list(body):
        body.append(sect_pr)


def m(n, d=0):
    """Format number as currency MXN."""
    sign = "-" if n < 0 else ""
    return f"{sign}${abs(n):,.{d}f} MXN"


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    E_price = np.mean(PRICES)

    print("Calculando utilidad esperada anual...")
    E_ut, E_ur = expected_annual_utility()
    print(f"  Temporal: {m(E_ut)}/año")
    print(f"  Riego:    {m(E_ur)}/año")

    cum_ut7 = E_ut * HORIZON
    cum_ur7 = E_ur * HORIZON - INVESTMENT
    print(f"  Acumulada 7 años temporal: {m(cum_ut7)}")
    print(f"  Acumulada 7 años riego:    {m(cum_ur7)}")

    print(f"\nSimulando {N_SIM:,} escenarios...")
    cum_t, cum_r = simulate()
    p_riego = np.mean(cum_r > cum_t)
    print(f"  Media temporal: {m(np.mean(cum_t))}")
    print(f"  Media riego:    {m(np.mean(cum_r))}")
    print(f"  P(riego > temporal): {p_riego*100:.1f}%")

    scenarios = build_scenarios()

    # ── Open template ──────────────────────────────────────────────────────
    print("\nGenerando documento...")
    doc = Document(TEMPLATE)

    # Replace title
    title_para = doc.paragraphs[1]
    title_para.clear()
    run = title_para.add_run(
        "Actividad 6 — Decisión de Inversión en Riego\n"
        "para Productor de Caña de Azúcar en Pánuco"
    )
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Fill metadata table
    t1 = doc.tables[1]
    t1.rows[1].cells[1].paragraphs[0].runs[0].text = "21 de abril de 2026"
    t1.rows[2].cells[1].paragraphs[0].runs[0].text = "Actividad 6 — Decisión de inversión en riego"
    t1.rows[3].cells[1].paragraphs[0].runs[0].text = "Python 3.13 / NumPy / python-docx"
    t1.rows[4].cells[1].paragraphs[0].runs[0].text = "conda env MCD — Python 3.13"
    t1.rows[5].cells[1].paragraphs[0].runs[0].text = "Homelab (ThinkPad T14 Gen 4) — cálculo analítico + simulación"
    t1.rows[6].cells[1].paragraphs[0].runs[0].text = "Datos del caso: rendimientos y precios caña de azúcar, Pánuco, Veracruz"

    # Clear template placeholder content
    clear_body_after_table1(doc)
    add_para(doc, space_before=6, space_after=0)

    # ── 1. Planteamiento del caso ──────────────────────────────────────────
    add_heading(doc, "1. Planteamiento del caso")
    add_para(doc,
        "Un productor de caña de azúcar en el municipio de Pánuco, Veracruz, cultiva 100 hectáreas "
        "bajo condiciones de temporal y enfrenta una caída progresiva en sus rendimientos, pasando "
        "de 90 a 60 toneladas por hectárea por año en los últimos cinco años. Ante la mayor "
        "variabilidad climática, evalúa invertir en un sistema de riego con un costo de "
        "4,000 USD/ha (80,000 MXN/ha, tipo de cambio 20 MXN/USD), lo que representa una "
        "inversión total de $8,000,000 MXN para las 100 hectáreas, desembolsada una sola vez "
        "al inicio del horizonte de análisis de 7 años."
    )
    add_para(doc,
        "El análisis considera tres fuentes de incertidumbre independientes entre sí: "
        "(1) el precio de la tonelada de caña, modelado como una distribución discreta uniforme "
        "sobre seis valores históricos observados; (2) la condición hídrica anual, con cuatro "
        "categorías de afectación (normal/anormal seca, sequía moderada, severa y extrema) y "
        "probabilidades 40%/30%/20%/10%; y (3) la ocurrencia de una tormenta severa con "
        "probabilidad del 5%, que destruye la cosecha completa independientemente de la alternativa."
    )

    # Parameters table
    add_subheading(doc, "Parámetros del modelo")
    make_table(doc,
        ["Parámetro", "Valor"],
        [
            ("Superficie total",                           "100 ha"),
            ("Horizonte de análisis",                      "7 años"),
            ("Inversión sistema de riego",                 "$80,000 MXN/ha  →  $8,000,000 MXN total"),
            ("Costo anual — temporal",                     "$38,000 MXN/ha/año"),
            ("Costo anual — riego (operación + mant.)",    "$55,000 + $8,000 = $63,000 MXN/ha/año"),
            ("Probabilidad tormenta severa",               "5%"),
            ("Precios históricos observados (MXN/ton)",    "701.49 · 757.16 · 755.59 · 900.95 · 829.39 · 897.65"),
            ("Precio esperado E[precio]",                  f"${E_price:,.2f} MXN/ton"),
        ],
        caption="Tabla 1 — Parámetros del modelo de decisión"
    )

    # ── 2. Árbol de decisión ───────────────────────────────────────────────
    add_heading(doc, "2. Árbol de decisión")
    add_para(doc,
        "El árbol de decisión tiene dos alternativas en el nodo raíz: (A) no invertir en riego "
        "(temporal) y (B) invertir en sistema de riego. En cada rama, el primer nodo de azar "
        "corresponde a la ocurrencia de una tormenta severa (P = 5%). Si no hay tormenta "
        "(P = 95%), se ramifica en cuatro nodos de condición hídrica. En la alternativa con "
        "riego, bajo condiciones normales o anormalmente secas existe un nodo adicional de azar "
        "con tres posibles rendimientos (90, 120 y 200 ton/ha con probabilidades 50%/30%/20%)."
    )

    add_subheading(doc, "Rendimientos por condición y alternativa (ton/ha/año)")
    make_table(doc,
        ["Condición hídrica", "P(condición)", "Temporal", "Riego"],
        [
            ("Tormenta severa (cualquier condición)", "5%",  "0",                       "0"),
            ("Normal / anormal seca",                 "40%", "60",                      "50%→90 · 30%→120 · 20%→200"),
            ("Sequía moderada",                       "30%", "50",                      "90"),
            ("Sequía severa",                         "20%", "40",                      "70"),
            ("Sequía extrema",                        "10%", "25",                      "40"),
        ],
        caption="Tabla 2 — Rendimientos por escenario (ton/ha/año). Tormenta aplica sobre las probabilidades anteriores."
    )

    # ── 3. Escenarios y utilidades ─────────────────────────────────────────
    add_heading(doc, "3. Escenarios productivos y utilidad anual")
    add_para(doc,
        f"La utilidad anual se calcula como: Utilidad = (Rendimiento × Precio − Costo/ha) × 100 ha. "
        f"Se utiliza el precio esperado E[precio] = ${E_price:,.2f} MXN/ton para el cálculo analítico. "
        "Las probabilidades combinadas incorporan la independencia entre condición hídrica y tormenta: "
        "P(escenario) = P(tormenta o no) × P(condición hídrica) × P(sub-escenario riego si aplica)."
    )

    scen_rows = []
    for s in scenarios:
        scen_rows.append((
            s["cond"],
            s["sub"],
            f"{s['prob']*100:.1f}%",
            f"{s['yt']} ton/ha",
            m(s["ut"]),
            f"{s['yr']} ton/ha",
            m(s["ur"]),
        ))
    make_table(doc,
        ["Condición", "Sub-cond. riego", "P(escenario)",
         "Rend. Temporal", "Util. Temporal", "Rend. Riego", "Util. Riego"],
        scen_rows,
        caption="Tabla 3 — Escenarios productivos y utilidad anual (precio esperado $807.04 MXN/ton, 100 ha)"
    )

    # ── 4. Utilidad esperada anual ─────────────────────────────────────────
    add_heading(doc, "4. Utilidad esperada anual")
    add_para(doc,
        "La utilidad esperada anual es la suma ponderada de las utilidades de cada escenario "
        "por su probabilidad. La diferencia entre alternativas en el ingreso bruto esperado "
        "es significativa: el riego eleva el rendimiento esperado de 47.0 a 88.7 ton/ha/año "
        "gracias a su efecto estabilizador y al potencial de rendimientos altos en años normales. "
        "Sin embargo, el mayor costo operativo del riego ($63,000 vs $38,000 MXN/ha/año) "
        "reduce la ventaja en utilidad."
    )

    E_yt = P_STORM * 0 + sum(
        DROUGHT[c]["prob"] * (1-P_STORM) * YIELD_TEMPORAL[c] for c in DROUGHT)
    E_yr_norm = sum(s["prob"] * s["yield"] for s in YIELD_RIEGO_NORMAL)
    E_yr = (
        DROUGHT["Normal / anormal seca"]["prob"] * (1-P_STORM) * E_yr_norm +
        DROUGHT["Sequía moderada"]["prob"]        * (1-P_STORM) * YIELD_RIEGO_FIXED["Sequía moderada"] +
        DROUGHT["Sequía severa"]["prob"]          * (1-P_STORM) * YIELD_RIEGO_FIXED["Sequía severa"] +
        DROUGHT["Sequía extrema"]["prob"]         * (1-P_STORM) * YIELD_RIEGO_FIXED["Sequía extrema"]
    )

    make_table_highlight_last(doc,
        ["Concepto", "Sin riego (temporal)", "Con riego"],
        [
            ("Rendimiento esperado (ton/ha/año)", f"{E_yt:.3f}", f"{E_yr:.3f}"),
            ("Precio esperado (MXN/ton)",          f"${E_price:,.2f}", f"${E_price:,.2f}"),
            ("Ingreso bruto esperado (MXN/año)",   m(E_yt*E_price*HECTARES), m(E_yr*E_price*HECTARES)),
            ("Costo operación total (MXN/año)",    m(-COST_TEMPORAL*HECTARES), m(-COST_RIEGO*HECTARES)),
            ("Utilidad esperada anual (MXN/año)",  m(E_ut), m(E_ur)),
        ],
        caption="Tabla 4 — Descomposición de la utilidad esperada anual"
    )

    # ── 5. Utilidad acumulada 7 años ───────────────────────────────────────
    add_heading(doc, "5. Utilidad acumulada esperada — horizonte de 7 años")
    add_para(doc,
        f"La utilidad acumulada a lo largo de los 7 años suma las utilidades anuales esperadas "
        f"para cada alternativa. En el caso de la inversión en riego, se descuenta adicionalmente "
        f"la inversión inicial de $8,000,000 MXN, desembolsada en el año 0."
    )
    add_para(doc,
        f"Temporal: {m(E_ut)} × 7 = {m(cum_ut7)}\n"
        f"Riego (operativo): {m(E_ur)} × 7 = {m(E_ur*7)}\n"
        f"Riego (neto): {m(E_ur*7)} − $8,000,000 MXN = {m(cum_ur7)}"
    )

    make_table_highlight_last(doc,
        ["Concepto", "Sin riego (temporal)", "Con riego"],
        [
            ("Utilidad esperada anual (MXN)",        m(E_ut),       m(E_ur)),
            ("Utilidad operativa acumulada (×7)",    m(E_ut*7),     m(E_ur*7)),
            ("Inversión inicial (MXN)",               "$0",          "−$8,000,000 MXN"),
            ("Utilidad neta acumulada 7 años (MXN)", m(cum_ut7),    m(cum_ur7)),
        ],
        caption="Tabla 5 — Utilidad acumulada esperada en horizonte de 7 años"
    )

    # ── 6. Simulación Monte Carlo ──────────────────────────────────────────
    add_heading(doc, "6. Simulación de Monte Carlo — 10,000 escenarios")
    add_para(doc,
        f"Se simularon {N_SIM:,} escenarios independientes de 7 años. En cada año de cada escenario "
        "se sortearon de forma aleatoria e independiente: el precio de la tonelada (distribución "
        "uniforme discreta sobre los 6 precios históricos), la condición hídrica (distribución "
        "multinomial con probabilidades 40%/30%/20%/10%) y la ocurrencia de tormenta severa "
        "(Bernoulli con P = 5%). Para la alternativa con riego en años normales sin tormenta, "
        "se sorteó adicionalmente el sub-escenario productivo (50%→90 / 30%→120 / 20%→200 ton/ha). "
        "La inversión inicial de $8,000,000 MXN se descuenta al total acumulado de la alternativa "
        "con riego en cada escenario simulado."
    )

    mean_t   = np.mean(cum_t)
    mean_r   = np.mean(cum_r)
    med_t    = np.median(cum_t)
    med_r    = np.median(cum_r)
    std_t    = np.std(cum_t)
    std_r    = np.std(cum_r)
    p5_t     = np.percentile(cum_t,  5)
    p5_r     = np.percentile(cum_r,  5)
    p95_t    = np.percentile(cum_t, 95)
    p95_r    = np.percentile(cum_r, 95)

    make_table(doc,
        ["Métrica — utilidad acumulada 7 años", "Sin riego (temporal)", "Con riego"],
        [
            ("Media (MXN)",           m(mean_t), m(mean_r)),
            ("Mediana (MXN)",         m(med_t),  m(med_r)),
            ("Desviación estándar",   m(std_t),  m(std_r)),
            ("Percentil 5% (MXN)",    m(p5_t),   m(p5_r)),
            ("Percentil 95% (MXN)",   m(p95_t),  m(p95_r)),
            (f"P(riego > temporal)",  f"{(1-p_riego)*100:.1f}% de escenarios favorables al temporal",
                                      f"{p_riego*100:.1f}% de escenarios favorables al riego"),
        ],
        caption="Tabla 6 — Estadísticas de la simulación de Monte Carlo (10,000 escenarios × 7 años)"
    )

    # ── 7. Comparación de criterios ────────────────────────────────────────
    add_heading(doc, "7. Comparación de criterios de decisión")
    add_para(doc,
        "Se evalúan dos criterios clásicos de decisión bajo incertidumbre:"
    )
    add_para(doc,
        "Criterio 1 — Mayor utilidad esperada: se elige la alternativa con mayor utilidad "
        "esperada acumulada en el horizonte de 7 años (resultado analítico)."
    )
    add_para(doc,
        "Criterio 2 — Mayoría de escenarios favorables: se elige la alternativa que resulta "
        "más rentable en más del 50% de los 10,000 escenarios simulados."
    )

    winner_ev  = "Temporal" if cum_ut7 > cum_ur7 else "Riego"
    winner_sim = "Temporal" if p_riego < 0.50 else "Riego"
    winner_med = "Temporal" if mean_t > mean_r else "Riego"

    make_table(doc,
        ["Criterio", "Sin riego (temporal)", "Con riego", "Decisión"],
        [
            ("Mayor utilidad esperada (analítica)",
             m(cum_ut7), m(cum_ur7), winner_ev),
            ("Mayoría de escenarios favorables (simulación)",
             f"{(1-p_riego)*100:.1f}%", f"{p_riego*100:.1f}%", winner_sim),
            ("Utilidad media simulada",
             m(mean_t), m(mean_r), winner_med),
        ],
        caption="Tabla 7 — Comparación de criterios de decisión"
    )

    # ── 8. Recomendación ──────────────────────────────────────────────────
    add_heading(doc, "8. Recomendación y conclusión")

    if cum_ur7 > cum_ut7 and p_riego > 0.50:
        recom = "invertir en el sistema de riego"
        justif = (
            f"Ambos criterios coinciden en recomendar la inversión. La utilidad neta acumulada "
            f"con riego ({m(cum_ur7)}) supera a la alternativa temporal ({m(cum_ut7)}) en el "
            f"horizonte de 7 años. La simulación confirma que en el {p_riego*100:.1f}% de los "
            "escenarios el riego es más rentable."
        )
    else:
        recom = "no invertir en el sistema de riego en el horizonte analizado de 7 años"
        justif = (
            f"Ambos criterios coinciden en no recomendar la inversión. La utilidad neta acumulada "
            f"con riego ({m(cum_ur7)}) es menor que la alternativa temporal ({m(cum_ut7)}). "
            f"La inversión inicial de $8,000,000 MXN no se recupera en 7 años bajo el precio "
            f"esperado de ${E_price:,.2f} MXN/ton. La simulación confirma que solo en el "
            f"{p_riego*100:.1f}% de los escenarios el riego resulta más rentable, lo que "
            "evidencia que la decisión de no invertir es robusta bajo incertidumbre."
        )

    add_para(doc,
        f"Con base en el análisis de árbol de decisión y la simulación de Monte Carlo, "
        f"se recomienda al productor {recom}."
    )
    add_para(doc, justif)
    add_para(doc,
        "Es relevante destacar que el sistema de riego presenta ventajas operativas importantes: "
        f"eleva el rendimiento esperado de {E_yt:.1f} a {E_yr:.1f} ton/ha/año y reduce la "
        "exposición a pérdidas severas en años de sequía moderada y severa. Sin embargo, "
        "el costo operativo adicional de $25,000 MXN/ha/año (riego vs temporal) y la magnitud "
        "de la inversión inicial hacen que, en un horizonte de 7 años, la alternativa de temporal "
        "sea financieramente superior en valor esperado. El productor debería reconsiderar la "
        "inversión si se presentan condiciones de financiamiento favorables (créditos subsidiados), "
        "si el horizonte de análisis se extiende más allá de los 7 años de vida útil del sistema, "
        "o si su aversión al riesgo de pérdidas en años de sequía extrema es determinante."
    )

    # Save
    doc.save(OUTPUT)
    print(f"\nGuardado: {OUTPUT}")
