# Actividad 4 · Red neuronal profunda

**Materia:** Tópicos Selectos de Grandes Bases de Datos II (NRC 176456)
**Profesor:** Mtro. Iván Alejandro Toledano Juárez
**Alumno:** Carlos Pulido Rosas

Notebook del profesor con las respuestas a sus cinco preguntas, apoyadas en experimentos con las
mismas funciones del notebook.
Plantilla original: [IvTole/Topicos_Selectos_II_CUCEA](https://github.com/IvTole/Topicos_Selectos_II_CUCEA/blob/main/04_deep_neural_network/04_red_neuronal_profunda.py).

## Archivos

| Archivo | Contenido |
|---|---|
| `Actividad4_TopicosGBDII_CarlosPulidoRosas.py` | Notebook de marimo con código, respuestas y gráficas (entregable) |
| `Actividad4_TopicosGBDII_CarlosPulidoRosas.ipynb` | El mismo notebook en formato Jupyter, ya ejecutado (se ve directo en GitHub) |
| `Actividad4_TopicosGBDII_CarlosPulidoRosas.html` | El mismo notebook ya ejecutado, para ver los resultados sin instalar nada |
| `requirements.txt` | Dependencias |

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
marimo edit Actividad4_TopicosGBDII_CarlosPulidoRosas.py   # abrir y usar los controles
jupyter notebook Actividad4_TopicosGBDII_CarlosPulidoRosas.ipynb  # versión Jupyter
```

## Resumen de resultados

- Más profundidad no garantiza mejorar: con 6 neuronas por capa las lunas pasan de 98.7 % (1 capa) a
  99.7 % (3 capas) y la cuarta capa ya no aporta; con ReLU, 4 capas de 3 neuronas caen a 89.7 %.
- tanh y ReLU clasifican igual con la arquitectura por defecto; ReLU da fronteras poligonales y
  tiene neuronas muertas en redes más profundas.
- No convergen: learning rate 0.01 con 500 iteraciones (lento), ReLU con 4 capas de 2 neuronas
  (neuronas muertas desde la inicialización, gradiente exactamente cero) y tanh con la misma
  arquitectura (desvanecimiento del gradiente).
- La arquitectura por defecto [2, 6, 6, 1] tiene 67 parámetros, Σ n_l (n_{l-1} + 1).
- Tabla de equivalencias con PyTorch (`nn.Linear`, activaciones, `BCELoss`, `backward`, `optimizer.step`).
