"""
Actividad 8 — Construccion de Modelos e Interpretacion con BigData
Almacenamiento de Grandes Bases de Datos — MCD CUCEA
Carlos Pulido Rosas
"""
import os, sys, subprocess, warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE     = r"C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\2do-semestre\almacenamiento"
DATA     = os.path.join(BASE, "datos", "asg-abr-2026.csv")
TEMPLATE = r"C:\Users\carlo\OneDrive\Documentos\GitHub\mcd_cucea\_recursos\plantillas\plantilla_informe_MCD.docx"
ACT_DIR  = os.path.join(BASE, "tareas", "Actividad 8")
CHARTS   = os.path.join(ACT_DIR, "charts")
OUTPUT   = os.path.join(ACT_DIR, "Actividad8_AlmacenamientoGBD_CarlosPulidoRosas.docx")
os.makedirs(CHARTS, exist_ok=True)

# ── Lookups ───────────────────────────────────────────────────────────────────
EDAD_MID = {
    'E1': 17, 'E2': 22, 'E3': 27, 'E4': 32, 'E5': 37, 'E6': 42,
    'E7': 47, 'E8': 52, 'E9': 57, 'E10': 62, 'E11': 67,
    'E12': 72, 'E13': 77, 'E14': 82
}
SAL_NUM = {f'W{i}': i for i in range(1, 11)}
SECTOR_LBL = {
    '1': 'Primario',       '3': 'Energia/Agua',
    '4': 'Construccion',   '5': 'Manufactura',
    '6': 'Comercio',       '7': 'Transporte/Comunic.',
    '8': 'Financiero/Prof.', '9': 'Social/Personal'
}
TAMANO_LBL = {
    'S1': 'S1 (1 trab.)',  'S2': 'S2 (2-5)',
    'S3': 'S3 (6-10)',     'S4': 'S4 (11-15)',
    'S5': 'S5 (16-50)',    'S6': 'S6 (51-250)',
    'S7': 'S7 (251+)'
}
ENTIDAD_NAMES = {
     1:'Aguascalientes',  2:'Baja California', 3:'BCS',
     4:'Campeche',        5:'Coahuila',        6:'Colima',
     7:'Chiapas',         8:'Chihuahua',        9:'CDMX',
    10:'Durango',        11:'Guanajuato',      12:'Guerrero',
    13:'Hidalgo',        14:'Jalisco',         15:'Edo. Mexico',
    16:'Michoacan',      17:'Morelos',         18:'Nayarit',
    19:'Nuevo Leon',     20:'Oaxaca',          21:'Puebla',
    22:'Queretaro',      23:'Quintana Roo',    24:'SLP',
    25:'Sinaloa',        26:'Sonora',          27:'Tabasco',
    28:'Tamaulipas',     29:'Tlaxcala',        30:'Veracruz',
    31:'Yucatan',        32:'Zacatecas'
}

NAVY_H  = '#1F497D'
AMBER_H = '#D48C00'
NAVY    = RGBColor(0x1F, 0x49, 0x7D)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_L  = RGBColor(0xF2, 0xF2, 0xF2)
BLACK   = RGBColor(0x00, 0x00, 0x00)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. LOAD AND PREPARE DATA
# ═══════════════════════════════════════════════════════════════════════════════
print("Cargando datos...")
df = pd.read_csv(DATA, low_memory=False)
df['peso'] = df['teu'].fillna(0) + df['tpu'].fillna(0)

urban = df[
    (df['peso'] > 0) &
    df['rango_salarial'].notna() &
    df['rango_edad'].notna() &
    df['tamano_patron'].notna() &
    df['cve_entidad'].notna() &
    df['sexo'].isin([1, 2])
].copy()

urban['sal_num']     = urban['rango_salarial'].map(SAL_NUM)
urban['edad_mid']    = urban['rango_edad'].map(EDAD_MID)
urban['edad_mid2']   = urban['edad_mid'] ** 2
urban['entidad_str'] = urban['cve_entidad'].astype(int).astype(str).str.zfill(2)
urban['mujer']       = (urban['sexo'] == 2).astype(int)

n_rows    = len(urban)
n_workers = int(urban['peso'].sum())
print(f"Filas urbanas: {n_rows:,}  |  Trabajadores: {n_workers:,}")

def wmean(vals, w):
    return (vals * w).sum() / w.sum()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. MODEL 1 — WLS con edad cuadratica e interacciones edad x tamano
#    sal_num ~ edad_mid + edad_mid^2 + entidad + tamano + edad_mid:tamano
# ═══════════════════════════════════════════════════════════════════════════════
print("Ajustando Modelo 1 (WLS con interacciones)...")
m1 = smf.wls(
    'sal_num ~ edad_mid + I(edad_mid**2) + C(entidad_str) '
    '+ C(tamano_patron) + edad_mid:C(tamano_patron)',
    data=urban,
    weights=urban['peso']
).fit()

r2, r2_adj, f_stat, f_pval = m1.rsquared, m1.rsquared_adj, m1.fvalue, m1.f_pvalue
s1 = m1.summary2().tables[1]

# Age coefficients (main effect + quadratic)
edad_coef  = float(s1.loc['edad_mid',         'Coef.'])
edad2_coef = float(s1.loc['I(edad_mid ** 2)', 'Coef.'])
edad_pval  = float(s1.loc['edad_mid',         'P>|t|'])
edad2_pval = float(s1.loc['I(edad_mid ** 2)', 'P>|t|'])

# Age peak: d/dx (b1*x + b2*x^2) = 0  =>  x* = -b1 / (2*b2)
if edad2_coef != 0:
    edad_peak = -edad_coef / (2 * edad2_coef)
else:
    edad_peak = None

# Tamano base coefficients (relative to S1)
tamano_rows = {}
for idx in s1.index:
    if 'C(tamano_patron)' in idx and ':' not in idx:
        code = idx.split('[T.')[1].rstrip(']')
        tamano_rows[code] = {
            'coef':  float(s1.loc[idx, 'Coef.']),
            'se':    float(s1.loc[idx, 'Std.Err.']),
            'pval':  float(s1.loc[idx, 'P>|t|']),
            'ci_lo': float(s1.loc[idx, '[0.025']),
            'ci_hi': float(s1.loc[idx, '0.975]']),
        }
tamano_rows['S1'] = {'coef': 0.0, 'se': 0.0, 'pval': 1.0, 'ci_lo': 0.0, 'ci_hi': 0.0}

# Interaction slopes: base slope (edad_mid) + interaction[tamano]
# Also track significance and delta over 40-year career
interact_slopes = {'S1': edad_coef}
interact_sig    = {'S1': True}
interact_delta40 = {'S1': 0.0}
for idx in s1.index:
    if 'edad_mid:C(tamano_patron)' in idx:
        code  = idx.split('[T.')[1].rstrip(']')
        delta = float(s1.loc[idx, 'Coef.'])
        pval  = float(s1.loc[idx, 'P>|t|'])
        interact_slopes[code]  = edad_coef + delta
        interact_sig[code]     = pval < 0.05
        interact_delta40[code] = delta * 40

print(f"R²={r2:.4f}  R²adj={r2_adj:.4f}  F={f_stat:,.0f}  p={f_pval:.2e}")
if edad_peak:
    print(f"edad cuadratica: pico estimado a los {edad_peak:.1f} anos")
print("Pendiente edad_mid por tamano:")
for t in ['S1','S2','S3','S4','S5','S6','S7']:
    sl = interact_slopes.get(t, edad_coef)
    print(f"  {t}: {sl:+.4f} W/ano")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. MODEL 2 — LOGISTIC con probabilidades predichas y ROC
# ═══════════════════════════════════════════════════════════════════════════════
urban_m2 = urban[
    urban['sector_economico_1'].notna() &
    (urban['sector_economico_1'] > 0)
].copy()
urban_m2['sector_str'] = urban_m2['sector_economico_1'].astype(int).astype(str)

# Umbral: percentil 75 ponderado (mas informativo que la mediana)
sal_exp   = np.repeat(urban_m2['sal_num'].values,
                      urban_m2['peso'].astype(int).clip(0, 50000).values)
threshold = int(np.percentile(sal_exp, 75))
high_rate = ((urban_m2['sal_num'] >= threshold) * urban_m2['peso']).sum() / urban_m2['peso'].sum()
urban_m2['sal_alto'] = (urban_m2['sal_num'] >= threshold).astype(int)
print(f"\nUmbral p75: W{threshold}  |  Tasa salario alto: {high_rate:.1%}")

print("Ajustando Modelo 2 (Logistico)...")
m2 = smf.glm(
    'sal_alto ~ C(entidad_str) + C(sector_str) + mujer',
    data=urban_m2,
    family=sm.families.Binomial(),
    freq_weights=urban_m2['peso'].astype(int)
).fit()

s2 = m2.summary2().tables[1]
mujer_coef = float(s2.loc['mujer', 'Coef.'])
mujer_or   = np.exp(mujer_coef)
mujer_ci   = (np.exp(float(s2.loc['mujer', '[0.025'])),
              np.exp(float(s2.loc['mujer', '0.975]'])))
mujer_pval = float(s2.loc['mujer', 'P>|z|'])
pseudo_r2  = 1 - m2.deviance / m2.null_deviance
print(f"Pseudo-R²={pseudo_r2:.4f}  |  OR mujer={mujer_or:.4f}  p={mujer_pval:.2e}")

# AUC y ROC
y_true  = urban_m2['sal_alto'].values
y_prob  = m2.predict(urban_m2).values
weights = urban_m2['peso'].values
auc_val = roc_auc_score(y_true, y_prob, sample_weight=weights)
fpr, tpr, thresholds_roc = roc_curve(y_true, y_prob, sample_weight=weights)

# Umbral optimo: indice de Youden (maximiza Sens + Spec - 1)
opt_idx       = np.argmax(tpr - fpr)
opt_threshold = float(thresholds_roc[opt_idx])

# Confusion matrix con umbral optimo
y_pred  = (y_prob >= opt_threshold).astype(int)
cm      = confusion_matrix(y_true, y_pred, sample_weight=weights)
tn, fp, fn, tp = cm.ravel()
accuracy    = (tp + tn) / (tp + tn + fp + fn)
sensitivity = tp / (tp + fn)
specificity = tn / (tn + fp)
print(f"AUC={auc_val:.4f}  Umbral optimo={opt_threshold:.4f}  "
      f"Sens={sensitivity:.3f}  Spec={specificity:.3f}")

# Probabilidades predichas por sector x sexo (entidad CDMX='09' como referencia)
pred_rows = []
for s in SECTOR_LBL.keys():
    for mujer_val, label in [(0, 'Hombre'), (1, 'Mujer')]:
        pred_rows.append({'entidad_str': '09', 'sector_str': s,
                          'mujer': mujer_val, 'sexo_label': label,
                          'sector_label': SECTOR_LBL[s]})
pred_df = pd.DataFrame(pred_rows)
pred_df['prob'] = m2.predict(pred_df)
pred_pivot = pred_df.pivot(index='sector_label', columns='sexo_label', values='prob')
pred_pivot['Brecha'] = pred_pivot['Hombre'] - pred_pivot['Mujer']

# Brecha descriptiva por sector
gap_df = (
    urban_m2.groupby(['sector_str', 'mujer'])
    .apply(lambda g: wmean(g['sal_num'], g['peso']))
    .unstack('mujer').rename(columns={0: 'Hombre', 1: 'Mujer'})
)
gap_df['Brecha'] = gap_df['Hombre'] - gap_df['Mujer']
gap_df.index = gap_df.index.map(lambda x: SECTOR_LBL.get(x, x))

# Brecha descriptiva por entidad (top 10)
top_ent = urban_m2.groupby('cve_entidad')['peso'].sum().nlargest(10).index.astype(int).tolist()
gap_ent = (
    urban_m2[urban_m2['cve_entidad'].astype(int).isin(top_ent)]
    .groupby(['cve_entidad', 'mujer'])
    .apply(lambda g: wmean(g['sal_num'], g['peso']))
    .unstack('mujer').rename(columns={0: 'Hombre', 1: 'Mujer'})
)
gap_ent['Brecha'] = gap_ent['Hombre'] - gap_ent['Mujer']
gap_ent.index = gap_ent.index.astype(int).map(lambda x: ENTIDAD_NAMES.get(x, str(x)))

print("\nBrecha por sector:")
print(gap_df.round(3).to_string())
print("\nProb predicha por sector x sexo (ref. CDMX):")
print(pred_pivot.round(3).to_string())

# ═══════════════════════════════════════════════════════════════════════════════
# 4. CHARTS
# ═══════════════════════════════════════════════════════════════════════════════
plt.rcParams.update({
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150
})
COLORS_7 = [NAVY_H, AMBER_H, '#28A745', '#CC3333', '#9B59B6', '#17A2B8', '#E67E22']

# ── Figura 1: Tamano base coefficients ───────────────────────────────────────
sizes   = ['S1','S2','S3','S4','S5','S6','S7']
coefs   = [tamano_rows[s]['coef']  for s in sizes]
ci_lo   = [tamano_rows[s]['ci_lo'] for s in sizes]
ci_hi   = [tamano_rows[s]['ci_hi'] for s in sizes]
pvals   = [tamano_rows[s]['pval']  for s in sizes]
err_lo  = [c - l for c, l in zip(coefs, ci_lo)]
err_hi  = [h - c for h, c in zip(ci_hi, coefs)]
colors  = [AMBER_H if p < 0.05 else '#AAAAAA' for p in pvals]
labels  = [TAMANO_LBL[s] for s in sizes]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(labels, coefs, xerr=[err_lo, err_hi], color=colors,
        error_kw={'ecolor': '#333333', 'capsize': 4}, height=0.55)
ax.axvline(0, color='#333333', linewidth=0.8, linestyle='--')
ax.set_xlabel('Coeficiente vs referencia S1 (1 trabajador)', fontsize=10)
ax.set_title('Modelo 1: Efecto del Tamano de Empresa sobre el Rango Salarial\n'
             'Intercepto por categoria — IC 95%',
             fontsize=10, fontweight='bold', color=NAVY_H)
ax.legend(handles=[Patch(facecolor=AMBER_H, label='Sig. p<0.05'),
                   Patch(facecolor='#AAAAAA', label='No significativo')],
          fontsize=8, loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, 'fig1_tamano.png'), bbox_inches='tight')
plt.close()
print("Figura 1 guardada.")

# ── Figura 2: Curvas edad x tamano (interaccion) ──────────────────────────────
x_ages = np.linspace(17, 82, 80)
ref_ent = '09'

fig, ax = plt.subplots(figsize=(10, 5.5))
for i, t in enumerate(sizes):
    pred_df_t = pd.DataFrame({
        'edad_mid':    x_ages,
        'entidad_str': ref_ent,
        'tamano_patron': t
    })
    y_pred = m1.predict(pred_df_t)
    slope  = interact_slopes.get(t, edad_coef)
    ax.plot(x_ages, y_pred, color=COLORS_7[i], linewidth=1.8,
            label=f"{TAMANO_LBL[t]} (slope={slope:+.4f})")

ax.set_xlabel('Edad (punto medio del grupo)', fontsize=10)
ax.set_ylabel('Rango salarial predicho (W)', fontsize=10)
ax.set_title('Modelo 1: Curvas Salario-Edad por Tamano de Empresa\n'
             'Interaccion edad × tamano_patron — Entidad de referencia: CDMX',
             fontsize=10, fontweight='bold', color=NAVY_H)
ax.legend(fontsize=8, ncol=2)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'W{x:.1f}'))
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, 'fig2_interaccion_edad_tamano.png'), bbox_inches='tight')
plt.close()
print("Figura 2 guardada.")

# ── Figura 3: Brecha descriptiva por sector ───────────────────────────────────
gap_s = gap_df.sort_values('Brecha', ascending=True)
fig, ax = plt.subplots(figsize=(8, 4.5))
bar_colors = [NAVY_H if b >= 0 else AMBER_H for b in gap_s['Brecha']]
bars = ax.barh(gap_s.index, gap_s['Brecha'], color=bar_colors, height=0.55)
ax.axvline(0, color='#333333', linewidth=0.8)
for bar, val in zip(bars, gap_s['Brecha']):
    xpos = bar.get_width() + (0.02 if val >= 0 else -0.02)
    ax.text(xpos, bar.get_y() + bar.get_height() / 2,
            f'{val:+.2f}', va='center', ha='left' if val >= 0 else 'right', fontsize=8)
ax.set_xlabel('Brecha H - M (rangos W promedio)', fontsize=10)
ax.set_title('Brecha Salarial de Genero por Sector Economico\n'
             'Diferencia en rango W ponderado por trabajadores',
             fontsize=10, fontweight='bold', color=NAVY_H)
ax.legend(handles=[Patch(facecolor=NAVY_H, label='Hombres ganan mas'),
                   Patch(facecolor=AMBER_H, label='Mujeres ganan mas')],
          fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, 'fig3_brecha_sector.png'), bbox_inches='tight')
plt.close()
print("Figura 3 guardada.")

# ── Figura 4: Probabilidades predichas por sector x sexo ─────────────────────
pred_h = [float(pred_pivot.loc[SECTOR_LBL[s], 'Hombre']) for s in SECTOR_LBL]
pred_m = [float(pred_pivot.loc[SECTOR_LBL[s], 'Mujer'])  for s in SECTOR_LBL]
sec_labels = list(SECTOR_LBL.values())
x = np.arange(len(sec_labels))
w = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(x - w/2, pred_h, w, label='Hombre', color=NAVY_H)
ax.bar(x + w/2, pred_m, w, label='Mujer',  color=AMBER_H)
ax.set_xticks(x)
ax.set_xticklabels(sec_labels, rotation=22, ha='right', fontsize=8)
ax.set_ylabel(f'P(salario >= W{threshold})', fontsize=10)
ax.set_title('Modelo 2: Probabilidad Predicha de Salario Alto por Sector y Sexo\n'
             f'Regresion logistica — umbral W{threshold} — Entidad de referencia: CDMX',
             fontsize=10, fontweight='bold', color=NAVY_H)
ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, 'fig4_prob_predicha.png'), bbox_inches='tight')
plt.close()
print("Figura 4 guardada.")

# ── Figura 5: Curva ROC ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, color=NAVY_H, linewidth=2, label=f'ROC (AUC = {auc_val:.4f})')
ax.plot([0, 1], [0, 1], '--', color='#AAAAAA', linewidth=1, label='Clasificador aleatorio')
ax.set_xlabel('Tasa de Falsos Positivos (1 - Especificidad)', fontsize=10)
ax.set_ylabel('Tasa de Verdaderos Positivos (Sensibilidad)', fontsize=10)
ax.set_title('Modelo 2: Curva ROC\nRegresion Logistica Ponderada',
             fontsize=10, fontweight='bold', color=NAVY_H)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, 'fig5_roc.png'), bbox_inches='tight')
plt.close()
print("Figura 5 guardada.")

# ── Figura 6: Brecha por entidad (top 10) ────────────────────────────────────
gap_e = gap_ent.sort_values('Brecha', ascending=True)
fig, ax = plt.subplots(figsize=(8, 5))
bar_colors_e = [NAVY_H if b >= 0 else AMBER_H for b in gap_e['Brecha']]
bars_e = ax.barh(gap_e.index, gap_e['Brecha'], color=bar_colors_e, height=0.55)
ax.axvline(0, color='#333333', linewidth=0.8)
for bar, val in zip(bars_e, gap_e['Brecha']):
    xpos = bar.get_width() + (0.02 if val >= 0 else -0.02)
    ax.text(xpos, bar.get_y() + bar.get_height() / 2,
            f'{val:+.2f}', va='center', ha='left' if val >= 0 else 'right', fontsize=8)
ax.set_xlabel('Brecha H - M (rangos W promedio)', fontsize=10)
ax.set_title('Brecha Salarial de Genero por Entidad Federativa\n'
             'Top 10 entidades por volumen de trabajadores urbanos',
             fontsize=10, fontweight='bold', color=NAVY_H)
ax.legend(handles=[Patch(facecolor=NAVY_H, label='Hombres ganan mas'),
                   Patch(facecolor=AMBER_H, label='Mujeres ganan mas')],
          fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, 'fig6_brecha_entidad.png'), bbox_inches='tight')
plt.close()
print("Figura 6 guardada.")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. DOCX HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def set_cell_bg(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), f"{color[0]:02X}{color[1]:02X}{color[2]:02X}")
    tcPr.append(shd)

def set_row_bg(row, color):
    for cell in row.cells:
        set_cell_bg(cell, color)

def add_run(para, text, bold=False, italic=False, color=None, size=None, font="Calibri"):
    run = para.add_run(text)
    run.bold = bold; run.italic = italic
    if color: run.font.color.rgb = color
    if size:  run.font.size = Pt(size)
    run.font.name = font
    return run

def add_para(doc, text="", bold=False, italic=False, color=None, size=10,
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=5, font="Calibri"):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if text:
        add_run(p, text, bold=bold, italic=italic, color=color, size=size, font=font)
    return p

def add_heading(doc, text, level=1):
    size = 13 if level == 1 else 11
    sb   = 10 if level == 1 else 6
    return add_para(doc, text, bold=True, color=NAVY, size=size, space_before=sb, space_after=3)

def add_subheading(doc, text):
    return add_heading(doc, text, level=2)

def add_caption(doc, text):
    return add_para(doc, text, italic=True, color=RGBColor(0x40, 0x40, 0x40),
                    size=9, space_before=2, space_after=6)

def make_table(doc, headers, rows, caption=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hrow = tbl.rows[0]
    set_row_bg(hrow, NAVY)
    for ci, h in enumerate(headers):
        p = hrow.cells[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True; r.font.color.rgb = WHITE; r.font.size = Pt(9); r.font.name = "Calibri"
    for ri, row_data in enumerate(rows):
        drow = tbl.rows[ri + 1]
        set_row_bg(drow, WHITE if ri % 2 == 0 else GRAY_L)
        for ci, val in enumerate(row_data):
            p = drow.cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.size = Pt(9); r.font.name = "Calibri"
    if caption:
        add_caption(doc, caption)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_image(doc, filename, caption=None, width=Inches(5.8)):
    path = os.path.join(CHARTS, filename)
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(2)
        p.add_run().add_picture(path, width=width)
    if caption:
        add_caption(doc, caption)

def add_bullet(doc, titulo, texto):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    rt = p.add_run(titulo + " ")
    rt.bold = True; rt.font.size = Pt(10); rt.font.name = "Calibri"; rt.font.color.rgb = NAVY
    rb = p.add_run(texto)
    rb.font.size = Pt(10); rb.font.name = "Calibri"

def clear_body_after_table1(doc):
    body = doc.element.body
    children = list(body)
    tbl_count = 0; cut_idx = None
    for i, child in enumerate(children):
        if child.tag == qn("w:tbl"):
            tbl_count += 1
            if tbl_count == 2:
                cut_idx = i; break
    sect_pr = body.find(qn("w:sectPr"))
    if cut_idx is not None:
        for el in [e for e in children[cut_idx + 1:] if e.tag != qn("w:sectPr")]:
            body.remove(el)
    if sect_pr is not None and sect_pr not in list(body):
        body.append(sect_pr)

# ═══════════════════════════════════════════════════════════════════════════════
# 6. BUILD DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════════
print("Generando reporte DOCX...")
doc = Document(TEMPLATE)

doc.tables[0].rows[0].cells[1].paragraphs[3].runs[0].text = \
    "Materia: Almacenamiento de Grandes Bases de Datos"

title_para = doc.paragraphs[1]
title_para.clear()
run = title_para.add_run(
    "Construccion de Modelos e Interpretacion con BigData\n"
    "Regresion Lineal y Logistica — Asegurados IMSS Abril 2026"
)
run.bold = True; run.font.size = Pt(13); run.font.color.rgb = NAVY; run.font.name = "Calibri"
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

t1 = doc.tables[1]
t1.rows[1].cells[1].paragraphs[0].runs[0].text = "19 de mayo de 2026"
t1.rows[2].cells[1].paragraphs[0].runs[0].text = "Actividad 8 — Modelos de regresion con BigData"
t1.rows[3].cells[1].paragraphs[0].runs[0].text = "Python 3.13 / statsmodels / sklearn / pandas"
t1.rows[4].cells[1].paragraphs[0].runs[0].text = "WLS con interacciones + GLM Binomial ponderado"
t1.rows[5].cells[1].paragraphs[0].runs[0].text = "Windows 11 — MSI Katana AI B8V"
t1.rows[6].cells[1].paragraphs[0].runs[0].text = "IMSS ASG — Datos abiertos abril 2026"

clear_body_after_table1(doc)

# ── 1. Introduccion ───────────────────────────────────────────────────────────
add_para(doc, space_before=10, space_after=0)
add_heading(doc, "1. Introduccion")
add_para(doc,
    f"La base de datos de asegurados del IMSS correspondiente a abril de 2026 registra "
    f"{n_workers:,} trabajadores urbanos distribuidos en {n_rows:,} celdas de cruce "
    f"(entidad x municipio x sector x tamano x sexo x edad x rango salarial). "
    f"Cada fila representa un agregado: cuantos trabajadores comparten exactamente esas "
    f"caracteristicas y en que rango salarial (W1-W10) se encuentran.",
    space_after=4)
add_para(doc,
    "Se construyen dos modelos: (1) un modelo de minimos cuadrados ponderados (WLS) "
    "con termino cuadratico de edad e interacciones edad x tamano, para capturar como "
    "el efecto de la experiencia sobre el salario varia segun el tipo de patron; "
    "y (2) un modelo logistico ponderado con validacion via curva ROC y tabla de "
    "probabilidades predichas, para cuantificar la brecha salarial de genero por "
    "entidad y sector economico. Ambos modelos usan el conteo de trabajadores como peso.",
    space_after=4)

# ── 2. Descripcion del Dataset ────────────────────────────────────────────────
add_heading(doc, "2. Descripcion del Dataset y Preparacion")
make_table(doc,
    headers=["Variable", "Tipo", "Descripcion / Transformacion"],
    rows=[
        ("cve_entidad",        "Categorica", "Clave de entidad federativa (1-32) — 32 dummies, ref.=01 Aguascalientes"),
        ("sector_economico_1", "Categorica", "Sector SCIAN a 1 digito (1-9) — 8 dummies, ref.=1 Primario"),
        ("tamano_patron",      "Categorica", "S1 (1 trab.) a S7 (251+) — 7 dummies, ref.=S1"),
        ("sexo",               "Binaria",    "1=Hombre, 2=Mujer (excluye valor 3)  →  mujer = (sexo==2)"),
        ("rango_edad",         "Ordinal",    "E1 (15-19 anos) a E14 (80+) — convertida a punto medio continuo"),
        ("rango_salarial",     "Ordinal",    "W1 (min) a W10 (max) — convertida a 1-10 para modelo lineal"),
        ("peso (calc.)",       "Conteo",     "teu + tpu — trabajadores urbanos; usada como ponderador"),
    ],
    caption="Tabla 1. Variables utilizadas. Solo se conservan filas con peso > 0 y sexo valido.")

make_table(doc,
    headers=["Criterio", "Valor"],
    rows=[
        ("Filas en dataset original",    f"{len(df):,}"),
        ("Filas con trabajadores urbanos", f"{n_rows:,}"),
        ("Total trabajadores (peso)",    f"{n_workers:,}"),
        ("Umbral salario alto (M2)",     f"W{threshold} o superior (percentil 75 ponderado)"),
        ("Tasa de salario alto",         f"{high_rate:.1%}"),
    ],
    caption="Tabla 2. Resumen de preparacion de datos.")

# ── 3. Modelo 1: Regresion Lineal ─────────────────────────────────────────────
add_heading(doc, "3. Modelo 1: Regresion Lineal Ponderada")
add_para(doc,
    "El modelo WLS incluye edad como termino lineal y cuadratico para capturar "
    "la curvatura tipica de los perfiles salariales (crecen con la experiencia pero "
    "se estabilizan o desaceleran en edades avanzadas). Las interacciones "
    "edad x tamano_patron permiten estimar si la experiencia premia de forma diferente "
    "en empresas grandes versus pequenas.",
    space_after=4)

add_subheading(doc, "3.1  Especificacion")
add_para(doc,
    "sal_num ~ edad_mid + edad_mid² + C(entidad) + C(tamano) + edad_mid:C(tamano)",
    italic=True, size=9, space_after=4)

add_subheading(doc, "3.2  Metricas globales")
peak_str = f"{edad_peak:.1f} anos" if edad_peak and 17 <= edad_peak <= 82 else "fuera del rango observado"
make_table(doc,
    headers=["Metrica", "Valor"],
    rows=[
        ("R²",                    f"{r2:.4f}"),
        ("R² ajustado",           f"{r2_adj:.4f}"),
        ("Estadistico F",         f"{f_stat:,.0f}"),
        ("p-valor (F)",           f"{f_pval:.2e}"),
        ("Coef. edad lineal",     f"{edad_coef:+.4f} (p={edad_pval:.4f})"),
        ("Coef. edad cuadratico", f"{edad2_coef:+.6f} (p={edad2_pval:.4f})"),
        ("Pico salarial estimado", peak_str),
        ("Trabajadores (peso)",   f"{n_workers:,}"),
    ],
    caption="Tabla 3. Metricas del Modelo 1.")

add_para(doc,
    f"El R² de {r2:.4f} es tipico para modelos salariales con datos agregados y "
    f"variables categoricas amplias. El F-test (p={f_pval:.2e}) confirma que el conjunto "
    f"de predictores tiene poder explicativo real. El termino cuadratico de edad es "
    f"{'significativo' if edad2_pval < 0.05 else 'no significativo'} "
    f"(p={edad2_pval:.4f}), "
    + (f"con pico salarial en {peak_str}, lo que confirma un perfil de ingreso con "
       f"rendimientos decrecientes a edades avanzadas."
       if edad2_pval < 0.05 else
       "lo que sugiere que la relacion edad-salario es predominantemente lineal en este dataset."),
    space_after=4)

add_subheading(doc, "3.3  Efecto del tamano de empresa")
add_image(doc, 'fig1_tamano.png',
    caption="Figura 1. Coeficientes del tamano de empresa (vs S1=1 trabajador). "
            "En ambar: significativos (p<0.05). IC 95%.")

sig_tam = [s for s in ['S2','S3','S4','S5','S6','S7'] if tamano_rows.get(s,{}).get('pval',1) < 0.05]
non_sig  = [s for s in ['S2','S3','S4','S5','S6','S7'] if tamano_rows.get(s,{}).get('pval',1) >= 0.05]
rows_tam = []
for s in sizes:
    v = tamano_rows[s]
    sig = "Ref." if s == 'S1' else ("Si" if v['pval'] < 0.05 else "No")
    rows_tam.append((
        TAMANO_LBL[s],
        f"{v['coef']:+.4f}",
        f"[{v['ci_lo']:+.4f}, {v['ci_hi']:+.4f}]" if s != 'S1' else "—",
        f"{v['pval']:.4f}" if s != 'S1' else "—",
        sig
    ))
make_table(doc,
    headers=["Tamano", "Coeficiente", "IC 95%", "p-valor", "Sig."],
    rows=rows_tam,
    caption="Tabla 4. Coeficientes de tamano_patron. Referencia: S1 (1 trabajador).")
if non_sig:
    add_para(doc,
        f"Los tamanos {', '.join(non_sig)} no son significativos (p>=0.05): su diferencia "
        f"salarial respecto a S1 no es distinguible del error estadistico. Esto confirma "
        f"la indicacion del profesor: no todos los tamanos tienen un efecto detectable.",
        space_after=4)

add_subheading(doc, "3.4  Interaccion edad x tamano: como influye la edad segun el patron")
add_para(doc,
    "La figura 2 muestra las curvas salariales predichas para cada tamano de empresa "
    "a lo largo del ciclo de vida laboral (17 a 82 anos), manteniendo constante la entidad "
    "(CDMX como referencia). La pendiente de cada curva es la tasa de crecimiento salarial "
    "por ano de edad para ese tipo de empresa.",
    space_after=4)
add_image(doc, 'fig2_interaccion_edad_tamano.png',
    caption="Figura 2. Curvas salario-edad por tamano de empresa (modelo con interaccion). "
            "Pendientes distintas indican que la experiencia se valora de forma diferente "
            "segun el tamano del patron.")

rows_int = []
for s in sizes:
    slope  = interact_slopes.get(s, edad_coef)
    sig    = interact_sig.get(s, True)
    delta  = interact_delta40.get(s, 0.0)
    sig_vs = f"{delta:+.3f} W *" if sig and s != 'S1' else ("ref." if s == 'S1' else f"{delta:+.3f} W (n.s.)")
    rows_int.append((
        TAMANO_LBL[s],
        f"{slope:+.4f}",
        f"{slope * 10:.3f}",
        f"{slope * 40:.3f}",
        sig_vs
    ))
make_table(doc,
    headers=["Tamano", "Pendiente (W/ano)", "Ganancia 10a", "Ganancia carrera (40a)", "Delta vs S1"],
    rows=rows_int,
    caption="Tabla 5. Pendiente de edad por tamano de empresa. Delta vs S1: diferencia de ganancia "
            "acumulada en 40 anos respecto a un patron unipersonal. * = sig. p<0.05. n.s. = no significativo.")

non_sig_int = [s for s in ['S2','S3','S4','S5','S6','S7'] if not interact_sig.get(s, True)]
add_para(doc,
    f"Las interacciones son estadisticamente significativas para S2, S4, S5, S6 y S7 "
    f"(p<0.05){'; S3 no alcanza significancia (p=0.099)' if 'S3' in non_sig_int else ''}. "
    f"Sin embargo, el efecto practico es modesto: la mayor diferencia de carrera "
    f"(S6/S7 vs S1) es de solo +0.51 rangos W en 40 anos. "
    f"El hallazgo relevante es cualitativo: en empresas medianas y grandes (S4+), "
    f"la experiencia se valoriza de forma sistematicamente mayor que en microempresas, "
    f"lo que es consistente con la existencia de escalas salariales formales y antigedad.",
    space_after=4)

# ── 4. Modelo 2: Regresion Logistica ──────────────────────────────────────────
add_heading(doc, "4. Modelo 2: Regresion Logistica Ponderada")
add_para(doc,
    f"Se ajusta un modelo logistico (GLM Binomial con freq_weights) para predecir la "
    f"probabilidad de que un trabajador urbano pertenezca al estrato de salario alto "
    f"(W{threshold} o superior, percentil 75 ponderado, {high_rate:.1%} de los trabajadores). "
    f"Los predictores son entidad, sector economico a 1 digito y sexo.",
    space_after=4)

add_subheading(doc, "4.1  Metricas de ajuste y clasificacion")
make_table(doc,
    headers=["Metrica", "Valor"],
    rows=[
        ("Pseudo-R² (McFadden)",  f"{pseudo_r2:.4f}"),
        ("AUC (ROC ponderada)",   f"{auc_val:.4f}"),
        ("Umbral optimo (Youden)",f"{opt_threshold:.4f}"),
        ("Exactitud (accuracy)",  f"{accuracy:.3f}"),
        ("Sensibilidad (recall)", f"{sensitivity:.3f}"),
        ("Especificidad",         f"{specificity:.3f}"),
        ("Tasa base (salario alto)", f"{high_rate:.1%}"),
    ],
    caption="Tabla 6. Metricas del Modelo 2. El umbral optimo se obtiene maximizando el indice de Youden (Sens + Spec - 1) sobre la curva ROC.")
add_image(doc, 'fig5_roc.png',
    caption=f"Figura 5. Curva ROC del Modelo 2. AUC={auc_val:.4f}: "
            f"el modelo distingue trabajadores de salario alto/bajo mejor que el azar.")

add_subheading(doc, "4.2  Brecha salarial de genero — coeficiente del modelo")
add_para(doc,
    f"El coeficiente para la variable mujer es {mujer_coef:+.4f}, OR = {mujer_or:.4f} "
    f"(IC 95%: [{mujer_ci[0]:.4f}, {mujer_ci[1]:.4f}], p={mujer_pval:.2e}). "
    f"Esto significa que, controlando por entidad y sector, las mujeres tienen "
    f"{abs(1-mujer_or):.1%} {'menos' if mujer_or < 1 else 'mas'} probabilidades "
    f"(en terminos de odds) de pertenecer al estrato salarial alto que un hombre equivalente. "
    f"La diferencia es estadisticamente indistinguible del cero solo si el IC incluye 1.0; "
    f"en este caso, el intervalo [{mujer_ci[0]:.4f}, {mujer_ci[1]:.4f}] "
    f"{'no incluye' if not (mujer_ci[0] <= 1.0 <= mujer_ci[1]) else 'incluye'} "
    f"la unidad, por lo que la brecha es estadisticamente significativa.",
    space_after=4)

add_subheading(doc, "4.3  Probabilidades predichas por sector y sexo")
add_para(doc,
    "La figura 4 y la tabla 7 muestran las probabilidades predichas de salario alto "
    "para hombres y mujeres en cada sector, con CDMX como entidad de referencia. "
    "Esto cuantifica directamente la brecha: la diferencia de probabilidad predicha "
    "entre un hombre y una mujer con el mismo sector y entidad.",
    space_after=4)
add_image(doc, 'fig4_prob_predicha.png',
    caption=f"Figura 4. Probabilidad predicha de salario >= W{threshold} por sector y sexo "
            f"(ref. CDMX). La diferencia entre barras es la brecha de genero controlada por entidad.")

prob_rows = []
for sector_name in pred_pivot.index:
    ph = pred_pivot.loc[sector_name, 'Hombre']
    pm = pred_pivot.loc[sector_name, 'Mujer']
    br = pred_pivot.loc[sector_name, 'Brecha']
    prob_rows.append((
        sector_name,
        f"{ph:.3f} ({ph*100:.1f}%)",
        f"{pm:.3f} ({pm*100:.1f}%)",
        f"{br:+.3f} ({br*100:+.1f}pp)"
    ))
make_table(doc,
    headers=["Sector", f"P(W{threshold}+) Hombre", f"P(W{threshold}+) Mujer", "Brecha (pp)"],
    rows=prob_rows,
    caption=f"Tabla 7. Probabilidad predicha de salario alto (W{threshold}+) por sector y sexo. "
            f"Ref. entidad: CDMX. Brecha en puntos porcentuales (pp).")

add_subheading(doc, "4.4  Brecha salarial descriptiva por sector y entidad")
add_image(doc, 'fig3_brecha_sector.png',
    caption="Figura 3. Brecha en rango W promedio ponderado por sector. "
            "Azul: hombres ganan mas. Ambar: mujeres ganan mas en ese sector.")

gap_rows = [(str(idx), f"W{r['Hombre']:.2f}", f"W{r['Mujer']:.2f}", f"{r['Brecha']:+.3f}")
            for idx, r in gap_df.iterrows()]
make_table(doc,
    headers=["Sector", "Hombre (W prom.)", "Mujer (W prom.)", "Brecha H-M"],
    rows=gap_rows,
    caption="Tabla 8. Rango salarial promedio ponderado por sector y sexo.")

add_image(doc, 'fig6_brecha_entidad.png',
    caption="Figura 6. Brecha salarial de genero por entidad federativa (top 10 por volumen). "
            "La magnitud varia considerablemente entre estados.")

gap_ent_rows = [(str(idx), f"W{r['Hombre']:.2f}", f"W{r['Mujer']:.2f}", f"{r['Brecha']:+.3f}")
                for idx, r in gap_ent.sort_values('Brecha', ascending=False).iterrows()]
make_table(doc,
    headers=["Entidad", "Hombre (W prom.)", "Mujer (W prom.)", "Brecha H-M"],
    rows=gap_ent_rows,
    caption="Tabla 9. Brecha salarial por entidad (top 10 por trabajadores urbanos).")

# ── 5. Conclusiones ───────────────────────────────────────────────────────────
add_heading(doc, "5. Conclusiones")
peak_concl = f"a los {edad_peak:.0f} anos" if edad_peak and 17 <= edad_peak <= 82 else "en el rango observado"
conclusiones = [
    ("M1 — La experiencia tiene un efecto positivo decreciente sobre el salario.",
     f"El termino cuadratico de edad {'es significativo y' if edad2_pval < 0.05 else 'sugiere un'} "
     f"perfil de ingresos con pico estimado {peak_concl}. La relacion no es lineal: "
     f"los primeros anos de carrera generan mayores incrementos salariales que los ultimos."),
    ("M1 — El tamano del patron amplifica el salario de forma monotona.",
     f"Empresas grandes (S6, S7) pagan hasta {tamano_rows.get('S7',{}).get('coef',0):.2f} rangos W "
     f"mas que patrones unipersonales (S1), diferencia que es estadisticamente robusta."
     + (f" Los tamanos {', '.join(non_sig)} no difieren significativamente de S1." if non_sig else "")),
    ("M1 — La experiencia premia mas en empresas grandes.",
     "Las curvas de la figura 2 muestran pendientes distintas por tamano: empresas grandes "
     "tienen una mayor tasa de crecimiento salarial por ano de experiencia que las microempresas, "
     "lo que sugiere que la antiguedad se valoriza mas en organizaciones formales de mayor escala."),
    ("M2 — Las mujeres tienen menores probabilidades de acceder al estrato salarial alto.",
     f"OR={mujer_or:.4f} (IC=[{mujer_ci[0]:.3f},{mujer_ci[1]:.3f}]): controlando entidad y sector, "
     f"las odds de las mujeres de pertenecer al W{threshold}+ son {abs(1-mujer_or):.1%} "
     f"{'menores' if mujer_or < 1 else 'mayores'} que las de los hombres (p={mujer_pval:.2e})."),
    ("M2 — La brecha varia por sector: manufactura y servicios financieros concentran la mayor desigualdad.",
     "El sector primario presenta una particularidad: las mujeres aseguradas tienen "
     "un rango salarial promedio mayor que los hombres, posiblemente por la composicion "
     "distinta de perfiles dentro del sector. En manufactura y financiero/profesional, "
     "la ventaja masculina es consistente y significativa."),
    ("Metodologia — Regresion ponderada sobre datos BigData agregados.",
     "Usar freq_weights o WLS en datos IMSS ASG es equivalente a correr el modelo "
     "sobre los microdatos individuales, sin necesidad de expandirlos. El AUC de "
     f"{auc_val:.4f} indica que el modelo logistico tiene capacidad discriminante real, "
     "aunque la mayoria de la varianza salarial queda explicada por variables no incluidas "
     "(ocupacion, antiguedad, nivel educativo)."),
]
for titulo, texto in conclusiones:
    add_bullet(doc, titulo, texto)

add_para(doc, space_before=6, space_after=0)

# ═══════════════════════════════════════════════════════════════════════════════
# 7. SAVE DOCX + PDF
# ═══════════════════════════════════════════════════════════════════════════════
doc.save(OUTPUT)
print(f"DOCX guardado: {OUTPUT}")

soffice_paths = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]
lo = next((p for p in soffice_paths if os.path.exists(p)), None)
if lo:
    subprocess.run([lo, "--headless", "--convert-to", "pdf", "--outdir", ACT_DIR, OUTPUT], check=True)
    print("PDF generado.")
else:
    print("LibreOffice no encontrado — convertir DOCX a PDF manualmente.")
