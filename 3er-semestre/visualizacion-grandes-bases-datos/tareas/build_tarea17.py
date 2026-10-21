# -*- coding: utf-8 -*-
"""
Tarea 1.7 - Refined multiple regression NO2 ~ PM10 + PM2.5: line forced through the origin and
Tukey outliers of NO2, PM10 and PM2.5 removed, compared against the Tarea 1.6 models (intercept).
Also looks at how PM10 and PM2.5 relate to each other, with K-means as in Session 9.
Reuses the data preparation (imputed NO2 series, Tukey-clean corpus) of build_tarea16.
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_tarea16 as t16                                     # noqa: E402
from build_tarea16 import (add_para, add_heading, add_caption, add_pic, make_table,  # noqa: E402
                           add_apa, clear_body_after_table1, NAVY, NAVY_HEX, AMBER_HEX,
                           RED_HEX, TEMPLATE, SOFFICE, f, pct, num)

COURSE = r"C:\Users\carlo\GitHub\mcd_cucea\3er-semestre\visualizacion-grandes-bases-datos"
OUT = COURSE + r"\tareas\Tarea1_7"
GRAY_HEX = "#777777"


# ============================ MODELS ========================================
def ajuste(Z, origen):
    X = Z[["PM10", "PM2.5"]]
    X = X if origen else sm.add_constant(X)
    m = sm.OLS(Z["NO2"], X).fit()
    y, e = Z["NO2"], m.resid
    return {"m": m, "n": len(Z), "r2_modelo": m.rsquared,
            "r2_media": 1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum(),
            "rmse": np.sqrt((e ** 2).mean()), "sesgo": e.mean(),
            "r_y_yhat": np.corrcoef(y, m.fittedvalues)[0, 1]}


SERIES = {"Completada": (t16.Zc_all, t16.Zc), "Observada": (t16.Zo_all, t16.Zo)}
M = {}
for s, (ZA, Z) in SERIES.items():
    M[s] = {"bruto_int": ajuste(ZA, False), "t16": ajuste(Z, False),
            "t17": ajuste(Z, True), "bruto_origen": ajuste(ZA, True),
            "r_bruto": ZA[t16.VARS].corr(), "r_limpio": Z[t16.VARS].corr(),
            "n_bruto": len(ZA), "n_limpio": len(Z)}
    # PM2.5 as a fraction of PM10 (line through the origin)
    mp = sm.OLS(Z["PM2.5"], Z[["PM10"]]).fit()
    M[s]["frac"] = mp.params.iloc[0]; M[s]["frac_r2"] = mp.rsquared
    M[s]["vif"] = 1 / (1 - Z[["PM10", "PM2.5"]].corr().iloc[0, 1] ** 2)

C, O = M["Completada"], M["Observada"]

# K-means on the observed hours (standardized PM10 and PM2.5)
Zk = t16.Zo.copy()
Xk = StandardScaler().fit_transform(Zk[["PM10", "PM2.5"]].values)
inercias = {k: KMeans(k, n_init=10, random_state=42).fit(Xk).inertia_ for k in range(1, 8)}
K = 3
km = KMeans(K, n_init=10, random_state=42).fit(Xk)
Zk["grupo"] = km.labels_
# relabel the groups from low to high PM10 so the names make sense
orden = Zk.groupby("grupo")["PM10"].mean().sort_values().index
Zk["grupo"] = Zk["grupo"].map({g: i for i, g in enumerate(orden)})
grupos = Zk.groupby("grupo").agg(n=("NO2", "size"), PM10=("PM10", "mean"), PM25=("PM2.5", "mean"),
                                  NO2=("NO2", "mean"))
grupos["ratio"] = grupos["PM25"] / grupos["PM10"]
NOMBRES_G = ["Bajo", "Medio", "Alto"]


# ============================ FIGURES =======================================
def fig_pred_vs_real():
    p = OUT + r"\real_vs_predicho.png"
    Z = SERIES["Completada"][1]
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True)
    for axx, key, titulo, col in [(ax[0], "t16", "Tarea 1.6: con intercepto", NAVY_HEX),
                                  (ax[1], "t17", "Tarea 1.7: por el origen", AMBER_HEX)]:
        r = C[key]
        axx.scatter(Z["NO2"], r["m"].fittedvalues, s=4, alpha=0.2, color=col, edgecolors="none")
        lim = [0, Z["NO2"].max() * 1.05]
        axx.plot(lim, lim, ls="--", color=GRAY_HEX, lw=1.2, label="predicción perfecta")
        axx.set_xlim(lim); axx.set_ylim(lim)
        axx.set_title(f"{titulo}\nRMSE = {r['rmse'] * 1000:.1f} ppb, sesgo = {r['sesgo'] * 1000:+.1f} ppb",
                      color=NAVY_HEX, weight="bold", fontsize=10)
        axx.set_xlabel("NO₂ real (ppm)", fontsize=9); axx.grid(linestyle=":", alpha=0.4)
        axx.legend(fontsize=8, loc="upper left")
    ax[0].set_ylabel("NO₂ estimado (ppm)", fontsize=9)
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


def fig_residuales():
    p = OUT + r"\residuales.png"
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 7))
    for j, (key, titulo, col) in enumerate([("t16", "Tarea 1.6: con intercepto", NAVY_HEX),
                                            ("t17", "Tarea 1.7: por el origen", AMBER_HEX)]):
        r = C[key]; e = r["m"].resid; yh = r["m"].fittedvalues
        a = ax[0, j]
        a.scatter(yh, e, s=4, alpha=0.2, color=col, edgecolors="none")
        a.axhline(0, color="black", lw=1)
        # running mean of the residuals to make the pattern visible
        orden_ = np.argsort(yh.values)
        movil = pd.Series(e.values[orden_]).rolling(300, center=True).mean()
        a.plot(yh.values[orden_], movil, color=RED_HEX, lw=2, label="promedio móvil de residuales")
        a.set_title(f"Residuales vs. estimado: {titulo}", color=NAVY_HEX, weight="bold", fontsize=9.5)
        a.set_xlabel("NO₂ estimado (ppm)", fontsize=8); a.set_ylabel("Residual (ppm)", fontsize=8)
        a.legend(fontsize=7, loc="upper left"); a.grid(linestyle=":", alpha=0.4)
        b = ax[1, j]
        b.hist(e, bins=60, color=col, alpha=0.8)
        b.axvline(0, color="black", lw=1)
        b.axvline(e.mean(), color=RED_HEX, lw=2, ls="--", label=f"media = {e.mean() * 1000:+.1f} ppb")
        b.set_title(f"Distribución de residuales: {titulo}", color=NAVY_HEX, weight="bold", fontsize=9.5)
        b.set_xlabel("Residual (ppm)", fontsize=8); b.set_ylabel("Horas", fontsize=8)
        b.legend(fontsize=7); b.grid(linestyle=":", alpha=0.4)
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


def fig_pm():
    p = OUT + r"\relacion_pm10_pm25.png"
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.3), gridspec_kw={"width_ratios": [1.6, 1]})
    cols = ["#7FB3D5", AMBER_HEX, RED_HEX]
    for g in range(K):
        s = Zk[Zk["grupo"] == g]
        ax[0].scatter(s["PM10"], s["PM2.5"], s=6, alpha=0.4, color=cols[g], edgecolors="none",
                      label=f"Grupo {NOMBRES_G[g].lower()} ({len(s)} h)")
    for g in range(K):
        ax[0].scatter(grupos.loc[g, "PM10"], grupos.loc[g, "PM25"], marker="+", s=220, color="black", lw=2)
    xs = np.linspace(0, Zk["PM10"].max(), 50)
    ax[0].plot(xs, O["frac"] * xs, color="black", lw=1.5, ls="--",
               label=f"PM2.5 = {O['frac']:.2f}·PM10")
    ax[0].set_xlim(left=0); ax[0].set_ylim(bottom=0)
    ax[0].set_xlabel("PM10 (µg/m³)", fontsize=9); ax[0].set_ylabel("PM2.5 (µg/m³)", fontsize=9)
    ax[0].set_title("PM2.5 vs. PM10 y grupos de K-medias (k = 3)", color=NAVY_HEX, weight="bold", fontsize=10)
    ax[0].legend(fontsize=7.5, loc="upper left"); ax[0].grid(linestyle=":", alpha=0.4)
    ks = list(inercias.keys())
    ax[1].plot(ks, [inercias[k] for k in ks], marker="o", color=NAVY_HEX)
    ax[1].axvline(K, color=AMBER_HEX, ls="--", lw=1.5)
    ax[1].set_xlabel("Número de grupos k", fontsize=9); ax[1].set_ylabel("J (suma de distancias²)", fontsize=9)
    ax[1].set_title("Criterio del codo", color=NAVY_HEX, weight="bold", fontsize=10)
    ax[1].grid(linestyle=":", alpha=0.4)
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


# ============================ BUILD =========================================
def build():
    os.makedirs(OUT, exist_ok=True)
    p_rv, p_res, p_pm = fig_pred_vs_real(), fig_residuales(), fig_pm()

    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Visualización de Grandes Bases de Datos"
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Tarea 1.7. Modelo refinado del NO₂ con PM10 y PM2.5\n"
                   "Estación de monitoreo Centro, Zona Metropolitana de Guadalajara, 2024")
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]; cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]: extra.text = ""
    si(1, "21 de octubre de 2026")
    si(2, "Tarea 1.7. Modelado de NO₂ y PM2.5/PM10 refinado")
    si(3, "Python 3.13 (pandas, NumPy, Matplotlib, statsmodels, scikit-learn)")
    si(4, "SIMAJ, base de calidad del aire 2024 (BD_2024)")
    si(5, "Equipo personal, entorno conda MCD")
    si(6, "Calidad del aire ZMG 2024, estación Centro (CEN)")
    clear_body_after_table1(doc)

    c16, c17, o16, o17 = C["t16"], C["t17"], O["t16"], O["t17"]

    # ---------------- 1. Introduccion
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        "En la tarea anterior completé el NO₂ de la estación Centro con el CO y armé modelos de "
        "regresión múltiple con el PM10 y el PM2.5. En esta tarea refino ese modelo. Le quité el "
        "intercepto para que el plano pase por el origen, NO₂ = b₁·PM10 + b₂·PM2.5, quité los "
        "atípicos de las tres variables y comparé el resultado contra los modelos de la 1.6.")
    add_para(doc,
        "Trabajé con las mismas dos series de la 1.6. La completada tiene el NO₂ imputado y suma "
        f"{num(C['n_bruto'])} horas con las tres variables. La observada solo tiene NO₂ medido "
        f"({num(O['n_bruto'])} horas) y la uso para comprobar que lo que veo no sea efecto de la "
        "imputación.")

    # ---------------- 2. Metodologia
    add_heading(doc, "2. Metodología")
    add_heading(doc, "2.1 Exclusión de atípicos", level=2)
    add_para(doc,
        "Seguí el mismo criterio de Tukey de las tareas pasadas. Si en una hora el NO₂, el PM10 o el "
        "PM2.5 quedan fuera de [Q1 − 1.5·RIC, Q3 + 1.5·RIC], quito esa hora completa. Me quedaron "
        f"{num(C['n_limpio'])} horas en la serie completada y {num(O['n_limpio'])} en la observada. "
        "También calculé las correlaciones con los datos sin depurar para ver qué cambiaba.")
    add_heading(doc, "2.2 Modelo por el origen", level=2)
    add_para(doc,
        "El modelo de la 1.6 era NO₂ = b₀ + b₁·PM10 + b₂·PM2.5. Al quitarle b₀, el modelo supone que "
        "si no hay partículas tampoco hay NO₂. Para compararlos no me quise quedar solo con el R² que "
        "da cada modelo. Como vimos en la Tarea 1.5, cuando no hay intercepto el R² se mide contra "
        "cero y no contra el promedio, y sale alto aunque el modelo ajuste mal. Así que además "
        "calculé el R² contra el promedio en los dos casos, el RMSE y el promedio de los residuales.")
    add_heading(doc, "2.3 Relación entre las partículas y K-medias", level=2)
    add_para(doc,
        "Para ver cómo se relacionan el PM10 y el PM2.5 usé su correlación y una recta por el origen "
        "PM2.5 = b·PM10. También probé K-medias, que vimos en la sesión 9. El algoritmo junta las "
        "horas en k grupos buscando que la suma J = Σ Σ ‖xᵢ − cⱼ‖² de las distancias al centroide sea "
        "la menor posible. Estandaricé las dos variables antes de agrupar para que ninguna pesara más "
        "y escogí k con la gráfica del codo.")

    # ---------------- 3. Resultados
    add_heading(doc, "3. Resultados")
    add_heading(doc, "3.1 ¿Mejoró la correlación?", level=2)
    add_para(doc, "En la Tabla 1 están las correlaciones antes y después de quitar los atípicos.", keep=True)
    rb_c, rl_c, rb_o, rl_o = C["r_bruto"], C["r_limpio"], O["r_bruto"], O["r_limpio"]
    pares = [("NO₂ – PM10", "NO2", "PM10"), ("NO₂ – PM2.5", "NO2", "PM2.5"), ("PM10 – PM2.5", "PM10", "PM2.5")]
    make_table(doc, ["Par", "Completada sin depurar", "Completada depurada", "Observada sin depurar",
                     "Observada depurada"],
               [[nm, f(rb_c.loc[a, b]), f(rl_c.loc[a, b]), f(rb_o.loc[a, b]), f(rl_o.loc[a, b])]
                for nm, a, b in pares],
               "Tabla 1. Correlación de Pearson antes y después de excluir los atípicos de NO₂, PM10 y PM2.5.",
               [1.4, 1.3, 1.3, 1.3, 1.3])
    add_para(doc,
        "La correlación no mejoró. Bajó en todos los pares. Con los datos observados, la del NO₂ con "
        f"el PM10 pasó de {f(rb_o.loc['NO2', 'PM10'])} a {f(rl_o.loc['NO2', 'PM10'])}. Ya me había pasado "
        "algo parecido con las partículas en la Tarea 1.5. Las horas atípicas son episodios de mucha "
        "contaminación donde todo sube al mismo tiempo, y como quedan muy lejos del resto, jalan la "
        "correlación hacia arriba. Sin ellas la relación es más débil, pero se parece más a lo que "
        "pasa normalmente. El origen aquí no influye, porque la correlación no depende del modelo.")

    add_heading(doc, "3.2 ¿Mejoraron el R² y los residuales?", level=2)
    add_para(doc, "La Tabla 2 pone lado a lado el modelo de la 1.6 y el refinado.", keep=True)

    def fila(serie, nombre, r):
        pr = r["m"].params
        b0 = f"{pr['const'] * 1000:.2f}" if "const" in pr else "0 (forzado)"
        return [f"{serie}: {nombre}", b0, f"{pr['PM10'] * 1000:.3f}", f"{pr['PM2.5'] * 1000:.3f}",
                f(r["r2_modelo"]), f(r["r2_media"]), f"{r['rmse'] * 1000:.2f}", f"{r['sesgo'] * 1000:+.2f}"]
    make_table(doc, ["Serie y modelo", "b₀ (ppb)", "b PM10", "b PM2.5", "R² del modelo",
                     "R² vs. promedio", "RMSE (ppb)", "Residual medio (ppb)"],
               [fila("Completada", "1.6 con intercepto", c16), fila("Completada", "1.7 por el origen", c17),
                fila("Observada", "1.6 con intercepto", o16), fila("Observada", "1.7 por el origen", o17)],
               "Tabla 2. Modelo de la Tarea 1.6 contra el modelo refinado, datos depurados. Los "
               "coeficientes están en ppb de NO₂ por µg/m³. El R² del modelo es el que reporta "
               "statsmodels; en el modelo por el origen se calcula contra cero.",
               [1.9, 0.7, 0.6, 0.6, 0.7, 0.7, 0.7, 0.9], hl=1)
    add_para(doc,
        "Cuando vi el R² del modelo refinado pensé que había mejorado mucho, porque en la serie "
        f"completada subió de {f(c16['r2_modelo'])} a {f(c17['r2_modelo'])}. Luego recordé lo de la "
        "Tarea 1.5. Ese R² se mide contra cero, y como el NO₂ casi nunca vale cero, cualquier plano "
        "más o menos cercano a los puntos da un número alto. Con el R² medido contra el promedio, que "
        f"es el que sí se puede comparar, el refinado cae a {f(c17['r2_media'])} en la serie completada "
        f"y a {f(o17['r2_media'])} en la observada. Los dos quedan por debajo de los de la 1.6. El RMSE "
        f"también empeora, de {c16['rmse'] * 1000:.1f} a {c17['rmse'] * 1000:.1f} ppb en la serie "
        "completada.")
    add_para(doc,
        "Los residuales tampoco mejoraron. En la 1.6 su promedio es cero, que es lo normal cuando el "
        f"modelo tiene intercepto. En el refinado el promedio es de {c17['sesgo'] * 1000:+.1f} ppb, o sea "
        "que en general el modelo se queda corto. Las Figuras 1 y 2 lo muestran.", keep=True)
    add_pic(doc, p_rv, 6.4)
    add_caption(doc, "Figura 1. NO₂ real contra NO₂ estimado por el modelo de la Tarea 1.6 y por el "
                     "modelo refinado, serie completada depurada. La línea punteada es la predicción perfecta.")
    add_pic(doc, p_res, 6.4)
    add_caption(doc, "Figura 2. Residuales de los dos modelos, serie completada depurada. Arriba, "
                     "residuales contra valor estimado con su promedio móvil; abajo, su distribución.")
    add_para(doc,
        "Lo más claro está en la parte de arriba de la Figura 2. En la 1.6 la línea roja, que es el "
        "promedio móvil de los residuales, se mantiene casi pegada al cero. En el refinado va "
        "bajando. Cuando el modelo estima poco NO₂ los residuales son positivos, y cuando estima "
        "mucho son negativos. Eso quiere decir que en horas con pocas partículas el modelo predice "
        "muy poco NO₂ cuando sí lo hay, y en horas con muchas partículas se pasa. Si los residuales "
        "tienen una tendencia así, al modelo le falta algo, y aquí lo que le falta es la constante. "
        "En el histograma de abajo también se nota, porque los residuales del refinado están "
        "corridos a la derecha del cero.")
    add_para(doc,
        "Hay dos detalles más en la figura. La línea recta de puntos que se ve en la parte de arriba "
        "son horas imputadas que en la 1.6 quedaron fijas en el valor límite de "
        f"{t16.pred15(t16.co_lim):.3f} ppm. Y la correlación entre el NO₂ real y el estimado casi no "
        f"cambia ({f(c16['r_y_yhat'])} y {f(c17['r_y_yhat'])}). Los dos modelos ordenan las horas casi "
        "igual de más a menos contaminadas; el refinado lo que pierde es el nivel.")

    add_heading(doc, "3.3 ¿Cómo se relacionan las partículas entre sí?", level=2)
    add_para(doc,
        "El PM10 y el PM2.5 son el par con la correlación más alta de todo el análisis, "
        f"{f(rl_o.loc['PM10', 'PM2.5'])} con los datos observados y {f(rl_c.loc['PM10', 'PM2.5'])} en la "
        "serie completada. Era de esperarse, porque el PM2.5 forma parte del PM10. Con una recta por "
        f"el origen me salió PM2.5 ≈ {O['frac']:.2f}·PM10 (R²₀ = {f(O['frac_r2'])}), es decir, cerca "
        f"del {O['frac'] * 100:.0f} % del PM10 son partículas finas. El VIF de {f(O['vif'], 2)} indica "
        "colinealidad moderada entre las dos.")
    add_para(doc,
        "Con K-medias quería ver si había distintos tipos de horas según sus partículas. En la "
        "gráfica del codo (Figura 3, derecha) la J baja mucho hasta k = 3 y después casi no cambia, "
        "así que me quedé con tres grupos. Sus promedios están en la Tabla 3.", keep=True)
    add_pic(doc, p_pm, 6.4)
    add_caption(doc, "Figura 3. Izquierda: PM2.5 contra PM10 con los tres grupos de K-medias (las cruces "
                     "son los centroides) y la recta por el origen. Derecha: J para k de 1 a 7. Horas "
                     "con NO₂ observado, sin atípicos.")
    make_table(doc, ["Grupo", "Horas", "PM10 (µg/m³)", "PM2.5 (µg/m³)", "PM2.5 / PM10", "NO₂ (ppb)"],
               [[NOMBRES_G[g], num(grupos.loc[g, "n"]), f(grupos.loc[g, "PM10"], 1), f(grupos.loc[g, "PM25"], 1),
                 f(grupos.loc[g, "ratio"], 2), f(grupos.loc[g, "NO2"] * 1000, 1)] for g in range(K)],
               "Tabla 3. Promedio de cada grupo de K-medias (k = 3), horas con NO₂ observado.",
               [1.0, 0.8, 1.1, 1.1, 1.0, 0.9])
    add_para(doc,
        "No salieron tipos de partículas distintos. Los tres grupos están sobre la misma diagonal y "
        "lo que los separa es qué tanta contaminación hay, poca, media o mucha. La proporción de "
        f"finas cambia poco, de {f(grupos.loc[0, 'ratio'], 2)} en el grupo bajo a "
        f"{f(grupos.loc[2, 'ratio'], 2)} en el alto. Esto me confirma que el PM10 y el PM2.5 se mueven "
        "casi como si fueran una sola variable.")
    add_para(doc,
        "Lo que sí me llamó la atención es el NO₂. No lo usé para formar los grupos y aun así sube de "
        f"uno a otro, de {f(grupos.loc[0, 'NO2'] * 1000, 1)} a {f(grupos.loc[2, 'NO2'] * 1000, 1)} ppb. "
        "Además, en el grupo con menos partículas el NO₂ sigue en "
        f"{f(grupos.loc[0, 'NO2'] * 1000, 1)} ppb, que está lejos de cero. Ahí se ve por qué el modelo "
        "por el origen no funciona con estos datos.")

    # ---------------- 4. Interpretacion
    add_heading(doc, "4. ¿Qué nos dice este modelo?")
    p16 = c16["m"].params; p17 = c17["m"].params
    add_para(doc,
        "En el modelo refinado de la serie completada, cada µg/m³ de PM10 va con "
        f"{p17['PM10'] * 1000:.2f} ppb de NO₂ y cada µg/m³ de PM2.5 con {p17['PM2.5'] * 1000:.2f} ppb. "
        f"En la 1.6 eran {p16['PM10'] * 1000:.2f} y {p16['PM2.5'] * 1000:.2f}. Las pendientes crecieron "
        "porque, al quitar la constante, tienen que cargar con el NO₂ que antes explicaba ella. Esa "
        f"constante valía {p16['const'] * 1000:.1f} ppb en la serie completada y "
        f"{o16['m'].params['const'] * 1000:.1f} ppb en la observada, y en los dos casos era "
        "significativa.")
    add_para(doc,
        "Creo que la razón es física. Con el CO funcionó forzar el origen porque el CO y el NO₂ salen "
        "del mismo escape. Las partículas, en cambio, también vienen del polvo, de la construcción y "
        "de otras cosas que no producen NO₂. Hay horas con pocas partículas en las que sigue habiendo "
        "NO₂ por el tráfico, y horas con mucho polvo y no tanto NO₂. Por eso no tiene sentido que el "
        "NO₂ sea cero cuando las partículas son cero, y el modelo refinado lo confirma, porque al "
        "quitar la constante ajusta peor y los residuales quedan sesgados.")

    # ---------------- 5. Conclusiones
    add_heading(doc, "5. Conclusiones")
    add_para(doc,
        "Al quitar los atípicos la correlación bajó, porque esas horas extremas la estaban inflando. "
        "Forzar el plano por el origen hizo que el R² del modelo subiera de "
        f"{f(c16['r2_modelo'])} a {f(c17['r2_modelo'])}, pero eso es por la forma en que se calcula sin "
        f"intercepto. Comparado de forma justa bajó a {f(c17['r2_media'])}, el RMSE subió y los "
        "residuales quedaron sesgados. En resumen, el modelo refinado es peor que el de la 1.6.")
    add_para(doc,
        f"El PM10 y el PM2.5 están muy relacionados y el PM2.5 es más o menos el {O['frac'] * 100:.0f} % "
        "del PM10. K-medias no encontró tipos de horas distintos, solo niveles de contaminación, y el "
        "NO₂ sube junto con ellos. Si tuviera que describir el NO₂ con partículas usaría el modelo con "
        "intercepto de la 1.6 o el de fracción fina y gruesa. La recta por el origen la dejaría para "
        "casos como el NO₂ con el CO, que sí vienen de la misma fuente.")

    add_heading(doc, "Referencias")
    add_apa(doc, "Montgomery, D. C., Peck, E. A., & Vining, G. G. (2021). Introduction to linear "
                 "regression analysis (6.ª ed.). Wiley.")
    add_apa(doc, "Ruiz Chávez, C. F. (2026). Visualización de grandes bases de datos: Sesión 9 "
                 "[Diapositivas de clase]. Maestría en Ciencia de los Datos, Centro Universitario de "
                 "Ciencias Económico Administrativas, Universidad de Guadalajara.")
    add_apa(doc, "Secretaría de Medio Ambiente y Desarrollo Territorial. (2024). Sistema de "
                 "Monitoreo Atmosférico de Jalisco (SIMAJ): base de datos de calidad del aire 2024. "
                 "Gobierno del Estado de Jalisco. https://siga.jalisco.gob.mx/aire/")
    add_apa(doc, "Seinfeld, J. H., & Pandis, S. N. (2016). Atmospheric chemistry and physics: From "
                 "air pollution to climate change (3.ª ed.). Wiley.")
    out = OUT + r"\Tarea1_7_VisualizacionGBD_CarlosPulidoRosas.docx"
    doc.save(out); print("DOCX:", out)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", OUT, out],
                   check=True, capture_output=True)
    print("PDF:", out.replace(".docx", ".pdf"))
    return out


if __name__ == "__main__":
    build()
