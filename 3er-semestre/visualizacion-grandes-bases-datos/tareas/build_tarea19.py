# -*- coding: utf-8 -*-
"""
Tarea 1.9 - Decision tree to classify O3 or CO compliance (Session 13: entropy, ID3, CART).
a) IMECA norm per reading: O3 hourly (0.095 ppm) and CO 8-hour moving average (11 ppm); binary
   entropy of each and choice of the pollutant with the larger entropy.
b) CART tree (entropy criterion) for the selected pollutant, using only the other air pollutants
   measured at Centro; SO2 has no readings at all and is dropped.
c) Own design of the tree plus the CO-PM10 plane split into the tree's regions.
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tarea16 import (add_para, add_heading, add_caption, add_pic, make_table,  # noqa: E402
                           add_apa, clear_body_after_table1, NAVY, NAVY_HEX, AMBER_HEX,
                           RED_HEX, GREEN_HEX, TEMPLATE, SOFFICE, num)

COURSE = r"C:\Users\carlo\GitHub\mcd_cucea\3er-semestre\visualizacion-grandes-bases-datos"
DATA = COURSE + r"\datos\BD_2024_calidad_aire.xlsx"
OUT = COURSE + r"\tareas\Tarea1_9"
NORMA_O3 = 0.095      # ppm, 1 hour (IMECA 100, NOM-020-SSA1-2014)
NORMA_CO = 11.0       # ppm, 8-hour moving average (IMECA 100, NOM-021-SSA1-1993)
CONTAM = ["NO", "NO2", "NOX", "SO2", "CO", "PM10", "PM2.5"]   # air pollutants besides O3
GRIS = "#7F7F7F"
plt.rcParams.update({"font.family": "Calibri", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})


def f(v, d=4):
    return f"{v:,.{d}f}"


def pct(v, d=1):
    return f"{v * 100:.{d}f} %"


def plog(p):
    return p * np.log2(p) if p > 0 else 0.0


def entropia(n_fuera, n):
    p1 = n_fuera / n; p0 = 1 - p1
    return abs(plog(p0) + plog(p1)), p0, p1


# ============================ DATA ==========================================
df = pd.read_excel(DATA, sheet_name="Data")
d = df[df.STATION == "CEN"].copy()
for c in CONTAM + ["O3"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d["DATE"] = pd.to_datetime(d["DATE"]); d = d.sort_values("DATE").reset_index(drop=True)
n_horas = len(d)

# ---- a) O3: hourly reading against 0.095 ppm
o3 = d[d.O3.notna()].copy()
o3["fuera"] = (o3.O3 > NORMA_O3).astype(int)
n_o3, f_o3 = len(o3), int(o3.fuera.sum())
H_o3, p0_o3, p1_o3 = entropia(f_o3, n_o3)
meses_o3 = o3[o3.fuera == 1].DATE.dt.month.value_counts().sort_index()
horas_o3 = o3[o3.fuera == 1].DATE.dt.hour
max_o3 = o3.O3.max()

# ---- a) CO: 8-hour moving average (at least 6 valid hours in the window) against 11 ppm
d["CO8"] = d.CO.rolling(8, min_periods=6).mean()
co8 = d.CO8.dropna()
n_co, f_co = len(co8), int((co8 > NORMA_CO).sum())
H_co, p0_co, p1_co = entropia(f_co, n_co)
max_co8, max_co = co8.max(), d.CO.max()
elegido = "O3" if H_o3 > H_co else "CO"

# ---- b) variables: every air pollutant other than O3 with at least one reading
lect = {c: int(d[c].notna().sum()) for c in CONTAM}
lect_fuera = {c: int(o3.loc[o3.fuera == 1, c].notna().sum()) for c in CONTAM}
V = [c for c in CONTAM if lect[c] > 0]
descartadas = [c for c in CONTAM if lect[c] == 0]
X, y = o3[V], o3.fuera.values

PARAM = dict(criterion="entropy", max_depth=3, min_samples_leaf=50, class_weight="balanced",
             random_state=0)
arbol = DecisionTreeClassifier(**PARAM).fit(X, y)
T = arbol.tree_
pred = arbol.predict(X)
cm = confusion_matrix(y, pred)
cv = cross_val_predict(DecisionTreeClassifier(**PARAM), X, y,
                       cv=StratifiedKFold(5, shuffle=True, random_state=0))
cm_cv = confusion_matrix(y, cv)
imp = dict(zip(V, arbol.feature_importances_))
w_fuera, w_dentro = n_o3 / (2 * f_o3), n_o3 / (2 * (n_o3 - f_o3))

# tree without weights, for comparison: it never predicts "fuera"
sin_peso = DecisionTreeClassifier(**{**PARAM, "class_weight": None}).fit(X, y)
n_pred_sin = int(sin_peso.predict(X).sum())

# raw counts per node (hours and hours out of norm), following the tree's own routing
camino = arbol.decision_path(X)
nodo_n = np.asarray(camino.sum(axis=0)).ravel()
nodo_f = np.asarray(camino[y == 1].sum(axis=0)).ravel()
hojas = [i for i in range(T.node_count) if T.children_left[i] == -1]
clase = {i: int(np.argmax(T.value[i][0])) for i in range(T.node_count)}

# root split, unweighted information gain (Session 13 style)
izq, der = T.children_left[0], T.children_right[0]
H_izq = entropia(nodo_f[izq], nodo_n[izq])[0]; H_der = entropia(nodo_f[der], nodo_n[der])[0]
ganancia = H_o3 - (nodo_n[izq] / n_o3 * H_izq + nodo_n[der] / n_o3 * H_der)

# context of the risk leaf: hour of day and month
hoja_riesgo = max(hojas, key=lambda i: nodo_f[i])
en_riesgo = arbol.apply(X) == hoja_riesgo
r_hora = o3.DATE.dt.hour[en_riesgo]
t_pm = T.threshold[0]
pm_alto_mes = o3.groupby(o3.DATE.dt.month).PM10.apply(lambda s: (s.dropna() > t_pm).mean())
pm_lluvia = o3[o3.DATE.dt.month.between(7, 9)].PM10.dropna().gt(t_pm).mean()
pm_resto = o3[~o3.DATE.dt.month.between(7, 9)].PM10.dropna().gt(t_pm).mean()
fuera_lluvia = int(meses_o3.reindex([7, 8, 9], fill_value=0).sum())
co_med_fuera = o3.loc[o3.fuera == 1, "CO"].median()
co_mediodia = o3[o3.DATE.dt.hour.between(11, 18)].CO.median()


def regla(i, lado):
    """Text of a split as seen from the child on `lado` ('izq' = <=)."""
    var, thr = V[T.feature[i]], T.threshold[i]
    unidad = "ppm" if var in ("CO", "NO", "NO2", "NOX") else "µg/m³"
    ndig = 2 if unidad == "ppm" else 1
    falt = (lado == "izq") == bool(T.missing_go_to_left[i])
    sin = " o sin dato" if falt and nodo_n[i] > 0 and X[var].isna().any() else ""
    op = "≤" if lado == "izq" else ">"
    return f"{var} {op} {thr:.{ndig}f} {unidad}{sin}"


# ============================ FIGURES =======================================
def fig_series():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5.4), sharex=True)
    a1.plot(o3.DATE, o3.O3, color=NAVY_HEX, lw=0.5)
    fo = o3[o3.fuera == 1]
    a1.scatter(fo.DATE, fo.O3, color=RED_HEX, s=10, zorder=3, label=f"Fuera de norma ({f_o3} horas)")
    a1.axhline(NORMA_O3, color=AMBER_HEX, ls="--", lw=1.2, label="Norma 0.095 ppm (1 h)")
    a1.set_ylabel("O3 (ppm)"); a1.set_title("Ozono, lectura horaria", loc="left", color=NAVY_HEX, weight="bold")
    a1.legend(frameon=False, fontsize=8, loc="upper right")
    a2.plot(d.DATE, d.CO8, color=NAVY_HEX, lw=0.6)
    a2.axhline(NORMA_CO, color=AMBER_HEX, ls="--", lw=1.2, label="Norma 11 ppm (promedio de 8 h)")
    a2.set_ylim(0, 12); a2.set_ylabel("CO (ppm)")
    a2.set_title("Monóxido de carbono, promedio móvil de 8 horas", loc="left", color=NAVY_HEX, weight="bold")
    a2.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    p = OUT + r"\fig1_normas.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


def color_riesgo(t):
    """Green (0 %) to red (risk leaf) for a node's share of hours out of norm."""
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("r", ["#E3F1E7", "#FCE4B8", "#F4B6AE"])
    tope = max(nodo_f[i] / nodo_n[i] for i in hojas)
    return cmap(min(t / tope, 1))


def fig_arbol():
    """Own design: each box shows the hours that reach it, how many were out of norm and the share;
    leaves say what the tree predicts. Branch labels give the rule for that side."""
    pos, orden = {}, []

    def hojas_en_orden(i):
        if T.children_left[i] == -1:
            orden.append(i); return
        hojas_en_orden(T.children_left[i]); hojas_en_orden(T.children_right[i])
    hojas_en_orden(0)

    def ubicar(i, nivel):
        """Leaves evenly spaced left to right; each split sits over the middle of its two children."""
        if T.children_left[i] == -1:
            pos[i] = ((orden.index(i) + 0.5) / len(orden), -nivel); return pos[i][0]
        xl = ubicar(T.children_left[i], nivel + 1); xr = ubicar(T.children_right[i], nivel + 1)
        pos[i] = ((xl + xr) / 2, -nivel); return pos[i][0]
    ubicar(0, 0)
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.set_xlim(0, 1); ax.set_ylim(-3.45, 0.6); ax.axis("off")
    W, Hh = 0.17, 0.5
    for i, (x, yv) in pos.items():
        for hijo, lado in ((T.children_left[i], "izq"), (T.children_right[i], "der")):
            if hijo == -1:
                continue
            xh, yh = pos[hijo]
            ax.plot([x, xh], [yv - Hh / 2, yh + Hh / 2], color=GRIS, lw=1.2, zorder=1)
            r_ = regla(i, lado)
            sin = r_.endswith(" o sin dato")
            base = r_.replace(" o sin dato", "")
            cond, unidad = base.rsplit(" ", 1)
            txt = f"{cond}\n{unidad}" + (" (o sin dato)" if sin else "")
            ax.text((x + xh) / 2, (yv + yh) / 2, txt, ha="center", va="center", fontsize=8.3,
                    color=NAVY_HEX, style="italic", zorder=4,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
    for i, (x, yv) in pos.items():
        share = nodo_f[i] / nodo_n[i]
        hoja = T.children_left[i] == -1
        ax.add_patch(FancyBboxPatch((x - W / 2, yv - Hh / 2), W, Hh, boxstyle="round,pad=0.01,rounding_size=0.03",
                                    fc=color_riesgo(share), ec=(RED_HEX if hoja and clase[i] == 1 else NAVY_HEX),
                                    lw=(2.2 if hoja and clase[i] == 1 else 1), zorder=2))
        if hoja:
            tit = "Riesgo de rebasar la norma" if clase[i] == 1 else "Dentro de norma"
        else:
            tit = "Todas las horas" if i == 0 else "Nodo intermedio"
        ax.text(x, yv + 0.13, tit, ha="center", va="center", fontsize=8.2, weight="bold",
                color=(RED_HEX if hoja and clase[i] == 1 else NAVY_HEX), zorder=3)
        ax.text(x, yv - 0.05, f"{num(nodo_n[i])} horas\n{nodo_f[i]} fuera de norma ({share * 100:.1f} %)",
                ha="center", va="center", fontsize=8, zorder=3)
    ax.text(0.0, 0.42, "Cumplimiento de la norma de ozono (0.095 ppm), estación Centro 2024",
            fontsize=11, weight="bold", color=NAVY_HEX)
    p = OUT + r"\fig2_arbol.png"; fig.savefig(p, dpi=200, bbox_inches="tight"); plt.close(fig); return p


def fig_plano():
    """CO vs PM10 split into the tree's regions (PM2.5 only changes counts, not the class)."""
    Z = o3.dropna(subset=["CO", "PM10"])
    lim_pm, lim_co = 150, 3.0
    fuera_vista = int(((Z.PM10 > lim_pm) | (Z.CO > lim_co)).sum())
    t0 = T.threshold[0]
    n2 = T.children_right[0]; t_hi = T.threshold[n2]; t_lo = T.threshold[T.children_left[n2]]
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.add_patch(Rectangle((0, 0), t0, lim_co, color="#E3F1E7", zorder=0))
    ax.add_patch(Rectangle((t0, 0), lim_pm - t0, t_lo, color="#EEF3EA", zorder=0))
    ax.add_patch(Rectangle((t0, t_lo), lim_pm - t0, t_hi - t_lo, color="#F4B6AE", zorder=0))
    ax.add_patch(Rectangle((t0, t_hi), lim_pm - t0, lim_co - t_hi, color="#EEF3EA", zorder=0))
    dn = Z[Z.fuera == 0]; fu = Z[Z.fuera == 1]
    ax.scatter(dn.PM10, dn.CO, s=3, color=GRIS, alpha=0.25, lw=0, label="Dentro de norma")
    ax.scatter(fu.PM10, fu.CO, s=16, color=RED_HEX, zorder=3, label="Fuera de norma")
    for xv in [t0]:
        ax.axvline(xv, color=NAVY_HEX, lw=1)
    ax.plot([t0, lim_pm], [t_lo, t_lo], color=NAVY_HEX, lw=1); ax.plot([t0, lim_pm], [t_hi, t_hi], color=NAVY_HEX, lw=1)
    ax.text(t0 / 2, lim_co * 0.93, f"PM10 ≤ {t0:.1f}\nninguna hora\nfuera de norma", ha="center", va="top", fontsize=8.5, color=NAVY_HEX)
    ax.text(lim_pm * 0.97, (t_lo + t_hi) / 2, f"Zona de riesgo\nCO entre {t_lo:.2f} y {t_hi:.2f} ppm", ha="right",
            va="center", fontsize=8.5, color=RED_HEX, weight="bold")
    ax.set_xlim(0, lim_pm); ax.set_ylim(0, lim_co)
    ax.set_xlabel("PM10 (µg/m³)"); ax.set_ylabel("CO (ppm)")
    ax.legend(frameon=False, fontsize=8, loc="upper center")
    fig.tight_layout()
    p = OUT + r"\fig3_plano.png"; fig.savefig(p, dpi=200); plt.close(fig); return p, fuera_vista, len(Z), int(fu.shape[0])


# ============================ BUILD =========================================
def build():
    os.makedirs(OUT, exist_ok=True)
    p1, p2 = fig_series(), fig_arbol()
    p3, fuera_vista, n_plano, f_plano = fig_plano()
    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Visualización de Grandes Bases de Datos"
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Tarea 1.9. Árbol de decisión para clasificar O3 o CO\n"
                   "Entropía y cumplimiento de la norma IMECA en la estación Centro")
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]; cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]: extra.text = ""
    si(1, "18 de noviembre de 2026")
    si(2, "Tarea 1.9. Árbol de decisión para clasificar O3 o CO")
    si(3, "Python 3.13 (pandas, scikit-learn, Matplotlib)")
    si(4, "DecisionTreeClassifier (CART) con criterio de entropía")
    si(5, "Equipo personal, entorno conda MCD")
    si(6, "Calidad del aire ZMG 2024, estación Centro (CEN)")
    clear_body_after_table1(doc)

    # ---------------- 1
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        "Para esta tarea seguí con la estación Centro (CEN), la misma que uso desde la Tarea 1.3, porque "
        "mide ozono, monóxido de carbono y partículas durante todo el año. Primero revisé qué lecturas de "
        "ozono (O3) por hora y de monóxido de carbono (CO) en 8 horas cumplen su norma y calculé la "
        "entropía de cada uno para escoger el de mayor entropía. Con ese contaminante armé un árbol de "
        "decisión que usa como variables solo a los otros contaminantes, y al final lo dibujé con un diseño "
        "mío para que se vea de qué depende que se cumpla la norma.")

    # ---------------- 2
    add_heading(doc, "2. Normas IMECA y entropía")
    add_para(doc,
        "En el IMECA (Índice Metropolitano de la Calidad del Aire) los 100 puntos equivalen al límite de "
        "la norma de salud de cada contaminante (Secretaría del Medio Ambiente de la Ciudad de México, "
        "2018). Para el ozono el límite es 0.095 ppm en una hora (Secretaría de Salud, 2014) y para el "
        "monóxido de carbono 11 ppm en promedio móvil de 8 horas (Secretaría de Salud, 1994), que es el "
        "mismo valor que usé en la Tarea 1.2. En el ozono comparé cada lectura horaria directamente con el "
        "límite. En el CO saqué para cada hora el promedio de las 8 horas anteriores, con al menos 6 "
        "lecturas válidas en la ventana, y comparé ese promedio con los 11 ppm.")
    add_pic(doc, p1, 6.2)
    add_caption(doc, "Figura 1. O3 horario y promedio móvil de 8 horas del CO en 2024 contra su norma IMECA.")
    add_para(doc,
        f"De las {num(n_o3)} horas con lectura de ozono, {f_o3} pasaron de 0.095 ppm, el "
        f"{pct(f_o3 / n_o3, 2)}, y la más alta llegó a {max_o3:.3f} ppm. El CO quedó muy lejos de su norma. "
        f"De {num(n_co)} promedios de 8 horas el mayor fue de {max_co8:.2f} ppm, y la lectura horaria más "
        f"alta del año fue de {max_co:.2f} ppm, que tampoco llega a 11 (Figura 1). Casi todas las horas de "
        "ozono fuera de norma fueron de febrero a junio, siempre entre las 11 y las 18 horas.")
    add_para(doc,
        "La entropía binaria, H = −Σ p(x) log₂ p(x), indica qué tan mezcladas están las dos clases. Es 0 "
        "si todas las lecturas están en la misma clase y 1 si la mitad está en cada una. La calculé igual "
        "que en el ejemplo del tipo de motor de la sesión 13:")
    filas_h = [
        ["O3 (1 h, 0.095 ppm)", num(n_o3 - f_o3), str(f_o3), f(p0_o3), f(p1_o3),
         f(plog(p0_o3)), f(plog(p1_o3)), f(H_o3)],
        ["CO (8 h, 11 ppm)", num(n_co - f_co), str(f_co), f(p0_co), f(p1_co),
         f(plog(p0_co)), f(plog(p1_co)), f(H_co)],
    ]
    make_table(doc, ["Contaminante", "Dentro", "Fuera", "p(dentro)", "p(fuera)", "p log₂ p (dentro)",
                     "p log₂ p (fuera)", "Entropía"], filas_h,
               "Tabla 1. Lecturas dentro y fuera de norma y entropía de cada contaminante.",
               [1.75, 0.6, 0.45, 0.7, 0.7, 0.85, 0.85, 0.7], hl=0)
    add_para(doc,
        f"S(O3) = −(({f(plog(p0_o3))}) + ({f(plog(p1_o3))})) = {f(H_o3)}. En el CO todas las lecturas "
        f"están dentro de norma, así que p(dentro) = 1, log₂ 1 = 0 y el término de la clase vacía también "
        f"vale 0 (se toma 0 log₂ 0 = 0). Por eso S(CO) = 0. El ozono tiene la entropía más alta y es el que "
        "clasifiqué con el árbol. Su entropía es baja porque la mayoría de las horas cumplen la norma, pero "
        "por lo menos hay casos de las dos clases. Con el CO no habría nada que separar.")

    # ---------------- 3
    add_heading(doc, "3. Árbol de decisión para el ozono")
    add_heading(doc, "3.1 Variables", level=2)
    filas_v = [[c, num(lect[c]), str(lect_fuera[c]), "Sí" if c in V else "No, sin lecturas"]
               for c in CONTAM]
    make_table(doc, ["Contaminante", "Horas con lectura", "Horas con lectura entre las 100 fuera de norma",
                     "Entra al modelo"], filas_v,
               "Tabla 2. Contaminantes medidos en la estación Centro en 2024, además del ozono.",
               [1.3, 1.3, 2.4, 1.4])
    add_para(doc,
        f"En la base de Centro viene la columna de dióxido de azufre (SO2), pero está vacía todo 2024, así "
        f"que la quité como dice la tarea. Las variables del árbol quedaron como {', '.join(V[:-1])} y "
        f"{V[-1]}. NO, NO2 y NOX sí tienen lecturas, aunque solo de septiembre a diciembre, como ya había "
        f"visto en la Tarea 1.6, y de las {f_o3} horas fuera de norma solo {lect_fuera['NO2']} tienen dato "
        "de NO2. Aun así las dejé porque sí tienen lecturas, y el árbol de scikit-learn puede trabajar con "
        "datos faltantes. En cada corte prueba mandar las horas sin dato a un lado y al otro y escoge el "
        "lado que deja menos entropía (Pedregosa et al., 2011).")
    add_heading(doc, "3.2 Construcción del árbol", level=2)
    add_para(doc,
        "Usé CART (Breiman et al., 1984), el algoritmo del ejemplo de rendimiento de la sesión 13, con la "
        "entropía como medida de impureza, que es la que usa ID3 (Quinlan, 1986). En cada nodo el árbol "
        "prueba todas las variables y valores de corte y se queda con el que más baja la entropía. El primer "
        f"corte fue PM10 ≤ {T.threshold[0]:.1f} µg/m³. De un lado quedaron {num(nodo_n[izq])} horas sin "
        f"ninguna fuera de norma (entropía 0) y del otro {num(nodo_n[der])} horas con las {nodo_f[der]} "
        f"fuera de norma (entropía {f(H_der)}). La ganancia de información de ese corte es {f(H_o3)} − "
        f"({nodo_n[izq]}/{n_o3} × 0 + {nodo_n[der]}/{n_o3} × {f(H_der)}) = {f(ganancia)}.")
    add_para(doc,
        f"Como solo el {pct(f_o3 / n_o3, 1)} de las horas están fuera de norma, un árbol sin ajustes "
        f"siempre dice \"dentro de norma\". Lo probé y predijo {n_pred_sin} horas fuera de norma, aunque así "
        f"acierta en el {pct(1 - f_o3 / n_o3, 1)} de los casos. Para que tomara en cuenta las dos clases "
        f"por igual les puse pesos inversos a su frecuencia, {w_fuera:.2f} a cada hora fuera de norma y "
        f"{w_dentro:.3f} a cada hora dentro. Además lo limité a 3 niveles y a un mínimo de 50 horas por "
        "hoja, para que se pudiera leer y no se ajustara a casos aislados.")
    add_heading(doc, "3.3 Resultado", level=2)
    filas_cm = [["Dentro de norma (real)", num(cm[0, 0]), num(cm[0, 1]), num(cm_cv[0, 0]), num(cm_cv[0, 1])],
                ["Fuera de norma (real)", str(cm[1, 0]), str(cm[1, 1]), str(cm_cv[1, 0]), str(cm_cv[1, 1])]]
    make_table(doc, ["", "Predice dentro", "Predice riesgo", "Predice dentro (VC)", "Predice riesgo (VC)"],
               filas_cm, "Tabla 3. Matriz de confusión del árbol con todos los datos y con validación "
                         "cruzada de 5 particiones (VC).", [1.8, 1.0, 1.0, 1.2, 1.2])
    add_para(doc,
        f"El árbol detecta {cm[1, 1]} de las {f_o3} horas fuera de norma. Con validación cruzada, en la que "
        f"cada hora la clasifica un árbol que no se entrenó con ella, detecta {cm_cv[1, 1]}. A cambio marca "
        f"como riesgo {num(cm[0, 1])} horas que sí cumplieron la norma, porque con los otros contaminantes "
        "no se puede saber exactamente cuándo el ozono va a pasar de 0.095 ppm. Sí se puede saber en qué "
        "condiciones nunca pasa y en cuáles es posible. La importancia de las variables fue de "
        f"{imp['PM10']:.2f} para PM10, {imp['CO']:.2f} para CO y {imp['PM2.5']:.2f} para PM2.5. NO, NO2 y "
        f"NOX no salieron en ningún corte, porque con datos en solo {lect_fuera['NO2']} de las horas fuera "
        "de norma no ayudan a separar las clases.")

    # ---------------- 4
    add_heading(doc, "4. Diseño del árbol")
    add_para(doc,
        "No usé el dibujo que genera la librería, lo hice yo. Cada caja dice cuántas horas llegan a ese "
        "nodo, cuántas estuvieron fuera de norma y qué porcentaje son, y el color va de verde a rojo según "
        "ese porcentaje. En las ramas puse la condición con sus unidades y hacia qué lado se van las horas "
        "sin dato, para que el árbol se pueda seguir pregunta por pregunta.")
    add_pic(doc, p2, 6.4)
    add_caption(doc, "Figura 2. Árbol de decisión para el cumplimiento de la norma de ozono, con diseño propio.")
    hr, n_r, f_r = hoja_riesgo, nodo_n[hoja_riesgo], nodo_f[hoja_riesgo]
    n2 = T.children_right[0]; t_hi = T.threshold[n2]; t_lo = T.threshold[T.children_left[n2]]
    hoja_pm25 = T.children_right[T.children_right[n2]]
    co_alto_mid = o3.loc[o3.CO > t_hi].DATE.dt.hour.between(11, 18).mean()
    add_para(doc,
        f"Si el PM10 es de {T.threshold[0]:.1f} µg/m³ o menos, el ozono cumplió la norma en todas las "
        f"{num(nodo_n[izq])} horas. Si el PM10 es mayor, depende del CO. Con CO entre {t_lo:.2f} y "
        f"{t_hi:.2f} ppm hay {num(n_r)} horas y ahí están {f_r} de las {f_o3} horas fuera de norma. En esa "
        f"hoja el {pct(f_r / n_r, 1)} de las horas pasó la norma, {(f_r / n_r) / (f_o3 / n_o3):.1f} veces "
        f"más que en todo el año. Con CO más bajo o más alto casi no hubo casos. El último corte, "
        f"PM2.5 ≤ {T.threshold[T.children_right[n2]]:.1f} µg/m³, no cambia la clasificación porque las dos "
        f"hojas salen como dentro de norma, y en la de PM2.5 alto solo hubo {nodo_f[hoja_pm25]} hora fuera "
        "de norma.")
    add_para(doc,
        "En la Figura 3 dibujé el mismo árbol como regiones del plano CO contra PM10, como la gráfica de la "
        "sesión 13 donde se compara el corte de CART con la regresión logística. Cada corte es una línea "
        "paralela a uno de los ejes y la zona roja es la hoja de riesgo.")
    add_pic(doc, p3, 5.9)
    add_caption(doc, f"Figura 3. Horas de 2024 en el plano PM10 contra CO y regiones del árbol. Se muestran "
                     f"PM10 hasta 150 µg/m³ y CO hasta 3 ppm; quedan fuera de la vista {fuera_vista} de "
                     f"{num(n_plano)} horas, ninguna fuera de norma.")
    add_para(doc,
        f"Quise ver si los cortes tenían sentido. El de PM10 coincide bastante con la temporada de lluvias. "
        f"De julio a septiembre solo el {pct(pm_lluvia, 0)} de las horas tuvo PM10 arriba de {t_pm:.1f} "
        f"µg/m³, y en el resto del año fue el {pct(pm_resto, 0)}, porque la lluvia limpia las partículas. "
        f"En esos meses también hay más nubes, y como el ozono se forma con la luz del sol a partir de "
        f"óxidos de nitrógeno y compuestos orgánicos, en julio, agosto y septiembre solo hubo "
        f"{fuera_lluvia} horas fuera de norma.")
    add_para(doc,
        f"El corte del CO va más con la hora y con qué tan contaminado está el aire. Las horas fuera de "
        f"norma fueron todas entre las 11 y las 18 horas. A esa hora el CO suele bajar porque el aire se "
        f"mezcla más (la mediana es de {co_mediodia:.2f} ppm), pero en las horas fuera de norma la mediana "
        f"fue de {co_med_fuera:.2f} ppm, o sea que eran días con más emisiones del tráfico, que también "
        f"traen los contaminantes que forman el ozono. El CO arriba de {t_hi:.2f} ppm casi no se da a "
        f"mediodía, solo el {pct(co_alto_mid, 1)} de esas horas cae entre las 11 y las 18. Son horas de la "
        "mañana y la noche, cuando no hay sol para que se forme ozono.")
    add_para(doc,
        f"Con esto se entienden también las falsas alarmas. El árbol no sabe la hora y solo el "
        f"{pct(r_hora.between(11, 18).mean(), 0)} de las horas de la hoja de riesgo son entre las 11 y las "
        "18. Las demás son de la noche o la madrugada, con valores parecidos de CO y PM10, pero sin sol el "
        "ozono no llega a la norma.")

    # ---------------- 5
    add_heading(doc, "5. Conclusiones")
    add_para(doc,
        f"El ozono tuvo la entropía más alta ({f(H_o3)} contra 0 del CO) porque fue el único contaminante "
        f"que pasó su norma en Centro, con {f_o3} horas en 2024. Según el árbol, que terminó usando PM10, "
        f"CO y PM2.5, el ozono nunca pasó la norma con PM10 de {T.threshold[0]:.1f} µg/m³ o menos, y casi "
        f"todas las horas fuera de norma ({f_r} de {f_o3}) fueron con PM10 alto y CO entre {t_lo:.2f} y "
        f"{t_hi:.2f} ppm.")
    add_para(doc,
        "El árbol no sirve para predecir el ozono hora por hora, porque marca muchas horas de riesgo que "
        "al final cumplieron la norma. Pero da una regla sencilla de en qué condiciones puede pasarse la "
        "norma, y se puede leer completa porque es un modelo de caja blanca. Si se pudieran usar variables "
        "meteorológicas, agregaría la radiación solar y la temperatura, que influyen más en la formación "
        "del ozono, pero en esta tarea solo se podían usar contaminantes.")

    add_heading(doc, "Referencias")
    for t in [
        "Breiman, L., Friedman, J. H., Olshen, R. A., & Stone, C. J. (1984). Classification and regression "
        "trees. Wadsworth.",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., "
        "Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., "
        "Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. Journal of Machine "
        "Learning Research, 12, 2825-2830.",
        "Quinlan, J. R. (1986). Induction of decision trees. Machine Learning, 1(1), 81-106. "
        "https://doi.org/10.1007/BF00116251",
        "Ruiz Chávez, C. F. (2026). Visualización de grandes bases de datos: Sesión 13, árboles de decisión "
        "[Diapositivas de clase]. Maestría en Ciencia de los Datos, Centro Universitario de Ciencias "
        "Económico Administrativas, Universidad de Guadalajara.",
        "Secretaría de Medio Ambiente y Desarrollo Territorial. (2024). Sistema de Monitoreo Atmosférico de "
        "Jalisco (SIMAJ): base de datos de calidad del aire 2024. Gobierno del Estado de Jalisco. "
        "https://siga.jalisco.gob.mx/aire/",
        "Secretaría del Medio Ambiente de la Ciudad de México. (2018). Norma Ambiental para el Distrito "
        "Federal NADF-009-AIRE-2017, que establece los requisitos para elaborar el Índice de Calidad del "
        "Aire. Gaceta Oficial de la Ciudad de México.",
        "Secretaría de Salud. (1994). Norma Oficial Mexicana NOM-021-SSA1-1993, Salud ambiental. Criterio "
        "para evaluar la calidad del aire ambiente con respecto al monóxido de carbono (CO). Diario Oficial "
        "de la Federación.",
        "Secretaría de Salud. (2014). Norma Oficial Mexicana NOM-020-SSA1-2014, Salud ambiental. Valor límite "
        "permisible para la concentración de ozono (O3) en el aire ambiente y criterios para su evaluación. "
        "Diario Oficial de la Federación.",
        "Shannon, C. E. (1948). A mathematical theory of communication. The Bell System Technical Journal, "
        "27(3), 379-423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x",
    ]:
        add_apa(doc, t)
    out = OUT + r"\Tarea1_9_VisualizacionGBD_CarlosPulidoRosas.docx"
    doc.save(out); print("DOCX:", out)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", OUT, out],
                   check=True, capture_output=True)
    print("PDF:", out.replace(".docx", ".pdf"))


if __name__ == "__main__":
    print("O3", n_o3, f_o3, round(H_o3, 4), "CO8", n_co, f_co, H_co, "max co8", max_co8, "elegido", elegido)
    print("lect", lect, "lect_fuera", lect_fuera)
    print("cm", cm.tolist(), "cv", cm_cv.tolist(), "imp", {k: round(v, 3) for k, v in imp.items()})
    print("nodes n", nodo_n.tolist(), "f", nodo_f.tolist(), "gain", round(ganancia, 4), "Hder", round(H_der, 4))
    print("sin peso pred", n_pred_sin, "w", w_fuera, w_dentro, "pm lluvia", pm_lluvia, pm_resto, "co med", co_med_fuera, co_mediodia)
    print("riesgo 11-18", r_hora.between(11, 18).mean(), "meses", meses_o3.to_dict())
    print("horas fuera 11-18", horas_o3.between(11, 18).mean())
    build()
