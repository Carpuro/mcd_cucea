# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - local check of the team's SSD300 (sgrvinod/a-PyTorch-Tutorial-to-Object-Detection).
Runs in the `torch` conda env on the RTX 4060.

1. Builds TEST_images.json / TEST_objects.json from the official VOC2007 test set (same format as
   create_data_lists.py, difficult objects kept, as in the team's evaluation).
2. Evaluates the professor's checkpoint (83 epochs) and Héctor's epoch-160 checkpoint with the
   repository's calculate_mAP (11-point AP, IoU > 0.5, min_score 0.01, max_overlap 0.45, top_k 200).
3. Experiment: NMS overlap threshold (0.30, 0.45, 0.60) on the epoch-160 model.
4. Inference speed (batch of 1) and example detections for the report.
Writes resultados/evaluacion_local.json and resultados/detecciones_ejemplo.json.
"""
import json
import os
import random
import sys
import time

import torch
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model  # noqa: E402,F401  (needed to unpickle the checkpoint)
from utils import parse_annotation, calculate_mAP, rev_label_map  # noqa: E402
from datasets import PascalVOCDataset  # noqa: E402

PROY = os.path.dirname(HERE)
VOC07 = os.path.join(PROY, "..", "..", "datos", "voc", "VOCdevkit", "VOC2007")
LISTAS = os.path.join(PROY, "..", "..", "datos", "voc", "listas")
RES = os.path.join(PROY, "resultados")
MODELOS = os.path.join(PROY, "modelos")
CKPTS = {"epoca83_profesor": "checkpoint_ssd300.pth.tar",
         "epoca160": "checkpoint_ssd300_epoch160_rtxpro6000.pth.tar"}
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def crear_listas():
    """Same output as utils.create_data_lists for the VOC2007 test split."""
    os.makedirs(LISTAS, exist_ok=True)
    if os.path.exists(os.path.join(LISTAS, "TEST_objects.json")):
        return
    ids = open(os.path.join(VOC07, "ImageSets", "Main", "test.txt")).read().split()
    imagenes, objetos, n_obj = [], [], 0
    for i in ids:
        o = parse_annotation(os.path.join(VOC07, "Annotations", i + ".xml"))
        if len(o["boxes"]) == 0:
            continue
        n_obj += len(o["boxes"])
        objetos.append(o)
        imagenes.append(os.path.join(VOC07, "JPEGImages", i + ".jpg"))
    json.dump(imagenes, open(os.path.join(LISTAS, "TEST_images.json"), "w"))
    json.dump(objetos, open(os.path.join(LISTAS, "TEST_objects.json"), "w"))
    print("test images", len(imagenes), "objects", n_obj)


def cargar(nombre):
    ck = torch.load(os.path.join(MODELOS, CKPTS[nombre]), map_location="cpu", weights_only=False)
    m = ck["model"].to(device).eval()
    m.priors_cxcy = m.priors_cxcy.to(device)
    return m, int(ck["epoch"])


def calc_map_rapido(det_boxes, det_labels, det_scores, true_boxes, true_labels, true_difficulties):
    """Same rules as utils.calculate_mAP (VOC2007 11-point AP, IoU > 0.5, a detection matched to a
    difficult object is neither TP nor FP, a second detection of the same object is FP), but on the
    CPU and with the ground truth indexed by image, instead of one GPU sync per detection."""
    import numpy as np
    n_cls = len(rev_label_map)
    gt = {}   # (class, image) -> (boxes, difficult)
    n_easy = np.zeros(n_cls)
    for i, (b, l, d) in enumerate(zip(true_boxes, true_labels, true_difficulties)):
        b, l, d = b.cpu().numpy(), l.cpu().numpy(), d.cpu().numpy()
        for c in np.unique(l):
            k = l == c
            gt[(int(c), i)] = (b[k], d[k].astype(int))
            n_easy[c] += int((d[k] == 0).sum())
    dets = {c: [] for c in range(1, n_cls)}
    for i, (b, l, s) in enumerate(zip(det_boxes, det_labels, det_scores)):
        b, l, s = b.cpu().numpy(), l.cpu().numpy(), s.cpu().numpy()
        for bb, ll, ss in zip(b, l, s):
            if int(ll) != 0:
                dets[int(ll)].append((float(ss), i, bb))
    umbrales = torch.arange(start=0, end=1.1, step=.1).tolist()
    aps = {}
    for c in range(1, n_cls):
        L = sorted(dets[c], key=lambda t: -t[0])
        tp = np.zeros(len(L)); fp = np.zeros(len(L)); usado = {}
        for k, (_, i, bb) in enumerate(L):
            if (c, i) not in gt:
                fp[k] = 1; continue
            g, dif = gt[(c, i)]
            ix0 = np.maximum(bb[0], g[:, 0]); iy0 = np.maximum(bb[1], g[:, 1])
            ix1 = np.minimum(bb[2], g[:, 2]); iy1 = np.minimum(bb[3], g[:, 3])
            inter = np.clip(ix1 - ix0, 0, None) * np.clip(iy1 - iy0, 0, None)
            union = (bb[2] - bb[0]) * (bb[3] - bb[1]) + (g[:, 2] - g[:, 0]) * (g[:, 3] - g[:, 1]) - inter
            iou = inter / union; j = int(np.argmax(iou))
            if iou[j] > 0.5:
                if dif[j] == 0:
                    if not usado.get((i, j)):
                        tp[k] = 1; usado[(i, j)] = True
                    else:
                        fp[k] = 1
            else:
                fp[k] = 1
        # float32 torch tensors, exactly as the repository, so the 11 recall thresholds compare the same way
        ctp = torch.cumsum(torch.tensor(tp, dtype=torch.float), 0)
        cfp = torch.cumsum(torch.tensor(fp, dtype=torch.float), 0)
        prec = ctp / (ctp + cfp + 1e-10); rec = ctp / float(n_easy[c])
        aps[rev_label_map[c]] = float(torch.tensor([prec[rec >= t].max().item() if (rec >= t).any() else 0.0
                                                    for t in umbrales]).mean()) if len(L) else 0.0
    return aps, float(np.mean(list(aps.values())))


def evaluar(m, max_overlap=0.45, min_score=0.01, top_k=200, limite=None):
    ds = PascalVOCDataset(LISTAS, split="test", keep_difficult=True)
    sub = torch.utils.data.Subset(ds, range(limite)) if limite else ds
    dl = torch.utils.data.DataLoader(sub, batch_size=32, shuffle=False, collate_fn=ds.collate_fn,
                                     num_workers=1, pin_memory=True)
    det_b, det_l, det_s, tb, tl, td = [], [], [], [], [], []
    t0 = time.time()
    with torch.no_grad():
        for images, boxes, labels, difficulties in tqdm(dl, leave=False):
            images = images.to(device)
            locs, scores = m(images)
            b, l, s = m.detect_objects(locs, scores, min_score=min_score, max_overlap=max_overlap, top_k=top_k)
            det_b.extend([x.cpu() for x in b]); det_l.extend([x.cpu() for x in l]); det_s.extend([x.cpu() for x in s])
            tb.extend(boxes); tl.extend(labels); td.extend(difficulties)
    t_inf = time.time() - t0
    aps, mAP = calc_map_rapido(det_b, det_l, det_s, tb, tl, td)
    n_det = sum(len(x) for x in det_l)
    return {"mAP": float(mAP), "AP_by_class": {k: float(v) for k, v in aps.items()},
            "segundos": time.time() - t0, "segundos_inferencia": t_inf, "detecciones": int(n_det),
            "imagenes": len(sub), "_crudo": (det_b, det_l, det_s, tb, tl, td)}


def comprobar(n=150):
    """Fast mAP vs the repository's calculate_mAP on the first n test images (repo function on CPU)."""
    import utils
    m, _ = cargar("epoca160")
    r = evaluar(m, limite=n)
    utils.device = torch.device("cpu")
    torch.save(r["_crudo"], os.path.join(RES, "_crudo150.pt"))
    aps_r, map_r = utils.calculate_mAP(*r["_crudo"])
    print("rapido", round(r["mAP"], 6), "repo", round(map_r, 6),
          "max dif clase", max(abs(r["AP_by_class"][k] - aps_r[k]) for k in aps_r), flush=True)


PRE = transforms.Compose([transforms.Resize((300, 300)), transforms.ToTensor(),
                          transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


def velocidad(m, n=200):
    x = torch.randn(1, 3, 300, 300, device=device)
    with torch.no_grad():
        for _ in range(20):
            m(x)
        torch.cuda.synchronize()
        t0 = time.time()
        for _ in range(n):
            locs, sc = m(x)
            m.detect_objects(locs, sc, min_score=0.2, max_overlap=0.45, top_k=200)
        torch.cuda.synchronize()
    return n / (time.time() - t0)


def ejemplos(m, n=8, min_score=0.4):
    imgs = json.load(open(os.path.join(LISTAS, "TEST_images.json")))
    objs = json.load(open(os.path.join(LISTAS, "TEST_objects.json")))
    random.seed(7)
    idx = random.sample(range(len(imgs)), n)
    out = []
    for i in idx:
        im = Image.open(imgs[i]).convert("RGB")
        with torch.no_grad():
            locs, sc = m(PRE(im).unsqueeze(0).to(device))
            b, l, s = m.detect_objects(locs, sc, min_score=min_score, max_overlap=0.45, top_k=200)
        esc = torch.tensor([im.width, im.height, im.width, im.height])
        det = [{"clase": rev_label_map[int(c)], "score": float(p), "caja": (bb.cpu() * esc).tolist()}
               for bb, c, p in zip(b[0], l[0], s[0]) if int(c) != 0]
        gt = [{"clase": rev_label_map[c], "caja": bx, "dificil": int(d)}
              for bx, c, d in zip(objs[i]["boxes"], objs[i]["labels"], objs[i]["difficulties"])]
        out.append({"imagen": imgs[i], "detecciones": det, "reales": gt})
    return out


SALIDA = os.path.join(RES, "evaluacion_local.json")
N_NMS = 1000


def guardar(R):
    json.dump(R, open(SALIDA, "w"), indent=1)


def main():
    """Resumable: every step is saved to evaluacion_local.json as soon as it finishes, and steps
    already in the file are skipped. Pass a step name to run only that one:
    epoca83_profesor, epoca160, nms, ejemplos."""
    solo = sys.argv[1] if len(sys.argv) > 1 else None
    if solo == "comprobar":
        crear_listas(); comprobar(); return
    print("device", device, torch.cuda.get_device_name(0) if device.type == "cuda" else "", flush=True)
    crear_listas()
    R = json.load(open(SALIDA)) if os.path.exists(SALIDA) else \
        {"gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "evaluaciones": {}, "nms": {}}
    for nombre in CKPTS:
        if (solo and solo != nombre) or nombre in R["evaluaciones"]:
            continue
        m, ep = cargar(nombre)
        r = evaluar(m); r.pop("_crudo"); r["checkpoint_epoch"] = ep
        R["evaluaciones"][nombre] = r; guardar(R)
        print(nombre, "epoch", ep, "mAP", round(r["mAP"], 4), "seg", round(r["segundos"]), flush=True)
        del m; torch.cuda.empty_cache()
    if "epoca160" in R["evaluaciones"] and (solo in (None, "nms", "ejemplos")):
        m, _ = cargar("epoca160")
        if solo in (None, "nms"):
            # NMS experiment on the first N_NMS test images (a full pass takes ~23 min on the laptop);
            # the three thresholds use exactly the same images, so they are comparable
            for mo in (0.30, 0.45, 0.60):
                if str(mo) in R["nms"]:
                    continue
                rr = evaluar(m, max_overlap=mo, limite=N_NMS); rr.pop("_crudo")
                R["nms"][str(mo)] = {"mAP": rr["mAP"], "detecciones": rr["detecciones"], "imagenes": rr["imagenes"]}
                guardar(R)
                print("nms", mo, round(rr["mAP"], 4), rr["detecciones"], flush=True)
        if solo in (None, "ejemplos"):
            R["fps"] = velocidad(m); guardar(R)
            json.dump(ejemplos(m), open(os.path.join(RES, "detecciones_ejemplo.json"), "w"), indent=1)
            print("fps", R["fps"], flush=True)
    guardar(R)


if __name__ == "__main__":
    main()
