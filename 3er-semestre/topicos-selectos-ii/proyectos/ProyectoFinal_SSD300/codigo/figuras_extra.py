# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - extra figures (torch env):
  fig7_comparacion.png  professor's checkpoint (83) vs epoch 160 on the same test images
  fig8_pr.png           precision-recall curves for a few classes (epoch 160)
  fig9_tamano.png       AP by object size (small / medium / large)
Writes resultados/extra.json with the numbers quoted in the report.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.patches import Rectangle
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "resultados"); FIG = os.path.join(RES, "figuras")
LISTAS = os.path.join(os.path.dirname(HERE), "..", "..", "datos", "voc", "listas")
NAVY, AMBER, RED, GREEN, GRIS = "#1F497D", "#D48C00", "#C0392B", "#2E8B57", "#7F7F7F"
plt.rcParams.update({"font.family": "Calibri", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})
ES = {"aeroplane": "avión", "bicycle": "bicicleta", "bird": "ave", "boat": "bote", "bottle": "botella",
      "bus": "autobús", "car": "auto", "cat": "gato", "chair": "silla", "cow": "vaca",
      "diningtable": "mesa", "dog": "perro", "horse": "caballo", "motorbike": "motocicleta",
      "person": "persona", "pottedplant": "planta", "sheep": "oveja", "sofa": "sofá", "train": "tren",
      "tvmonitor": "monitor"}
LBL = {v: k for k, v in json.load(open(os.path.join(RES, "label_map_voc.json"))).items()}
EXTRA = {}


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)


def aciertos(dets, objs):
    """Detections that match a not-yet-matched real object of the same class with IoU > 0.5."""
    usado, ok = set(), []
    for d in sorted(dets, key=lambda t: -t["score"]):
        best, j = 0, -1
        for k, (bx, lb) in enumerate(zip(objs["boxes"], objs["labels"])):
            if LBL[lb] == d["clase"] and k not in usado:
                v = iou(d["caja"], bx)
                if v > best: best, j = v, k
        ok.append(best > 0.5)
        if best > 0.5: usado.add(j)
    return ok


def fig_comparacion(n=3):
    C = json.load(open(os.path.join(RES, "comparacion_83_160.json")))
    imgs = json.load(open(os.path.join(LISTAS, "TEST_images.json")))
    objs = json.load(open(os.path.join(LISTAS, "TEST_objects.json")))
    pos = {p: i for i, p in enumerate(imgs)}
    filas = []
    for k, p in enumerate(C["imagenes"]):
        o = objs[pos[p]]
        a83 = aciertos(C["epoca83_profesor"][k], o); a160 = aciertos(C["epoca160"][k], o)
        filas.append((sum(a160) - sum(a83) - (len(a160) - sum(a160)) + (len(a83) - sum(a83)), k, a83, a160))
    filas.sort(key=lambda t: -t[0])
    elegidas = filas[:n]
    tot = {"bien83": sum(sum(f[2]) for f in filas), "mal83": sum(len(f[2]) - sum(f[2]) for f in filas),
           "bien160": sum(sum(f[3]) for f in filas), "mal160": sum(len(f[3]) - sum(f[3]) for f in filas),
           "imagenes": len(filas), "reales": sum(len(objs[pos[p]]["boxes"]) for p in C["imagenes"])}
    EXTRA["comparacion"] = tot
    fig, axs = plt.subplots(2, n, figsize=(10, 6.2))
    for col, (_, k, a83, a160) in enumerate(elegidas):
        im = Image.open(C["imagenes"][k]).convert("RGB")
        for fila, (nombre, ok, tit) in enumerate([("epoca83_profesor", a83, "Época 83 (profesor)"),
                                                  ("epoca160", a160, "Época 160")]):
            ax = axs[fila, col]; ax.imshow(im); ax.set_xticks([]); ax.set_yticks([])
            dets = sorted(C[nombre][k], key=lambda t: -t["score"])
            for d, bien in zip(dets, ok):
                x0, y0, x1, y1 = d["caja"]; c = GREEN if bien else RED
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=c, lw=2))
                ax.text(x0 + 3, y0 + 3, f"{ES[d['clase']]} {d['score']:.2f}", fontsize=7, color="white",
                        va="top", weight="bold", path_effects=[pe.withStroke(linewidth=2.5, foreground=c)])
            ax.set_title(f"{tit}. Correctas: {sum(ok)}, erróneas: {len(ok) - sum(ok)}", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig7_comparacion.png"), dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_pr():
    A = json.load(open(os.path.join(RES, "analisis_160.json")))
    ap = A["ap_clase"]; orden = sorted(ap, key=lambda c: -ap[c])
    sel = [orden[0], orden[len(orden) // 2], orden[-2], orden[-1]]
    cols = [GREEN, NAVY, AMBER, RED]
    fig, ax = plt.subplots(figsize=(6.6, 4))
    for c, col in zip(sel, cols):
        pr = A["pr"][c]
        ax.plot(pr["recall"], pr["precision"], color=col, lw=2, label=f"{ES[c]} (AP {ap[c] * 100:.1f} %)")
    ax.set_xlabel("Recall (proporción de objetos encontrados)"); ax.set_ylabel("Precisión")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    fig.savefig(os.path.join(FIG, "fig8_pr.png"), dpi=200, bbox_inches="tight"); plt.close(fig)
    EXTRA["pr_clases"] = {c: ap[c] for c in sel}
    EXTRA["pr_max_recall"] = {c: max(A["pr"][c]["recall"]) for c in sel}


def fig_tamano():
    A = json.load(open(os.path.join(RES, "analisis_160.json")))
    k = ["pequeño", "mediano", "grande"]
    v = [A["map_tam"][x] * 100 for x in k]; n = [A["n_obj_tam"][x] for x in k]
    fig, ax = plt.subplots(figsize=(5.6, 3))
    ax.bar([f"{x}\n({m:,} objetos)" for x, m in zip(k, n)], v, color=[RED, AMBER, GREEN])
    for i, x in enumerate(v):
        ax.text(i, x + 1, f"{x:.1f} %", ha="center", fontsize=9)
    ax.set_ylabel("mAP (%)"); ax.set_ylim(0, 100)
    fig.savefig(os.path.join(FIG, "fig9_tamano.png"), dpi=200, bbox_inches="tight"); plt.close(fig)
    EXTRA["map_tam"] = A["map_tam"]; EXTRA["n_obj_tam"] = A["n_obj_tam"]; EXTRA["map_analisis"] = A["map"]
    EXTRA["ap_tam_clase"] = A["ap_tam"]


if __name__ == "__main__":
    fig_comparacion()
    if os.path.exists(os.path.join(RES, "analisis_160.json")):
        fig_pr(); fig_tamano()
    json.dump(EXTRA, open(os.path.join(RES, "extra.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in EXTRA.items() if k != "ap_tam_clase"}, ensure_ascii=False))
