# Tópicos Selectos de Grandes Bases de Datos II
**Semestre:** 3ro | **Departamento:** DMC | **Créditos:** 7
**Profesor:** Mtro. Iván Alejandro Toledano Juárez | **NRC:** 176456 | **Día:** martes (en línea)

Deep learning desde cero: de una neurona entrenada con descenso del gradiente a redes profundas
escritas solo con NumPy, antes de pasar a PyTorch. El material del profesor está en
[IvTole/Topicos_Selectos_II_CUCEA](https://github.com/IvTole/Topicos_Selectos_II_CUCEA).

## Actividades (`tareas/`)

Cada actividad parte del notebook de marimo del profesor y agrega las respuestas a sus preguntas,
apoyadas en experimentos con las mismas funciones del notebook. Cada carpeta tiene el notebook en
`.py` (marimo, el entregable), `.ipynb` (Jupyter, ya ejecutado) y `.html`, más un `README.md` y un
`requirements.txt`.

| # | Actividad | Tema | Carpeta |
|---|-----------|------|---------|
| 1 | Entrenamiento paso a paso de una neurona artificial | Regresión con una neurona, gradientes, iteración a mano, tasa de aprendizaje | [Actividad1](tareas/Actividad1/) |
| 2 | Límites de un perceptrón | Frontera lineal, XOR, capacidad contra optimización | [Actividad2](tareas/Actividad2/) |
| 3 | Red neuronal con una capa oculta | Dos notebooks: la red con capa oculta y qué aprende cada neurona | [Actividad3](tareas/Actividad3/) |
| 4 | Red neuronal profunda | `layer_dims`, profundidad, tanh contra ReLU, no convergencia, parámetros, PyTorch | [Actividad4](tareas/Actividad4/) |

Convención de nombres: `ActividadN_TopicosGBDII_CarlosPulidoRosas.py`. Cuando una actividad tiene
dos notebooks se numeran `ActividadN_1_…` y `ActividadN_2_…`.

## Cómo ejecutar

```bash
pip install -r tareas/Actividad4/requirements.txt
marimo edit tareas/Actividad4/Actividad4_TopicosGBDII_CarlosPulidoRosas.py
```

## Herramientas

Python · NumPy · Matplotlib · scikit-learn (datos sintéticos) · marimo · Jupyter
