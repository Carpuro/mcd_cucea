# Actividad 1 · Entrenamiento paso a paso de una neurona artificial

**Materia:** Tópicos Selectos de Grandes Bases de Datos II (NRC 176456)
**Profesor:** Mtro. Iván Alejandro Toledano Juárez
**Alumno:** Carlos Pulido Rosas

Neurona para regresión implementada solo con NumPy y entrenada con descenso del gradiente.
Plantilla original: [IvTole/Topicos_Selectos_II_CUCEA](https://github.com/IvTole/Topicos_Selectos_II_CUCEA/blob/main/01_perceptron/01_actividad_entrenamiento_neurona_regresion.py).

## Archivos

| Archivo | Contenido |
|---|---|
| `01_actividad_entrenamiento_neurona_regresion.py` | Notebook de marimo con código, respuestas y gráficas (entregable) |
| `01_actividad_entrenamiento_neurona_regresion.html` | El mismo notebook ya ejecutado, para ver los resultados sin instalar nada |
| `requirements.txt` | Dependencias |

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
marimo edit 01_actividad_entrenamiento_neurona_regresion.py   # abrir y editar
marimo run 01_actividad_entrenamiento_neurona_regresion.py    # solo ver
python 01_actividad_entrenamiento_neurona_regresion.py        # ejecutar como script
```

Con el entorno del repo del profesor (`uv`) también funciona: `uv run marimo edit <archivo>`.

## Resumen de resultados

- La iteración manual (sección 6) coincide con NumPy: la pérdida pasa de 3.25 a 1.265625.
- Con α = 0.1, 200 iteraciones y semilla 42, la pérdida baja de 0.8917 a 0.0224 y los parámetros
  llegan a W ≈ (1.421, −0.995), b ≈ 0.749, prácticamente la solución exacta de mínimos cuadrados.
- α = 0.01 converge lento, α = 3.0 diverge (el límite de estabilidad con estos datos es α ≈ 1.9).
- Los gradientes analíticos coinciden con los numéricos (diferencias finitas) hasta ~1e-10.
