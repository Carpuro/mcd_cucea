# Actividad 2 · Límites de un perceptrón

**Materia:** Tópicos Selectos de Grandes Bases de Datos II (NRC 176456)
**Profesor:** Mtro. Iván Alejandro Toledano Juárez
**Alumno:** Carlos Pulido Rosas

Notebook del profesor con las respuestas a las cuatro preguntas, apoyadas en experimentos con las
mismas funciones del notebook.
Plantilla original: [IvTole/Topicos_Selectos_II_CUCEA](https://github.com/IvTole/Topicos_Selectos_II_CUCEA/blob/main/02_perceptron_limits/02_perceptron_limites.py).

## Archivos

| Archivo | Contenido |
|---|---|
| `Actividad2_TopicosGBDII_CarlosPulidoRosas.py` | Notebook de marimo con código, respuestas y gráficas (entregable) |
| `Actividad2_TopicosGBDII_CarlosPulidoRosas.ipynb` | El mismo notebook en formato Jupyter, ya ejecutado (se ve directo en GitHub) |
| `Actividad2_TopicosGBDII_CarlosPulidoRosas.html` | El mismo notebook ya ejecutado, para ver los resultados sin instalar nada |
| `requirements.txt` | Dependencias |

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
marimo edit Actividad2_TopicosGBDII_CarlosPulidoRosas.py   # abrir y usar los controles
marimo run Actividad2_TopicosGBDII_CarlosPulidoRosas.py    # solo ver
jupyter notebook Actividad2_TopicosGBDII_CarlosPulidoRosas.ipynb  # versión Jupyter
```

## Resumen de resultados

- Exactitud con una sola neurona: grupos separables 100 %, dos lunas 86.5 %, XOR 50 %.
- En XOR el costo se queda en ln 2 = 0.6931 con 100 o con 20,000 iteraciones y con cualquier
  learning rate: el límite es de capacidad del modelo, no de optimización.
- Agregar variables lineales o de ruido no resuelve XOR; agregar x1·x2 sí (100 %), y eso es lo
  que una capa oculta aprende por su cuenta.
