# Actividad 1 · Entrenamiento paso a paso de una neurona artificial

**Materia:** Tópicos Selectos de Grandes Bases de Datos II (NRC 176456)
**Profesor:** Mtro. Iván Alejandro Toledano Juárez
**Alumno:** Carlos Pulido Rosas

Neurona para regresión implementada solo con NumPy y entrenada con descenso del gradiente.
Plantilla original: [IvTole/Topicos_Selectos_II_CUCEA](https://github.com/IvTole/Topicos_Selectos_II_CUCEA/blob/main/01_perceptron/01_actividad_entrenamiento_neurona_regresion.py).

## Archivos

| Archivo | Contenido |
|---|---|
| `Actividad1_TopicosGBDII_CarlosPulidoRosas.py` | Notebook de marimo con código, respuestas y gráficas (entregable) |
| `Actividad1_TopicosGBDII_CarlosPulidoRosas.ipynb` | El mismo notebook en formato Jupyter, ya ejecutado (se ve directo en GitHub) |
| `Actividad1_TopicosGBDII_CarlosPulidoRosas.html` | El mismo notebook ya ejecutado, para ver los resultados sin instalar nada |
| `requirements.txt` | Dependencias |

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
marimo edit Actividad1_TopicosGBDII_CarlosPulidoRosas.py   # abrir y editar
marimo run Actividad1_TopicosGBDII_CarlosPulidoRosas.py    # solo ver
python Actividad1_TopicosGBDII_CarlosPulidoRosas.py        # ejecutar como script
jupyter notebook Actividad1_TopicosGBDII_CarlosPulidoRosas.ipynb  # versión Jupyter
```

Con el entorno del repo del profesor (`uv`) también funciona: `uv run marimo edit <archivo>`.

## Resumen de resultados

- La iteración manual (sección 6) coincide con NumPy: la pérdida pasa de 3.25 a 1.265625.
- Con α = 0.1, 200 iteraciones y semilla 42, la pérdida baja de 0.8917 a 0.0224 y los parámetros
  llegan a W ≈ (1.421, −0.995), b ≈ 0.749, prácticamente la solución exacta de mínimos cuadrados.
- α = 0.01 converge lento y α = 3.0 oscila y diverge (w1 cambia de dirección en las 199 iteraciones);
  probando tasas intermedias, a partir de α = 2.0 diverge.
- Tabla y gráfica de valores reales contra predichos antes y después de entrenar.
- Los gradientes analíticos coinciden con los numéricos (diferencias finitas) hasta ~1e-10.
