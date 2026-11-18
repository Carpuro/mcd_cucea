# -*- coding: utf-8 -*-
"""
Actividad 5 - figures and summary numbers for the report, read from resultados/ (written by
entrenar_actividad5.py). Runs in the `torch` env because it reads the image cache.
Writes resultados/figuras/*.png and resultados/resumen.json.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "resultados")
FIG = os.path.join(RES, "figuras")
CACHE = os.path.join(HERE, "..", "..", "datos", "pokemon", "cache", "imagenes.pt")
NAVY, AMBER, RED, GREEN, GRIS = "#1F497D", "#D48C00", "#C0392B", "#2E8B57", "#7F7F7F"
plt.rcParams.update({"font.family": "Calibri", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})

J = json.load(open(os.path.join(RES, "resultados.json"), encoding="utf-8"))
info, R = J["info"], J["R"]
clases = info["clases"]
test_idx = json.load(open(os.path.join(RES, "split.json")))["test_idx"]
os.makedirs(FIG, exist_ok=True)


def guardar(fig, nombre):
    p = os.path.join(FIG, nombre)
    fig.savefig(p, dpi=200, bbox_inches="tight"); plt.close(fig)
    return p


def fig_muestras(d):
    """One image per class at 224x224 (EfficientNet) and at 64x64 (what TinyVGG sees)."""
    rng = np.random.default_rng(3)
    elegidas = ["Pikachu", "Charmander", "Bulbasaur", "Squirtle", "Nidoran-f", "Nidorina"]
    y = d["y"].numpy()
    fig, axs = plt.subplots(2, 6, figsize=(9, 3.3))
    for k, c in enumerate(elegidas):
        i = rng.choice(np.where(y == clases.index(c))[0])
        for fila, (x, t) in enumerate([(d["x224"], "224 x 224"), (d["x64"], "64 x 64")]):
            a = axs[fila, k]; a.imshow(x[i].permute(1, 2, 0).numpy()); a.set_xticks([]); a.set_yticks([])
            if fila == 0: a.set_title(c, fontsize=9)
            if k == 0: a.set_ylabel(t, fontsize=9)
    fig.tight_layout()
    return guardar(fig, "fig1_muestras.png")


def fig_conteo():
    fig, a = plt.subplots(figsize=(6, 2.6))
    a.hist(info["conteo"], bins=20, color=NAVY, edgecolor="white")
    a.axvline(np.median(info["conteo"]), color=AMBER, ls="--", lw=1.2)
    a.text(np.median(info["conteo"]) + 1.5, a.get_ylim()[1] * 0.9, f"mediana = {np.median(info['conteo']):.0f}",
           color=AMBER, fontsize=9)
    a.set_xlabel("Imágenes por especie"); a.set_ylabel("Número de especies")
    return guardar(fig, "fig0_conteo.png")


def curvas(ax_l, ax_a, r, color, etiqueta):
    e = np.arange(1, len(r["train_loss"]) + 1)
    ax_l.plot(e, r["train_loss"], color=color, ls="--", lw=1.4, label=f"{etiqueta} entrenamiento")
    ax_l.plot(e, r["test_loss"], color=color, lw=1.8, label=f"{etiqueta} prueba")
    ax_a.plot(e, np.array(r["train_acc"]) * 100, color=color, ls="--", lw=1.4)
    ax_a.plot(e, np.array(r["test_acc"]) * 100, color=color, lw=1.8)


def fig_e1():
    fig, (l, a) = plt.subplots(1, 2, figsize=(9, 3.2))
    curvas(l, a, R["E1"], RED, "E1")
    e = np.arange(1, 11)
    l.plot(e, R["E2"]["test_loss"][:10], color=NAVY, lw=1.8, label="E2 prueba (separación limpia)")
    a.plot(e, np.array(R["E2"]["test_acc"][:10]) * 100, color=NAVY, lw=1.8)
    l.set_title("Pérdida (entropía cruzada)"); a.set_title("Exactitud (%)")
    for ax in (l, a): ax.set_xlabel("Época")
    l.legend(frameon=False, fontsize=8)
    return guardar(fig, "fig2_e1.png")


def fig_e2e3():
    fig, (l, a) = plt.subplots(1, 2, figsize=(9, 3.4))
    curvas(l, a, R["E2"], NAVY, "Con aumento (E2)")
    curvas(l, a, R["E3"], AMBER, "Sin aumento (E3)")
    l.set_title("Pérdida (entropía cruzada)"); a.set_title("Exactitud (%)")
    for ax in (l, a): ax.set_xlabel("Época")
    l.legend(frameon=False, fontsize=8)
    return guardar(fig, "fig3_e2e3.png")


def fig_comparacion():
    fig, (l, a) = plt.subplots(1, 2, figsize=(9, 3.2))
    curvas(l, a, R["E4"], GREEN, "EfficientNet-B0 (E4)")
    e2 = R["E2"]
    a.axhline(max(e2["test_acc"]) * 100, color=NAVY, lw=1, ls=":")
    a.text(3.6, max(e2["test_acc"]) * 100 - 6, "mejor TinyVGG (E2)", color=NAVY, fontsize=8)
    l.set_title("Pérdida (entropía cruzada)"); a.set_title("Exactitud (%)")
    for ax in (l, a): ax.set_xlabel("Época"); ax.set_xticks(range(1, len(R["E4"]["train_loss"]) + 1))
    a.set_ylim(0, 100)
    l.legend(frameon=False, fontsize=8)
    return guardar(fig, "fig4_e4.png")


def por_clase(nombre):
    z = np.load(os.path.join(RES, f"pred_{nombre}.npz"))
    y, p = z["y"], z["p"]
    acc = np.array([(p[y == c] == c).mean() for c in range(len(clases))])
    conf = {}
    for a_, b_ in zip(y, p):
        if a_ != b_: conf[(int(a_), int(b_))] = conf.get((int(a_), int(b_)), 0) + 1
    return y, p, acc, sorted(conf.items(), key=lambda t: -t[1])


def fig_errores(d, nombre):
    """Most frequent confusions of the transfer-learning model, with one example image each."""
    y, p, acc, conf = por_clase(nombre)
    top = conf[:5]
    fig, axs = plt.subplots(2, len(top), figsize=(9, 4))
    yy = d["y"].numpy()
    for k, ((a_, b_), n) in enumerate(top):
        pos = np.where((y == a_) & (p == b_))[0][0]
        i = test_idx[pos]
        j = np.where(yy == b_)[0][0]
        axs[0, k].imshow(d["x224"][i].permute(1, 2, 0).numpy())
        axs[0, k].set_title(f"Real: {clases[a_]}\n({n} de 15 como {clases[b_]})", fontsize=8)
        axs[1, k].imshow(d["x224"][j].permute(1, 2, 0).numpy())
        axs[1, k].set_title(f"Ejemplo de {clases[b_]}", fontsize=8)
        for ax in axs[:, k]: ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    return guardar(fig, "fig5_errores.png")


def main():
    d = torch.load(CACHE)
    rutas = {"conteo": fig_conteo(), "muestras": fig_muestras(d), "e1": fig_e1(), "e2e3": fig_e2e3(),
             "e4": fig_comparacion(), "errores": fig_errores(d, "E4")}
    res = {"figuras": rutas}
    for nombre in ("E2", "E4"):
        y, p, acc, conf = por_clase(nombre)
        orden = np.argsort(acc)
        res[nombre] = {"peores": [(clases[c], float(acc[c])) for c in orden[:8]],
                       "n_perfectas": int((acc == 1).sum()), "n_cero": int((acc == 0).sum()),
                       "confusiones": [(clases[a_], clases[b_], n) for (a_, b_), n in conf[:10]],
                       "corr_conteo_acc": float(np.corrcoef(info["conteo"], acc)[0, 1])}
    json.dump(res, open(os.path.join(RES, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "figuras"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
