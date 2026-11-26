# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - extra analysis of the epoch-160 SSD300 (torch env).

  python analisis_ssd.py pasada     one pass over VOC2007 test, saves every detection (CPU) to
                                    resultados/_dets160.pt (gitignored, ~20 MB)
  python analisis_ssd.py analisis   precision-recall curves per class and AP by object size from that file
  python analisis_ssd.py comparar   same test images with the professor's checkpoint (83) and epoch 160

Object size follows the COCO convention on the original image, in pixels: small < 32x32,
medium 32x32 to 96x96, large > 96x96. For a size bucket, ground-truth objects of other sizes are
ignored (like VOC 'difficult' objects) and unmatched detections whose box falls outside the bucket
are also ignored, so each bucket only scores its own objects.
"""
import json
import os
import random
import sys

import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from evaluar_ssd import cargar, evaluar, crear_listas, PRE, LISTAS, RES, device  # noqa: E402
from utils import rev_label_map  # noqa: E402

DETS = os.path.join(RES, "_dets160.pt")
TAM = {"pequeño": (0, 32 ** 2), "mediano": (32 ** 2, 96 ** 2), "grande": (96 ** 2, 1e12)}


def pasada():
    crear_listas()
    m, _ = cargar("epoca160")
    r = evaluar(m)
    imgs = json.load(open(os.path.join(LISTAS, "TEST_images.json")))
    tam = [Image.open(p).size for p in imgs]                     # (width, height), header only
    torch.save({"crudo": r["_crudo"], "tam": tam, "mAP": r["mAP"]}, DETS)
    print("pasada mAP", round(r["mAP"], 4), flush=True)


def ap11(tp, fp, n_pos):
    ctp = torch.cumsum(torch.tensor(tp, dtype=torch.float), 0)
    cfp = torch.cumsum(torch.tensor(fp, dtype=torch.float), 0)
    prec = ctp / (ctp + cfp + 1e-10); rec = ctp / max(float(n_pos), 1e-10)
    umbrales = torch.arange(start=0, end=1.1, step=.1).tolist()
    ap = float(torch.tensor([prec[rec >= t].max().item() if (rec >= t).any() else 0.0 for t in umbrales]).mean())
    return ap, prec.numpy(), rec.numpy()


def evaluar_clase(c, D, G, cubeta=None):
    """D: list (score, img, box_px); G: {img: (boxes_px, ignore_flags)}. Returns AP, precision, recall."""
    lo, hi = TAM[cubeta] if cubeta else (0, 1e12)
    n_pos = 0; Gc = {}
    for i, (g, dif) in G.items():
        area = (g[:, 2] - g[:, 0]) * (g[:, 3] - g[:, 1])
        ign = (dif == 1) | (area < lo) | (area >= hi)
        Gc[i] = (g, ign); n_pos += int((~ign).sum())
    L = sorted(D, key=lambda t: -t[0]); tp, fp, usado = [], [], set()
    for s, i, bb in L:
        a_det = (bb[2] - bb[0]) * (bb[3] - bb[1])
        fuera = a_det < lo or a_det >= hi
        if i not in Gc:
            if not fuera: tp.append(0); fp.append(1)
            continue
        g, ign = Gc[i]
        ix0 = np.maximum(bb[0], g[:, 0]); iy0 = np.maximum(bb[1], g[:, 1])
        ix1 = np.minimum(bb[2], g[:, 2]); iy1 = np.minimum(bb[3], g[:, 3])
        inter = np.clip(ix1 - ix0, 0, None) * np.clip(iy1 - iy0, 0, None)
        iou = inter / (a_det + (g[:, 2] - g[:, 0]) * (g[:, 3] - g[:, 1]) - inter)
        j = int(np.argmax(iou))
        if iou[j] > 0.5:
            if ign[j]:
                continue
            if (i, j) in usado:
                tp.append(0); fp.append(1)
            else:
                usado.add((i, j)); tp.append(1); fp.append(0)
        elif not fuera:
            tp.append(0); fp.append(1)
    if not tp:
        return 0.0, np.array([]), np.array([]), n_pos
    ap, prec, rec = ap11(tp, fp, n_pos)
    return ap, prec, rec, n_pos


def analisis():
    z = torch.load(DETS, weights_only=False)
    db, dl, ds, tb, tl, td = z["crudo"]; tam = z["tam"]
    objs = json.load(open(os.path.join(LISTAS, "TEST_objects.json")))   # boxes in original pixels
    clases = range(1, len(rev_label_map))
    D = {c: [] for c in clases}; G = {c: {} for c in clases}
    for i, (b, l, s) in enumerate(zip(db, dl, ds)):
        w, h = tam[i]; esc = np.array([w, h, w, h], dtype=np.float32)
        for bb, ll, ss in zip(b.numpy(), l.numpy(), s.numpy()):
            if int(ll) != 0:
                D[int(ll)].append((float(ss), i, bb * esc))
        o = objs[i]
        gb = np.array(o["boxes"], dtype=np.float32); gl = np.array(o["labels"]); gd = np.array(o["difficulties"])
        for c in np.unique(gl):
            G[int(c)][i] = (gb[gl == c], gd[gl == c])
    R = {"ap_clase": {}, "pr": {}, "ap_tam": {k: {} for k in TAM}, "n_obj_tam": {k: 0 for k in TAM}}
    for c in clases:
        n = rev_label_map[c]
        ap, prec, rec, _ = evaluar_clase(c, D[c], G[c])
        R["ap_clase"][n] = ap
        idx = np.linspace(0, len(rec) - 1, min(len(rec), 300)).astype(int)
        R["pr"][n] = {"precision": prec[idx].tolist(), "recall": rec[idx].tolist()}
        for k in TAM:
            apk, _, _, npos = evaluar_clase(c, D[c], G[c], k)
            R["ap_tam"][k][n] = apk if npos > 0 else None
            R["n_obj_tam"][k] += npos
    R["map"] = float(np.mean(list(R["ap_clase"].values())))
    R["map_tam"] = {k: float(np.mean([v for v in R["ap_tam"][k].values() if v is not None])) for k in TAM}
    json.dump(R, open(os.path.join(RES, "analisis_160.json"), "w"), indent=1)
    print("mAP", round(R["map"], 4), "por tamaño", {k: round(v, 4) for k, v in R["map_tam"].items()},
          "objetos", R["n_obj_tam"], flush=True)


def comparar(n=4, min_score=0.4):
    """Detections of the professor's checkpoint and of epoch 160 on the same test images."""
    imgs = json.load(open(os.path.join(LISTAS, "TEST_images.json")))
    random.seed(21)
    idx = random.sample(range(len(imgs)), 40)
    out = {"imagenes": [], "epoca83_profesor": [], "epoca160": []}
    for nombre in ("epoca83_profesor", "epoca160"):
        m, _ = cargar(nombre)
        for i in idx:
            im = Image.open(imgs[i]).convert("RGB")
            with torch.no_grad():
                locs, sc = m(PRE(im).unsqueeze(0).to(device))
                b, l, s = m.detect_objects(locs, sc, min_score=min_score, max_overlap=0.45, top_k=200)
            esc = torch.tensor([im.width, im.height, im.width, im.height])
            out[nombre].append([{"clase": rev_label_map[int(c)], "score": float(p), "caja": (bb.cpu() * esc).tolist()}
                                for bb, c, p in zip(b[0], l[0], s[0]) if int(c) != 0])
        del m; torch.cuda.empty_cache()
    out["imagenes"] = [imgs[i] for i in idx]
    json.dump(out, open(os.path.join(RES, "comparacion_83_160.json"), "w"), indent=1)
    print("comparar listo", flush=True)


if __name__ == "__main__":
    {"pasada": pasada, "analisis": analisis, "comparar": comparar}[sys.argv[1]]()
