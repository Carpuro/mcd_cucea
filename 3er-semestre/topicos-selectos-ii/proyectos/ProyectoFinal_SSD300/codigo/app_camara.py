# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - SSD300 detector with camera, image upload or VOC example (Streamlit).
Complements the team's marimo app on molab: this one runs locally and can use the laptop camera.

    conda run -n torch streamlit run app_camara.py
"""
import json
import os
import sys
import time

import streamlit as st
import torch
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model  # noqa: E402,F401  (needed to unpickle the checkpoints)
from utils import rev_label_map  # noqa: E402

PROY = os.path.dirname(HERE)
MODELOS = {"Época 160 (mejor, mAP 75.19 %)": "checkpoint_ssd300_epoch160_rtxpro6000.pth.tar",
           "Época 83 (checkpoint del profesor, mAP 66.91 %)": "checkpoint_ssd300.pth.tar"}
LISTAS = os.path.join(PROY, "..", "..", "datos", "voc", "listas", "TEST_images.json")
ES = {"aeroplane": "avión", "bicycle": "bicicleta", "bird": "ave", "boat": "bote", "bottle": "botella",
      "bus": "autobús", "car": "auto", "cat": "gato", "chair": "silla", "cow": "vaca",
      "diningtable": "mesa", "dog": "perro", "horse": "caballo", "motorbike": "motocicleta",
      "person": "persona", "pottedplant": "planta", "sheep": "oveja", "sofa": "sofá", "train": "tren",
      "tvmonitor": "monitor"}
COLORES = ["#D48C00", "#1F497D", "#C0392B", "#2E8B57", "#8E44AD", "#16A085", "#D35400"]
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PRE = transforms.Compose([transforms.Resize((300, 300)), transforms.ToTensor(),
                          transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


@st.cache_resource
def cargar(archivo):
    ck = torch.load(os.path.join(PROY, "modelos", archivo), map_location="cpu", weights_only=False)
    m = ck["model"].to(device).eval()
    m.priors_cxcy = m.priors_cxcy.to(device)
    return m


def detectar(m, im, min_score, max_overlap):
    t0 = time.time()
    with torch.no_grad():
        locs, sc = m(PRE(im).unsqueeze(0).to(device))
        b, l, s = m.detect_objects(locs, sc, min_score=min_score, max_overlap=max_overlap, top_k=200)
    ms = (time.time() - t0) * 1000
    esc = torch.tensor([im.width, im.height, im.width, im.height])
    det = [(ES[rev_label_map[int(c)]], float(p), (bb.cpu() * esc).tolist())
           for bb, c, p in zip(b[0], l[0], s[0]) if int(c) != 0]
    return det, ms


def dibujar(im, det):
    im = im.copy(); d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("calibrib.ttf", max(14, im.width // 45))
    except OSError:
        f = ImageFont.load_default()
    clases = sorted({c for c, _, _ in det})
    for c, p, (x0, y0, x1, y1) in det:
        col = COLORES[clases.index(c) % len(COLORES)]
        d.rectangle([x0, y0, x1, y1], outline=col, width=max(2, im.width // 250))
        txt = f"{c} {p:.2f}"; tb = d.textbbox((x0, y0), txt, font=f)
        d.rectangle([tb[0], tb[1], tb[2] + 6, tb[3] + 4], fill=col)
        d.text((x0 + 3, y0 + 1), txt, fill="white", font=f)
    return im


st.set_page_config(page_title="Detector SSD300", layout="wide")
st.title("Detector de objetos SSD300 · PASCAL VOC")
st.caption("Versión local del detector del proyecto: usa la cámara de la computadora, una imagen propia "
           "o una imagen de prueba de VOC2007. Reconoce las 20 clases de PASCAL VOC.")
with st.sidebar:
    nombre = st.selectbox("Modelo", list(MODELOS))
    min_score = st.slider("Umbral de confianza (min_score)", 0.05, 0.95, 0.40, 0.05)
    max_overlap = st.slider("Solape máximo de NMS (max_overlap)", 0.10, 0.90, 0.45, 0.05)
    st.caption(f"Dispositivo: {device}")
m = cargar(MODELOS[nombre])

FUENTES = ["Cámara", "Subir imagen", "Ejemplo de VOC2007 test"]
inicio = 2 if st.query_params.get("fuente") == "voc" else 0   # ?fuente=voc opens the VOC example directly
fuente = st.radio("Fuente de la imagen", FUENTES, index=inicio, horizontal=True)
im = None
if fuente == "Cámara":
    foto = st.camera_input("Toma una foto")
    if foto is not None:
        im = Image.open(foto).convert("RGB")
elif fuente == "Subir imagen":
    arch = st.file_uploader("Imagen JPG o PNG", type=["jpg", "jpeg", "png"])
    if arch is not None:
        im = Image.open(arch).convert("RGB")
elif os.path.exists(LISTAS):
    imgs = json.load(open(LISTAS))
    k = st.number_input("Número de imagen de prueba", 0, len(imgs) - 1, int(st.query_params.get("img", 132)))
    im = Image.open(imgs[int(k)]).convert("RGB")

if im is None:
    st.info("Toma una foto o sube una imagen para ver las detecciones.")
else:
    det, ms = detectar(m, im, min_score, max_overlap)
    c1, c2 = st.columns([3, 1])
    c1.image(dibujar(im, det), use_container_width=True)
    c2.metric("Objetos detectados", len(det))
    c2.metric("Tiempo de detección", f"{ms:.0f} ms")
    if det:
        c2.dataframe({"Clase": [c for c, _, _ in det], "Confianza": [round(p, 2) for _, p, _ in det]},
                     hide_index=True)
