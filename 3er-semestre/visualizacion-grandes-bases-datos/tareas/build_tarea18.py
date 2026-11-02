# -*- coding: utf-8 -*-
"""
Tarea 1.8 - Noise and redundancy reduction before K-means, following Sessions 9 and 10.
Noise = slight variations around central values -> removed by quantization (rounding).
Redundancy = repeated coordinates -> collapsed into one point weighted by its count.
Standard K-means on the raw points vs. K-means modified for grouped data (weighted re-centring,
Session 10, slide 62). Both runs share the same initial centroids, as in the class example.
The unweighted run on the de-duplicated points (Session 10, slide 59) is kept as a reference.
"""
import os
import sys
import subprocess
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, kmeans_plusplus
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tarea16 import (add_para, add_heading, add_caption, add_pic, make_table,  # noqa: E402
                           add_apa, clear_body_after_table1, NAVY, NAVY_HEX, AMBER_HEX,
                           RED_HEX, TEMPLATE, SOFFICE, f, num)

COURSE = r"C:\Users\carlo\GitHub\mcd_cucea\3er-semestre\visualizacion-grandes-bases-datos"
DATA = COURSE + r"\datos\datos_1.csv"
OUT = COURSE + r"\tareas\Tarea1_8"
KS = list(range(2, 13))
SEMILLA = 7
DEC = 4               # quantization: coordinates rounded to 4 decimals (about 11 m)
GRIS = "#7F7F7F"
PALETA = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3",
          "#8C8C8C", "#CCB974", "#64B5CD", "#2F4B7C", "#A05195"]


# ============================ DATA ==========================================
d = pd.read_csv(DATA)
X = d[["x", "y"]].values
n_total = len(X)
n_unicos_crudos = len(d.drop_duplicates())

# precision test: how many distinct points remain at each number of decimals
prec = {dec: len(d.round(dec).drop_duplicates()) for dec in [6, 5, 4, 3, 2]}

# noise (quantization) + redundancy (aggregation with weights)
g = d.round(DEC).groupby(["x", "y"]).size().reset_index(name="w")
Xq, wq = g[["x", "y"]].values, g["w"].values.astype(float)
n_q = len(Xq)
max_rep = int(wq.max())
n_rep = int((wq > 1).sum())


# ============================ ALGORITHMS ====================================
def kmeans_ponderado(X, w, centros_ini, max_iter=300):
    """
    K-means modified for grouped data. Assignment step as in the standard algorithm; in the
    re-centring step each centroid is the weighted mean of its points, c_j = sum(w_i x_i) / sum(w_i),
    so a point that represents n records counts n times. With all w_i = 1 it is the standard algorithm.
    Returns labels, centroids, weighted J and number of iterations.
    """
    c = centros_ini.copy()
    for it in range(1, max_iter + 1):
        et = ((X[:, None, :] - c[None, :, :]) ** 2).sum(2).argmin(1)
        nuevo = np.array([np.average(X[et == j], axis=0, weights=w[et == j]) if (et == j).any() else c[j]
                          for j in range(len(c))])
        if np.allclose(nuevo, c, atol=1e-12):
            c = nuevo
            break
        c = nuevo
    et = ((X[:, None, :] - c[None, :, :]) ** 2).sum(2).argmin(1)
    J = float((w * ((X - c[et]) ** 2).sum(1)).sum())
    return et, c, J, it


def var_total(X, w):
    mu = np.average(X, axis=0, weights=w)
    return float((w * ((X - mu) ** 2).sum(1)).sum())


def iniciales(k):
    # same initial centroids for every approach (k-means++ on the original data, fixed seed)
    c, _ = kmeans_plusplus(X, k, random_state=SEMILLA)
    return c


def correr(XX, w, k):
    t0 = time.perf_counter()
    et, c, J, it = kmeans_ponderado(XX, w, iniciales(k))
    seg = time.perf_counter() - t0
    return {"et": et, "c": c, "J": J, "bt": 1 - J / var_total(XX, w), "it": it, "seg": seg}


ENFOQUES = {"est": (X, np.ones(n_total)), "pond": (Xq, wq), "sinpeso": (Xq, np.ones(n_q))}
R = {e: {k: correr(XX, ww, k) for k in KS} for e, (XX, ww) in ENFOQUES.items()}


def codo(e):
    J = np.array([R[e][k]["J"] for k in KS])
    xn = (np.array(KS) - KS[0]) / (KS[-1] - KS[0])
    yn = (J - J.min()) / (J.max() - J.min())
    return KS[int(np.argmax((1 - xn) - yn))]


k_est, k_pond = codo("est"), codo("pond")

# check: own weighted K-means vs scikit-learn with sample_weight, same initial centroids
km_sk = KMeans(k_pond, init=iniciales(k_pond), n_init=1).fit(Xq, sample_weight=wq)
J_sk = km_sk.inertia_


def asignacion_original(c):
    return ((X[:, None, :] - c[None, :, :]) ** 2).sum(2).argmin(1)


def cambio_vs_est(e, k):
    """Share of the original records whose cluster changes, and largest centroid shift (m)."""
    a = R["est"][k]["et"]
    b = asignacion_original(R[e][k]["c"])
    desp = np.linalg.norm(R["est"][k]["c"] - R[e][k]["c"], axis=1).max() * 111.32 * 1000
    return float((a != b).mean()), float(desp)


ch_pond, desp_pond = cambio_vs_est("pond", k_est)
ch_sin7, desp_sin7 = cambio_vs_est("sinpeso", 7)
ch_pond7, desp_pond7 = cambio_vs_est("pond", 7)


# ============================ FIGURES =======================================
def fig_datos():
    p = OUT + r"\datos_ruido_redundancia.png"
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, sharey=True)
    ax[0].scatter(X[:, 0], X[:, 1], s=4, color="#9BC4DE", edgecolors="none")
    ax[0].set_title(f"Fenómeno X: datos originales ({num(n_total)} puntos)", color=NAVY_HEX,
                    weight="bold", fontsize=10)
    ax[1].scatter(Xq[:, 0], Xq[:, 1], s=2 + 2.5 * wq, color=NAVY_HEX, alpha=0.45, edgecolors="none")
    ax[1].set_title(f"Sin ruido ni redundancia ({num(n_q)} puntos ponderados)", color=NAVY_HEX,
                    weight="bold", fontsize=10)
    ax[1].text(0.02, 0.03, "tamaño del punto = número de registros que representa", transform=ax[1].transAxes,
               fontsize=7.5, color="#444444")
    for a in ax:
        a.set_xlabel("lng", fontsize=9); a.set_ylabel("lat", fontsize=9); a.grid(linestyle=":", alpha=0.4)
        a.xaxis.set_major_locator(plt.MaxNLocator(5)); a.tick_params(labelsize=7.5)
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


def fig_codo():
    p = OUT + r"\codo_comparativo.png"
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for e, col, nom, ls in [("est", NAVY_HEX, "Estándar (datos originales)", "-"),
                            ("pond", AMBER_HEX, "Modificado con pesos (datos procesados)", "--")]:
        J = [R[e][k]["J"] for k in KS]; bt = [R[e][k]["bt"] * 100 for k in KS]
        ax[0].plot(KS, J, marker="o", color=col, ls=ls, label=nom)
        ax[1].plot(KS, bt, marker="o", color=col, ls=ls, label=nom)
    ax[0].axvline(k_est, color=RED_HEX, ls=":", lw=1.5)
    ax[0].set(xlabel="Número de agrupaciones k", ylabel="J (suma de distancias al cuadrado)")
    ax[0].set_title(f"Criterio del codo (línea roja: k = {k_est})", color=NAVY_HEX, weight="bold", fontsize=10)
    ax[1].set(xlabel="Número de agrupaciones k", ylabel="between / total (%)")
    ax[1].set_title("Variación explicada por las agrupaciones", color=NAVY_HEX, weight="bold", fontsize=10)
    for a in ax:
        a.set_xticks(KS); a.grid(linestyle=":", alpha=0.4); a.legend(fontsize=8)
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


def panel(a, e, k, titulo):
    XX, ww = ENFOQUES[e]
    r = R[e][k]
    a.scatter(XX[:, 0], XX[:, 1], s=3 if e == "est" else 2 + 2 * ww, c=[PALETA[l] for l in r["et"]],
              edgecolors="none", alpha=0.8)
    ini = iniciales(k)
    a.scatter(ini[:, 0], ini[:, 1], marker="^", s=55, color="red", zorder=5)
    a.scatter(r["c"][:, 0], r["c"][:, 1], marker="+", s=170, color="black", lw=2, zorder=6)
    a.set_title(titulo, color=NAVY_HEX, weight="bold", fontsize=9.5)
    a.set_xlabel(f"lng\nk = {k}, between/total = {r['bt'] * 100:.1f} %", fontsize=8.5)
    a.set_ylabel("lat", fontsize=9); a.grid(linestyle=":", alpha=0.3)
    a.xaxis.set_major_locator(plt.MaxNLocator(4)); a.tick_params(labelsize=7.5)


def fig_grupos():
    p = OUT + r"\agrupaciones_k_elegido.png"
    fig, ax = plt.subplots(1, 2, figsize=(11, 5), sharex=True, sharey=True)
    panel(ax[0], "est", k_est, "Fenómeno X: algoritmo estándar")
    panel(ax[1], "pond", k_pond, "Sin ruido ni redundancia: algoritmo modificado")
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


def fig_k7():
    p = OUT + r"\agrupaciones_k7.png"
    fig, ax = plt.subplots(1, 3, figsize=(14, 5), sharex=True, sharey=True)
    panel(ax[0], "est", 7, "Estándar")
    panel(ax[1], "sinpeso", 7, "Sin redundancia, sin pesos")
    panel(ax[2], "pond", 7, "Sin ruido ni redundancia, con pesos")
    plt.tight_layout(); plt.savefig(p, dpi=190, bbox_inches="tight"); plt.close()
    return p


# ============================ BUILD =========================================
def build():
    os.makedirs(OUT, exist_ok=True)
    p_dat, p_codo, p_g, p_7 = fig_datos(), fig_codo(), fig_grupos(), fig_k7()
    e_k, p_k = R["est"][k_est], R["pond"][k_pond]
    e7, s7, p7 = R["est"][7], R["sinpeso"][7], R["pond"][7]

    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Visualización de Grandes Bases de Datos"
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Tarea 1.8. Reducción de ruido y redundancia\n"
                   "K-medias estándar y K-medias para datos agrupados: Fenómeno X")
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]; cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]: extra.text = ""
    si(1, "1 de noviembre de 2026")
    si(2, "Tarea 1.8. Reducción de ruido y redundancia")
    si(3, "Python 3.13 (pandas, NumPy, Matplotlib, scikit-learn)")
    si(4, "Conjunto de datos de la clase (datos_1.csv)")
    si(5, "Equipo personal, entorno conda MCD")
    si(6, "Fenómeno X: coordenadas (lng, lat) en la ZMG")
    clear_body_after_table1(doc)

    # ---------------- 1
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        f"El conjunto de datos es el Fenómeno X de la sesión 10: {num(n_total)} registros con la "
        "longitud y la latitud de un fenómeno en la Zona Metropolitana de Guadalajara. Como se vio en "
        "la sesión 9, un conjunto grande de datos no tiene necesariamente más información, porque es "
        "común que tenga redundancia (valores repetidos) y ruido (ligeras variaciones de los valores "
        "centrales). La tarea consiste en obtener el mejor número de agrupaciones con K-medias "
        "estándar, quitar el ruido y la redundancia, volver a obtener el mejor número de agrupaciones "
        "con el algoritmo modificado para datos agrupados y comparar ambos resultados.")

    # ---------------- 2
    add_heading(doc, "2. Metodología")
    add_heading(doc, "2.1 K-medias estándar", level=2)
    add_para(doc,
        "K-medias agrupa los datos en k grupos minimizando J = Σ Σ ‖x_i − c_j‖², la suma de las "
        "distancias euclidianas al cuadrado entre cada punto y el centroide de su grupo. En cada "
        "iteración asigna cada punto al centroide más cercano y después re-centra cada centroide con "
        "la media de sus puntos. Para que la comparación entre los dos abordajes fuera justa, igual "
        "que en el ejemplo de la clase, usé los mismos centroides iniciales en ambos (los triángulos "
        "rojos de las gráficas), elegidos con k-means++ sobre los datos originales y una semilla fija.")
    add_para(doc,
        "Para elegir el mejor número de agrupaciones probé de 2 a 12 grupos y apliqué el criterio del "
        "codo: normalicé la curva de J y elegí la k que queda más lejos de la recta que une el primer "
        "y el último punto, que es donde la curva deja de bajar rápido (Satopää et al., 2011). También "
        "reporto la proporción between/total, la parte de la variación total que explican los grupos, "
        "que es la medida que se usó en la sesión 10.")
    add_heading(doc, "2.2 Ruido: cuantización de las coordenadas", level=2)
    filas_p = [["Sin redondear", "", "", num(n_unicos_crudos)]] + [[f"{dec} decimales", f"{10 ** -dec:g}°", f"{111320 * 10 ** -dec:,.1f} m", num(prec[dec])]
               for dec in [6, 5, 4, 3, 2]]
    add_para(doc,
        "El ruido, en el sentido de la sesión 9, son variaciones muy pequeñas alrededor de un mismo "
        "valor, como dos registros del mismo lugar cuyas coordenadas difieren en el quinto o sexto "
        "decimal. Para quitarlo cuanticé las coordenadas, es decir, las redondeé a una precisión "
        "fija. Para escoger la precisión revisé cuántos puntos distintos quedan con cada número de "
        "decimales (Tabla 1).", keep=True)
    make_table(doc, ["Redondeo", "Paso", "Distancia aproximada", "Puntos distintos"], filas_p,
               "Tabla 1. Puntos distintos según el número de decimales de las coordenadas.",
               [1.4, 0.9, 1.5, 1.4], hl=3)
    add_para(doc,
        f"Sin redondear hay {num(n_unicos_crudos)} coordenadas distintas, pero con solo 6 decimales "
        f"bajan a {num(prec[6])}: casi 900 puntos se distinguían únicamente en decimales que "
        f"equivalen a menos de un metro. De 6 a 4 decimales el cambio es pequeño ({num(prec[6])} "
        f"contra {num(prec[4])}): las diferencias más allá del cuarto decimal, de menos de 11 metros, son "
        "las ligeras variaciones que corresponden a ruido. Con 3 decimales ya se juntarían lugares "
        "separados por unos 111 metros y se perdería estructura del fenómeno. Por eso redondeé a 4 "
        "decimales.")
    add_heading(doc, "2.3 Redundancia: agrupación de coordenadas repetidas", level=2)
    add_para(doc,
        f"Después de redondear quedan {num(n_q)} coordenadas distintas para {num(n_total)} registros; "
        f"{num(n_rep)} de ellas aparecen más de una vez y la más repetida aparece {max_rep} veces. "
        "Los registros repetidos no dicen nada nuevo sobre dónde está el fenómeno, solo cuántas veces "
        "ocurrió en ese lugar. Por eso los junté en un solo punto y le asigné un peso w_i igual al "
        "número de registros que representa (Figura 1). Así el conjunto baja de "
        f"{num(n_total)} a {num(n_q)} puntos, un {(1 - n_q / n_total) * 100:.1f} % menos, sin perder la "
        "frecuencia.")
    add_pic(doc, p_dat, 6.4)
    add_caption(doc, "Figura 1. Fenómeno X original (izquierda) y después de quitar ruido y redundancia "
                     "(derecha), donde el tamaño de cada punto es su peso.")
    add_heading(doc, "2.4 K-medias modificado para datos agrupados", level=2)
    add_para(doc,
        "Como cada punto ahora representa varios registros, el algoritmo tiene que considerar su peso. "
        "Siguiendo la sesión 10, la modificación está en el re-centrado: cada centroide se calcula "
        "como la media ponderada de sus puntos, c_j = Σ w_i x_i / Σ w_i, de modo que se minimiza "
        "Σ w_i ‖x_i − c_j‖². La asignación al centroide más cercano no cambia, y si todos los pesos "
        "valen 1 se recupera el algoritmo estándar. Programé el algoritmo con NumPy y lo comparé "
        "contra scikit-learn con pesos y los mismos centroides iniciales: la J ponderada de mi "
        f"versión es {p_k['J']:.6f} y la de scikit-learn {J_sk:.6f} para k = {k_pond}, prácticamente "
        f"iguales (la diferencia es de {abs(p_k['J'] - J_sk) / J_sk * 100:.2f} %).")

    # ---------------- 3
    add_heading(doc, "3. Resultados")
    add_heading(doc, "3.1 Mejor número de agrupaciones", level=2)
    add_pic(doc, p_codo, 6.4)
    add_caption(doc, "Figura 2. Curva de J y proporción between/total de k = 2 a 12 en los dos abordajes.")
    filas_k = [[k, f(R["est"][k]["J"], 3), f"{R['est'][k]['bt'] * 100:.2f} %", f(R["pond"][k]["J"], 3),
                f"{R['pond'][k]['bt'] * 100:.2f} %"] for k in KS]
    make_table(doc, ["k", "J estándar", "between/total estándar", "J modificado", "between/total modificado"],
               filas_k, "Tabla 2. J y variación explicada para cada k en los dos abordajes.",
               [0.5, 1.1, 1.6, 1.2, 1.7], hl=k_est - KS[0])
    gan = [(R["est"][k + 1]["bt"] - R["est"][k]["bt"]) * 100 for k in KS[:-1]]
    add_para(doc,
        f"Con el algoritmo estándar el codo queda en k = {k_est}. Hasta ese punto cada grupo "
        f"adicional explica bastante más variación (de 2 a 3 grupos se ganan {gan[0]:.1f} puntos "
        f"porcentuales y de {k_est - 1} a {k_est}, {gan[k_est - 3]:.1f}), y después las ganancias bajan "
        f"a {gan[k_est - 2]:.1f}, {gan[k_est - 1]:.1f} y {gan[k_est]:.1f} puntos. Con los datos procesados "
        f"y el algoritmo modificado el codo también queda en k = {k_pond}, y las dos curvas de la "
        "Figura 2 prácticamente se enciman.")
    add_heading(doc, "3.2 Agrupaciones con el mejor k", level=2)
    add_pic(doc, p_g, 6.4)
    add_caption(doc, f"Figura 3. Agrupaciones con k = {k_est}. Los triángulos rojos son los centroides "
                     "iniciales, iguales en los dos abordajes, y las cruces son los centroides finales.")
    add_para(doc,
        f"Las dos visualizaciones muestran los mismos {k_est} grupos. La proporción between/total es de "
        f"{e_k['bt'] * 100:.2f} % en el estándar y {p_k['bt'] * 100:.2f} % en el modificado, los "
        f"centroides se mueven como máximo {desp_pond:.1f} metros y solo el {ch_pond * 100:.2f} % de los "
        "registros cambia de grupo. Es decir, el algoritmo modificado encuentra la misma estructura que "
        f"el estándar, pero trabajando con {num(n_q)} puntos en lugar de {num(n_total)}.")
    add_heading(doc, "3.3 Comparación con el ejemplo de la clase (k = 7)", level=2)
    add_para(doc,
        "En la sesión 10 el ejemplo se hizo con k = 7 y se comparó el Fenómeno X con y sin redundancia. "
        "Para relacionar mis resultados con ese ejemplo, la Figura 4 agrega un tercer caso: K-medias "
        "estándar sobre los puntos sin redundancia pero sin usar los pesos.", keep=True)
    add_pic(doc, p_7, 6.6)
    add_caption(doc, "Figura 4. Agrupaciones con k = 7: estándar, sin redundancia sin pesos, y sin ruido ni "
                     "redundancia con el algoritmo modificado.")
    add_para(doc,
        f"Con k = 7 el estándar explica {e7['bt'] * 100:.1f} % de la variación, el mismo 84.7 % que se "
        f"mostró en clase. Si se quitan las repeticiones pero no se usan pesos, la proporción sube a "
        f"{s7['bt'] * 100:.1f} %, parecido al 85.3 % de la clase, y los grupos se reacomodan: el "
        f"{ch_sin7 * 100:.1f} % de los registros cambia de grupo y un centroide se mueve hasta "
        f"{desp_sin7:.0f} metros. Esto pasa porque, sin pesos, un lugar donde el fenómeno ocurrió {max_rep} "
        f"veces cuenta igual que uno donde ocurrió una sola vez, y los centroides se desplazan hacia "
        "las zonas dispersas. Con el algoritmo modificado la proporción vuelve a "
        f"{p7['bt'] * 100:.1f} % y la partición es prácticamente la del estándar "
        f"({ch_pond7 * 100:.2f} % de registros que cambian).")

    # ---------------- 4
    add_heading(doc, "4. Comparativa entre los dos abordajes")
    make_table(doc, ["Indicador", "Estándar", "Sin ruido ni redundancia, modificado"],
               [["Puntos que procesa el algoritmo", num(n_total), num(n_q)],
                ["Mejor k (criterio del codo)", k_est, k_pond],
                ["between/total con el mejor k", f"{e_k['bt'] * 100:.2f} %", f"{p_k['bt'] * 100:.2f} %"],
                ["between/total con k = 7", f"{e7['bt'] * 100:.2f} %", f"{p7['bt'] * 100:.2f} %"],
                ["Iteraciones hasta converger (mejor k)", e_k["it"], p_k["it"]],
                ["Tiempo de ajuste (mejor k)", f"{e_k['seg']:.3f} s", f"{p_k['seg']:.3f} s"],
                ["Registros que cambian de grupo", "referencia", f"{ch_pond * 100:.2f} %"]],
               "Tabla 3. Comparación entre K-medias estándar y K-medias para datos agrupados.",
               [2.8, 1.3, 2.2])
    add_para(doc,
        f"Los dos abordajes llegan al mismo número de agrupaciones (k = {k_est}) y a prácticamente los "
        f"mismos grupos, pero el segundo lo hace con {(1 - n_q / n_total) * 100:.1f} % menos puntos. "
        "Eso reduce el costo de cada iteración, que depende del número de puntos por el número de "
        "grupos, y también el de visualizar los datos. Es lo que se planteó en la sesión 10: manejar "
        "la redundancia reduce el tamaño del conjunto y los recursos que se necesitan para procesarlo.")
    add_para(doc,
        "La comparación con el caso sin pesos muestra la otra parte del planteamiento de la clase: "
        "quitar la redundancia sí modifica la captura de estructuras si las repeticiones simplemente "
        "se eliminan. Al modificar el algoritmo para que use los pesos se conserva la estructura "
        "original, porque cada punto sigue contando tantas veces como registros representa.")

    # ---------------- 5
    add_heading(doc, "5. Conclusiones")
    add_para(doc,
        f"Con el algoritmo estándar el mejor número de agrupaciones del Fenómeno X es k = {k_est}. "
        f"Después de quitar el ruido con la cuantización a 4 decimales y la redundancia con la "
        f"agrupación de coordenadas repetidas, el algoritmo modificado también llega a k = {k_pond}, "
        "con la misma variación explicada y los mismos grupos, pero procesando "
        f"{num(n_q)} puntos en lugar de {num(n_total)}.")
    add_para(doc,
        "Lo que más me llamó la atención fue la diferencia entre quitar las repeticiones con y sin "
        "pesos. Sin pesos la proporción between/total sube un poco, pero porque los grupos cambian y "
        "ya no representan dónde se concentra el fenómeno. Con el re-centrado ponderado se obtiene el "
        "mismo resultado que con todos los datos, así que la reducción de tamaño no tiene costo en la "
        "calidad del agrupamiento.")

    add_heading(doc, "Referencias")
    add_apa(doc, "Lloyd, S. (1982). Least squares quantization in PCM. IEEE Transactions on Information "
                 "Theory, 28(2), 129-137. https://doi.org/10.1109/TIT.1982.1056489")
    add_apa(doc, "Ruiz Chávez, C. F. (2026). Visualización de grandes bases de datos: Sesiones 9 y 10 "
                 "[Diapositivas de clase]. Maestría en Ciencia de los Datos, Centro Universitario de "
                 "Ciencias Económico Administrativas, Universidad de Guadalajara.")
    add_apa(doc, "Satopää, V., Albrecht, J., Irwin, D., & Raghavan, B. (2011). Finding a \"kneedle\" in a "
                 "haystack: Detecting knee points in system behavior. En 31st International Conference on "
                 "Distributed Computing Systems Workshops (pp. 166-171). IEEE. "
                 "https://doi.org/10.1109/ICDCSW.2011.20")
    out = OUT + r"\Tarea1_8_VisualizacionGBD_CarlosPulidoRosas.docx"
    doc.save(out); print("DOCX:", out)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", OUT, out],
                   check=True, capture_output=True)
    print("PDF:", out.replace(".docx", ".pdf"))
    return out


if __name__ == "__main__":
    print("prec", prec, "n_q", n_q, "k_est", k_est, "k_pond", k_pond, "J own", R["pond"][k_pond]["J"], "J sk", J_sk)
    print("bt k7", {e: round(R[e][7]["bt"] * 100, 2) for e in R}, "cambio pond", ch_pond, desp_pond,
          "sin7", ch_sin7, desp_sin7, "pond7", ch_pond7)
    print("iters/time", R["est"][k_est]["it"], R["est"][k_est]["seg"], R["pond"][k_pond]["it"], R["pond"][k_pond]["seg"])
    build()
