# Actividad 3 · Red neuronal con una capa oculta

**Materia:** Tópicos Selectos de Grandes Bases de Datos II (NRC 176456)
**Profesor:** Mtro. Iván Alejandro Toledano Juárez
**Alumno:** Carlos Pulido Rosas

Los dos notebooks del tema 3 con las respuestas a sus preguntas, apoyadas en experimentos con las
mismas funciones de cada notebook.
Plantillas originales: [IvTole/Topicos_Selectos_II_CUCEA/03_neural_network_hidden_layer](https://github.com/IvTole/Topicos_Selectos_II_CUCEA/tree/main/03_neural_network_hidden_layer).

## Archivos

| Archivo | Plantilla | Contenido |
|---|---|---|
| `Actividad3_1_TopicosGBDII_CarlosPulidoRosas.py` | `03_red_neuronal_una_capa_oculta.py` | Red con una capa oculta: 1 contra 4 neuronas, tanh contra ReLU, capacidad contra optimización |
| `Actividad3_2_TopicosGBDII_CarlosPulidoRosas.py` | `03_visualizacion_neuronas_ocultas.py` | Qué aprende cada neurona oculta: rectas, neuronas redundantes, número de neuronas, pesos negativos |

Cada notebook viene también en `.ipynb` (ya ejecutado, se ve directo en GitHub) y `.html`.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
marimo edit Actividad3_1_TopicosGBDII_CarlosPulidoRosas.py   # abrir y usar los controles
marimo edit Actividad3_2_TopicosGBDII_CarlosPulidoRosas.py
jupyter notebook Actividad3_1_TopicosGBDII_CarlosPulidoRosas.ipynb  # versión Jupyter
```

## Resumen de resultados

**Notebook 3.1**
- Con una neurona oculta la frontera sigue siendo una recta (84.4 %); con cuatro se curva (97.2 %).
- Con cuatro neuronas tanh y ReLU dan casi lo mismo (97.2 % y 98.0 %); con tres, ReLU se queda en 87.2 %.
- Falta de capacidad: una neurona no mejora con más iteraciones ni con otro learning rate.
  Optimización: learning rate de 0.01, pocas iteraciones, o ReLU con 3 neuronas y mala
  inicialización (87.2 % con la semilla 42 contra 97.2 % con la semilla 3).

**Notebook 3.2**
- La neurona 3 tiene pesos pequeños y al apagarla la exactitud sigue en 100 %: no es necesaria.
- De 3 neuronas en adelante la exactitud ya no mejora (100 % en entrenamiento, 98.8 % en datos nuevos).
- Un peso de salida negativo solo indica el sentido: cambiar el signo de todos los pesos de la
  neurona da exactamente la misma red.
