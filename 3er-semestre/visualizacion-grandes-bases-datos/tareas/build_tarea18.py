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
        f"Para esta tarea usé el Fenómeno X de la sesión 10, que tiene {num(n_total)} registros con la "
        "longitud y la latitud de un fenómeno en la Zona Metropolitana de Guadalajara. En la sesión 9 "
        "vimos que tener muchos datos no significa tener más información, porque es común que haya "
        "redundancia (valores repetidos) y ruido (ligeras variaciones de los valores centrales). Lo que "
        "pide la tarea es encontrar el mejor número de agrupaciones con K-medias estándar, quitar el "
        "ruido y la redundancia, volver a buscar el mejor número de agrupaciones con el algoritmo "
        "modificado para datos agrupados y comparar los dos resultados.")

    # ---------------- 2
    add_heading(doc, "2. Metodología")
    add_heading(doc, "2.1 K-medias estándar", level=2)
    add_para(doc,
        "K-medias forma k grupos buscando que J = Σ Σ ‖x_i − c_j‖², la suma de las distancias "
        "euclidianas al cuadrado de cada punto al centroide de su grupo, sea lo más chica posible. En "
        "cada iteración manda cada punto al centroide más cercano y luego mueve cada centroide al "
        "promedio de sus puntos. Como el resultado depende de dónde empiezan los centroides, usé los "
        "mismos centroides iniciales en los dos abordajes, igual que en el ejemplo de la clase. Son "
        "los triángulos rojos de las gráficas y los elegí con k-means++ sobre los datos originales, "
        "con una semilla fija para que se pueda repetir.")
    add_para(doc,
        "Para el mejor número de agrupaciones probé de 2 a 12 grupos y usé el criterio del codo. Para "
        "no elegirlo a ojo, normalicé la curva de J y tomé la k que queda más lejos de la recta que va "
        "del primer al último punto, que es donde la curva deja de bajar rápido (Satopää et al., 2011). "
        "Además reporto la proporción between/total, la parte de la variación total que explican los "
        "grupos, que fue la medida que usamos en la sesión 10.")
    add_heading(doc, "2.2 Ruido: cuantización de las coordenadas", level=2)
    filas_p = [["Sin redondear", "", "", num(n_unicos_crudos)]] + [
        [f"{dec} decimales", f"{10 ** -dec:.{dec}f}°", f"{111320 * 10 ** -dec:,.1f} m", num(prec[dec])]
        for dec in [6, 5, 4, 3, 2]]
    add_para(doc,
        "Tomé el ruido como lo definimos en la sesión 9: variaciones muy pequeñas alrededor de un "
        "mismo valor. En estos datos eso se ve en registros que son prácticamente el mismo lugar pero "
        "cuyas coordenadas cambian en el quinto o sexto decimal. Para quitarlo cuanticé las "
        "coordenadas, o sea, las redondeé a una precisión fija. Antes de decidir cuántos decimales "
        "dejar, conté cuántos puntos distintos quedan con cada opción (Tabla 1).", keep=True)
    make_table(doc, ["Redondeo", "Paso", "Distancia aproximada", "Puntos distintos"], filas_p,
               "Tabla 1. Puntos distintos según el número de decimales de las coordenadas.",
               [1.4, 1.0, 1.5, 1.4], hl=3)
    add_para(doc,
        f"Sin redondear hay {num(n_unicos_crudos)} coordenadas distintas, y con 6 decimales ya bajan a "
        f"{num(prec[6])}. Eso quiere decir que casi 900 puntos solo se distinguían por diferencias de "
        f"menos de un metro. De 6 a 4 decimales el cambio es chico ({num(prec[6])} contra "
        f"{num(prec[4])}), así que lo que hay después del cuarto decimal, menos de 11 metros, lo tomé "
        "como ruido. Con 3 decimales ya se juntarían lugares que están a unos 111 metros entre sí, y "
        "con 2 quedarían apenas 143 puntos para toda la zona, lo que borraría la forma del fenómeno. "
        "Por eso me quedé con 4 decimales.")
    add_heading(doc, "2.3 Redundancia: agrupación de coordenadas repetidas", level=2)
    add_para(doc,
        f"Ya redondeados, los {num(n_total)} registros caen en {num(n_q)} coordenadas distintas. De "
        f"ellas, {num(n_rep)} se repiten y la que más se repite aparece {max_rep} veces. Que un mismo "
        "punto aparezca muchas veces no dice nada nuevo sobre dónde está el fenómeno, solo cuántas "
        "veces pasó ahí. Entonces junté cada coordenada repetida en un solo punto con un peso w_i igual "
        f"al número de registros que representa (Figura 1). El conjunto pasa de {num(n_total)} a "
        f"{num(n_q)} puntos, {(1 - n_q / n_total) * 100:.1f} % menos, y la frecuencia queda guardada "
        "en el peso.")
    add_pic(doc, p_dat, 6.4)
    add_caption(doc, "Figura 1. Fenómeno X original (izquierda) y después de quitar ruido y redundancia "
                     "(derecha), donde el tamaño de cada punto es su peso.")
    add_heading(doc, "2.4 K-medias modificado para datos agrupados", level=2)
    add_para(doc,
        "Si a estos puntos les aplicara el algoritmo estándar, una coordenada que representa "
        f"{max_rep} registros contaría lo mismo que una que representa uno. La modificación que vimos "
        "en la sesión 10 está en el re-centrado: cada centroide se calcula como la media ponderada de "
        "sus puntos, c_j = Σ w_i x_i / Σ w_i, y lo que se minimiza es Σ w_i ‖x_i − c_j‖². La asignación "
        "de cada punto al centroide más cercano queda igual, y si todos los pesos valen 1 se regresa "
        "al algoritmo estándar.")
    add_para(doc,
        "Hay una razón por la que esta versión debería dar casi lo mismo que el estándar: el promedio "
        "de 10 registros en el mismo lugar es igual a ese lugar con peso 10. La única diferencia viene "
        "del redondeo, que mueve cada punto unos metros como máximo. Programé el algoritmo con NumPy y "
        "lo comparé contra scikit-learn con pesos y los mismos centroides iniciales; para k = "
        f"{k_pond} la J ponderada de mi versión es {p_k['J']:.6f} y la de scikit-learn {J_sk:.6f}, una "
        f"diferencia de {abs(p_k['J'] - J_sk) / J_sk * 100:.2f} %.")

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
        f"Con el algoritmo estándar el codo queda en k = {k_est}. Hasta ahí cada grupo nuevo explica "
        f"bastante más variación: de 2 a 3 grupos se ganan {gan[0]:.1f} puntos porcentuales y de "
        f"{k_est - 1} a {k_est} todavía {gan[k_est - 3]:.1f}. Después las ganancias bajan a "
        f"{gan[k_est - 2]:.1f}, {gan[k_est - 1]:.1f} y {gan[k_est]:.1f} puntos, así que agregar grupos ya "
        f"aporta poco. Con los datos procesados y el algoritmo modificado el codo vuelve a caer en "
        f"k = {k_pond}; en la Figura 2 las dos curvas van una encima de la otra.")
    add_heading(doc, "3.2 Agrupaciones con el mejor k", level=2)
    add_pic(doc, p_g, 6.4)
    add_caption(doc, f"Figura 3. Agrupaciones con k = {k_est}. Los triángulos rojos son los centroides "
                     "iniciales, iguales en los dos abordajes, y las cruces son los centroides finales.")
    add_para(doc,
        f"En las dos visualizaciones aparecen los mismos {k_est} grupos. La proporción between/total es "
        f"de {e_k['bt'] * 100:.2f} % en el estándar y {p_k['bt'] * 100:.2f} % en el modificado, el "
        f"centroide que más se mueve lo hace {desp_pond:.0f} metros y solo el {ch_pond * 100:.2f} % de "
        "los registros cambia de grupo. El algoritmo modificado llega a la misma estructura que el "
        f"estándar, pero trabajando con {num(n_q)} puntos en lugar de {num(n_total)}.")
    add_heading(doc, "3.3 Comparación con el ejemplo de la clase (k = 7)", level=2)
    add_para(doc,
        "En la sesión 10 el ejemplo se hizo con k = 7, comparando el Fenómeno X con y sin redundancia. "
        "Para poder relacionar mis resultados con ese ejemplo agregué un tercer caso en la Figura 4: "
        "K-medias estándar sobre los puntos sin repetir, pero sin pesos.", keep=True)
    add_pic(doc, p_7, 6.6)
    add_caption(doc, "Figura 4. Agrupaciones con k = 7: estándar, sin redundancia sin pesos, y sin ruido ni "
                     "redundancia con el algoritmo modificado.")
    add_para(doc,
        f"Con k = 7 el estándar explica {e7['bt'] * 100:.1f} % de la variación, el mismo valor que se "
        f"mostró en clase. Quitando las repeticiones sin usar pesos, la proporción sube a "
        f"{s7['bt'] * 100:.1f} %, cerca del 85.3 % de la clase, pero los grupos cambian bastante: el "
        f"{ch_sin7 * 100:.1f} % de los registros queda en otro grupo y un centroide se mueve "
        f"{desp_sin7 / 1000:.1f} km. La razón es que, sin pesos, el lugar donde el fenómeno ocurrió "
        f"{max_rep} veces cuenta igual que uno donde ocurrió una vez, y los centroides se van hacia las "
        "zonas con puntos dispersos. Con el algoritmo modificado la proporción regresa a "
        f"{p7['bt'] * 100:.1f} % y la partición es la misma del estándar salvo por el "
        f"{ch_pond7 * 100:.2f} % de los registros.")

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
        f"Los dos abordajes llegan al mismo número de agrupaciones (k = {k_est}) y a los mismos grupos, "
        f"pero el segundo usa {(1 - n_q / n_total) * 100:.1f} % menos puntos. Como cada iteración "
        "calcula la distancia de cada punto a cada centroide, menos puntos significan menos cálculos, "
        "y también una gráfica más fácil de dibujar y de leer. Con estos 7 mil registros la diferencia "
        f"de tiempo es de milésimas ({e_k['seg']:.3f} contra {p_k['seg']:.3f} segundos), pero en una "
        "base de millones de registros con muchas repeticiones sería mucho más notoria.")
    add_para(doc,
        "El caso sin pesos explica la otra parte de lo que vimos en clase: quitar la redundancia sí "
        "cambia las estructuras que encuentra el algoritmo cuando las repeticiones simplemente se "
        "borran. Cuando el algoritmo se modifica para usar los pesos, la estructura se conserva, porque "
        "cada punto sigue contando tantas veces como registros representa.")

    # ---------------- 5
    add_heading(doc, "5. Conclusiones")
    add_para(doc,
        f"El mejor número de agrupaciones del Fenómeno X con el algoritmo estándar es k = {k_est}. "
        f"Después de quitar el ruido redondeando a 4 decimales y la redundancia juntando las "
        f"coordenadas repetidas, el algoritmo modificado también da k = {k_pond}, con la misma variación "
        f"explicada y los mismos grupos, pero con {num(n_q)} puntos en lugar de {num(n_total)}.")
    add_para(doc,
        "Me quedo con la comparación entre quitar las repeticiones con y sin pesos. A primera vista el "
        "caso sin pesos parece mejor porque su between/total es un poco más alto, pero es mejor solo en "
        "apariencia: los grupos cambian y dejan de reflejar dónde se concentra el fenómeno. Con el "
        "re-centrado ponderado la reducción del tamaño no le cuesta nada a la calidad del agrupamiento, "
        "que es justo lo que se busca al trabajar con datos agrupados.")

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
