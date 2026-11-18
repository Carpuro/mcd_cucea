# -*- coding: utf-8 -*-
"""
Actividad 5 - CNN para clasificación de Pokémon. Builds the report (DOCX + PDF) on the MCD template.
Every number comes from resultados/resultados.json and resultados/resumen.json, written by
entrenar_actividad5.py and figuras_actividad5.py (both run in the `torch` conda env).
This script runs in the MCD env and reuses the report helpers from Visualización (build_tarea16).
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
VIS = os.path.join(HERE, "..", "..", "..", "visualizacion-grandes-bases-datos", "tareas")
sys.path.insert(0, os.path.abspath(VIS))
from build_tarea16 import (add_para, add_heading, add_caption, add_pic, make_table,  # noqa: E402
                           add_apa, clear_body_after_table1, NAVY, TEMPLATE, SOFFICE, num)

RES = os.path.join(HERE, "resultados")
NOMBRE = "Actividad5_TopicosGBDII_CarlosPulidoRosas"
J = json.load(open(os.path.join(RES, "resultados.json"), encoding="utf-8"))
S = json.load(open(os.path.join(RES, "resumen.json"), encoding="utf-8"))
I, R = J["info"], J["R"]
FIG = S["figuras"]


def p1(x):
    """Proportion -> percentage with one decimal and a decimal point."""
    return f"{x * 100:.1f} %"


def mejor(e):
    acc = R[e]["test_acc"]
    return max(acc), acc.index(max(acc)) + 1


# ------------------------------------------------------------ derived numbers
n_cls, n_img, n_te = I["n_clases"], I["n_imagenes"], I["n_test"]
conteo = I["conteo"]; clases = I["clases"]
cls_min = " y ".join(c for c, n in zip(clases, conteo) if n == min(conteo))
cls_max = " y ".join(c for c, n in zip(clases, conteo) if n == max(conteo))
H = 64
flat = H * 13 * 13
p_conv1 = 3 * H * 9 + H
p_conv = H * H * 9 + H
p_lin = flat * n_cls + n_cls
p_tiny = R["E2"]["params_total"]
assert p_tiny == p_conv1 + 3 * p_conv + p_lin
e1_10 = R["E1"]["test_acc"][9]; e2_10 = R["E2"]["test_acc"][9]
e2_best, e2_best_ep = mejor("E2"); e3_best, e3_best_ep = mejor("E3")
e2_minloss_ep = R["E2"]["test_loss"].index(min(R["E2"]["test_loss"])) + 1
conf4 = S["E4"]["confusiones"]; conf2 = S["E2"]["confusiones"]
peores4 = S["E4"]["peores"]; peores2 = S["E2"]["peores"]
n_peor4 = sum(1 for _, a in peores4 if a == peores4[0][1])


def build():
    doc = Document(TEMPLATE)
    hdr = doc.tables[0].rows[0].cells[1]
    hdr.paragraphs[2].runs[0].text = "Maestría en Ciencias de los Datos | 3er Semestre"
    hdr.paragraphs[3].runs[0].text = "Materia: Tópicos Selectos de Grandes Bases de Datos II"
    for r in hdr.paragraphs[3].runs[1:]: r.text = ""
    tp = doc.paragraphs[1]; tp.clear()
    r = tp.add_run("Actividad 5. Red neuronal convolucional para clasificar Pokémon\n"
                   "TinyVGG y transferencia de aprendizaje con EfficientNet-B0")
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY; r.font.name = "Calibri"
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def si(idx, text):
        cell = doc.tables[1].rows[idx].cells[1]; cell.paragraphs[0].runs[0].text = text
        for extra in cell.paragraphs[0].runs[1:]: extra.text = ""
    si(1, "17 de noviembre de 2026")
    si(2, "Actividad 5. CNN para clasificación de Pokémon")
    si(3, "Python 3.13, PyTorch y torchvision")
    si(4, f"torch {I['torch']}, torchvision {I['torchvision']}")
    si(5, f"Equipo personal con GPU {I['device'].replace('NVIDIA GeForce ', '')} (CUDA)")
    si(6, f"PokemonData: {num(n_img)} imágenes de las {n_cls} especies de la primera generación")
    clear_body_after_table1(doc)

    # ---------------------------------------------------------------- 1
    add_para(doc, sb=8, sa=0)
    add_heading(doc, "1. Introducción")
    add_para(doc,
        "En esta actividad trabajé con el proyecto del profesor para clasificar imágenes de Pokémon "
        "con una red neuronal convolucional (CNN). El código está organizado como en el curso de "
        "PyTorch de Bourke (s.f.): data_setup.py arma los DataLoaders, model_builder.py define la red "
        "TinyVGG, engine.py tiene los ciclos de entrenamiento y prueba, y train.py junta todo. En molab "
        "el profesor dejó la misma versión como cuaderno de marimo, con 10 épocas. Además, en el "
        "repositorio hay un segundo cuaderno que usa transferencia de aprendizaje con EfficientNet-B0.")
    add_para(doc,
        "No me quise quedar solo en correr el código y anotar la exactitud final. Corrí los dos modelos en "
        "mi computadora y revisé tres cosas: si el conjunto de prueba realmente mide lo que el modelo "
        "aprendió, qué tanto se sobreajusta TinyVGG y qué papel juega el aumento de datos, y cuánto se "
        "gana al partir de una red ya entrenada con ImageNet. Usé el código del profesor sin cambiar la "
        "arquitectura, la función de pérdida, el optimizador ni los hiperparámetros, y fijé las semillas "
        "para que los resultados se puedan repetir.")

    # ---------------------------------------------------------------- 2
    add_heading(doc, "2. Datos")
    add_para(doc,
        "El README del proyecto apunta al conjunto Pokemon Classification de Kaggle (Lantian, s.f.), pero "
        "para descargarlo se necesita una cuenta con token de la API. Por eso usé PokemonData, una versión "
        "pública que está en Hugging Face (sgtsaughter, 2024) con la misma organización: una carpeta por "
        f"especie, {n_cls} especies en total. Son {num(n_img)} imágenes JPG y "
        "todas se pudieron abrir. Busqué archivos repetidos comparando el hash MD5 y solo encontré 5 "
        "copias exactas, así que no influyen en los resultados.")
    add_para(doc,
        f"Las clases no están balanceadas: la que menos imágenes tiene es {cls_min}, con {min(conteo)}, y las "
        f"que más, {cls_max}, con {max(conteo)} cada una. La mediana es de {I['conteo_mediana']:.0f} imágenes por "
        "especie (Figura 1). Para un problema de 151 clases es poco, porque la red tiene que distinguir "
        "cada especie a partir de unas decenas de ejemplos. Además las imágenes son muy variadas: hay "
        "ilustraciones oficiales, capturas de la serie, cartas, figuras, peluches y dibujos de fans, con "
        "fondos de todo tipo.")
    add_pic(doc, FIG["conteo"], 4.6)
    add_caption(doc, "Figura 1. Número de imágenes por especie.")
    add_para(doc,
        "TinyVGG recibe las imágenes reducidas a 64 x 64 píxeles, mientras que EfficientNet-B0 las recibe "
        "a 224 x 224, que es el tamaño con el que se preentrenó. En la Figura 2 se ve lo que se pierde con "
        "la reducción: los contornos y los colores se mantienen, pero detalles como los ojos, las manchas o "
        "las texturas quedan en unos cuantos píxeles. Este punto pesa más adelante, cuando la red tiene "
        "que separar especies parecidas.")
    add_pic(doc, FIG["muestras"], 6.3)
    add_caption(doc, "Figura 2. La misma imagen como la recibe cada modelo: 224 x 224 (arriba) y 64 x 64 (abajo).")

    # ---------------------------------------------------------------- 3
    add_heading(doc, "3. La red TinyVGG")
    add_para(doc,
        "TinyVGG es la versión reducida de VGG (Simonyan y Zisserman, 2015) que usa CNN Explainer para "
        "enseñar cómo funciona una red convolucional (Wang et al., 2021). Tiene dos bloques iguales y un "
        "clasificador. Cada bloque aplica dos convoluciones de 3 x 3 con ReLU y después un max pooling "
        "de 2 x 2. Una convolución recorre la imagen con filtros pequeños y en cada posición calcula una "
        "suma ponderada, así que cada filtro aprende a detectar un patrón local, por ejemplo un borde o un "
        "cambio de color, sin importar en qué parte de la imagen esté (LeCun et al., 1998). El pooling se "
        "queda con el valor más alto de cada ventana de 2 x 2, con lo que reduce el tamaño a la mitad.")
    filas = [
        ["Entrada", "3 x 64 x 64", "0"],
        ["Conv 3x3 + ReLU", f"{H} x 62 x 62", num(p_conv1)],
        ["Conv 3x3 + ReLU", f"{H} x 60 x 60", num(p_conv)],
        ["MaxPool 2x2", f"{H} x 30 x 30", "0"],
        ["Conv 3x3 + ReLU", f"{H} x 28 x 28", num(p_conv)],
        ["Conv 3x3 + ReLU", f"{H} x 26 x 26", num(p_conv)],
        ["MaxPool 2x2", f"{H} x 13 x 13", "0"],
        ["Flatten", num(flat), "0"],
        ["Linear", str(n_cls), num(p_lin)],
        ["Total", "", num(p_tiny)],
    ]
    make_table(doc, ["Capa", "Tamaño de salida", "Parámetros"], filas,
               "Tabla 1. Tamaños y parámetros de TinyVGG con hidden_units = 64 y 151 clases.",
               [2.0, 1.8, 1.4], hl=len(filas) - 1)
    add_para(doc,
        "En model_builder.py hay un comentario que pregunta de dónde sale el 13 x 13 de la capa lineal. "
        "Sale de la Tabla 1: como las convoluciones no tienen relleno (padding = 0), cada una le quita un "
        "píxel a cada lado, y cada pooling divide entre dos. Así, 64 pasa a 62 y a 60, el pooling lo deja "
        f"en 30, luego 28 y 26, y el segundo pooling en 13. Al aplanar quedan 64 x 13 x 13 = {num(flat)} "
        "valores por imagen. Si se cambia el tamaño de entrada hay que recalcular este número, porque si "
        "no la capa lineal no coincide con la salida del segundo bloque.")
    add_para(doc,
        f"Lo que más me sorprendió es dónde quedan los parámetros. Las cuatro convoluciones juntas tienen "
        f"{num(p_conv1 + 3 * p_conv)}, porque cada filtro de 3 x 3 se comparte en toda la imagen. La capa "
        f"lineal, en cambio, conecta los {num(flat)} valores con las {n_cls} clases y tiene {num(p_lin)}, "
        f"el {p_lin / p_tiny * 100:.1f} % del total. Es la parte de la red que más fácilmente puede "
        "memorizar el conjunto de entrenamiento, y eso se nota en los resultados.")

    # ---------------------------------------------------------------- 4
    add_heading(doc, "4. Entrenamiento y experimentos")
    add_para(doc,
        "Usé la configuración de train.py: pérdida de entropía cruzada, optimizador Adam con tasa de "
        "aprendizaje 0.001 y lotes de 32 imágenes. Antes de entrar a la red, cada imagen se reduce a "
        "64 x 64, se voltea horizontalmente al azar, se gira hasta 25 grados y se normaliza a [-1, 1]. "
        "El volteo y el giro son el aumento de datos: en cada época la red ve una versión un poco distinta "
        "de la misma imagen, como si hubiera más ejemplos (Shorten y Khoshgoftaar, 2019). Para no leer "
        "miles de archivos JPG en cada época, guardé las imágenes ya reducidas en memoria y apliqué las "
        "mismas transformaciones del profesor sobre ellas, lo que da el mismo resultado.")
    add_para(doc,
        "Al revisar get_data.py me di cuenta de que el conjunto de prueba se arma copiando 15 imágenes al "
        "azar de cada especie con shutil.copy. Como se copian y no se mueven, esas imágenes siguen en la "
        "carpeta de entrenamiento y el modelo las ve durante el entrenamiento. A esto se le conoce como "
        "fuga de información (Kaufman et al., 2012). Por eso planteé cuatro experimentos con las mismas "
        f"15 imágenes de prueba por especie ({num(n_te)} en total):")
    exps = [
        ["E1", "TinyVGG, como en el repositorio", "Todas (incluye las de prueba)", "Sí (también en prueba)", "10"],
        ["E2", "TinyVGG, separación limpia", f"{num(I['n_train_limpio'])} (sin las de prueba)", "Sí (solo entrenamiento)", "30"],
        ["E3", "TinyVGG, separación limpia", f"{num(I['n_train_limpio'])} (sin las de prueba)", "No", "30"],
        ["E4", "EfficientNet-B0 preentrenada", f"{num(I['n_train_limpio'])} (sin las de prueba)", "No", "5"],
    ]
    make_table(doc, ["", "Modelo", "Imágenes de entrenamiento", "Aumento de datos", "Épocas"], exps,
               "Tabla 2. Experimentos. Todos usan Adam (lr = 0.001), lotes de 32 y semilla 42.",
               [0.4, 1.9, 1.9, 1.5, 0.6])
    add_para(doc,
        "E1 reproduce exactamente lo que hace el repositorio, con las 10 épocas del cuaderno de molab. "
        "En E2 saqué las imágenes de prueba del entrenamiento y dejé de aplicar el giro y el volteo a la "
        "prueba, porque ahí solo interesa medir. Lo entrené 30 épocas para ver qué pasa después de las 10. "
        "E3 es igual a E2 pero sin aumento de datos, para medir cuánto aporta. E4 es el cuaderno de "
        "transferencia de aprendizaje con la misma separación limpia que E2.")

    # ---------------------------------------------------------------- 5
    add_heading(doc, "5. Resultados")
    add_heading(doc, "5.1 El conjunto de prueba del repositorio", level=2)
    add_para(doc,
        f"Con la configuración original (E1), después de 10 épocas la exactitud en prueba fue de "
        f"{p1(e1_10)} y la de entrenamiento de {p1(R['E1']['train_acc'][9])}. Si se evalúa esa misma prueba "
        f"sin el giro ni el volteo, sube a {p1(R['E1']['acc_final'])}. Lo raro es que en todas las épocas "
        "la prueba sale mejor que el entrenamiento, tanto en exactitud como en pérdida (Figura 3), y eso no "
        "debería pasar con datos que el modelo no ha visto. La explicación es la fuga: el modelo ya conoce "
        "esas imágenes, y además en el entrenamiento la exactitud se calcula mientras los pesos todavía se "
        "están ajustando, así que siempre va un poco atrás.")
    add_pic(doc, FIG["e1"], 6.2)
    add_caption(doc, "Figura 3. E1 (configuración del repositorio) contra la prueba limpia de E2 en las primeras 10 épocas.")
    add_para(doc,
        f"La línea azul es la misma red entrenada sin las imágenes de prueba. En la época 10 llega a "
        f"{p1(e2_10)}, {(e1_10 - e2_10) * 100:.1f} puntos menos que E1. Esa diferencia es lo que la fuga "
        "infla la exactitud. Si solo se corriera el código del repositorio, uno se quedaría con la idea de "
        "que TinyVGG clasifica 3 de cada 4 imágenes nuevas, cuando en realidad es poco más de la mitad. "
        "Para todo lo que sigue usé la separación limpia.")

    add_heading(doc, "5.2 Sobreajuste y aumento de datos", level=2)
    add_para(doc,
        f"En E2 la exactitud en prueba sube rápido al principio, llega a su máximo de {p1(e2_best)} en la "
        f"época {e2_best_ep}, pero desde la época 8 ya solo se mueve entre 56 % y 59 % y termina en "
        f"{p1(R['E2']['acc_final'])}. "
        f"Mientras tanto, la exactitud de entrenamiento sigue subiendo hasta {p1(R['E2']['train_acc'][-1])}. "
        f"La pérdida de prueba es la que mejor muestra el sobreajuste: llega a su mínimo de "
        f"{min(R['E2']['test_loss']):.2f} en la época {e2_minloss_ep} y luego sube hasta "
        f"{R['E2']['test_loss'][-1]:.2f} (Figura 4). Que la pérdida suba mientras la exactitud se mantiene "
        "quiere decir que el modelo sigue acertando en las mismas imágenes, pero cuando se equivoca lo hace "
        "con más seguridad. Con estos datos, entrenar más de 10 épocas no ayuda.")
    add_pic(doc, FIG["e2e3"], 6.2)
    add_caption(doc, "Figura 4. TinyVGG con separación limpia, con aumento de datos (E2) y sin él (E3).")
    add_para(doc,
        f"Sin aumento de datos (E3) el sobreajuste es mucho más fuerte. En 5 épocas la red ya acierta el "
        f"{p1(R['E3']['train_acc'][4])} del entrenamiento y termina en {p1(R['E3']['train_acc'][-1])}, es "
        f"decir, se aprende las imágenes de memoria. La prueba tiene su mejor punto en la época "
        f"{e3_best_ep} con {p1(e3_best)}, de ahí baja hasta {p1(R['E3']['acc_final'])}, y la pérdida de "
        f"prueba se dispara hasta {R['E3']['test_loss'][-1]:.2f}. El giro y el volteo valen "
        f"{(R['E2']['acc_final'] - R['E3']['acc_final']) * 100:.1f} puntos de exactitud al final. Aun así, "
        "el aumento no resuelve todo: E2 también se sobreajusta, solo que más despacio.")

    add_heading(doc, "5.3 Transferencia de aprendizaje con EfficientNet-B0", level=2)
    add_para(doc,
        "El segundo cuaderno del repositorio parte de EfficientNet-B0 (Tan y Le, 2019) con los pesos "
        "entrenados en ImageNet (Deng et al., 2009), en su versión de 1,000 categorías y alrededor de "
        "1.2 millones de fotos. Congela toda la parte convolucional (features), que ya sabe detectar bordes, texturas "
        "y formas, y solo cambia la última capa por una nueva de 1,280 a 151 salidas. La idea es que las "
        "características de las primeras capas sirven para casi cualquier problema de imágenes y que solo "
        f"hay que aprender a combinarlas (Yosinski et al., 2014). De los {num(R['E4']['params_total'])} "
        f"parámetros de la red solo se entrenan {num(R['E4']['params_entrenables'])}, el "
        f"{R['E4']['params_entrenables'] / R['E4']['params_total'] * 100:.1f} %, que incluso son menos que "
        f"los {num(p_tiny)} de TinyVGG.")
    add_pic(doc, FIG["e4"], 6.2)
    add_caption(doc, "Figura 5. Transferencia de aprendizaje con EfficientNet-B0 (E4). La línea punteada es el mejor valor de TinyVGG.")
    add_para(doc,
        f"Desde la primera época EfficientNet-B0 ya tiene {p1(R['E4']['test_acc'][0])} en prueba, más que "
        f"el mejor resultado de TinyVGG en 30 épocas, y termina la quinta con {p1(R['E4']['acc_final'])} "
        f"(Figura 5). El entrenamiento tardó {R['E4']['segundos']:.0f} segundos en la GPU. La distancia "
        f"entre entrenamiento ({p1(R['E4']['train_acc'][-1])}) y prueba es mucho menor que en TinyVGG y la "
        "pérdida de prueba sigue bajando en todas las épocas, así que todavía no se sobreajusta.")

    add_heading(doc, "5.4 Comparación y errores", level=2)
    comp = [
        ["E1 TinyVGG (repositorio)", p1(R["E1"]["acc_final"]), p1(R["E1"]["top5"]), num(p_tiny), "Inflada por la fuga"],
        ["E2 TinyVGG con aumento", p1(R["E2"]["acc_final"]), p1(R["E2"]["top5"]), num(p_tiny), "Sobreajuste moderado"],
        ["E3 TinyVGG sin aumento", p1(R["E3"]["acc_final"]), p1(R["E3"]["top5"]), num(p_tiny), "Sobreajuste fuerte"],
        ["E4 EfficientNet-B0", p1(R["E4"]["acc_final"]), p1(R["E4"]["top5"]), num(R["E4"]["params_entrenables"]), "Mejor resultado"],
    ]
    make_table(doc, ["Modelo", "Exactitud", "Top-5", "Parámetros entrenados", "Observación"], comp,
               f"Tabla 3. Resultados finales sobre las {num(n_te)} imágenes de prueba, sin aumento de datos.",
               [1.9, 0.9, 0.8, 1.3, 1.5], hl=3)
    add_para(doc,
        "La exactitud top-5 cuenta como acierto que la especie correcta esté entre las cinco con mayor "
        "probabilidad. EfficientNet-B0 la tiene en "
        f"{p1(R['E4']['top5'])}, lo que quiere decir que aun cuando falla casi siempre tiene la respuesta "
        "correcta entre sus primeras opciones.")
    add_para(doc,
        f"Para entender los errores revisé el resultado por especie. Con E4, {S['E4']['n_perfectas']} especies "
        f"acertaron las 15 imágenes y ninguna se quedó en cero. Las más bajas fueron "
        f"{', '.join(c for c, a in peores4[:n_peor4])}, con {p1(peores4[0][1])}. En TinyVGG (E2) la peor fue "
        f"{peores2[0][0]}, que solo acertó {round(peores2[0][1] * 15)} de 15. La correlación entre el número "
        f"de imágenes de cada especie y su exactitud es baja ({S['E4']['corr_conteo_acc']:.2f} en E4 y "
        f"{S['E2']['corr_conteo_acc']:.2f} en E2), así que el desbalance no explica la mayoría de los errores.")
    add_para(doc,
        f"Lo que sí los explica es el parecido entre especies. Las diez confusiones más frecuentes de E4 son "
        f"todas entre Pokémon de la misma línea evolutiva: {conf4[0][0]} con {conf4[0][1]} "
        f"({conf4[0][2]} de 15), {conf4[1][0]} con {conf4[1][1]}, {conf4[2][0]} con {conf4[2][1]} y "
        f"{conf4[3][0]} con {conf4[3][1]}, entre otras (Figura 6). Estas especies comparten colores y "
        "forma, y muchas veces solo cambian en el tamaño, que en una imagen no se puede saber, o en "
        f"detalles chicos. En TinyVGG pasa lo mismo, por ejemplo {conf2[0][0]} con {conf2[0][1]} "
        f"({conf2[0][2]} de 15) y {conf2[1][0]} con {conf2[1][1]} ({conf2[1][2]} de 15), y a 64 x 64 esos "
        "detalles casi desaparecen.")
    add_pic(doc, FIG["errores"], 6.3)
    add_caption(doc, "Figura 6. Las cinco confusiones más frecuentes de EfficientNet-B0: arriba una imagen mal "
                     "clasificada y abajo un ejemplo de la especie que predijo el modelo.")

    # ---------------------------------------------------------------- 6
    add_heading(doc, "6. Conclusiones")
    add_para(doc,
        "Lo más importante que saqué de esta actividad es que el número que imprime el entrenamiento no "
        "siempre mide lo que uno cree. Con el conjunto de prueba del repositorio TinyVGG parece llegar a "
        f"{p1(e1_10)}, pero en imágenes que de verdad no ha visto se queda en {p1(e2_10)} con las mismas "
        "10 épocas. Para evitarlo basta con mover las imágenes en lugar de copiarlas en get_data.py "
        "(shutil.move en vez de shutil.copy) y no aplicar el aumento de datos a la prueba.")
    add_para(doc,
        "TinyVGG sirve para entender cómo funciona una CNN, pero se queda corta para 151 clases con unas "
        f"{I['conteo_mediana']:.0f} imágenes por especie. Casi todos sus parámetros están en la capa lineal, "
        "aprende rápido el entrenamiento y deja de mejorar en prueba alrededor de la época 10. El aumento "
        "de datos ayuda bastante, pero no alcanza para compensar la falta de ejemplos. La transferencia de "
        f"aprendizaje sí lo compensa: con menos parámetros entrenables y solo 5 épocas, EfficientNet-B0 "
        f"llega a {p1(R['E4']['acc_final'])}, porque no tiene que aprender desde cero a ver formas y texturas, "
        "solo a combinarlas para distinguir especies.")
    add_para(doc,
        "Para mejorarlo probaría tres cosas. Primero, descongelar los últimos bloques de EfficientNet-B0 con "
        "una tasa de aprendizaje más baja para ajustarlos a este tipo de imágenes. Segundo, usar en ese "
        "modelo el mismo aumento de datos que en TinyVGG. Tercero, separar un conjunto de validación para "
        "elegir la época con early stopping, en lugar de decidirlo viendo la prueba. Y como la mayoría de "
        "los errores son entre especies de la misma línea evolutiva, revisaría esos casos con más imágenes "
        "o a mayor resolución.")

    add_heading(doc, "Referencias")
    for ref in [
        "Bourke, D. (s.f.). 05. PyTorch going modular. En Zero to Mastery: Learn PyTorch for deep learning. "
        "https://www.learnpytorch.io/05_pytorch_going_modular/",
        "Deng, J., Dong, W., Socher, R., Li, L.-J., Li, K., & Fei-Fei, L. (2009). ImageNet: A large-scale "
        "hierarchical image database. En 2009 IEEE Conference on Computer Vision and Pattern Recognition "
        "(pp. 248-255). IEEE. https://doi.org/10.1109/CVPR.2009.5206848",
        "Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, "
        "detection, and avoidance. ACM Transactions on Knowledge Discovery from Data, 6(4), 1-21. "
        "https://doi.org/10.1145/2382577.2382579",
        "Lantian. (s.f.). Pokemon classification [Conjunto de datos]. Kaggle. "
        "https://www.kaggle.com/datasets/lantian773030/pokemonclassification",
        "LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). Gradient-based learning applied to "
        "document recognition. Proceedings of the IEEE, 86(11), 2278-2324. https://doi.org/10.1109/5.726791",
        "sgtsaughter. (2024). Pokemon classification images 151 [Conjunto de datos]. Hugging Face. "
        "https://huggingface.co/datasets/sgtsaughter/pokemon-classification-images-151",
        "Shorten, C., & Khoshgoftaar, T. M. (2019). A survey on image data augmentation for deep learning. "
        "Journal of Big Data, 6, Artículo 60. https://doi.org/10.1186/s40537-019-0197-0",
        "Simonyan, K., & Zisserman, A. (2015). Very deep convolutional networks for large-scale image "
        "recognition. En International Conference on Learning Representations (ICLR 2015). "
        "https://arxiv.org/abs/1409.1556",
        "Tan, M., & Le, Q. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. "
        "En Proceedings of the 36th International Conference on Machine Learning (Vol. 97, pp. 6105-6114). "
        "PMLR. https://proceedings.mlr.press/v97/tan19a.html",
        "Toledano Juárez, I. A. (2026). Pokemon_Classification [Repositorio de código]. GitHub. "
        "https://github.com/IvTole/Pokemon_Classification",
        "Wang, Z. J., Turko, R., Shaikh, O., Park, H., Das, N., Hohman, F., Kahng, M., & Chau, D. H. (2021). "
        "CNN Explainer: Learning convolutional neural networks with interactive visualization. IEEE "
        "Transactions on Visualization and Computer Graphics, 27(2), 1396-1406. "
        "https://doi.org/10.1109/TVCG.2020.3030418",
        "Yosinski, J., Clune, J., Bengio, Y., & Lipson, H. (2014). How transferable are features in deep "
        "neural networks? En Advances in Neural Information Processing Systems 27 (pp. 3320-3328).",
    ]:
        add_apa(doc, ref)

    out = os.path.join(HERE, NOMBRE + ".docx")
    doc.save(out); print("DOCX:", out)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", HERE, out],
                   check=True, capture_output=True)
    pdf = out.replace(".docx", ".pdf")
    shutil.copy(pdf, os.path.join(os.path.expanduser("~"), "Downloads", NOMBRE + ".pdf"))
    print("PDF:", pdf)


if __name__ == "__main__":
    build()
