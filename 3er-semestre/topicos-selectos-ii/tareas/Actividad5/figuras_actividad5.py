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
EJ = {}   # numbers about the example figures, quoted in the report


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


def fig_consola():
    """The real console output of E1 (the repository's setup), as printed by engine.train."""
    lineas = open(os.path.join(HERE, "entrenamiento.log"), encoding="utf-8").read().splitlines()
    i = next(k for k, l in enumerate(lineas) if l.startswith("device"))
    texto = [lineas[i]] + [l for l in lineas[i + 1:] if l.startswith("Epoch")][:10]   # verbatim
    fig, a = plt.subplots(figsize=(9, 2.9))
    fig.patch.set_facecolor("#1E1E1E"); a.set_facecolor("#1E1E1E"); a.axis("off")
    a.text(0.01, 0.98, "\n".join(texto), family="Consolas", fontsize=8.6, color="#D4D4D4",
           va="top", ha="left", transform=a.transAxes, linespacing=1.45)
    return guardar(fig, "fig_consola.png")


def _img(d, j, chico):
    return (d["x64"] if chico else d["x224"])[j].permute(1, 2, 0).numpy()


def fig_predicciones(d):
    """Same 8 random test images: TinyVGG (E2, 64x64) on top and EfficientNet-B0 (E4, 224x224) below.
    Title = prediction and its softmax probability; green if correct, red if wrong."""
    z2 = np.load(os.path.join(RES, "pred_E2.npz")); z4 = np.load(os.path.join(RES, "pred_E4.npz"))
    rng = np.random.default_rng(11)
    pos = rng.choice(len(test_idx), 8, replace=False)
    fig, axs = plt.subplots(2, 8, figsize=(9.6, 3.5))
    for k, q in enumerate(pos):
        j = test_idx[q]
        for fila, (z, chico) in enumerate([(z2, True), (z4, False)]):
            pred, prob = int(z["top5_idx"][q, 0]), float(z["top5_prob"][q, 0])
            ok = pred == int(z["y"][q])
            ax = axs[fila, k]; ax.imshow(_img(d, j, chico)); ax.set_xticks([]); ax.set_yticks([])
            for s_ in ax.spines.values(): s_.set_edgecolor(GREEN if ok else RED); s_.set_linewidth(2.5); s_.set_visible(True)
            ax.set_title(f"{clases[pred]}\n{prob * 100:.0f} %", fontsize=8, color=GREEN if ok else RED)
            if fila == 1: ax.set_xlabel(f"Real: {clases[int(z['y'][q])]}", fontsize=7.5)
    EJ["pred_detalle"] = [{"real": clases[int(z2["y"][q])],
                           "E2": [clases[int(z2["top5_idx"][q, 0])], float(z2["top5_prob"][q, 0])],
                           "E4": [clases[int(z4["top5_idx"][q, 0])], float(z4["top5_prob"][q, 0])]} for q in pos]
    EJ["pred_aciertos"] = {"E2": int((z2["p"][pos] == z2["y"][pos]).sum()),
                           "E4": int((z4["p"][pos] == z4["y"][pos]).sum()), "n": len(pos)}
    axs[0, 0].set_ylabel("TinyVGG\n64 x 64", fontsize=8.5); axs[1, 0].set_ylabel("EfficientNet-B0\n224 x 224", fontsize=8.5)
    fig.tight_layout()
    return guardar(fig, "fig_predicciones.png")


def fig_top5(d):
    """Top-5 probabilities of EfficientNet-B0 for three test images: a sure hit, the most frequent
    confusion and a miss where the right species is still in the top 5."""
    z = np.load(os.path.join(RES, "pred_E4.npz"))
    y, p, ti, tp = z["y"], z["p"], z["top5_idx"], z["top5_prob"]
    _, _, _, conf = por_clase("E4")
    (a_, b_), _ = conf[0]
    bien = np.where((p == y) & (tp[:, 0] > 0.9))[0]
    q1 = bien[np.random.default_rng(5).integers(len(bien))]
    q2 = np.where((y == a_) & (p == b_))[0][0]
    otros = np.where((p != y) & (ti[:, 1:] == y[:, None]).any(1) & (y != a_))[0]
    q3 = otros[np.argmax(tp[otros, 0] < 0.6)] if len(otros) else otros[0]
    EJ["top5"] = [{"real": clases[y[q]], "nombres": [clases[c] for c in ti[q]],
                   "prob": [float(v) for v in tp[q]]} for q in (q1, q2, q3)]
    fig, axs = plt.subplots(2, 3, figsize=(9.2, 4.6), gridspec_kw={"height_ratios": [1.15, 1]})
    for k, q in enumerate([q1, q2, q3]):
        ax = axs[0, k]; ax.imshow(_img(d, test_idx[q], False)); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"Real: {clases[y[q]]}", fontsize=9)
        b = axs[1, k]
        nombres = [clases[c] for c in ti[q]][::-1]; vals = (tp[q] * 100)[::-1]
        colores = [GREEN if c == y[q] else (RED if c == ti[q, 0] else GRIS) for c in ti[q]][::-1]
        b.barh(nombres, vals, color=colores)
        for yy, v in enumerate(vals): b.text(v + 1, yy, f"{v:.1f} %", va="center", fontsize=8)
        b.set_xlim(0, 115); b.set_xticks([]); b.spines["bottom"].set_visible(False); b.tick_params(labelsize=8.5)
    fig.tight_layout()
    return guardar(fig, "fig_top5.png")


def main():
    d = torch.load(CACHE)
    rutas = {"conteo": fig_conteo(), "muestras": fig_muestras(d), "e1": fig_e1(), "e2e3": fig_e2e3(),
             "e4": fig_comparacion(), "errores": fig_errores(d, "E4"), "consola": fig_consola(),
             "predicciones": fig_predicciones(d), "top5": fig_top5(d)}
    res = {"figuras": rutas, "ejemplos": EJ}
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
