# -*- coding: utf-8 -*-
"""Proyecto final Tópicos II - figures from mas_analisis.json (torch env): loss per checkpoint and error types."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "resultados"); FIG = os.path.join(RES, "figuras")
NAVY, AMBER, RED, GREEN, GRIS = "#1F497D", "#D48C00", "#C0392B", "#2E8B57", "#7F7F7F"
plt.rcParams.update({"font.family": "Calibri", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})
A = json.load(open(os.path.join(RES, "mas_analisis.json"), encoding="utf-8"))


def fig_perdidas():
    P = A["perdidas"]["por_epoca"]; ep = sorted(int(k) for k in P)
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.2))
    a.plot(ep, [P[str(e)]["total"] for e in ep], color=NAVY, marker="o", lw=2, label="Total")
    a.plot(ep, [P[str(e)]["confianza"] for e in ep], color=AMBER, marker="o", lw=2, label="Confianza")
    a.set_title("Pérdida MultiBox", fontsize=10); a.set_xlabel("Épocas completadas"); a.set_xticks(ep)
    a.legend(frameon=False, fontsize=8)
    b.plot(ep, [P[str(e)]["localizacion"] for e in ep], color=GREEN, marker="o", lw=2)
    b.set_title("Componente de localización", fontsize=10); b.set_xlabel("Épocas completadas"); b.set_xticks(ep)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig12_perdidas.png"), dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_errores():
    T = A["errores"]["tipos"]
    etiquetas = {"correcta": "Correctas", "localizacion": "Caja mal ubicada", "confusion": "Confusión de clase",
                 "fondo": "Fondo", "duplicada": "Duplicadas"}
    orden = ["correcta", "localizacion", "confusion", "fondo", "duplicada"]
    cols = [GREEN, AMBER, RED, GRIS, NAVY]
    tot = sum(T.values())
    fig, ax = plt.subplots(figsize=(7, 1.5))
    izq = 0
    for k, c in zip(orden, cols):
        v = T[k] / tot * 100
        ax.barh([0], [v], left=izq, color=c, label=f"{etiquetas[k]} ({T[k]:,}, {v:.1f} %)")
        if v > 4:
            ax.text(izq + v / 2, 0, f"{v:.0f} %", ha="center", va="center", color="white", fontsize=9, weight="bold")
        izq += v
    ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_xlabel("% de las detecciones con confianza de al menos 0.4")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.45), ncol=3)
    for s in ("left",): ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(FIG, "fig13_errores.png"), dpi=200, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    fig_perdidas(); fig_errores(); print("ok")
