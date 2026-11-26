# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - figures for the report. Runs in the `torch` env (needs PIL + matplotlib).
Reads the team's metrics (resultados/metrics_*.json, Modal/L4) and the local evaluation
(resultados/evaluacion_local.json, detecciones_ejemplo.json) and writes resultados/figuras/*.png.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image
import matplotlib.patheffects as pe

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "resultados")
FIG = os.path.join(RES, "figuras")
os.makedirs(FIG, exist_ok=True)
NAVY, AMBER, RED, GREEN, GRIS = "#1F497D", "#D48C00", "#C0392B", "#2E8B57", "#7F7F7F"
plt.rcParams.update({"font.family": "Calibri", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})

M1 = json.load(open(os.path.join(RES, "metrics_100_vs_130.json")))["checkpoints"]
M2 = json.load(open(os.path.join(RES, "metrics_130_160_190.json")))["checkpoints"]
L = json.load(open(os.path.join(RES, "evaluacion_local.json")))
EJ = json.load(open(os.path.join(RES, "detecciones_ejemplo.json")))
AP = {100: M1["epoch100"], 130: M2["epoch130"], 160: M2["epoch160"], 190: M2["epoch190"]}
CLASES = list(AP[160]["AP_by_class"].keys())
ES = {"aeroplane": "avión", "bicycle": "bicicleta", "bird": "ave", "boat": "bote", "bottle": "botella",
      "bus": "autobús", "car": "auto", "cat": "gato", "chair": "silla", "cow": "vaca",
      "diningtable": "mesa", "dog": "perro", "horse": "caballo", "motorbike": "motocicleta",
      "person": "persona", "pottedplant": "planta", "sheep": "oveja", "sofa": "sofá", "train": "tren",
      "tvmonitor": "monitor"}


def guardar(fig, nombre):
    p = os.path.join(FIG, nombre)
    fig.savefig(p, dpi=200, bbox_inches="tight"); plt.close(fig)
    return p


def fig_arquitectura():
    """SSD300 pipeline: VGG-16 base, auxiliary convolutions and the six feature maps that predict."""
    mapas = [("conv4_3", 38, 512, 4, 0.1), ("conv7", 19, 1024, 6, 0.2), ("conv8_2", 10, 512, 6, 0.375),
             ("conv9_2", 5, 256, 6, 0.55), ("conv10_2", 3, 256, 4, 0.725), ("conv11_2", 1, 256, 4, 0.9)]
    fig, ax = plt.subplots(figsize=(10, 4.3)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.6)
    ax.add_patch(FancyBboxPatch((0.1, 1.6), 1.1, 1.4, boxstyle="round,pad=0.03", fc="#EAF0F7", ec=NAVY))
    ax.text(0.65, 2.3, "Imagen\n300 x 300\nx 3", ha="center", va="center", fontsize=9)
    ax.add_patch(FancyBboxPatch((1.5, 1.4), 1.9, 1.8, boxstyle="round,pad=0.03", fc="#D6E2F0", ec=NAVY))
    ax.text(2.45, 2.3, "VGG-16 base\n(preentrenada en\nImageNet)\nfc6 y fc7 pasan a\nconv6 y conv7", ha="center",
            va="center", fontsize=8.5)
    ax.add_patch(FancyBboxPatch((3.7, 1.4), 1.6, 1.8, boxstyle="round,pad=0.03", fc="#FCE4B8", ec=AMBER))
    ax.text(4.5, 2.3, "Convoluciones\nauxiliares\nconv8 a conv11", ha="center", va="center", fontsize=8.5)
    for x0, x1 in ((1.2, 1.5), (3.4, 3.7)):
        ax.annotate("", xy=(x1, 2.3), xytext=(x0, 2.3), arrowprops=dict(arrowstyle="->", color=GRIS))
    total = 0
    for k, (n, d, c, b, s) in enumerate(mapas):
        x = 5.75 + k * 0.72
        h = 0.35 + 1.6 * d / 38
        ax.add_patch(Rectangle((x, 3.0 - h / 2 + 0.5), 0.5, h, fc="#D6E2F0" if k < 2 else "#FCE4B8", ec=NAVY, lw=0.8))
        ax.text(x + 0.25, 4.32, n, ha="center", va="bottom", fontsize=7.5)
        ax.text(x + 0.25, 1.55, f"{d}x{d}\n{b} cajas\nescala {s}", ha="center", va="top", fontsize=7)
        ax.text(x + 0.25, 0.62, f"{d * d * b:,}", ha="center", fontsize=8, color=NAVY, weight="bold")
        total += d * d * b
    ax.text(5.6, 0.62, "priors:", ha="right", fontsize=8, color=NAVY)
    ax.text(10.0, 0.15, f"Total: {total:,} cajas por imagen, cada una con 4 ajustes de posición y 21 puntajes "
            "de clase", ha="right", fontsize=8.5, color=NAVY, weight="bold")
    ax.text(5.75, 4.6, "Mapas que predicen (convoluciones 3x3 de localización y de clase)", fontsize=8.5,
            color=NAVY, weight="bold", va="bottom")
    return guardar(fig, "fig1_arquitectura.png"), total


def fig_map_epocas():
    ep = [83, 100, 130, 160, 190]
    v = [L["evaluaciones"]["epoca83_profesor"]["mAP"]] + [AP[e]["mAP"] for e in (100, 130, 160, 190)]
    fig, ax = plt.subplots(figsize=(7.5, 3.3))
    ax.plot(ep, [x * 100 for x in v], color=NAVY, marker="o", lw=2)
    for e, x in zip(ep, v):
        ax.annotate(f"{x * 100:.2f} %", (e, x * 100), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5)
    ax.scatter([160], [L["evaluaciones"]["epoca160"]["mAP"] * 100], marker="x", color=RED, s=60, zorder=3,
               label="Época 160 evaluada en nuestra RTX 4060")
    gpus = {100: "T4", 130: "L4", 160: "RTX PRO 6000", 190: "B300"}
    for e, g in gpus.items():
        ax.text(e, 60.6, g, ha="center", fontsize=8, color=GRIS)
    ax.set_ylim(60, 80); ax.set_xlabel("Épocas completadas"); ax.set_ylabel("mAP en VOC2007 test (%)")
    ax.set_xticks(ep); ax.legend(frameon=False, fontsize=8, loc="upper left")
    return guardar(fig, "fig2_map_epocas.png")


def fig_ap_clases():
    orden = sorted(CLASES, key=lambda c: AP[160]["AP_by_class"][c])
    fig, ax = plt.subplots(figsize=(8, 5.2))
    y = range(len(orden))
    ax.barh([i + 0.2 for i in y], [AP[130]["AP_by_class"][c] * 100 for c in orden], height=0.38, color="#C9D6E8", label="Época 130")
    ax.barh([i - 0.2 for i in y], [AP[160]["AP_by_class"][c] * 100 for c in orden], height=0.38, color=NAVY, label="Época 160")
    for i, c in enumerate(orden):
        ax.text(AP[160]["AP_by_class"][c] * 100 + 0.8, i - 0.2, f"{AP[160]['AP_by_class'][c] * 100:.1f}", va="center", fontsize=7.5)
    ax.set_yticks(list(y)); ax.set_yticklabels([ES[c] for c in orden])
    ax.axvline(AP[160]["mAP"] * 100, color=AMBER, ls="--", lw=1)
    ax.text(AP[160]["mAP"] * 100 + 0.5, len(orden) - 0.3, f"mAP {AP[160]['mAP'] * 100:.2f} %", color=AMBER, fontsize=8.5)
    ax.set_xlabel("AP (%)"); ax.set_xlim(0, 100); ax.legend(frameon=False, fontsize=8, loc="lower right")
    return guardar(fig, "fig3_ap_clases.png")


def fig_ejemplos(n=6):
    fig, axs = plt.subplots(2, 3, figsize=(10, 6.4))
    for ax, e in zip(axs.ravel(), EJ[:n]):
        ax.imshow(Image.open(e["imagen"]).convert("RGB")); ax.set_xticks([]); ax.set_yticks([])
        for g in e["reales"]:
            x0, y0, x1, y1 = g["caja"]
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="white", lw=1.2, ls="--"))
        for d in e["detecciones"]:
            x0, y0, x1, y1 = d["caja"]
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=AMBER, lw=2))
            # plain text and text bboxes do not render over imshow in this matplotlib build; an outline does
            ax.text(x0 + 3, y0 + 3, f"{ES[d['clase']]} {d['score']:.2f}", fontsize=7, color="white", va="top",
                    weight="bold", path_effects=[pe.withStroke(linewidth=2.5, foreground=AMBER)])
        ax.set_title(f"Detecciones: {len(e['detecciones'])}   Objetos reales: {len(e['reales'])}", fontsize=8.5)
    fig.tight_layout()
    return guardar(fig, "fig4_ejemplos.png")


def fig_nms():
    k = ["0.3", "0.45", "0.6"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(8, 2.8))
    a.bar(k, [L["nms"][x]["mAP"] * 100 for x in k], color=[GRIS, NAVY, GRIS])
    for i, x in enumerate(k):
        a.text(i, L["nms"][x]["mAP"] * 100 + 0.2, f"{L['nms'][x]['mAP'] * 100:.2f}", ha="center", fontsize=8.5)
    lo = min(L["nms"][x]["mAP"] for x in k) * 100
    a.set_ylim(lo - 3, lo + 3); a.set_ylabel("mAP (%)"); a.set_xlabel("max_overlap de NMS")
    b.bar(k, [L["nms"][x]["detecciones"] / 1000 for x in k], color=[GRIS, NAVY, GRIS])
    b.set_ylabel("Detecciones (miles)"); b.set_xlabel("max_overlap de NMS")
    fig.tight_layout()
    return guardar(fig, "fig5_nms.png")


if __name__ == "__main__":
    _, tot = fig_arquitectura()
    print("priors", tot)
    print(fig_map_epocas(), fig_ap_clases(), fig_ejemplos(), fig_nms())
