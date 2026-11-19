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
EJ = S["ejemplos"]
assert EJ["top5"][2]["nombres"][2] == EJ["top5"][2]["real"]   # "tercer lugar" in 5.4


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
        "Para esta actividad usé el proyecto del profesor que clasifica imágenes de Pokémon con una red "
        "neuronal convolucional (CNN). El código sigue la estructura del curso de PyTorch de Bourke (s.f.), "
        "con un archivo para cada parte: data_setup.py crea los DataLoaders, model_builder.py tiene la red "
        "TinyVGG, engine.py los ciclos de entrenamiento y prueba, y train.py manda llamar todo. La versión "
        "de molab es el mismo código en un cuaderno de marimo, con 10 épocas. En el repositorio también "
        "viene un cuaderno de transferencia de aprendizaje con EfficientNet-B0.")
    add_para(doc,
        "Entrené los dos modelos en mi computadora con la GPU. No cambié la arquitectura, la pérdida, el "
        "optimizador ni los hiperparámetros del profesor, y fijé las semillas para poder repetir los "
        "resultados. Además de ver qué exactitud alcanzaba cada modelo, revisé si el conjunto de prueba "
        "estaba bien separado, qué tanto se sobreajusta TinyVGG, cuánto ayuda el aumento de datos y en qué "
        "Pokémon se equivocan los modelos.")

    # ---------------------------------------------------------------- 2
    add_heading(doc, "2. Datos")
    add_para(doc,
        "El README del proyecto usa el conjunto Pokemon Classification de Kaggle (Lantian, s.f.), pero para "
        "bajarlo se necesita cuenta y token de la API. Usé en su lugar PokemonData, que está público en "
        "Hugging Face (sgtsaughter, 2024) y viene organizado igual, con una carpeta por especie. Tiene "
        f"{num(n_img)} imágenes JPG de las {n_cls} especies de la primera generación y todas abrieron sin "
        "problema. Revisé si había archivos repetidos con el hash MD5 y solo había 5, así que no afectan.")
    add_para(doc,
        f"No todas las especies tienen el mismo número de imágenes. {cls_min} es la que menos tiene, con "
        f"{min(conteo)}, y {cls_max} las que más, con {max(conteo)} cada una. La mediana es de "
        f"{I['conteo_mediana']:.0f} (Figura 1). Para 151 clases son pocas imágenes por clase, y además son "
        "muy distintas entre sí: hay ilustraciones oficiales, escenas de la serie, cartas, figuras, peluches "
        "y dibujos hechos por fans, cada una con su propio fondo.")
    add_pic(doc, FIG["conteo"], 4.6)
    add_caption(doc, "Figura 1. Número de imágenes por especie.")
    add_para(doc,
        "TinyVGG trabaja con las imágenes a 64 x 64 píxeles y EfficientNet-B0 a 224 x 224, que es el tamaño "
        "con el que se preentrenó. En la Figura 2 se nota la diferencia. A 64 x 64 se siguen viendo la "
        "silueta y los colores, pero los ojos, las manchas y otros detalles quedan en muy pocos píxeles, y "
        "eso después se refleja en los errores entre especies parecidas.")
    add_pic(doc, FIG["muestras"], 6.3)
    add_caption(doc, "Figura 2. La misma imagen como la recibe cada modelo: 224 x 224 (arriba) y 64 x 64 (abajo).")

    # ---------------------------------------------------------------- 3
    add_heading(doc, "3. La red TinyVGG")
    add_para(doc,
        "TinyVGG es una versión chica de VGG (Simonyan y Zisserman, 2015) que se usa en CNN Explainer para "
        "explicar cómo funciona una red convolucional (Wang et al., 2021). Tiene dos bloques y un "
        "clasificador. En cada bloque hay dos convoluciones de 3 x 3 con ReLU y luego un max pooling de "
        "2 x 2. La convolución pasa filtros pequeños por toda la imagen y en cada posición calcula una suma "
        "ponderada de los píxeles, por lo que cada filtro termina detectando un patrón local, como un borde o "
        "un cambio de color, en cualquier parte de la imagen (LeCun et al., 1998). El max pooling toma el "
        "valor más alto de cada ventana de 2 x 2 y así reduce a la mitad el alto y el ancho.")
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
        "En model_builder.py el profesor dejó un comentario preguntando de dónde sale el 13 x 13 de la capa "
        "lineal. Las convoluciones no usan relleno (padding = 0), así que cada una le quita un píxel a cada "
        "orilla, y cada pooling divide el tamaño entre dos. La imagen pasa de 64 a 62 y a 60, el pooling la "
        f"deja en 30, después baja a 28 y a 26, y con el segundo pooling queda en 13 (Tabla 1). Al aplanar "
        f"son 64 x 13 x 13 = {num(flat)} valores por imagen. Si se usa otro tamaño de entrada hay que "
        "recalcular este número, si no la capa lineal no coincide con lo que sale del segundo bloque.")
    add_para(doc,
        f"Contando parámetros, las cuatro convoluciones suman {num(p_conv1 + 3 * p_conv)}, porque cada filtro "
        f"de 3 x 3 se reutiliza en toda la imagen. La capa lineal une los {num(flat)} valores con las "
        f"{n_cls} clases y tiene {num(p_lin)} parámetros, el {p_lin / p_tiny * 100:.1f} % de la red. Con "
        "tantos parámetros en una sola capa es fácil que el modelo memorice las imágenes de entrenamiento, y "
        "eso se ve en los resultados.")

    # ---------------------------------------------------------------- 4
    add_heading(doc, "4. Entrenamiento y experimentos")
    add_para(doc,
        "La configuración es la de train.py: entropía cruzada como pérdida, Adam con tasa de aprendizaje "
        "0.001 y lotes de 32 imágenes. Cada imagen se reduce a 64 x 64, se voltea horizontalmente al azar, "
        "se gira hasta 25 grados y se normaliza a [-1, 1]. El volteo y el giro son aumento de datos, porque "
        "en cada época la red ve la imagen un poco cambiada y es como tener más ejemplos (Shorten y "
        "Khoshgoftaar, 2019). Para que el entrenamiento no tuviera que leer los JPG en cada época, cargué "
        "las imágenes ya reducidas en memoria y sobre ellas apliqué las mismas transformaciones.")
    add_para(doc,
        "Revisando get_data.py vi que el conjunto de prueba se forma copiando 15 imágenes al azar de cada "
        "especie con shutil.copy. Al copiarlas, las imágenes se quedan también en la carpeta de "
        "entrenamiento, y el modelo entrena con las mismas imágenes con las que después se evalúa. Esto es "
        "una fuga de información (Kaufman et al., 2012). Para medir su efecto hice cuatro experimentos, "
        f"todos con las mismas 15 imágenes de prueba por especie ({num(n_te)} en total):")
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
        "E1 es el repositorio tal cual, con las 10 épocas de molab. En E2 quité las imágenes de prueba del "
        "entrenamiento y ya no les apliqué el giro ni el volteo, porque en la prueba solo se quiere medir. "
        "Lo dejé 30 épocas para ver qué pasaba después de la 10. E3 es igual a E2 pero sin aumento de datos. "
        "E4 es el cuaderno de transferencia de aprendizaje con la misma separación que E2.")
    add_para(doc,
        "En la Figura 3 está lo que imprime engine.train en la consola durante E1, una línea por época con "
        "la pérdida y la exactitud de entrenamiento y de prueba, igual que en el cuaderno de molab. Al final "
        "de cada experimento guardé los pesos del modelo con torch.save, como hace utils.save_model en "
        "train.py, y con esos modelos ya entrenados hice las predicciones de la sección 5.4.")
    add_pic(doc, FIG["consola"], 6.2)
    add_caption(doc, "Figura 3. Salida de la consola durante el entrenamiento de E1 (configuración del repositorio).")

    # ---------------------------------------------------------------- 5
    add_heading(doc, "5. Resultados")
    add_heading(doc, "5.1 El conjunto de prueba del repositorio", level=2)
    add_para(doc,
        f"En E1, al terminar las 10 épocas, la exactitud fue de {p1(e1_10)} en prueba y "
        f"{p1(R['E1']['train_acc'][9])} en entrenamiento. Evaluando la prueba sin giro ni volteo sube a "
        f"{p1(R['E1']['acc_final'])}. En todas las épocas la prueba sale mejor que el entrenamiento, en "
        "exactitud y en pérdida (Figura 4), y con imágenes nuevas eso normalmente no pasa. Pasa porque el "
        "modelo ya había visto esas imágenes. También influye que la exactitud de entrenamiento se va "
        "calculando mientras los pesos cambian dentro de la época, y por eso queda un poco abajo.")
    add_pic(doc, FIG["e1"], 6.2)
    add_caption(doc, "Figura 4. E1 (configuración del repositorio) contra la prueba limpia de E2 en las primeras 10 épocas.")
    add_para(doc,
        f"En azul está la misma red pero entrenada sin las imágenes de prueba (E2). En la época 10 tiene "
        f"{p1(e2_10)}, {(e1_10 - e2_10) * 100:.1f} puntos abajo de E1, y esa es la parte de la exactitud "
        f"que viene de la fuga. Con el código original parecería que TinyVGG acierta el {p1(e1_10)} de las "
        "imágenes nuevas, y en realidad acierta poco más de la mitad. Por eso en el resto del trabajo usé la "
        "separación limpia.")

    add_heading(doc, "5.2 Sobreajuste y aumento de datos", level=2)
    add_para(doc,
        f"En E2 la exactitud de prueba sube rápido en las primeras épocas. Su máximo es {p1(e2_best)} en la "
        f"época {e2_best_ep}, pero desde la época 8 solo se mueve entre 56 % y 59 %, y al final queda en "
        f"{p1(R['E2']['acc_final'])}. La de entrenamiento, en cambio, sigue subiendo hasta "
        f"{p1(R['E2']['train_acc'][-1])}. El sobreajuste se ve mejor en la pérdida de prueba, que tiene su "
        f"mínimo de {min(R['E2']['test_loss']):.2f} en la época {e2_minloss_ep} y de ahí sube hasta "
        f"{R['E2']['test_loss'][-1]:.2f} (Figura 5). La exactitud casi no cambia mientras la pérdida sube "
        "porque el modelo acierta más o menos las mismas imágenes, pero en las que falla cada vez está más "
        "seguro de la respuesta equivocada. Entrenar más de 10 épocas no le sirvió.")
    add_pic(doc, FIG["e2e3"], 6.2)
    add_caption(doc, "Figura 5. TinyVGG con separación limpia, con aumento de datos (E2) y sin él (E3).")
    add_para(doc,
        f"Sin aumento de datos (E3) se sobreajusta mucho más. A la época 5 ya acierta el "
        f"{p1(R['E3']['train_acc'][4])} del entrenamiento y termina en {p1(R['E3']['train_acc'][-1])}, o sea, "
        f"ya se memorizó las imágenes. En prueba su mejor época es la {e3_best_ep}, con {p1(e3_best)}, luego "
        f"baja a {p1(R['E3']['acc_final'])} y la pérdida de prueba llega a {R['E3']['test_loss'][-1]:.2f}. "
        f"Al final, el giro y el volteo aportan {(R['E2']['acc_final'] - R['E3']['acc_final']) * 100:.1f} "
        "puntos de exactitud. Aun con aumento de datos E2 también se sobreajusta, nada más que tarda más.")

    add_heading(doc, "5.3 Transferencia de aprendizaje con EfficientNet-B0", level=2)
    add_para(doc,
        "El otro cuaderno del repositorio usa EfficientNet-B0 (Tan y Le, 2019) con pesos entrenados en "
        "ImageNet (Deng et al., 2009), en la versión de 1,000 categorías y alrededor de 1.2 millones de "
        "fotos. Las capas convolucionales (features) se congelan, porque ya saben reconocer bordes, texturas "
        "y formas, y solo se reemplaza la última capa por una de 1,280 entradas a 151 salidas. Las "
        "características que aprenden las primeras capas sirven para casi cualquier problema de imágenes "
        f"(Yosinski et al., 2014). De los {num(R['E4']['params_total'])} parámetros de la red solo se "
        f"entrenan {num(R['E4']['params_entrenables'])}, el "
        f"{R['E4']['params_entrenables'] / R['E4']['params_total'] * 100:.1f} %, que son menos que los "
        f"{num(p_tiny)} de TinyVGG.")
    add_pic(doc, FIG["e4"], 6.2)
    add_caption(doc, "Figura 6. Transferencia de aprendizaje con EfficientNet-B0 (E4). La línea punteada es el mejor valor de TinyVGG.")
    add_para(doc,
        f"En la primera época EfficientNet-B0 ya llega a {p1(R['E4']['test_acc'][0])} en prueba, arriba de "
        f"lo mejor que logró TinyVGG en 30 épocas, y en la quinta termina con {p1(R['E4']['acc_final'])} "
        f"(Figura 6). Entrenarla tomó {R['E4']['segundos']:.0f} segundos en la GPU. La diferencia entre "
        f"entrenamiento ({p1(R['E4']['train_acc'][-1])}) y prueba es menor que en TinyVGG y la pérdida de "
        "prueba bajó en todas las épocas, así que en 5 épocas todavía no se sobreajusta.")

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
        "En la exactitud top-5 se cuenta como acierto si la especie correcta está entre las cinco que el "
        f"modelo considera más probables. Con EfficientNet-B0 es {p1(R['E4']['top5'])}, entonces aunque "
        "se equivoque, casi siempre tiene la respuesta correcta entre sus primeras opciones.")
    pa, pd_ = EJ["pred_aciertos"], EJ["pred_detalle"]
    mal2 = [x for x in pd_ if x["E2"][0] != x["real"]]
    mal4 = [x for x in pd_ if x["E4"][0] != x["real"]]
    seguro2 = max(mal2, key=lambda x: x["E2"][1])
    add_para(doc,
        f"Para ver a los modelos clasificando, tomé {pa['n']} imágenes de prueba al azar y les pedí la "
        "predicción a TinyVGG (E2) y a EfficientNet-B0 (E4), cargando los pesos que guardé (Figura 7). "
        "Arriba de cada imagen está la especie que eligió el modelo y su probabilidad, que es la salida de "
        "softmax para esa clase. El marco es verde si acertó y rojo si no. En estas imágenes TinyVGG acertó "
        f"{pa['E2']} de {pa['n']} y EfficientNet-B0 {pa['E4']}. Lo que más se nota es cómo se equivocan. "
        f"TinyVGG falla muy seguro, por ejemplo al {seguro2['real']} lo clasifica como {seguro2['E2'][0]} "
        f"con {seguro2['E2'][1] * 100:.0f} %, que es lo mismo que se veía con la pérdida de prueba subiendo. "
        "EfficientNet-B0, cuando falla, lo hace con probabilidades bajas, entre "
        f"{min(x['E4'][1] for x in mal4) * 100:.0f} % y {max(x['E4'][1] for x in mal4) * 100:.0f} %, o sea "
        "que el modelo tampoco estaba seguro.")
    add_pic(doc, FIG["predicciones"], 6.4)
    add_caption(doc, "Figura 7. Predicciones sobre las mismas imágenes de prueba: TinyVGG a 64 x 64 (arriba) y "
                     "EfficientNet-B0 a 224 x 224 (abajo). Verde = acierto, rojo = error.")
    t1, t2, t3 = EJ["top5"]
    add_para(doc,
        "En la Figura 8 están las cinco especies con mayor probabilidad que da EfficientNet-B0 para tres "
        f"imágenes. Al {t1['real']} lo reconoce sin dudar ({t1['prob'][0] * 100:.1f} %). Con el "
        f"{t2['real']} se queda entre {t2['nombres'][0]} ({t2['prob'][0] * 100:.1f} %), {t2['nombres'][1]} "
        f"({t2['prob'][1] * 100:.1f} %) y {t2['nombres'][2]} ({t2['prob'][2] * 100:.1f} %), que son las tres "
        f"etapas de la misma evolución y juntas suman {sum(t2['prob'][:3]) * 100:.0f} %. Con el {t3['real']} "
        f"pasa lo mismo: reparte la probabilidad entre {t3['nombres'][0]}, {t3['nombres'][1]} y "
        f"{t3['nombres'][2]}, y la especie correcta queda en tercer lugar con {t3['prob'][2] * 100:.1f} %. El "
        "modelo sí identifica la familia, lo que no logra es saber en qué etapa está.")
    add_pic(doc, FIG["top5"], 5.8)
    add_caption(doc, "Figura 8. Las cinco especies más probables según EfficientNet-B0. Verde = especie real, "
                     "rojo = predicción equivocada.")
    add_para(doc,
        f"También revisé los aciertos por especie. Con E4, {S['E4']['n_perfectas']} especies tuvieron las 15 "
        f"imágenes bien y ninguna se quedó en cero. Las más bajas fueron "
        f"{', '.join(c for c, a in peores4[:n_peor4])}, con {p1(peores4[0][1])}. En TinyVGG (E2) la peor fue "
        f"{peores2[0][0]}, con solo {round(peores2[0][1] * 15)} de 15. Calculé la correlación entre cuántas "
        f"imágenes tiene cada especie y su exactitud, y salió baja ({S['E4']['corr_conteo_acc']:.2f} en E4 y "
        f"{S['E2']['corr_conteo_acc']:.2f} en E2), así que la mayoría de los errores no vienen del desbalance.")
    add_para(doc,
        f"Los errores vienen más bien de especies que se parecen. Las diez confusiones más frecuentes de E4 "
        f"son entre Pokémon de la misma línea evolutiva, por ejemplo {conf4[0][0]} con {conf4[0][1]} "
        f"({conf4[0][2]} de 15), {conf4[1][0]} con {conf4[1][1]}, {conf4[2][0]} con {conf4[2][1]} y "
        f"{conf4[3][0]} con {conf4[3][1]} (Figura 9). Tienen colores y formas parecidas, y muchas veces "
        "cambian en el tamaño, que en una imagen no se puede saber, o en detalles pequeños. TinyVGG se "
        f"confunde igual, por ejemplo {conf2[0][0]} con {conf2[0][1]} ({conf2[0][2]} de 15) y "
        f"{conf2[1][0]} con {conf2[1][1]} ({conf2[1][2]} de 15), y a 64 x 64 esos detalles casi no se ven.")
    add_pic(doc, FIG["errores"], 6.3)
    add_caption(doc, "Figura 9. Las cinco confusiones más frecuentes de EfficientNet-B0: arriba una imagen mal "
                     "clasificada y abajo un ejemplo de la especie que predijo el modelo.")

    # ---------------------------------------------------------------- 6
    add_heading(doc, "6. Conclusiones")
    add_para(doc,
        "Con el conjunto de prueba del repositorio TinyVGG parece llegar a "
        f"{p1(e1_10)}, pero con imágenes que no vio en el entrenamiento se queda en {p1(e2_10)} con las "
        "mismas 10 épocas. No me esperaba una diferencia tan grande por un shutil.copy. Se corrige moviendo "
        "las imágenes en get_data.py (shutil.move en lugar de shutil.copy) y sin aplicar aumento de datos "
        "al conjunto de prueba.")
    add_para(doc,
        "TinyVGG está bien para entender cómo funciona una CNN, pero para 151 clases con unas "
        f"{I['conteo_mediana']:.0f} imágenes por especie no alcanza. Tiene casi todos sus parámetros en la "
        "capa lineal, memoriza rápido el entrenamiento y en prueba ya no mejora después de la época 10. El "
        "aumento de datos ayuda, pero no suple la falta de ejemplos. Con transferencia de aprendizaje el "
        "resultado cambia mucho, porque EfficientNet-B0 ya sabe reconocer formas y texturas y solo tiene "
        f"que aprender a usarlas para separar especies. Con menos parámetros entrenables y 5 épocas llegó a "
        f"{p1(R['E4']['acc_final'])}.")
    add_para(doc,
        "Si siguiera con el proyecto, descongelaría los últimos bloques de EfficientNet-B0 con una tasa de "
        "aprendizaje más baja y le pondría el mismo aumento de datos que a TinyVGG. También separaría un "
        "conjunto de validación para escoger la época con early stopping, porque aquí la decidí viendo la "
        "prueba. Como casi todos los errores son entre especies de la misma línea evolutiva, valdría la pena "
        "conseguir más imágenes de esos casos o usar una resolución mayor.")

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
