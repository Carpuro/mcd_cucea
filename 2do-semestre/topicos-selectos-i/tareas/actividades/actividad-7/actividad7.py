"""
Actividad 7 — Tópicos Selectos de Grandes Bases de Datos
Condiciones de viabilidad para la inversión en riego — perspectiva del vendedor
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
OUTPUT   = "/home/carpuro/Documents/mcd/mcd_cucea/2do-semestre/topicos-selectos-i/tareas/actividades/actividad-7/Actividad7_TopicosSelectos_CarlosPulidoRosas.docx"

NAVY   = RGBColor(0x1F, 0x49, 0x7D)
AMBER  = RGBColor(0xD4, 0x8C, 0x00)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L = RGBColor(0xF2, 0xF2, 0xF2)
GREEN  = RGBColor(0x1F, 0x7A, 0x3C)
RED    = RGBColor(0x9B, 0x1C, 0x1C)
BLACK  = RGBColor(0x00, 0x00, 0x00)

# ─────────────────────────────────────────────
# PARAMETERS  (identical to Actividad 6)
# ─────────────────────────────────────────────
HECTARES      = 100
HORIZON       = 7
INVESTMENT    = 8_000_000          # MXN — full price
DISCOUNT      = 0.30
INVESTMENT_D  = INVESTMENT * (1 - DISCOUNT)   # 5_600_000

COST_TEMPORAL = 38_000             # MXN/ha/year
COST_RIEGO    = 63_000             # MXN/ha/year

PRICES        = [701.49, 757.16, 755.59, 900.95, 829.39, 897.65]
E_PRICE       = np.mean(PRICES)

P_STORM       = 0.05

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
# ANALYSIS FUNCTIONS
# ─────────────────────────────────────────────
def expected_yield():
    """Expected yield (ton/ha/year) for each alternative."""
    E_yt = sum(DROUGHT[c]["prob"] * (1 - P_STORM) * YIELD_TEMPORAL[c] for c in DROUGHT)
    E_yr_norm = sum(s["prob"] * s["yield"] for s in YIELD_RIEGO_NORMAL)
    E_yr = (
        DROUGHT["Normal / anormal seca"]["prob"] * (1 - P_STORM) * E_yr_norm
        + DROUGHT["Sequía moderada"]["prob"]      * (1 - P_STORM) * YIELD_RIEGO_FIXED["Sequía moderada"]
        + DROUGHT["Sequía severa"]["prob"]        * (1 - P_STORM) * YIELD_RIEGO_FIXED["Sequía severa"]
        + DROUGHT["Sequía extrema"]["prob"]       * (1 - P_STORM) * YIELD_RIEGO_FIXED["Sequía extrema"]
    )
    return E_yt, E_yr


def annual_utility(price, investment_total=None):
    """
    Annual expected utility for both alternatives at a given price.
    investment_total is ignored here (only affects cumulative).
    Returns (E_ut, E_ur) in MXN/year.
    """
    E_yt, E_yr = expected_yield()
    E_ut = (E_yt * price - COST_TEMPORAL) * HECTARES
    E_ur = (E_yr * price - COST_RIEGO)    * HECTARES
    return E_ut, E_ur


def cumulative_utility(price, investment_total, horizon=HORIZON):
    E_ut, E_ur = annual_utility(price)
    cum_ut = E_ut * horizon
    cum_ur = E_ur * horizon - investment_total
    return cum_ut, cum_ur


def breakeven_price(investment_total, horizon=HORIZON):
    """Price at which cum_ur == cum_ut (analytical)."""
    E_yt, E_yr = expected_yield()
    # (E_yr*p - COST_R)*100*H - inv = (E_yt*p - COST_T)*100*H
    # (E_yr - E_yt)*p*100*H = inv + (COST_R - COST_T)*100*H
    lhs_coef = (E_yr - E_yt) * HECTARES * horizon
    rhs      = investment_total + (COST_RIEGO - COST_TEMPORAL) * HECTARES * horizon
    return rhs / lhs_coef


def breakeven_horizon(price, investment_total):
    """Years at which cum_ur == cum_ut (analytical)."""
    E_ut, E_ur = annual_utility(price)
    diff = E_ur - E_ut
    if diff <= 0:
        return None
    return investment_total / diff


def fira_monthly_payment(principal, annual_rate=0.085, years=HORIZON):
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)


def simulate(investment_total):
    prices        = np.array(PRICES)
    drought_probs = np.array([0.40, 0.30, 0.20, 0.10])
    yield_t       = np.array([60.0, 50.0, 40.0, 25.0])
    yield_r_det   = np.array([121.0, 90.0, 70.0, 40.0])   # E[yr|normal] = 121 ≈ weighted

    cum_t = np.zeros(N_SIM)
    cum_r = np.zeros(N_SIM)

    for _ in range(HORIZON):
        p     = prices[RNG.integers(0, 6, N_SIM)]
        d_idx = RNG.choice(4, N_SIM, p=drought_probs)
        storm = RNG.random(N_SIM) < P_STORM

        yt = np.where(storm, 0.0, yield_t[d_idx])

        yr_base   = np.where(storm, 0.0, yield_r_det[d_idx])
        sub_rng   = RNG.random(N_SIM)
        yr_normal = np.where(sub_rng < 0.50, 90.0,
                    np.where(sub_rng < 0.80, 120.0, 200.0))
        is_norm   = (~storm) & (d_idx == 0)
        yr        = np.where(is_norm, yr_normal, yr_base)

        cum_t += (yt * p - COST_TEMPORAL) * HECTARES
        cum_r += (yr * p - COST_RIEGO)    * HECTARES

    cum_r -= investment_total
    return cum_t, cum_r


# ─────────────────────────────────────────────
# DOCX HELPERS
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
    return add_para(doc, text, bold=True, color=NAVY, size=size,
                    align=WD_ALIGN_PARAGRAPH.LEFT, space_before=before, space_after=4)


def add_subheading(doc, text):
    return add_heading(doc, text, level=2)


def add_caption(doc, text):
    return add_para(doc, text, italic=True, color=RGBColor(0x40, 0x40, 0x40),
                    size=9, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=2, space_after=8)


def make_table(doc, headers, data_rows, caption=None, highlight_last=False,
               highlight_col=None):
    tbl = doc.add_table(rows=1 + len(data_rows), cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
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

    # Data rows
    for ri, row_data in enumerate(data_rows):
        drow = tbl.rows[ri + 1]
        is_last = (ri == len(data_rows) - 1)
        if highlight_last and is_last:
            set_row_bg(drow, NAVY)
        else:
            bg = WHITE if ri % 2 == 0 else GRAY_L
            set_row_bg(drow, bg)
        for ci, val in enumerate(row_data):
            p = drow.cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "Calibri"
            if highlight_last and is_last:
                run.bold = True
                run.font.color.rgb = WHITE
            elif highlight_col is not None and ci == highlight_col:
                # color positive/negative
                try:
                    numeric = float(str(val).replace("$","").replace(",","")
                                   .replace(" MXN","").replace("✅","").replace("❌","").strip())
                    run.font.color.rgb = GREEN if numeric >= 0 else RED
                    run.bold = True
                except ValueError:
                    pass

    if caption:
        add_caption(doc, caption)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl


def clear_body_after_table1(doc):
    body      = doc.element.body
    children  = list(body)
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
    sect_pr = body.find(qn("w:sectPr"))
    if sect_pr is not None and sect_pr not in list(body):
        body.append(sect_pr)


def m(n, d=0):
    sign = "−" if n < 0 else ""
    return f"{sign}${abs(n):,.{d}f} MXN"


def pct(v):
    return f"{v*100:.1f}%"


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    E_yt, E_yr = expected_yield()

    # Base utilities (Act6 results)
    E_ut_base, E_ur_base = annual_utility(E_PRICE)
    cum_ut_base, cum_ur_base = cumulative_utility(E_PRICE, INVESTMENT)

    # With 30% discount
    E_ut_d, E_ur_d     = annual_utility(E_PRICE)   # same annual — discount only affects cumulative
    cum_ut_d, cum_ur_d = cumulative_utility(E_PRICE, INVESTMENT_D)

    # Break-even price (full & discounted)
    p_be_full = breakeven_price(INVESTMENT)
    p_be_disc = breakeven_price(INVESTMENT_D)

    # Break-even horizon (full & discounted at E_PRICE)
    h_be_full = breakeven_horizon(E_PRICE, INVESTMENT)
    h_be_disc = breakeven_horizon(E_PRICE, INVESTMENT_D)

    # FIRA monthly payment on discounted investment
    fira_payment_monthly = fira_monthly_payment(INVESTMENT_D)
    fira_payment_annual  = fira_payment_monthly * 12
    riego_monthly        = E_ur_base / 12
    gap_monthly          = fira_payment_monthly - riego_monthly

    # Sensitivity: cumulative utility at years 1-15
    horizons = list(range(1, 16))
    cum_t_years = [E_ut_base * h for h in horizons]
    cum_r_years = [E_ur_base * h - INVESTMENT   for h in horizons]
    cum_rd_years= [E_ur_base * h - INVESTMENT_D for h in horizons]

    # Sensitivity: utility at different price levels
    price_range   = np.arange(700, 1001, 25)
    cum_t_prices  = [cumulative_utility(p, INVESTMENT)[0]   for p in price_range]
    cum_r_prices  = [cumulative_utility(p, INVESTMENT)[1]   for p in price_range]
    cum_rd_prices = [cumulative_utility(p, INVESTMENT_D)[1] for p in price_range]

    # Monte Carlo — full & discounted
    print("Simulando escenario base...")
    cum_t_mc, cum_r_mc = simulate(INVESTMENT)
    p_riego_full = np.mean(cum_r_mc > cum_t_mc)

    print("Simulando escenario con descuento 30%...")
    RNG = np.random.default_rng(42)   # reset seed for fair comparison
    cum_t_mc2, cum_r_mc2 = simulate(INVESTMENT_D)
    p_riego_disc = np.mean(cum_r_mc2 > cum_t_mc2)

    print(f"\n=== RESULTADOS ===")
    print(f"Utilidad anual esperada temporal:     {m(E_ut_base)}/año")
    print(f"Utilidad anual esperada riego:        {m(E_ur_base)}/año")
    print(f"Acumulada 7 años temporal:            {m(cum_ut_base)}")
    print(f"Acumulada 7 años riego (sin desc.):   {m(cum_ur_base)}")
    print(f"Acumulada 7 años riego (30% desc.):   {m(cum_ur_d)}")
    print(f"Precio indiferencia sin desc.:        ${p_be_full:,.2f} MXN/ton")
    print(f"Precio indiferencia con desc.:        ${p_be_disc:,.2f} MXN/ton")
    print(f"Horizonte recuperación sin desc.:     {h_be_full:.1f} años")
    print(f"Horizonte recuperación con desc.:     {h_be_disc:.1f} años")
    print(f"Pago FIRA mensual (30% desc.):        {m(fira_payment_monthly)}/mes")
    print(f"Riego genera mensualmente:            {m(riego_monthly)}/mes")
    print(f"Brecha mensual del productor:         {m(gap_monthly)}/mes")
    print(f"P(riego > temporal) sin desc.:        {pct(p_riego_full)}")
    print(f"P(riego > temporal) con 30% desc.:    {pct(p_riego_disc)}")

    # ── Open template ──────────────────────────────────────────────────────
    print("\nGenerando documento...")
    doc = Document(TEMPLATE)

    # Subject name in header
    doc.tables[0].rows[0].cells[1].paragraphs[3].runs[0].text = \
        "Materia: Tópicos Selectos de Grandes Bases de Datos"

    # Title
    title_para = doc.paragraphs[1]
    title_para.clear()
    run = title_para.add_run(
        "Actividad 7 — Condiciones de Viabilidad para la Inversión en Riego\n"
        "Productor de Caña de Azúcar en Pánuco, Veracruz"
    )
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata table
    t1 = doc.tables[1]
    t1.rows[1].cells[1].paragraphs[0].runs[0].text = "28 de abril de 2026"
    t1.rows[2].cells[1].paragraphs[0].runs[0].text = "Actividad 7 — Condiciones de viabilidad del sistema de riego"
    t1.rows[3].cells[1].paragraphs[0].runs[0].text = "Python 3.13 / NumPy / python-docx"
    t1.rows[4].cells[1].paragraphs[0].runs[0].text = "conda env MCD — Python 3.13"
    t1.rows[5].cells[1].paragraphs[0].runs[0].text = "Homelab (ThinkPad T14 Gen 4) — análisis de sensibilidad + simulación"
    t1.rows[6].cells[1].paragraphs[0].runs[0].text = "Datos del caso: rendimientos y precios caña de azúcar, Pánuco, Veracruz"

    clear_body_after_table1(doc)
    add_para(doc, space_before=6, space_after=0)

    # ══════════════════════════════════════════════════════════════════════
    # 1. EL PROBLEMA ACTUAL — LA PÉRDIDA QUE YA EXISTE
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "1. El problema actual — la pérdida que ya existe")
    add_para(doc,
        "Antes de evaluar si conviene invertir, es necesario entender el punto de partida: "
        "el productor ya está perdiendo dinero. En los últimos cinco años, el rendimiento cayó "
        "de 90 a 60 ton/ha/año — una reducción del 33% atribuida al aumento en la frecuencia "
        "e intensidad de sequías. Bajo las condiciones actuales de temporal, el análisis "
        "probabilístico muestra que la operación genera una utilidad anual esperada negativa."
    )

    make_table(doc,
        ["Indicador", "Situación actual (temporal)"],
        [
            ("Rendimiento histórico (hace 5 años)",     "90 ton/ha/año"),
            ("Rendimiento actual",                       "60 ton/ha/año"),
            ("Caída en rendimiento",                     "−30 ton/ha/año  (−33%)"),
            ("Rendimiento esperado probabilístico",      f"{E_yt:.1f} ton/ha/año"),
            ("Precio esperado E[precio]",                f"${E_PRICE:,.2f} MXN/ton"),
            ("Ingreso bruto esperado (100 ha/año)",      m(E_yt * E_PRICE * HECTARES)),
            ("Costo operativo anual (100 ha)",           m(-COST_TEMPORAL * HECTARES)),
            ("Utilidad anual esperada",                  m(E_ut_base)),
            ("Utilidad acumulada esperada en 7 años",    m(cum_ut_base)),
        ],
        caption="Tabla 1 — Diagnóstico financiero del productor bajo temporal (precio esperado $807.04 MXN/ton)"
    )

    add_para(doc,
        f"El rendimiento esperado de {E_yt:.1f} ton/ha/año incorpora la probabilidad del 5% de "
        f"una tormenta severa que destruye la cosecha completa, y la distribución de condiciones "
        f"hídricas: 40% normal, 30% sequía moderada, 20% sequía severa y 10% sequía extrema. "
        f"El resultado es una utilidad anual esperada de {m(E_ut_base)}, es decir, el productor "
        f"opera prácticamente en el umbral de pérdida. En un horizonte de 7 años, la acumulación "
        f"de estas pérdidas alcanza {m(cum_ut_base)} — sin considerar el deterioro adicional "
        f"del suelo ni el impacto de sequías más frecuentes por cambio climático."
    )

    add_subheading(doc, "Proyección año a año sin riego")
    year_rows = []
    acum = 0
    for yr in range(1, HORIZON + 1):
        acum += E_ut_base
        year_rows.append((
            f"Año {yr}",
            m(E_ut_base),
            m(acum),
            "❌ Pérdida" if acum < 0 else "✅ Ganancia",
        ))
    make_table(doc,
        ["Año", "Utilidad anual", "Utilidad acumulada", "Estado"],
        year_rows,
        caption="Tabla 2 — Proyección anual de utilidad bajo temporal (precio esperado constante $807.04 MXN/ton)"
    )

    add_para(doc,
        "La Tabla 2 evidencia que, bajo el esquema actual de temporal, el productor no alcanza "
        "rentabilidad positiva acumulada en ningún año del horizonte de análisis. Continuar "
        "operando sin intervención no es una alternativa neutral — es una pérdida progresiva."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 2. RESULTADO BASE CON RIEGO (sin descuento) — contexto
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "2. Resultado base con riego — inversión a precio de lista")
    add_para(doc,
        f"El sistema de riego tiene un costo de $80,000 MXN/ha (4,000 USD × $20 MXN/USD), "
        f"equivalente a {m(INVESTMENT)} para las 100 ha. Con este costo de inversión y un "
        f"precio de la caña de ${E_PRICE:,.2f} MXN/ton, el análisis de la Actividad 6 "
        f"determinó que la inversión no se recupera en el horizonte de 7 años."
    )

    make_table(doc,
        ["Concepto", "Temporal", "Riego (precio lista)", "Diferencia"],
        [
            ("Rendimiento esperado (ton/ha/año)",    f"{E_yt:.1f}", f"{E_yr:.1f}",
             f"+{E_yr - E_yt:.1f} ton/ha/año"),
            ("Costo operativo anual (100 ha)",        m(-COST_TEMPORAL * HECTARES),
             m(-COST_RIEGO * HECTARES), m(-(COST_RIEGO - COST_TEMPORAL) * HECTARES)),
            ("Utilidad anual esperada",               m(E_ut_base), m(E_ur_base),
             m(E_ur_base - E_ut_base)),
            ("Inversión inicial",                     "$0", m(-INVESTMENT), m(-INVESTMENT)),
            ("Utilidad neta acumulada 7 años",        m(cum_ut_base), m(cum_ur_base),
             m(cum_ur_base - cum_ut_base)),
        ],
        caption="Tabla 3 — Comparación base: temporal vs riego a precio de lista ($8,000,000 MXN)"
    )

    add_para(doc,
        f"Aunque el riego genera {m(E_ur_base)}/año en operación — frente a {m(E_ut_base)}/año "
        f"del temporal — la inversión inicial de {m(INVESTMENT)} consume la ventaja operativa "
        f"y deja una utilidad neta acumulada de {m(cum_ur_base)} al cabo de 7 años. "
        f"La inversión necesita {h_be_full:.1f} años para recuperarse al precio esperado actual. "
        f"Esta es la condición de partida que justifica analizar los escenarios de viabilidad."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 3. CONDICIÓN 1 — DESCUENTO COMERCIAL DEL 30%
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "3. Condición 1 — Descuento comercial del 30%")
    add_para(doc,
        f"Una reducción del {DISCOUNT*100:.0f}% sobre el precio de lista lleva la inversión "
        f"de {m(INVESTMENT)} a {m(INVESTMENT_D)}, un ahorro inmediato de "
        f"{m(INVESTMENT - INVESTMENT_D)}. Este ajuste cambia completamente el resultado "
        f"del análisis: la utilidad neta acumulada en 7 años pasa de negativa a positiva, "
        f"y el punto de recuperación cae dentro del horizonte de análisis."
    )

    make_table(doc,
        ["Concepto", "Sin descuento", "Con 30% descuento"],
        [
            ("Inversión inicial",                 m(-INVESTMENT),   m(-INVESTMENT_D)),
            ("Ahorro por descuento",              "$0",             m(INVESTMENT - INVESTMENT_D)),
            ("Utilidad anual esperada (riego)",   m(E_ur_base),     m(E_ur_base)),
            ("Utilidad operativa acumulada (×7)", m(E_ur_base * HORIZON), m(E_ur_base * HORIZON)),
            ("Utilidad neta acumulada 7 años",    m(cum_ur_base),   m(cum_ur_d)),
            ("Punto de recuperación (años)",      f"{h_be_full:.1f} años",
                                                   f"{h_be_disc:.1f} años"),
        ],
        highlight_last=False,
        caption="Tabla 4 — Impacto del descuento del 30% sobre la viabilidad financiera"
    )

    add_para(doc,
        f"Con el descuento del 30%, el punto de recuperación cae a {h_be_disc:.1f} años — "
        f"dentro del horizonte de 7 años — y la utilidad neta acumulada al final del periodo "
        f"es de {m(cum_ur_d)}, frente a {m(cum_ut_base)} del temporal. "
        f"El productor termina el ciclo de vida del sistema con una ganancia neta positiva "
        f"de {m(cum_ur_d - cum_ut_base)} respecto a continuar con temporal."
    )

    # Year-by-year with discount
    add_subheading(doc, "Proyección año a año con descuento del 30%")
    yr_rows_d = []
    acum_t = 0
    acum_r = -INVESTMENT_D
    for yr in range(1, HORIZON + 1):
        acum_t += E_ut_base
        acum_r += E_ur_base
        gap     = acum_r - acum_t
        yr_rows_d.append((
            f"Año {yr}",
            m(acum_t),
            m(acum_r),
            m(gap),
            "✅ Riego gana" if gap > 0 else "❌ Temporal gana",
        ))
    make_table(doc,
        ["Año", "Acum. Temporal", "Acum. Riego (−30%)", "Diferencia", "Ventaja"],
        yr_rows_d,
        caption="Tabla 5 — Utilidad acumulada año a año: temporal vs riego con descuento 30%"
    )

    # ══════════════════════════════════════════════════════════════════════
    # 4. CONDICIÓN 2 — PRECIO DE INDIFERENCIA
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "4. Condición 2 — Precio de indiferencia")
    add_para(doc,
        "El precio de indiferencia es el precio mínimo de la caña que hace que la utilidad "
        "neta acumulada del riego iguale a la del temporal en exactamente 7 años. Por debajo "
        "de ese precio, el temporal es preferible; por encima, el riego es más rentable. "
        "Se calcula analíticamente despejando el precio en la ecuación de igualdad de "
        "utilidades acumuladas."
    )

    make_table(doc,
        ["Escenario de inversión", "Precio de indiferencia (7 años)",
         "Precio esperado actual", "¿Viable al precio actual?"],
        [
            ("Precio de lista ($8,000,000 MXN)",
             f"${p_be_full:,.2f} MXN/ton",
             f"${E_PRICE:,.2f} MXN/ton",
             "❌ No — faltan $"f"{p_be_full - E_PRICE:,.2f}"),
            ("Con descuento 30% ($5,600,000 MXN)",
             f"${p_be_disc:,.2f} MXN/ton",
             f"${E_PRICE:,.2f} MXN/ton",
             "✅ Sí — excede por $"f"{E_PRICE - p_be_disc:,.2f}"),
        ],
        caption="Tabla 6 — Precio de indiferencia por escenario de inversión (horizonte 7 años)"
    )

    # Sensitivity table: price vs cumulative utility
    add_subheading(doc, "Sensibilidad: precio vs utilidad neta acumulada a 7 años")
    price_sens_rows = []
    for i, p in enumerate(price_range):
        ut = cum_t_prices[i]
        ur = cum_r_prices[i]
        ur_d = cum_rd_prices[i]
        price_sens_rows.append((
            f"${p:,.0f}",
            m(ut),
            m(ur),
            "✅" if ur > ut else "❌",
            m(ur_d),
            "✅" if ur_d > ut else "❌",
        ))
    make_table(doc,
        ["Precio (MXN/ton)", "Temporal (7 años)", "Riego precio lista", "¿Viable?",
         "Riego −30%", "¿Viable?"],
        price_sens_rows,
        caption="Tabla 7 — Sensibilidad de la utilidad acumulada a 7 años según el precio de la caña"
    )

    add_para(doc,
        f"La Tabla 7 muestra que, al precio de lista, el riego únicamente supera al temporal "
        f"cuando el precio de la caña se ubica por encima de ${p_be_full:,.2f} MXN/ton — "
        f"nivel que se ha alcanzado históricamente (se observaron $900.95 y $897.65 MXN/ton "
        f"en el histórico), aunque no es garantizable como promedio sostenido. "
        f"Con el descuento del 30%, el umbral cae a ${p_be_disc:,.2f} MXN/ton, por debajo "
        f"del precio esperado actual de ${E_PRICE:,.2f} MXN/ton, lo que hace viable la "
        f"inversión incluso en condiciones conservadoras de precio."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 5. CONDICIÓN 3 — HORIZONTE DE RECUPERACIÓN
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "5. Condición 3 — Horizonte de recuperación")
    add_para(doc,
        f"Si la vida útil del sistema se extiende más allá de los 7 años del horizonte base, "
        f"la inversión a precio de lista también se vuelve viable. A precio esperado "
        f"de ${E_PRICE:,.2f} MXN/ton, el punto de recuperación sin descuento es de "
        f"{h_be_full:.1f} años. Sistemas de riego por goteo o aspersión bien mantenidos "
        f"pueden operar 15 a 20 años, lo que hace que este escenario sea realista."
    )

    # Horizon sensitivity table (years 1-15)
    horizon_rows = []
    for i, h in enumerate(horizons):
        ut = cum_t_years[i]
        ur = cum_r_years[i]
        ur_d = cum_rd_years[i]
        horizon_rows.append((
            f"{h} años",
            m(ut),
            m(ur),
            "✅" if ur > ut else "❌",
            m(ur_d),
            "✅" if ur_d > ut else "❌",
        ))
    make_table(doc,
        ["Horizonte", "Temporal acum.", "Riego precio lista", "¿Viable?",
         "Riego −30%", "¿Viable?"],
        horizon_rows,
        caption="Tabla 8 — Sensibilidad al horizonte de análisis (precio esperado $807.04 MXN/ton)"
    )

    add_para(doc,
        f"La Tabla 8 muestra que el riego a precio de lista supera al temporal a partir del "
        f"año {int(np.ceil(h_be_full))} (punto exacto: {h_be_full:.1f} años). Con el descuento "
        f"del 30%, el cruce ocurre en el año {int(np.ceil(h_be_disc))} ({h_be_disc:.1f} años). "
        f"En ambos casos, extender el horizonte de análisis transforma una decisión negativa "
        f"en una inversión claramente rentable a largo plazo."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 6. CONDICIÓN 4 — FINANCIAMIENTO FIRA
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "6. Condición 4 — Financiamiento FIRA a tasa preferencial")
    add_para(doc,
        "FIRA (Fideicomisos Instituidos en Relación con la Agricultura) opera el programa "
        "FONAGUA, cuyo objetivo es financiar inversiones en infraestructura hidroagrícola. "
        "A través del Fondo 'Cosechando Soberanía', FIRA ofrece créditos a tasa preferencial "
        "de hasta 8.5% anual para productores de caña en estados productores. "
        "Combinado con el descuento comercial del 30%, el financiamiento elimina la barrera "
        "del desembolso inicial y convierte la inversión en un flujo mensual manejable."
    )

    make_table(doc,
        ["Parámetro FIRA", "Valor"],
        [
            ("Principal financiado (inversión con 30% desc.)", m(INVESTMENT_D)),
            ("Tasa anual preferencial (Cosechando Soberanía)", "8.5% anual"),
            ("Plazo",                                           f"{HORIZON} años ({HORIZON*12} meses)"),
            ("Pago mensual (annuity formula)",                  m(fira_payment_monthly) + "/mes"),
            ("Pago anual equivalente",                          m(fira_payment_annual) + "/año"),
            ("Riego genera mensualmente (utilidad operativa)",  m(riego_monthly) + "/mes"),
            ("Brecha mensual a cubrir por el productor",        m(gap_monthly) + "/mes"),
            ("Brecha anual a cubrir por el productor",          m(gap_monthly * 12) + "/año"),
        ],
        caption="Tabla 9 — Estructura del financiamiento FIRA con descuento 30% (inversión $5,600,000 MXN a 8.5%)"
    )

    add_para(doc,
        f"Con financiamiento FIRA, el productor no desembolsa los {m(INVESTMENT_D)} de un "
        f"solo golpe. En cambio, paga {m(fira_payment_monthly)}/mes durante 7 años. "
        f"El sistema de riego genera en operación {m(riego_monthly)}/mes, por lo que "
        f"la brecha real que el productor debe cubrir de su bolsillo es de apenas "
        f"{m(gap_monthly)}/mes — equivalente a {m(gap_monthly * 12)}/año. "
        f"Esta cifra es significativamente menor al costo de contratar jornaleros adicionales "
        f"o al costo de pérdidas por una sola temporada de sequía severa "
        f"({m(abs((YIELD_TEMPORAL['Sequía severa'] * E_PRICE - COST_TEMPORAL) * HECTARES))}/año "
        f"bajo sequía severa vs. {m((YIELD_RIEGO_FIXED['Sequía severa'] * E_PRICE - COST_RIEGO) * HECTARES)}/año "
        f"con riego)."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 7. SIMULACIÓN MONTE CARLO — CON Y SIN DESCUENTO
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "7. Simulación de Monte Carlo — efecto del descuento")
    add_para(doc,
        f"Se corrieron dos simulaciones de {N_SIM:,} escenarios × 7 años con la misma semilla "
        f"aleatoria: una con la inversión a precio de lista ({m(INVESTMENT)}) y otra con el "
        f"descuento del 30% ({m(INVESTMENT_D)}). En ambos casos se sortearon de forma "
        f"independiente el precio, la condición hídrica y la ocurrencia de tormenta "
        f"en cada año de cada escenario."
    )

    mean_t1  = np.mean(cum_t_mc)
    mean_r1  = np.mean(cum_r_mc)
    mean_r2  = np.mean(cum_r_mc2)
    p5_t     = np.percentile(cum_t_mc, 5)
    p5_r1    = np.percentile(cum_r_mc, 5)
    p5_r2    = np.percentile(cum_r_mc2, 5)
    p95_t    = np.percentile(cum_t_mc, 95)
    p95_r1   = np.percentile(cum_r_mc, 95)
    p95_r2   = np.percentile(cum_r_mc2, 95)

    make_table(doc,
        ["Métrica (7 años)", "Temporal", "Riego precio lista", "Riego −30% desc."],
        [
            ("Media (MXN)",             m(mean_t1),  m(mean_r1),  m(mean_r2)),
            ("Percentil 5% (MXN)",      m(p5_t),     m(p5_r1),    m(p5_r2)),
            ("Percentil 95% (MXN)",     m(p95_t),    m(p95_r1),   m(p95_r2)),
            ("% escenarios donde riego > temporal",
             "—",
             pct(p_riego_full),
             pct(p_riego_disc)),
        ],
        caption=(
            "Tabla 10 — Estadísticas Monte Carlo: 10,000 escenarios × 7 años. "
            "Inversión completa vs inversión con descuento 30%"
        )
    )

    add_para(doc,
        f"Sin descuento, el riego supera al temporal en el {pct(p_riego_full)} de los "
        f"escenarios simulados. Con el descuento del 30%, esa proporción sube a "
        f"{pct(p_riego_disc)} — una mejora significativa, aunque la mayoría de escenarios "
        f"individuales aún favorece al temporal. Esta aparente contradicción con el resultado "
        f"analítico (+{m(cum_ur_d)} para riego con descuento) se explica por la asimetría "
        f"de la distribución del riego: en los escenarios donde el riego gana, lo hace con "
        f"márgenes muy amplios (años con 120 o 200 ton/ha y precios altos), lo que eleva "
        f"fuertemente la media ({m(mean_r2)}) por encima de la mediana. "
        f"El valor esperado es el criterio correcto para decisiones repetibles — y bajo ese "
        f"criterio, el riego con descuento es la alternativa superior."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 8. RESUMEN DE CONDICIONES DE VIABILIDAD
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "8. Resumen de condiciones de viabilidad")
    add_para(doc,
        "La Tabla 11 consolida las cuatro condiciones analizadas. La inversión es viable "
        "cuando se cumple al menos una de ellas; la combinación de varias condiciones "
        "amplía significativamente el margen de seguridad financiero."
    )

    make_table(doc,
        ["Condición", "Umbral requerido", "Situación actual", "Resultado", "Acción del vendedor"],
        [
            ("Descuento comercial",
             "≥ 30% sobre precio lista",
             "Oferta disponible",
             "✅ Viable — util. neta 7 años: " + m(cum_ur_d),
             "Aplicar descuento 30%"),
            ("Precio de la caña",
             f"≥ ${p_be_disc:,.0f} MXN/ton (con −30%)",
             f"E[precio] = ${E_PRICE:,.2f}",
             "✅ Precio actual supera el umbral",
             "Mostrar histórico de precios"),
            ("Horizonte de análisis",
             f"≥ {int(np.ceil(h_be_disc))} años (con −30%)",
             "Garantía sistema: 7 años",
             "✅ Recuperación en " + f"{h_be_disc:.1f} años",
             "Extender garantía si es posible"),
            ("Financiamiento FIRA",
             "Crédito 8.5% — 7 años",
             "Disponible via FONAGUA",
             "✅ Brecha: solo " + m(gap_monthly) + "/mes",
             "Gestionar trámite FIRA"),
        ],
        caption="Tabla 11 — Condiciones suficientes para viabilidad de la inversión en riego"
    )

    # ══════════════════════════════════════════════════════════════════════
    # 9. RECOMENDACIÓN DEL VENDEDOR
    # ══════════════════════════════════════════════════════════════════════
    add_heading(doc, "9. Recomendación del vendedor")
    add_para(doc,
        "Con base en el análisis de cuatro condiciones de viabilidad, la recomendación "
        "es clara: la inversión en el sistema de riego es financieramente justificable "
        "cuando se combina un descuento del 30% con financiamiento FIRA a tasa preferencial. "
        "Bajo esta estructura, el productor:"
    )
    add_para(doc,
        f"(1) No desembolsa {m(INVESTMENT_D)} de contado — financia a través de FIRA "
        f"a una cuota de {m(fira_payment_monthly)}/mes.",
        size=10
    )
    add_para(doc,
        f"(2) El sistema genera {m(riego_monthly)}/mes en operación, cubriendo el "
        f"{(riego_monthly/fira_payment_monthly)*100:.0f}% del pago mensual de forma automática. "
        f"La brecha real es de {m(gap_monthly)}/mes.",
        size=10
    )
    add_para(doc,
        f"(3) Al término de los 7 años, recupera la inversión completa y acumula "
        f"{m(cum_ur_d)} en utilidad neta — {m(cum_ur_d - cum_ut_base)} por encima "
        f"de lo que generaría continuando con temporal.",
        size=10
    )
    add_para(doc,
        f"(4) El valor esperado analítico con descuento es {m(cum_ur_d)} — "
        f"{m(cum_ur_d - cum_ut_base)} por encima del temporal. La simulación confirma "
        f"una media de {m(mean_r2)}. Aunque el riego supera al temporal en el "
        f"{pct(p_riego_disc)} de los escenarios individuales (frente a {pct(p_riego_full)} "
        f"sin descuento), su distribución asimétrica — con escenarios de hasta 200 ton/ha — "
        f"produce una media significativamente superior. El criterio de valor esperado, "
        f"el más robusto para decisiones bajo incertidumbre, favorece al riego.",
        size=10
    )
    add_para(doc,
        "El argumento final al productor: continuar con temporal garantiza pérdidas acumuladas "
        f"de {m(abs(cum_ut_base))} en 7 años. El sistema de riego con descuento y "
        "financiamiento transforma esa trayectoria en una utilidad positiva, reduce la "
        "exposición a sequías severas y sienta las bases para escalar la operación. "
        "La pregunta no es si puede permitirse el sistema — es cuánto más puede "
        "permitirse seguir sin él."
    )

    # Save
    doc.save(OUTPUT)
    print(f"\nGuardado: {OUTPUT}")
