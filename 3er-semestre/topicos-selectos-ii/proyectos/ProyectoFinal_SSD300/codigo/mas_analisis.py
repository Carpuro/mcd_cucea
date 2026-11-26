# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - more analysis for the report (torch env).

  python mas_analisis.py perdidas   MultiBox loss (confidence and localization) of the 5 checkpoints
                                    on the first 1,000 VOC2007 test images
  python mas_analisis.py ficha      parameters, file size, GPU/CPU speed and GPU memory of the model
  python mas_analisis.py errores    error types and precision/recall by threshold (from _dets160.pt)
  python mas_analisis.py cajas      prior matching and box regression on one test image (figure)
Results go to resultados/mas_analisis.json (each step updates its own key).
"""
import json
import os
import sys
import time

import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from model import MultiBoxLoss  # noqa: E402
from utils import rev_label_map, find_jaccard_overlap, cxcy_to_xy, xy_to_cxcy, cxcy_to_gcxgcy, gcxgcy_to_cxcy  # noqa: E402
from datasets import PascalVOCDataset  # noqa: E402
from evaluar_ssd import MODELOS, LISTAS, RES, PRE, device  # noqa: E402

SALIDA = os.path.join(RES, "mas_analisis.json")
CKPTS = [(83, "checkpoint_ssd300.pth.tar"), (100, "checkpoint_ssd300_epoch100.pth.tar"),
         (130, "checkpoint_ssd300_epoch130.pth.tar"), (160, "checkpoint_ssd300_epoch160_rtxpro6000.pth.tar"),
         (190, "checkpoint_ssd300_epoch190_b300.pth.tar")]


def leer():
    return json.load(open(SALIDA, encoding="utf-8")) if os.path.exists(SALIDA) else {}


def escribir(clave, valor):
    R = leer(); R[clave] = valor
    json.dump(R, open(SALIDA, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def cargar_archivo(archivo):
    ck = torch.load(os.path.join(MODELOS, archivo), map_location="cpu", weights_only=False)
    m = ck["model"].to(device).eval(); m.priors_cxcy = m.priors_cxcy.to(device)
    return m


def perdidas(n=1000):
    ds = PascalVOCDataset(LISTAS, split="test", keep_difficult=True)
    dl = torch.utils.data.DataLoader(torch.utils.data.Subset(ds, range(n)), batch_size=16, shuffle=False,
                                     collate_fn=ds.collate_fn, num_workers=1)
    out = {}
    for ep, archivo in CKPTS:
        m = cargar_archivo(archivo)
        total = MultiBoxLoss(m.priors_cxcy, alpha=1.); solo_conf = MultiBoxLoss(m.priors_cxcy, alpha=0.)
        st, sc, nb = 0.0, 0.0, 0
        with torch.no_grad():
            for images, boxes, labels, _ in dl:
                images = images.to(device)
                boxes = [b.to(device) for b in boxes]; labels = [l.to(device) for l in labels]
                locs, scores = m(images)
                st += total(locs, scores, boxes, labels).item(); sc += solo_conf(locs, scores, boxes, labels).item(); nb += 1
        out[str(ep)] = {"total": st / nb, "confianza": sc / nb, "localizacion": (st - sc) / nb}
        print(ep, {k: round(v, 4) for k, v in out[str(ep)].items()}, flush=True)
        del m; torch.cuda.empty_cache()
    escribir("perdidas", {"imagenes": n, "por_epoca": out})


def ficha():
    archivo = CKPTS[3][1]
    m = cargar_archivo(archivo)
    n_par = sum(p.numel() for p in m.parameters())
    partes = {"base_vgg": sum(p.numel() for p in m.base.parameters()),
              "auxiliares": sum(p.numel() for p in m.aux_convs.parameters()),
              "prediccion": sum(p.numel() for p in m.pred_convs.parameters())}
    x = torch.randn(1, 3, 300, 300, device=device)
    torch.cuda.reset_peak_memory_stats()
    with torch.no_grad():
        for _ in range(10): m(x)
        torch.cuda.synchronize(); t0 = time.time()
        for _ in range(100): m(x)
        torch.cuda.synchronize(); gpu_red = 100 / (time.time() - t0)
    mem = torch.cuda.max_memory_allocated() / 2 ** 20
    mc = m.to("cpu"); xc = x.cpu()
    with torch.no_grad():
        for _ in range(3): mc(xc)
        t0 = time.time()
        for _ in range(20): mc(xc)
        cpu_red = 20 / (time.time() - t0)
    escribir("ficha", {"parametros": n_par, "partes": partes,
                       "mb_archivo": os.path.getsize(os.path.join(MODELOS, archivo)) / 2 ** 20,
                       "imgs_seg_gpu_solo_red": gpu_red, "imgs_seg_cpu_solo_red": cpu_red,
                       "mem_gpu_mb": mem, "cpu_hilos": torch.get_num_threads()})
    print(leer()["ficha"], flush=True)


def errores(umbral=0.4):
    """Each detection with score >= umbral is labelled (one pass in score order, like the mAP):
    correcta, duplicada (same object already found), localizacion (right class, IoU 0.1-0.5),
    confusion (IoU >= 0.1 with an object of another class), fondo (no object nearby)."""
    z = torch.load(os.path.join(RES, "_dets160.pt"), weights_only=False)
    db, dl, ds, tb, tl, td = z["crudo"]
    tipos = {"correcta": 0, "duplicada": 0, "localizacion": 0, "confusion": 0, "fondo": 0}
    confus = {}
    prec_rec = {}
    n_easy = int(sum(int((d == 0).sum()) for d in td))
    for u in (0.2, 0.3, 0.4, 0.5, 0.6):
        tp = fp = 0
        for b, l, s, gb, gl, gd in zip(db, dl, ds, tb, tl, td):
            k = (s >= u) & (l != 0)
            if k.sum() == 0: continue
            bb, ll, ss = b[k], l[k], s[k]; o = torch.argsort(ss, descending=True); bb, ll = bb[o], ll[o]
            iou = find_jaccard_overlap(bb, gb) if gb.size(0) else torch.zeros(len(bb), 0)
            usado = set()
            for i in range(len(bb)):
                mism = (gl == ll[i])
                cand = iou[i].clone(); cand[~mism] = -1
                j = int(torch.argmax(cand)) if cand.numel() else -1
                if j >= 0 and cand[j] > 0.5:
                    if gd[j] == 1: continue
                    if j in usado:
                        fp += 1; t = "duplicada"
                    else:
                        usado.add(j); tp += 1; t = "correcta"
                else:
                    fp += 1
                    if j >= 0 and cand[j] >= 0.1: t = "localizacion"
                    elif iou[i].numel() and iou[i].max() >= 0.1:
                        t = "confusion"; jj = int(torch.argmax(iou[i]))
                        par = (rev_label_map[int(ll[i])], rev_label_map[int(gl[jj])])
                        if u == umbral: confus[par] = confus.get(par, 0) + 1
                    else: t = "fondo"
                if u == umbral: tipos[t] += 1
        prec_rec[str(u)] = {"precision": tp / max(tp + fp, 1), "recall": tp / n_easy, "detecciones": tp + fp}
    top = sorted(confus.items(), key=lambda t: -t[1])[:8]
    escribir("errores", {"umbral": umbral, "tipos": tipos, "confusiones": [[a, b, n] for (a, b), n in top],
                         "umbrales": prec_rec, "objetos_faciles": n_easy})
    print(tipos, top[:5], {k: {a: round(b, 3) for a, b in v.items()} for k, v in prec_rec.items()}, flush=True)


def cajas(idx=1503):
    """Priors matched to each object of one test image and the regression of the best prior."""
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.family": "Calibri", "font.size": 10})
    imgs = json.load(open(os.path.join(LISTAS, "TEST_images.json")))
    objs = json.load(open(os.path.join(LISTAS, "TEST_objects.json")))[idx]
    im = Image.open(imgs[idx]).convert("RGB"); W, H = im.size
    m = cargar_archivo(CKPTS[3][1])
    pri_cxcy = m.priors_cxcy; pri_xy = cxcy_to_xy(pri_cxcy).clamp(0, 1)
    gt = torch.tensor(objs["boxes"], dtype=torch.float, device=device) / torch.tensor([W, H, W, H], device=device)
    iou = find_jaccard_overlap(gt, pri_xy)                       # (n_obj, 8732)
    with torch.no_grad():
        locs, scores = m(PRE(im).unsqueeze(0).to(device))
    mapas = [("conv4_3", 38, 4), ("conv7", 19, 6), ("conv8_2", 10, 6), ("conv9_2", 5, 6), ("conv10_2", 3, 4), ("conv11_2", 1, 4)]
    limites, a = [], 0
    for n, d, b in mapas:
        limites.append((n, a, a + d * d * b)); a += d * d * b

    def mapa_de(k):
        return next(n for n, i0, i1 in limites if i0 <= k < i1)
    info = []
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
    col = ["#D48C00", "#1F497D", "#2E8B57", "#C0392B"]
    for ax in axs:
        ax.imshow(im); ax.set_xticks([]); ax.set_yticks([])
    for o in range(gt.size(0)):
        pos = torch.where(iou[o] > 0.5)[0]; best = int(torch.argmax(iou[o]))
        c = col[o % len(col)]; esc = np.array([W, H, W, H])
        for k in pos.tolist():
            x0, y0, x1, y1 = pri_xy[k].cpu().numpy() * esc
            axs[0].add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=c, lw=0.6, alpha=0.6))
        g = gt[o].cpu().numpy() * esc
        axs[0].add_patch(Rectangle((g[0], g[1]), g[2] - g[0], g[3] - g[1], fill=False, ec="white", lw=2, ls="--"))
        # best prior, target offsets, predicted offsets and decoded box
        meta = cxcy_to_gcxgcy(xy_to_cxcy(gt[o:o + 1]), pri_cxcy[best:best + 1])[0].cpu().numpy()
        pred = locs[0, best].cpu().numpy()
        dec = cxcy_to_xy(gcxgcy_to_cxcy(locs[0, best:best + 1], pri_cxcy[best:best + 1]))[0].cpu().numpy() * esc
        pb = pri_xy[best].cpu().numpy() * esc
        axs[1].add_patch(Rectangle((pb[0], pb[1]), pb[2] - pb[0], pb[3] - pb[1], fill=False, ec=c, lw=1.5, ls=":"))
        axs[1].add_patch(Rectangle((dec[0], dec[1]), dec[2] - dec[0], dec[3] - dec[1], fill=False, ec=c, lw=2.2))
        axs[1].add_patch(Rectangle((g[0], g[1]), g[2] - g[0], g[3] - g[1], fill=False, ec="white", lw=1.5, ls="--"))
        clase = rev_label_map[objs["labels"][o]]
        prob = torch.softmax(scores[0, best], 0)[objs["labels"][o]].item()
        iou_dec = find_jaccard_overlap(torch.tensor(dec / esc, dtype=torch.float, device=device)[None], gt[o:o + 1]).item()
        axs[0].text(g[0] + 3, g[1] + 3, f"{clase}: {len(pos)} priors", fontsize=8, color="white", va="top",
                    weight="bold", path_effects=[pe.withStroke(linewidth=2.5, foreground=c)])
        info.append({"clase": clase, "n_priors_positivos": len(pos), "mejor_prior": best, "mapa": mapa_de(best),
                     "iou_prior": iou[o, best].item(), "iou_prediccion": iou_dec, "prob_clase": prob,
                     "objetivo_g": meta.round(3).tolist(), "predicho_g": pred.round(3).tolist(),
                     "prior_cxcywh": pri_cxcy[best].cpu().numpy().round(3).tolist()})
    axs[0].set_title("Priors con IoU > 0.5 para cada objeto (positivos)", fontsize=9.5)
    axs[1].set_title("Mejor prior (punteado), caja ajustada por la red (sólida) y caja real (blanca)", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "figuras", "fig11_cajas.png"), dpi=200, bbox_inches="tight"); plt.close(fig)
    escribir("cajas", {"imagen": idx, "objetos": info})
    print(json.dumps(info, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    {"perdidas": perdidas, "ficha": ficha, "errores": errores, "cajas": cajas}[sys.argv[1]]()
