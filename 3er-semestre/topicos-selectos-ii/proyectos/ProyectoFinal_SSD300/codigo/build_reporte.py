# -*- coding: utf-8 -*-
"""
Proyecto final Tópicos II - team lab report on SSD300 (PASCAL VOC), built on the MCD template.
Runs in the MCD env. Numbers come from resultados/*.json (team metrics from Modal and the local
evaluation on the RTX 4060). Training numbers (times, costs, GPUs) come from Héctor's report
(REPORTE_ENTRENAMIENTO_SSD300_MODAL.md), stored as constants below.
"""
import json
import os
import shutil
import subprocess
import sys

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.dirname(HERE)
VIS = os.path.join(PROY, "..", "..", "..", "visualizacion-grandes-bases-datos", "tareas")
sys.path.insert(0, os.path.abspath(VIS))
from build_tarea16 import (add_para, add_heading, add_caption, add_pic, make_table,  # noqa: E402
                           add_apa, clear_body_after_table1, NAVY, TEMPLATE, SOFFICE, num)

RES = os.path.join(PROY, "resultados"); FIG = os.path.join(RES, "figuras")
NOMBRE = "ProyectoFinal_SSD300_TopicosGBDII"

M1 = json.load(open(os.path.join(RES, "metrics_100_vs_130.json")))["checkpoints"]
M2 = json.load(open(os.path.join(RES, "metrics_130_160_190.json")))["checkpoints"]
L = json.load(open(os.path.join(RES, "evaluacion_local.json")))
EJ = json.load(open(os.path.join(RES, "detecciones_ejemplo.json")))
AP = {100: M1["epoch100"], 130: M2["epoch130"], 160: M2["epoch160"], 190: M2["epoch190"]}
E83 = L["evaluaciones"]["epoca83_profesor"]; E160 = L["evaluaciones"]["epoca160"]
ES = {"aeroplane": "avión", "bicycle": "bicicleta", "bird": "ave", "boat": "bote", "bottle": "botella",
      "bus": "autobús", "car": "auto", "cat": "gato", "chair": "silla", "cow": "vaca",
      "diningtable": "mesa", "dog": "perro", "horse": "caballo", "motorbike": "motocicleta",
      "person": "persona", "pottedplant": "planta en maceta", "sheep": "oveja", "sofa": "sofá",
      "train": "tren", "tvmonitor": "monitor"}

# Héctor's training log (REPORTE_ENTRENAMIENTO_SSD300_MODAL.md, sections 2, 3 and 5)
TRAMOS = [("Base del profesor", "", "83", "22,000", "", ""),
          ("Tramo 1", "Tesla T4", "100", "30,806", "2 h 19 min", "1.37"),
          ("Tramo 2", "L4", "130", "46,346", "2 h 20 min", "1.87"),
          ("Tramo 3", "RTX PRO 6000", "160", "61,886", "~36 min", "1.82"),
          ("Tramo 4", "B300", "190", "77,426", "54 min", "6.48")]
BENCH = [("Tesla T4", "238.9", "1.194", "0.039"), ("L4", "128.0", "0.640", "0.028"),
         ("RTX PRO 6000 Blackwell", "34.7", "0.173", "0.029"), ("B300 SXM6", "107.5", "0.538", "0.212")]
COSTO_TOTAL = "11.85"


def p(x, d=2):
    return f"{x * 100:.{d}f} %"


def pp(x):
    return f"{x * 100:+.2f}"


def cambios(a, b):
    d = {c: AP[b]["AP_by_class"][c] - AP[a]["AP_by_class"][c] for c in AP[a]["AP_by_class"]}
    return sorted(d.items(), key=lambda t: -t[1])


def build():
    figs = {k: os.path.join(FIG, v) for k, v in [
        ("arq", "fig1_arquitectura.png"), ("map", "fig2_map_epocas.png"), ("ap", "fig3_ap_clases.png"),
        ("ej", "fig4_ejemplos.png"), ("nms", "fig5_nms.png"), ("app", "fig6_app_molab.png"),
        ("cmp", "fig7_comparacion.png"), ("pr", "fig8_pr.png"), ("tam", "fig9_tamano.png"), ("local", "fig10_app_local.png")]}
    ap160 = AP[160]["AP_by_class"]
    mejores = sorted(ap160, key=lambda c: -ap160[c])[:3]
    peores = sorted(ap160, key=lambda c: ap160[c])[:3]
    c130 = cambios(130, 160); c160 = cambios(160, 190)
    sube190 = sum(1 for _, v in c160 if v > 0)
    dif_local = E160["mAP"] - AP[160]["mAP"]
    n_det = sum(len(e["detecciones"]) for e in EJ[:6]); n_real = sum(len(e["reales"]) for e in EJ[:6])

    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Tópicos Selectos de Grandes Bases de Datos II"
    for r in hdr.paragraphs[3].runs[1:]: r.text = ""
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Proyecto final. Detección de objetos con SSD300\n"
                   "Entrenamiento, evaluación y demostración sobre PASCAL VOC")
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]; cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]: extra.text = ""
    si(0, "Equipo del proyecto final")
    si(1, "26 de noviembre de 2026")
    si(2, "Proyecto final: detección de objetos con SSD300")
    si(3, "Python, PyTorch, torchvision, marimo (molab), Modal")
    si(4, f"PyTorch {L['torch']}")
    si(5, "Modal (T4, L4, RTX PRO 6000, B300) y equipo local con RTX 4060")
    si(6, "PASCAL VOC 2007 y 2012 (20 clases de objetos)")
    clear_body_after_table1(doc)

    # ------------------------------------------------------------ 1
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción y objetivos")
    add_para(doc,
        "La detección de objetos va un paso más allá de la clasificación de imágenes que vimos con las "
        "redes convolucionales. Ya no basta con decir qué hay en la imagen, también hay que decir dónde "
        "está cada objeto, con una caja delimitadora y una clase para cada uno, aunque haya varios objetos "
        "de distintas clases en la misma foto. En este proyecto trabajamos con SSD300 (Single Shot MultiBox "
        "Detector) usando el tutorial de PyTorch de Vinodababu (2019) que nos dio el profesor, que "
        "implementa el modelo de Liu et al. (2016) y lo entrena con PASCAL VOC (Everingham et al., 2010).")
    add_para(doc,
        "Los objetivos fueron continuar el entrenamiento del modelo a partir del checkpoint del profesor, "
        "comparar el desempeño en distintas épocas y con distintas GPU, explicar cómo funciona la "
        "arquitectura, cómo aprende y cómo ajusta las cajas, evaluarlo con la métrica estándar (mAP) y "
        "construir una interfaz en marimo para probar el detector con imágenes propias.")

    # ------------------------------------------------------------ 2
    add_heading(doc, "2. Metodología y arquitectura del modelo")
    add_heading(doc, "2.1 Datos", level=2)
    add_para(doc,
        "PASCAL VOC tiene 20 clases de objetos comunes: personas, animales (ave, gato, vaca, perro, "
        "caballo, oveja), vehículos (avión, bicicleta, bote, autobús, auto, motocicleta, tren) y objetos "
        "de interior (botella, silla, mesa, planta en maceta, sofá, monitor). Para entrenar se juntan "
        "los conjuntos trainval de VOC2007 y VOC2012, que suman 16,551 imágenes con 47,223 objetos, y se "
        f"evalúa con VOC2007 test, que tiene {num(E160['imagenes'])} imágenes y 14,976 objetos. Cada objeto "
        "tiene su caja (x mínima, y mínima, x máxima, y máxima), su clase y una marca de \"difícil\" para "
        "objetos muy pequeños o tapados, que no cuentan en contra al evaluar.")
    add_heading(doc, "2.2 Arquitectura", level=2)
    add_para(doc,
        "SSD300 recibe imágenes de 300 x 300 píxeles y detecta todo en una sola pasada por la red, a "
        "diferencia de los detectores de dos etapas como Faster R-CNN, que primero proponen regiones y "
        "luego las clasifican. Tiene tres partes (Figura 1). La base es VGG-16 (Simonyan y Zisserman, "
        "2015) preentrenada en ImageNet, a la que se le quitan las capas totalmente conectadas: fc6 y fc7 "
        "se convierten en convoluciones (conv6, con dilatación, y conv7) para conservar la información "
        "espacial. Después vienen las convoluciones auxiliares (conv8 a conv11), que reducen el mapa de "
        "características hasta 1 x 1. Por último, las convoluciones de predicción, de 3 x 3, toman seis "
        "mapas de distintos tamaños y en cada posición predicen la clase y el ajuste de varias cajas.")
    add_pic(doc, figs["arq"], 6.4)
    add_caption(doc, "Figura 1. Arquitectura de SSD300 y número de cajas previas (priors) por mapa de características.")
    add_para(doc,
        "La idea de usar mapas de varios tamaños es que cada uno se encarga de objetos de cierto tamaño. "
        "El mapa conv4_3 (38 x 38) ve detalles finos y sirve para objetos chicos, con cajas de escala 0.1 "
        "respecto a la imagen, mientras que conv11_2 (1 x 1) ve toda la imagen y se encarga de objetos que "
        "la ocupan casi completa (escala 0.9). Como conv4_3 tiene valores de magnitud muy distinta a los "
        "demás, se normaliza con L2 y se multiplica por un factor que también se aprende (inicia en 20).")
    add_heading(doc, "2.3 Cajas previas y cómo se ajustan", level=2)
    add_para(doc,
        "En cada posición de cada mapa la red tiene cajas previas (priors) fijas, centradas en esa "
        "posición, con la escala del mapa y varias proporciones de ancho a alto (1:1, 2:1, 1:2 y en "
        "algunos mapas 3:1 y 1:3, más una caja cuadrada extra de escala intermedia). En total son "
        f"{num(8732)} cajas por imagen (Figura 1). La red no predice las coordenadas directamente: para cada "
        "prior predice cuatro ajustes (g_cx, g_cy, g_w, g_h). El centro se mueve en proporción al tamaño "
        "del prior, g_cx = (c_x − p_cx) / (p_w / 10), y el ancho y alto se ajustan en escala logarítmica, "
        "g_w = 5 log(w / p_w). Así un ajuste pequeño significa una caja parecida al prior, y el modelo "
        "aprende correcciones en lugar de posiciones absolutas.")
    add_para(doc,
        "Para entrenar, cada objeto real se asigna a los priors que más se le parecen según la IoU "
        "(intersección sobre unión, o índice de Jaccard), que mide el área compartida entre dos cajas "
        "dividida entre el área que cubren juntas. Un prior con IoU mayor a 0.5 con algún objeto es "
        "positivo y aprende esa clase y esos ajustes; los demás son negativos (fondo). Además, cada objeto "
        "se asegura su mejor prior aunque la IoU no llegue a 0.5, para que ningún objeto se quede sin "
        "caja asignada.")
    add_heading(doc, "2.4 Cómo aprende: la función de pérdida", level=2)
    add_para(doc,
        "La pérdida MultiBox suma dos partes. La de localización es Smooth L1 entre los ajustes predichos "
        "y los reales, y solo se calcula en los priors positivos, porque al fondo no le corresponde ninguna "
        "caja. La de confianza es entropía cruzada sobre las 21 clases (las 20 de VOC y el fondo). El "
        "problema es que en una imagen normal hay unas cuantas decenas de priors positivos contra miles de "
        "negativos, y si se usaran todos el modelo aprendería a decir siempre \"fondo\". Por eso se usa "
        "minería de negativos difíciles: solo entran a la pérdida los negativos con mayor error, tres por "
        "cada positivo. La pérdida total es L = L_conf + α L_loc con α = 1, dividida entre el número de "
        "positivos.")
    add_para(doc,
        "El optimizador es SGD con tasa de aprendizaje de 0.001 (el doble para los sesgos), momentum de "
        "0.9, decaimiento de pesos de 0.0005 y lotes de 32 imágenes. Para que el modelo vea más variedad, "
        "en entrenamiento cada imagen pasa por aumento de datos: cambios de brillo, contraste, saturación y "
        "tono, un alejamiento (zoom out) con probabilidad de 0.5, un recorte aleatorio que conserve parte "
        "de los objetos, un volteo horizontal con probabilidad de 0.5, el cambio a 300 x 300 y la "
        "normalización con la media y desviación de ImageNet.")
    add_heading(doc, "2.5 Detección y evaluación", level=2)
    add_para(doc,
        f"Al detectar, la red produce {num(8732)} cajas con 21 puntajes cada una. Para cada clase se quitan "
        "las cajas con puntaje menor a un umbral (min_score) y después se aplica supresión de no máximos "
        "(NMS): se toma la caja con mayor puntaje y se eliminan las de la misma clase que se empalman con "
        "ella más que max_overlap, y así sucesivamente. Al final se dejan como máximo top_k = 200 "
        "detecciones por imagen.")
    add_para(doc,
        "La métrica es la precisión promedio media (mAP). Para cada clase se ordenan todas las detecciones "
        "de mayor a menor puntaje; una detección es correcta si su IoU con un objeto real de esa clase que "
        "no se haya detectado antes es mayor a 0.5. Con eso se arma la curva de precisión contra "
        "exhaustividad (recall) y el AP es el promedio de la precisión máxima en 11 niveles de recall (0, "
        "0.1, ..., 1), como en VOC2007. El mAP es el promedio de los 20 AP. Para evaluar se usan "
        "min_score = 0.01, max_overlap = 0.45 y top_k = 200, y los objetos marcados como difíciles no "
        "cuentan como falsos negativos.")

    # ------------------------------------------------------------ 3
    add_heading(doc, "3. Entrenamiento y experimentos")
    add_heading(doc, "3.1 Continuación del entrenamiento en Modal", level=2)
    add_para(doc,
        "El profesor nos dio el modelo entrenado hasta la época 83 (22,000 pasos). Lo continuamos en "
        "Modal, una plataforma que renta GPU por segundo, con un volumen para los datos de VOC y otro para "
        "los checkpoints. Cada época son 518 lotes de 32 imágenes. Aprovechamos que cada tramo necesitaba "
        "una corrida distinta para probar una GPU diferente en cada uno (Tabla 1).")
    make_table(doc, ["Etapa", "GPU", "Épocas completadas", "Pasos acumulados", "Tiempo", "Costo (USD)"],
               [list(t) for t in TRAMOS],
               "Tabla 1. Tramos de entrenamiento en Modal.",
               [1.3, 1.2, 0.9, 1.0, 1.0, 0.8])
    add_para(doc,
        "Antes de los tramos largos hicimos una prueba de 200 lotes con las cuatro GPU en las mismas "
        "condiciones (Tabla 2). La RTX PRO 6000 fue 3.7 veces más rápida que la L4 y, como se cobra por "
        "segundo, costó prácticamente lo mismo. La B300, que es la más cara, quedó en tercer lugar: tardó "
        "64 segundos solo en el primer lote y después pasaba entre 0.12 y 0.14 s por lote esperando a que "
        "llegaran las imágenes del disco, contra 0.02 a 0.03 s en la RTX PRO 6000. El cuello de botella "
        "era la carga de datos, no el cálculo. En total el entrenamiento, las pruebas y las evaluaciones "
        f"costaron alrededor de {COSTO_TOTAL} dólares de GPU, cubiertos por los créditos gratuitos de Modal.")
    make_table(doc, ["GPU", "Tiempo de 200 lotes (s)", "Segundos por lote", "Costo estimado (USD)"],
               [list(b) for b in BENCH], "Tabla 2. Prueba de velocidad de 200 lotes por GPU.",
               [1.9, 1.5, 1.3, 1.5], hl=2)
    add_heading(doc, "3.2 Verificación local de los resultados", level=2)
    add_para(doc,
        "Para confirmar los resultados de Modal descargamos el conjunto oficial VOC2007 test y volvimos a "
        f"evaluar en una laptop con GPU {L['gpu'].replace('NVIDIA GeForce ', '')}, con el mismo código del "
        "repositorio y los mismos parámetros. Con el checkpoint de la época 160 obtuvimos un mAP de "
        f"{p(E160['mAP'])}, contra {p(AP[160]['mAP'])} en Modal (diferencia de "
        f"{abs(dif_local) * 100:.2f} puntos), así que el resultado se reproduce. También evaluamos el "
        f"checkpoint del profesor, que no tenía una evaluación propia, y dio {p(E83['mAP'])}. La evaluación "
        f"completa de las {num(E160['imagenes'])} imágenes tardó {E160['segundos']:.0f} segundos en la "
        f"laptop, y la detección de una sola imagen corre a unos {L['fps']:.0f} cuadros por segundo, lo que "
        "permitiría usarlo con video.")
    add_heading(doc, "3.3 Experimento con el umbral de NMS", level=2)
    nms = L["nms"]
    add_para(doc,
        "El parámetro max_overlap de la supresión de no máximos decide cuánto se pueden empalmar dos "
        "detecciones de la misma clase antes de quedarse solo con la mejor. Con el modelo de la época 160 "
        f"lo probamos en 0.30, 0.45 y 0.60 sobre las primeras {num(nms['0.45']['imagenes'])} imágenes de "
        "prueba, porque cada evaluación completa tardaba más de 10 minutos en la laptop; las tres usan las "
        f"mismas imágenes (Figura 2). Con 0.30 el mAP fue de {p(nms['0.3']['mAP'])}, con 0.45 de "
        f"{p(nms['0.45']['mAP'])} y con 0.60 de {p(nms['0.6']['mAP'])}. Un valor bajo borra detecciones "
        "de objetos que están juntos, como personas en grupo, y un valor alto deja cajas repetidas sobre "
        f"el mismo objeto: las detecciones pasaron de {num(nms['0.3']['detecciones'])} a "
        f"{num(nms['0.6']['detecciones'])}. El valor de 0.45 que usa el repositorio fue el mejor de los "
        "tres.")
    add_pic(doc, figs["nms"], 5.6)
    add_caption(doc, f"Figura 2. mAP y número de detecciones según el umbral de NMS (época 160, primeras "
                     f"{num(nms['0.45']['imagenes'])} imágenes de VOC2007 test).")

    # ------------------------------------------------------------ 4
    X = json.load(open(os.path.join(RES, "extra.json"), encoding="utf-8"))
    cmp_ = X["comparacion"]; mt = X["map_tam"]; nt = X["n_obj_tam"]; prc = X["pr_clases"]; prr = X["pr_max_recall"]
    pr_sel = list(prc)
    add_heading(doc, "4. Resultados y demostración del detector")
    add_heading(doc, "4.1 mAP por época", level=2)
    add_para(doc,
        f"El mAP pasó de {p(E83['mAP'])} en el checkpoint del profesor a {p(AP[100]['mAP'])} en la época "
        f"100, {p(AP[130]['mAP'])} en la 130 y {p(AP[160]['mAP'])} en la 160 (Figura 3). En la época 190 "
        f"bajó un poco, a {p(AP[190]['mAP'])}, así que nos quedamos con el modelo de la época 160. El mayor "
        f"salto fue de la 130 a la 160 ({pp(AP[160]['mAP'] - AP[130]['mAP'])} puntos), en el que subieron "
        "las 20 clases. De la 160 a la 190 solo "
        f"{sube190} clases mejoraron y el resto bajó un poco. Hay que considerar que el train.py tiene "
        "programado bajar la tasa de aprendizaje a la décima parte en el paso 80,000, y el entrenamiento "
        "llegó a 77,426 pasos, así que todo se hizo con la tasa inicial; probablemente con ese ajuste el "
        "modelo todavía podía mejorar. También hay que aclarar que escogimos la mejor época con el mismo "
        "conjunto de prueba, así que el 75 % puede estar un poco optimista.")
    add_pic(doc, figs["map"], 5.4)
    add_caption(doc, "Figura 3. mAP en VOC2007 test por época. La época 83 la evaluamos localmente; las demás son de la evaluación en Modal.")
    add_para(doc,
        "Para ver la mejora en imágenes y no solo en el número, pasamos el checkpoint del profesor y el "
        f"de la época 160 por las mismas {cmp_['imagenes']} imágenes de prueba escogidas al azar, con un "
        f"umbral de 0.4. En esas imágenes hay {cmp_['reales']} objetos reales. El modelo del profesor tuvo "
        f"{cmp_['bien83']} detecciones correctas y {cmp_['mal83']} erróneas, y el de la época 160 tuvo "
        f"{cmp_['bien160']} correctas y {cmp_['mal160']} erróneas. En la Figura 4 están tres de esas "
        "imágenes. El modelo de la época 160 encuentra personas que el del profesor no veía, separa mejor "
        "las dos motocicletas y en la última imagen reconoce al gato, que el modelo del profesor había "
        "marcado como perro, aunque todavía deja también una caja de perro sobre él.")
    add_pic(doc, figs["cmp"], 6.3)
    add_caption(doc, "Figura 4. El mismo detector antes (época 83, arriba) y después (época 160, abajo) del entrenamiento del equipo. Verde: detección correcta (IoU > 0.5 con un objeto real de la misma clase); rojo: errónea.")

    add_heading(doc, "4.2 AP por clase y curvas de precisión contra recall", level=2)
    add_para(doc,
        f"Las clases que mejor detecta el modelo son {ES[mejores[0]]} ({p(ap160[mejores[0]], 1)}), "
        f"{ES[mejores[1]]} ({p(ap160[mejores[1]], 1)}) y {ES[mejores[2]]} ({p(ap160[mejores[2]], 1)}), que "
        "suelen ser objetos grandes y con forma bien definida. Las más bajas son "
        f"{ES[peores[0]]} ({p(ap160[peores[0]], 1)}), {ES[peores[1]]} ({p(ap160[peores[1]], 1)}) y "
        f"{ES[peores[2]]} ({p(ap160[peores[2]], 1)}). Las botellas y las plantas suelen ser pequeñas y "
        "estar al fondo de la escena, y las sillas casi siempre aparecen tapadas por personas o mesas. "
        "Entre las épocas 130 y 160 las que más mejoraron fueron "
        f"{ES[c130[0][0]]} ({pp(c130[0][1])} puntos), {ES[c130[1][0]]} ({pp(c130[1][1])}) y "
        f"{ES[c130[2][0]]} ({pp(c130[2][1])}) (Figura 5).")
    add_pic(doc, figs["ap"], 5.4)
    add_caption(doc, "Figura 5. AP por clase en las épocas 130 y 160.")
    add_para(doc,
        "El AP de cada clase sale de su curva de precisión contra recall (Figura 6). Si se van aceptando "
        "las detecciones de mayor a menor confianza, el recall dice qué parte de los objetos reales ya se "
        "encontró y la precisión qué parte de lo aceptado era correcto. Un detector ideal mantiene la "
        f"precisión en 1 hasta encontrar todo. La curva de {ES[pr_sel[0]]} se queda arriba de 0.9 hasta "
        f"pasar el 80 % de recall y llega a encontrar el {p(prr[pr_sel[0]], 0)} de los gatos. En "
        f"{ES[pr_sel[3]]}, en cambio, la precisión empieza a caer desde el principio y el modelo nunca "
        f"encuentra más del {p(prr[pr_sel[3]], 0)} de las botellas, aunque se acepten detecciones con "
        "confianza de 0.01. El AP resume toda la curva en un número, por eso dos clases con AP parecido "
        "pueden comportarse distinto según el umbral que se use en la aplicación.")
    add_pic(doc, figs["pr"], 4.8)
    add_caption(doc, "Figura 6. Curvas de precisión contra recall de cuatro clases (época 160, VOC2007 test completo).")

    add_heading(doc, "4.3 AP según el tamaño del objeto", level=2)
    add_para(doc,
        "Para comprobar que el problema principal son los objetos pequeños, separamos los objetos de "
        "prueba por su área en la imagen original con el criterio de COCO: pequeños si miden menos de "
        "32 x 32 píxeles, medianos entre 32 x 32 y 96 x 96, y grandes arriba de 96 x 96. En cada grupo "
        "calculamos el mAP ignorando los objetos de los otros tamaños, igual que se hace con los objetos "
        f"difíciles. Con todo el conjunto el cálculo vuelve a dar {p(X['map_analisis'])}, lo que confirma que "
        f"la evaluación es la misma. En objetos grandes el mAP es de {p(mt['grande'], 1)}, en medianos de "
        f"{p(mt['mediano'], 1)} y en pequeños apenas de {p(mt['pequeño'], 1)} (Figura 7). Al reducir la "
        "imagen a 300 x 300 un objeto pequeño queda en unos cuantos píxeles, y solo el mapa conv4_3, el de "
        f"cajas de escala 0.1, tiene resolución para verlo. Los pequeños son solo {num(nt['pequeño'])} de "
        f"los {num(sum(nt.values()))} objetos que cuentan en la evaluación, por eso pesan poco en el mAP "
        "general, pero explican el bajo desempeño en botellas y plantas.")
    add_pic(doc, figs["tam"], 4.4)
    add_caption(doc, "Figura 7. mAP por tamaño de objeto (época 160, VOC2007 test).")

    add_heading(doc, "4.4 Ejemplos de detección", level=2)
    add_para(doc,
        "En la Figura 8 están seis imágenes de VOC2007 test escogidas al azar, con las detecciones del "
        "modelo de la época 160 con puntaje de al menos 0.4 (cajas naranjas) y las cajas reales "
        f"(punteadas en blanco). En total el modelo encontró {n_det} objetos contra {n_real} reales en esas "
        "imágenes. Las cajas quedan bien ajustadas en objetos grandes y separados, como el ave o el jinete "
        "con su caballo. En la escena de ciclistas las personas y las bicicletas se enciman y algunas cajas "
        "quedan corridas. En la primera imagen hay un error que muestra el alcance del modelo: detectó "
        "correctamente la silla y el monitor, pero también marcó la impresora como monitor con 0.60, porque "
        "las impresoras no están entre las 20 clases de VOC y el modelo la asigna a la clase que más se le "
        "parece.")
    add_pic(doc, figs["ej"], 6.3)
    add_caption(doc, "Figura 8. Detecciones del modelo (naranja, con su puntaje) y cajas reales (blanco punteado) en VOC2007 test.")

    add_heading(doc, "4.5 Interfaces para probar el detector", level=2)
    add_para(doc,
        "Para probar el detector construimos una aplicación en marimo, publicada en molab (Figura 9). Al "
        "abrirla descarga los cinco checkpoints desde Google Drive si no están en la carpeta. Permite "
        "escoger uno o varios modelos para comparar sus detecciones sobre la misma imagen, subir una "
        "imagen propia y mover dos controles: el umbral de confianza (min_score, 0.2 por defecto) y el "
        "solape máximo de NMS (0.5 por defecto). Para la demostración recomendamos el modelo de la época "
        "160 con un umbral entre 0.2 y 0.3, porque el 0.01 que se usa para calcular el mAP muestra "
        "demasiadas cajas de baja confianza. El detector solo reconoce las 20 clases de VOC; cualquier otro "
        "objeto lo ignora o lo confunde con la clase más parecida.")
    add_pic(doc, figs["app"], 5.6)
    add_caption(doc, "Figura 9. Aplicación del detector en molab (https://molab.marimo.io/notebooks/nb_9o5HDcMtHPxcr5FNwajrGh/app).")
    add_para(doc,
        "Como complemento hicimos una versión local en Streamlit, que el profesor también mencionó como "
        "opción, porque tiene un componente para tomar fotos con la cámara de la computadora (Figura 10). "
        "Corre en la GPU de la laptop y tiene tres fuentes de imagen: la cámara, una imagen subida o "
        "cualquiera de las imágenes de VOC2007 test. Igual que la de molab, deja escoger el modelo (época "
        "160 o la del profesor) y mover el umbral de confianza y el de NMS, y muestra cuántos objetos "
        "encontró, el tiempo de detección y la tabla de clases con su confianza. Se ejecuta con "
        "streamlit run app_camara.py.")
    add_pic(doc, figs["local"], 5.8)
    add_caption(doc, "Figura 10. Aplicación local con cámara (Streamlit) detectando autos y una persona en una imagen de VOC2007 test.")

    # ------------------------------------------------------------ 5
    add_heading(doc, "5. Conclusiones")
    add_para(doc,
        f"Continuando el entrenamiento desde la época 83 hasta la 160 el mAP subió de {p(E83['mAP'])} a "
        f"{p(AP[160]['mAP'])}, y lo pudimos reproducir en otra máquina ({p(E160['mAP'])}). Después de la "
        "época 160 el modelo ya no mejoró con la tasa de aprendizaje inicial. El SSD300 detecta bien "
        "objetos grandes como gatos, caballos o autos, y sus puntos débiles son los objetos pequeños o "
        f"tapados, como botellas, plantas y sillas: en objetos grandes el mAP es de {p(mt['grande'], 1)} y en "
        f"pequeños baja a {p(mt['pequeño'], 1)}. La comparación con el checkpoint del profesor sobre las mismas "
        "imágenes muestra que el entrenamiento adicional no solo subió el número, sino que el modelo "
        "encuentra más objetos y confunde menos clases.")
    add_para(doc,
        "Del trabajo con distintas GPU aprendimos que la tarjeta más cara no siempre es la más rápida: "
        "la B300 se quedó esperando los datos del disco y sus 30 épocas costaron más del triple que las "
        "mismas 30 épocas en la RTX PRO 6000. Para este modelo la RTX PRO 6000 fue la mejor opción en tiempo y costo. Como siguientes "
        "pasos proponemos aplicar el decaimiento de la tasa de aprendizaje, separar un conjunto de "
        "validación para escoger la época sin usar la prueba, y mejorar la carga de datos para aprovechar "
        "GPU más grandes.")

    add_heading(doc, "Referencias")
    for t in [
        "Everingham, M., Van Gool, L., Williams, C. K. I., Winn, J., & Zisserman, A. (2010). The Pascal "
        "Visual Object Classes (VOC) challenge. International Journal of Computer Vision, 88(2), 303-338. "
        "https://doi.org/10.1007/s11263-009-0275-4",
        "Liu, W., Anguelov, D., Erhan, D., Szegedy, C., Reed, S., Fu, C.-Y., & Berg, A. C. (2016). SSD: "
        "Single shot multibox detector. En Computer Vision - ECCV 2016 (pp. 21-37). Springer. "
        "https://doi.org/10.1007/978-3-319-46448-0_2",
        "Modal Labs. (2026). Pricing. https://modal.com/pricing",
        "Russakovsky, O., Deng, J., Su, H., Krause, J., Satheesh, S., Ma, S., Huang, Z., Karpathy, A., "
        "Khosla, A., Bernstein, M., Berg, A. C., & Fei-Fei, L. (2015). ImageNet large scale visual "
        "recognition challenge. International Journal of Computer Vision, 115(3), 211-252. "
        "https://doi.org/10.1007/s11263-015-0816-y",
        "Simonyan, K., & Zisserman, A. (2015). Very deep convolutional networks for large-scale image "
        "recognition. En International Conference on Learning Representations (ICLR 2015). "
        "https://arxiv.org/abs/1409.1556",
        "Vinodababu, S. (2019). a-PyTorch-Tutorial-to-Object-Detection [Repositorio de código]. GitHub. "
        "https://github.com/sgrvinod/a-PyTorch-Tutorial-to-Object-Detection",
    ]:
        add_apa(doc, t)

    out = os.path.join(PROY, NOMBRE + ".docx")
    doc.save(out); print("DOCX:", out)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", PROY, out], check=True, capture_output=True)
    for ext in (".docx", ".pdf"):
        shutil.copy(out.replace(".docx", ext), os.path.join(os.path.expanduser("~"), "Downloads", NOMBRE + ext))
    print("PDF:", out.replace(".docx", ".pdf"))


if __name__ == "__main__":
    build()
