import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    import numpy as np


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt

    return mo, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Actividad 1 · Entrenamiento paso a paso de una neurona artificial

    **Deep Learning para Computer Vision**

    **Nombre:** Carlos Pulido Rosas

    ## Objetivo
    Implementar y explicar el entrenamiento de una neurona para regresión con
    NumPy, desde una predicción inicial hasta la actualización de sus parámetros.
    Al finalizar, deberás relacionar las ecuaciones, las dimensiones de los
    arreglos y el comportamiento de la pérdida durante el aprendizaje.

    Usaremos una activación identidad: este modelo corresponde a una regresión
    lineal. En clase lo abordamos como una primera aproximación al perceptrón.

    ## Instrucciones y entrega
    - Completa las celdas con `TODO` y las respuestas marcadas con **Tu respuesta**.
    - Implementa el modelo con NumPy. No utilices modelos de scikit-learn,
      TensorFlow, PyTorch ni herramientas de diferenciación automática.
    - En cada paso incluye explicación, ecuación, código e interpretación.
    - Conserva la convención de ejemplos en las **columnas** de `X`.
    - Entrega este archivo `.py` de marimo con tus respuestas, código y gráficas.
      Debe ejecutarse completo sin errores y permitir reproducir los resultados.
    - Los bloques incompletos devuelven `None` para que puedas abrir la plantilla.
      Sustitúyelos por tu implementación; no dejes resultados escritos a mano
      como reemplazo del código.

    Esta actividad estudia la mecánica del entrenamiento. Los datos de trabajo
    se usan para entrenar; no se evaluará generalización a datos nuevos.

    > Nota: moví `import numpy as np` a `app.setup` para que las funciones
    > marcadas con `@app.function` (y las que dependen de ellas) puedan usarlo.
    > El resto de la estructura de la plantilla se conserva.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Problema y datos

    Predeciremos un **puntaje sintético de rendimiento** a partir de dos
    características numéricas ya preparadas. Estos datos son didácticos y no
    representan mediciones reales. No requieren limpieza ni estandarización.

    1. Identifica las entradas y la salida del modelo.
    2. ¿Por qué este problema es de regresión?
    3. ¿Qué significa un ejemplo de entrenamiento en esta tabla?

    **Respuesta:**

    1. Las entradas son las dos características numéricas (las filas de `X_datos`,
       $x_1$ y $x_2$). La salida es el puntaje de rendimiento (`y_datos`).
    2. Es regresión porque lo que queremos predecir es un número continuo
       (el puntaje puede valer -0.7, 1.3, 2.9, etc.) y no una clase o categoría.
    3. Un ejemplo es una fila de la tabla, que en `X` corresponde a una
       **columna**: un par de valores $(x_1, x_2)$ junto con el puntaje que le
       corresponde. Hay 8 ejemplos, así que $m = 8$.
    """)
    return


@app.cell
def _():
    X_datos = np.array([
        [-1.0, -0.5, 0.0, 0.5, 1.0, -1.0, 0.0, 1.0],
        [0.0, 1.0, -1.0, 0.5, -0.5, -1.0, 1.0, 1.0],
    ], dtype=float)
    y_datos = np.array([
        [-0.7, -0.9, 1.3, 1.0, 2.9, 0.6, -0.4, 1.2]
    ], dtype=float)
    return X_datos, y_datos


@app.cell
def _(X_datos, mo, y_datos):
    mo.ui.table([
        {"Ejemplo": i + 1, "Característica 1": float(X_datos[0, i]),
         "Característica 2": float(X_datos[1, i]), "Puntaje": float(y_datos[0, i])}
        for i in range(X_datos.shape[1])
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Dimensiones e inicialización

    Usaremos $m$ ejemplos, $n_x$ características y una salida:

    | Arreglo | Forma |
    |---|---|
    | $X$ | $(n_x,m)$ |
    | $y$ | $(1,m)$ |
    | $W$ | $(1,n_x)$ |
    | $b$ | $(1,1)$ |
    | $\hat y$ | $(1,m)$ |

    Completa `layer_sizes` e `initialize_parameters`. Inicializa pesos pequeños
    con `np.random.default_rng(seed)` y el sesgo en cero. Para esta neurona,
    inicializar en cero también sería posible; usaremos una semilla para
    comparar experimentos de forma reproducible.

    **Tu respuesta:**

    Con estos datos $n_x = 2$, $m = 8$ y $n_y = 1$, así que:
    $X$ es $(2, 8)$, $y$ es $(1, 8)$, $W$ es $(1, 2)$, $b$ es $(1, 1)$ y
    $\hat y$ es $(1, 8)$.

    El producto $WX$ es válido porque el número de columnas de $W$ (2) es igual
    al número de filas de $X$ (2); el resultado es $(1, 2)\cdot(2, 8) = (1, 8)$,
    una predicción por ejemplo. El sesgo $b$ es $(1, 1)$ y NumPy lo
    "estira" (broadcasting) a las 8 columnas, así que se suma el mismo $b$ a
    todas las predicciones.

    La semilla fija el generador de números aleatorios. Con la misma semilla
    los pesos iniciales salen siempre iguales, y eso permite repetir el
    entrenamiento y comparar experimentos (por ejemplo, distintas tasas de
    aprendizaje) partiendo exactamente del mismo punto.
    """)
    return


@app.function
def layer_sizes(X, y):
    # n_x: número de características (filas de X); n_y: número de salidas (filas de y)
    n_x = X.shape[0]
    n_y = y.shape[0]
    return n_x, n_y


@app.function
def initialize_parameters(n_x, n_y, seed=42):
    # pesos pequeños aleatorios y sesgo en cero
    rng = np.random.default_rng(seed)
    W = rng.normal(0.0, 0.01, size=(n_y, n_x))
    b = np.zeros((n_y, 1))
    return {"W": W, "b": b}


@app.cell
def _(X_datos, y_datos):
    n_x, n_y = layer_sizes(X_datos, y_datos)
    parametros_iniciales = initialize_parameters(n_x, n_y, seed=42)
    print(f"n_x = {n_x}, n_y = {n_y}, m = {X_datos.shape[1]}")
    print("W inicial:", parametros_iniciales["W"], "forma", parametros_iniciales["W"].shape)
    print("b inicial:", parametros_iniciales["b"], "forma", parametros_iniciales["b"].shape)
    return (parametros_iniciales,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Propagación hacia adelante

    $$Z=WX+b,\qquad \hat y=Z$$

    Implementa `forward_propagation`. Recibe los datos y un diccionario de
    parámetros; devuelve un arreglo con todas las predicciones.

    **Tu respuesta:**

    Los pesos indican cuánto pesa cada característica en la predicción: si
    $w_1$ es grande y positivo, al subir $x_1$ sube el puntaje; si es negativo,
    baja. El sesgo $b$ es el valor que predice el modelo cuando todas las
    entradas valen cero; mueve la recta (en este caso, el plano) hacia arriba o
    hacia abajo sin cambiar su inclinación.

    Usamos la identidad porque queremos predecir un número real sin límites.
    Una sigmoide, por ejemplo, encerraría la salida entre 0 y 1, y el puntaje
    puede ser negativo o mayor que 1. Con la identidad la neurona es
    exactamente una regresión lineal.
    """)
    return


@app.function
def forward_propagation(X, parameters):
    W = parameters["W"]
    b = parameters["b"]
    Z = W @ X + b      # (1, n_x) @ (n_x, m) + (1, 1) -> (1, m)
    y_hat = Z          # activación identidad
    return y_hat


@app.cell
def _(X_datos, parametros_iniciales):
    y_hat_inicial = forward_propagation(X_datos, parametros_iniciales)
    print("Predicciones iniciales:", y_hat_inicial.round(4), "forma", y_hat_inicial.shape)
    return (y_hat_inicial,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Función de pérdida

    $$J(W,b)=\frac{1}{2m}\sum_{i=1}^{m}(\hat y^{(i)}-y^{(i)})^2$$

    Implementa `compute_cost`: debe devolver un escalar. Utiliza `np.sum`;
    si aparecen valores no finitos, investiga su causa.

    **Tu respuesta:**

    Elevamos al cuadrado por dos razones. La primera es que así los errores
    positivos y negativos no se cancelan entre sí. La segunda es que los
    errores grandes se castigan mucho más que los chicos, y además la función
    queda suave y derivable en todos lados, lo que facilita el descenso del
    gradiente.

    El $\frac{1}{2}$ es solo por comodidad. Al derivar $(\hat y - y)^2$ aparece
    un 2 que se cancela con el $\frac{1}{2}$, y el gradiente queda simplemente
    $\frac{1}{m}\sum(\hat y - y)\,x$. No cambia dónde está el mínimo, solo
    escala la pérdida.

    Una pérdida de cero no garantiza que el modelo funcione bien con datos
    nuevos. Solo dice que se ajusta perfecto a los datos de entrenamiento; el
    modelo pudo haberse aprendido también el ruido (sobreajuste). Para saberlo
    habría que medir el error en datos que no usó para entrenar.
    """)
    return


@app.function
def compute_cost(y_hat, y):
    m = y.shape[1]
    cost = np.sum((y_hat - y) ** 2) / (2 * m)
    return float(cost)


@app.cell
def _(y_datos, y_hat_inicial):
    print(f"Pérdida inicial: {compute_cost(y_hat_inicial, y_datos):.6f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Gradientes y actualización

    Con pesos organizados como **fila**, las ecuaciones son:

    \[
    dZ=\hat y-y,\qquad dW=\frac{1}{m}dZ X^T,
    \qquad db=\frac{1}{m}\sum_{i=1}^{m}dZ^{(i)}\]

    \[W_{\mathrm{nuevo}}=W-\alpha dW,\qquad
    b_{\mathrm{nuevo}}=b-\alpha db\]

    Implementa las dos funciones. Conserva las formas de `dW` y `db`;
    `np.sum(..., axis=1, keepdims=True)` puede ayudarte con el sesgo.
    La actualización debe devolver un diccionario nuevo sin modificar
    los arreglos originales en el lugar.

    **Tu respuesta:**

    Para un ejemplo, la predicción es $\hat y^{(i)} = \sum_j W_j x_j^{(i)} + b$,
    así que $\partial \hat y^{(i)}/\partial W_j = x_j^{(i)}$ y
    $\partial \hat y^{(i)}/\partial b = 1$. Aplicando la regla de la cadena a la
    pérdida:

    $$\frac{\partial J}{\partial W_j}
    = \frac{1}{2m}\sum_{i=1}^{m} 2(\hat y^{(i)}-y^{(i)})\,\frac{\partial \hat y^{(i)}}{\partial W_j}
    = \frac{1}{m}\sum_{i=1}^{m} (\hat y^{(i)}-y^{(i)})\,x_j^{(i)}$$

    $$\frac{\partial J}{\partial b}
    = \frac{1}{2m}\sum_{i=1}^{m} 2(\hat y^{(i)}-y^{(i)})\cdot 1
    = \frac{1}{m}\sum_{i=1}^{m} (\hat y^{(i)}-y^{(i)})$$

    Si llamamos $dZ = \hat y - y$ (forma $(1, m)$), la suma sobre los ejemplos
    de $dZ^{(i)} x_j^{(i)}$ para todas las $j$ a la vez es justo el producto
    $dZ\,X^T$, de forma $(1, m)(m, n_x) = (1, n_x)$, la misma que $W$. Por eso
    $dW = \frac{1}{m} dZ X^T$ y $db$ es el promedio de $dZ$.

    Restamos el gradiente porque el gradiente apunta hacia donde la pérdida
    **crece** más rápido; movernos en sentido contrario la hace bajar. La tasa
    de aprendizaje $\alpha$ controla el tamaño de ese paso: si es muy chica el
    modelo aprende lento, y si es muy grande puede pasarse del mínimo y
    alejarse cada vez más.
    """)
    return


@app.function
def back_propagation(y_hat, y, X):
    m = X.shape[1]
    dZ = y_hat - y                                   # (1, m)
    dW = (1 / m) * (dZ @ X.T)                        # (1, n_x)
    db = (1 / m) * np.sum(dZ, axis=1, keepdims=True) # (1, 1)
    return {"dW": dW, "db": db}


@app.function
def update_parameters(parameters, grads, learning_rate):
    # se crean arreglos nuevos; no se modifican los originales en el lugar
    W = parameters["W"] - learning_rate * grads["dW"]
    b = parameters["b"] - learning_rate * grads["db"]
    return {"W": W, "b": b}


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Una iteración a mano y con NumPy

    Utiliza exclusivamente los siguientes dos ejemplos y parámetros:

    $$X_{\mathrm{manual}}=\begin{bmatrix}1&2\\0&1\end{bmatrix},
    \quad y_{\mathrm{manual}}=\begin{bmatrix}2&3\end{bmatrix}$$
    $$W_0=\begin{bmatrix}0&0\end{bmatrix},\quad b_0=0,\quad\alpha=0.1$$

    **Ejercicio:**, desarrolla a mano las predicciones iniciales,
    la pérdida, `dZ`, `dW`, `db`, los parámetros actualizados y la pérdida
    después de la actualización. Escribe las operaciones, no solo el resultado.

    **Tu desarrollo:**

    Aquí $m = 2$. El ejemplo 1 es $x^{(1)} = (1, 0)$ con $y^{(1)} = 2$ y el
    ejemplo 2 es $x^{(2)} = (2, 1)$ con $y^{(2)} = 3$.

    *Predicciones iniciales.* Con $W_0 = [0\ 0]$ y $b_0 = 0$:

    $$\hat y = W_0 X + b_0 = [0\cdot1 + 0\cdot0,\ \ 0\cdot2 + 0\cdot1] + 0 = [0\ \ 0]$$

    *Pérdida inicial.*

    $$J_0 = \frac{1}{2\cdot2}\left[(0-2)^2 + (0-3)^2\right] = \frac{4 + 9}{4} = 3.25$$

    *Gradientes.*

    $$dZ = \hat y - y = [0-2,\ \ 0-3] = [-2\ \ -3]$$

    $$dZ\,X^T = [-2\ \ -3]\begin{bmatrix}1&0\\2&1\end{bmatrix}
    = [(-2)(1) + (-3)(2),\ \ (-2)(0) + (-3)(1)] = [-8\ \ -3]$$

    $$dW = \tfrac{1}{2}[-8\ \ -3] = [-4\ \ -1.5],\qquad
    db = \tfrac{1}{2}(-2 - 3) = -2.5$$

    *Actualización.*

    $$W_1 = [0\ \ 0] - 0.1\,[-4\ \ -1.5] = [0.4\ \ 0.15],\qquad
    b_1 = 0 - 0.1(-2.5) = 0.25$$

    *Nuevas predicciones y pérdida.*

    $$\hat y^{(1)} = 0.4(1) + 0.15(0) + 0.25 = 0.65,\qquad
    \hat y^{(2)} = 0.4(2) + 0.15(1) + 0.25 = 1.20$$

    $$J_1 = \frac{1}{4}\left[(0.65-2)^2 + (1.20-3)^2\right]
    = \frac{1.8225 + 3.24}{4} = \frac{5.0625}{4} = 1.265625$$

    Después, completa la celda para repetir el cálculo usando tus funciones.
    Muestra los valores y comprueba que coinciden con tu
    desarrollo manual. Explica cualquier diferencia por redondeo.

    **Tu interpretación:**

    La pérdida bajó de 3.25 a 1.265625, un poco más de la mitad en un solo
    paso. Las dos predicciones subieron hacia sus valores reales (de 0 a 0.65 y
    de 0 a 1.20), aunque todavía quedan lejos de 2 y 3; con más iteraciones
    seguirían acercándose. Los valores de NumPy coinciden con los calculados a
    mano. Las únicas diferencias posibles son del orden de $10^{-16}$, por cómo
    la computadora representa números como 0.1 en punto flotante.
    """)
    return


@app.cell
def _():
    X_manual = np.array([[1.0, 2.0], [0.0, 1.0]])
    y_manual = np.array([[2.0, 3.0]])
    parametros_manual = {"W": np.zeros((1, 2)), "b": np.zeros((1, 1))}
    alpha_manual = 0.1

    y_hat_0 = forward_propagation(X_manual, parametros_manual)
    J_0 = compute_cost(y_hat_0, y_manual)
    grads_manual = back_propagation(y_hat_0, y_manual, X_manual)
    parametros_1 = update_parameters(parametros_manual, grads_manual, alpha_manual)
    y_hat_1 = forward_propagation(X_manual, parametros_1)
    J_1 = compute_cost(y_hat_1, y_manual)

    print("Predicciones iniciales:", y_hat_0)
    print("Pérdida inicial:", J_0)
    print("dZ:", y_hat_0 - y_manual)
    print("dW:", grads_manual["dW"], " db:", grads_manual["db"])
    print("W1:", parametros_1["W"], " b1:", parametros_1["b"])
    print("Predicciones después:", y_hat_1)
    print("Pérdida después:", J_1)

    # comprobación contra el desarrollo manual
    assert np.isclose(J_0, 3.25)
    assert np.allclose(grads_manual["dW"], [[-4.0, -1.5]])
    assert np.allclose(grads_manual["db"], [[-2.5]])
    assert np.allclose(parametros_1["W"], [[0.4, 0.15]]) and np.allclose(parametros_1["b"], [[0.25]])
    assert np.allclose(y_hat_1, [[0.65, 1.20]]) and np.isclose(J_1, 1.265625)
    # los parámetros originales no se modificaron en el lugar
    assert np.all(parametros_manual["W"] == 0) and np.all(parametros_manual["b"] == 0)
    print("Coincide con el cálculo manual.")
    return X_manual, y_manual


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Ciclo de entrenamiento

    Integra tus funciones en `train_model`:

    1. Obtén las dimensiones usando los argumentos `X` e `y`.
    2. Inicializa los parámetros una sola vez.
    3. Guarda la pérdida inicial.
    4. En cada iteración: predice, calcula gradientes, actualiza parámetros
       y guarda la pérdida **después** de actualizar.
    5. Devuelve los parámetros finales y el historial de pérdidas.

    El historial debe tener `iterations + 1` valores: el índice cero es
    la pérdida antes de entrenar. Usa únicamente los datos recibidos por
    la función, para que también funcione con el conjunto del cálculo manual.

    Entrena con 200 iteraciones, tasa 0.1 y semilla 42. Muestra los parámetros,
    las predicciones finales, las pérdidas inicial y final y una gráfica
    de pérdida contra número de actualizaciones.

    **Tu respuesta:**

    En cada iteración se repiten los mismos cuatro pasos: predecir con los
    parámetros actuales, calcular el error y los gradientes, actualizar $W$ y
    $b$, y guardar la nueva pérdida. Lo que se conserva de una iteración a otra
    son los parámetros: cada vuelta parte de los $W$ y $b$ que dejó la anterior
    (no se vuelven a inicializar). Los datos tampoco cambian.

    Sí, cada iteración usa los 8 ejemplos a la vez, porque los gradientes son
    el promedio sobre todo $X$. Esto se llama descenso del gradiente por lotes
    completos (*batch*). Si se usara un solo ejemplo o un subconjunto por paso
    sería descenso estocástico o por minilotes.
    """)
    return


@app.function
def train_model(X, y, iterations=200, learning_rate=0.1, seed=42):
    n_x, n_y = layer_sizes(X, y)
    parameters = initialize_parameters(n_x, n_y, seed=seed)
    cost_history = [compute_cost(forward_propagation(X, parameters), y)]
    for _ in range(iterations):
        y_hat = forward_propagation(X, parameters)
        grads = back_propagation(y_hat, y, X)
        parameters = update_parameters(parameters, grads, learning_rate)
        cost_history.append(compute_cost(forward_propagation(X, parameters), y))
    return parameters, np.array(cost_history)


@app.cell
def _(X_datos, plt, y_datos):
    params_final, historial = train_model(X_datos, y_datos, iterations=200,
                                          learning_rate=0.1, seed=42)
    y_hat_final = forward_propagation(X_datos, params_final)

    print("W final:", params_final["W"].round(4))
    print("b final:", params_final["b"].round(4))
    print("Predicciones finales:", y_hat_final.round(3))
    print("Valores reales:      ", y_datos)
    print(f"Pérdida inicial: {historial[0]:.6f}")
    print(f"Pérdida final:   {historial[-1]:.6f}")
    print("Valores en el historial:", len(historial))

    fig_entrenamiento, ax_entrenamiento = plt.subplots(figsize=(7, 4))
    ax_entrenamiento.plot(range(len(historial)), historial, color="#1F497D", lw=2)
    ax_entrenamiento.set_xlabel("Número de actualizaciones")
    ax_entrenamiento.set_ylabel("Pérdida J(W, b)")
    ax_entrenamiento.set_title("Pérdida durante el entrenamiento (α = 0.1)")
    ax_entrenamiento.grid(alpha=0.3)
    fig_entrenamiento
    return historial, params_final


@app.cell(hide_code=True)
def _(historial, mo, params_final):
    mo.md(rf"""
    **Interpretación.** La pérdida baja de {historial[0]:.4f} a {historial[-1]:.4f}.
    La curva cae rápido en las primeras 30 o 40 iteraciones y después se va
    aplanando, porque conforme el modelo se acerca al mínimo los gradientes se
    hacen más chicos y los pasos también. Los pesos finales
    ($w_1 \approx$ {params_final["W"][0, 0]:.3f}, $w_2 \approx$ {params_final["W"][0, 1]:.3f})
    indican que el puntaje sube con la característica 1 y baja con la 2. La
    pérdida no llega a cero porque los datos no caen exactamente sobre un plano:
    queda un error que un modelo lineal no puede eliminar.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Experimento con la tasa de aprendizaje

    Repite el entrenamiento con $\alpha\in\{0.01,0.1,3.0\}$.
    Usa los mismos datos, **200 iteraciones y la misma semilla** en todos
    los casos. Reinicia el entrenamiento del modelo para cada experimento.

    - Grafica las tres curvas, con leyenda y ejes etiquetados. Puedes usar
      escala logarítmica o paneles separados si las magnitudes lo requieren.
    - Construye una tabla con tasa, pérdida inicial, pérdida final y
      si observaste convergencia, oscilaciones o divergencia.
    - Si aparecen valores no finitos, indícalos y explica lo ocurrido.
    """)
    return


@app.cell
def _(X_datos, mo, plt, y_datos):
    tasas = [0.01, 0.1, 3.0]
    historiales = {}
    for alpha in tasas:
        # train_model inicializa de nuevo en cada llamada: cada experimento arranca igual
        _, historiales[alpha] = train_model(X_datos, y_datos, iterations=200,
                                            learning_rate=alpha, seed=42)

    def comportamiento(h):
        if not np.all(np.isfinite(h)):
            return "Divergencia (valores no finitos)"
        if h[-1] > h[0]:
            return "Divergencia"
        if np.any(np.diff(h) > 0):
            return "Oscilaciones"
        if abs(h[-1] - h[-2]) < 1e-6:
            return "Convergencia"
        return "Converge, pero lento (sigue bajando)"

    tabla_tasas = [
        {"Tasa α": alpha,
         "Pérdida inicial": f"{historiales[alpha][0]:.6f}",
         "Pérdida final": f"{historiales[alpha][-1]:.6g}",
         "Valores finitos": bool(np.all(np.isfinite(historiales[alpha]))),
         "Comportamiento": comportamiento(historiales[alpha])}
        for alpha in tasas
    ]

    fig_tasas, axes_tasas = plt.subplots(1, 2, figsize=(11, 4))
    colores = {0.01: "#D48C00", 0.1: "#1F497D", 3.0: "#C0392B"}
    for alpha in [0.01, 0.1]:
        axes_tasas[0].plot(historiales[alpha], color=colores[alpha], lw=2, label=f"α = {alpha}")
    axes_tasas[0].set_title("Tasas que convergen")
    axes_tasas[0].set_xlabel("Número de actualizaciones")
    axes_tasas[0].set_ylabel("Pérdida J(W, b)")
    axes_tasas[0].legend(); axes_tasas[0].grid(alpha=0.3)
    for alpha in tasas:
        axes_tasas[1].semilogy(historiales[alpha], color=colores[alpha], lw=2, label=f"α = {alpha}")
    axes_tasas[1].set_title("Las tres tasas (escala logarítmica)")
    axes_tasas[1].set_xlabel("Número de actualizaciones")
    axes_tasas[1].set_ylabel("Pérdida J(W, b), escala log")
    axes_tasas[1].legend(); axes_tasas[1].grid(alpha=0.3, which="both")
    plt.tight_layout()

    mo.vstack([mo.ui.table(tabla_tasas), fig_tasas])
    return (historiales,)


@app.cell(hide_code=True)
def _(historiales, mo):
    _h3 = historiales[3.0]
    _crec = _h3[-1] / _h3[-2]
    mo.md(rf"""
    **Tu análisis:**

    Con $\alpha = 0.01$ la pérdida baja todo el tiempo, pero muy despacio:
    después de 200 iteraciones va en {historiales[0.01][-1]:.4f} y sigue
    bajando. Con $\alpha = 0.1$ baja rápido y se estabiliza en
    {historiales[0.1][-1]:.4f}; en las últimas iteraciones ya casi no cambia,
    así que llegó prácticamente al mínimo. Con $\alpha = 3.0$ pasa lo contrario:
    la pérdida sube en cada paso (en cada iteración se multiplica por
    alrededor de {_crec:.1f}) hasta llegar a {_h3[-1]:.2e}. Los valores siguen
    siendo finitos en estas 200 iteraciones, pero son enormes; con unas cuantas
    más se desbordarían a `inf` y luego a `nan`.

    Elegiría $\alpha = 0.1$, porque es la única de las tres que llega al
    mínimo dentro de las 200 iteraciones sin volverse inestable.

    Una tasa mayor no siempre es mejor porque el gradiente solo dice hacia
    dónde bajar cerca del punto actual. Si el paso es demasiado grande, el
    modelo se pasa del mínimo y cae del otro lado del "valle" en un punto más
    alto que donde estaba; en el siguiente paso el gradiente es todavía mayor y
    el error crece cada vez más. Para esta pérdida cuadrática se puede ver que
    el descenso solo es estable si $\alpha$ es menor que $2/\lambda_{{max}}$,
    donde $\lambda_{{max}}$ es el valor propio más grande de
    $\frac{{1}}{{m}}\tilde X \tilde X^T$ (con una fila de unos para el sesgo).
    Con estos datos $\lambda_{{max}} \approx 1.05$, así que el límite es
    $\alpha \approx 1.9$, y 3.0 queda por encima.

    Con 200 iteraciones puedo decir que 0.1 converge, que 0.01 va en la
    dirección correcta pero lento y que 3.0 diverge. Lo que no puedo afirmar es
    que 0.1 sea la mejor tasa posible (no probé valores intermedios como 0.5 o
    1.0), ni que 0.01 no llegaría al mismo resultado con más iteraciones. Y
    como solo usé datos de entrenamiento, tampoco puedo decir nada de cómo
    funcionaría el modelo con datos nuevos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Comprobación de la implementación

    Para la pregunta 3 de las conclusiones hice dos verificaciones con NumPy.
    La primera compara los gradientes de `back_propagation` con una
    aproximación numérica por diferencias finitas:
    $\frac{\partial J}{\partial \theta} \approx \frac{J(\theta+\varepsilon) - J(\theta-\varepsilon)}{2\varepsilon}$.
    La segunda compara los parámetros entrenados con la solución exacta de
    mínimos cuadrados (`np.linalg.lstsq`), que es el mínimo al que debería
    llegar el descenso del gradiente.
    """)
    return


@app.cell
def _(X_datos, params_final, parametros_iniciales, y_datos):
    # 1) gradiente analítico vs numérico, en los parámetros iniciales
    eps = 1e-6
    grads_analiticos = back_propagation(forward_propagation(X_datos, parametros_iniciales), y_datos, X_datos)
    theta = np.concatenate([parametros_iniciales["W"].ravel(), parametros_iniciales["b"].ravel()])

    def costo_theta(t):
        p = {"W": t[:2].reshape(1, 2), "b": t[2:].reshape(1, 1)}
        return compute_cost(forward_propagation(X_datos, p), y_datos)

    grads_numericos = np.array([
        (costo_theta(theta + eps * e) - costo_theta(theta - eps * e)) / (2 * eps)
        for e in np.eye(3)
    ])
    grads_analiticos_vec = np.concatenate([grads_analiticos["dW"].ravel(), grads_analiticos["db"].ravel()])
    print("Gradiente analítico:", grads_analiticos_vec.round(8))
    print("Gradiente numérico: ", grads_numericos.round(8))
    print("Diferencia máxima:  ", np.abs(grads_analiticos_vec - grads_numericos).max())

    # 2) solución exacta de mínimos cuadrados
    A = np.vstack([X_datos, np.ones(X_datos.shape[1])]).T
    solucion_exacta = np.linalg.lstsq(A, y_datos.ravel(), rcond=None)[0]
    entrenados = np.concatenate([params_final["W"].ravel(), params_final["b"].ravel()])
    print("Mínimos cuadrados (w1, w2, b):", solucion_exacta.round(5))
    print("Descenso del gradiente:       ", entrenados.round(5))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Los dos gradientes coinciden hasta el orden de $10^{-10}$, y los parámetros
    entrenados con $\alpha = 0.1$ quedan prácticamente iguales a la solución
    exacta (difieren en la cuarta cifra decimal). Eso confirma que la
    derivación y el código están bien, más allá de ver que la pérdida baja.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Conclusiones y conexión con Deep Learning

    Responde con referencia a tus resultados:

    1. ¿Qué significa que la neurona haya aprendido? Relaciona parámetros,
       predicciones y pérdida.
    2. ¿Qué diferencia existe entre calcular gradientes y actualizar parámetros?
    3. ¿Cómo comprobarías si una implementación entrega resultados correctos,
       además de observar que la pérdida disminuye?
    4. Si usamos sigmoide y entropía cruzada para clasificación binaria,
       ¿qué partes del proceso cambian y cuáles conservan su estructura?

    **Tus conclusiones:**

    1. Que la neurona aprendió quiere decir que ajustó sus parámetros para que
       sus predicciones se parezcan a los datos. Empezó con pesos casi en cero,
       que predecían prácticamente 0 para todo, y una pérdida de 0.89. Después
       de 200 iteraciones con $\alpha = 0.1$ los pesos quedaron en
       $w \approx (1.42, -1.00)$ y $b \approx 0.75$, las predicciones quedaron
       cerca de los puntajes reales y la pérdida bajó a 0.022. Lo que
       "aprende" el modelo está guardado en esos tres números.

    2. Calcular los gradientes es medir: dice en qué dirección y con qué
       intensidad cambia la pérdida si se mueve cada parámetro, pero no cambia
       nada. Actualizar es actuar: usar esa información para mover los
       parámetros un paso de tamaño $\alpha$ en contra del gradiente. Por eso
       las separé en dos funciones, `back_propagation` y `update_parameters`.

    3. Además de que la pérdida baje, comprobaría tres cosas, que son las que
       hice en este notebook: (a) que una iteración coincida con el cálculo a
       mano en un caso pequeño (sección 6); (b) que los gradientes analíticos
       coincidan con los numéricos por diferencias finitas; y (c) en un caso
       como este, que tiene solución exacta, que el resultado coincida con
       mínimos cuadrados. También revisaría que las formas de los arreglos sean
       las esperadas en cada paso.

    4. Con sigmoide y entropía cruzada cambian la activación,
       $\hat y = \sigma(Z) = 1/(1+e^{-Z})$, y la función de pérdida,
       $J = -\frac{1}{m}\sum [y\log\hat y + (1-y)\log(1-\hat y)]$. Las
       predicciones pasan a ser probabilidades entre 0 y 1. Lo demás se
       conserva igual: las dimensiones, $Z = WX + b$, el ciclo de
       predecir, calcular gradientes y actualizar, y la regla
       $W \leftarrow W - \alpha\,dW$. Incluso las fórmulas de los gradientes
       quedan con la misma forma, $dZ = \hat y - y$, $dW = \frac{1}{m}dZ X^T$ y
       $db = \frac{1}{m}\sum dZ$, porque la derivada de la sigmoide se cancela
       con la de la entropía cruzada.

    ## Rúbrica

    | Criterio | Valor | Evidencia esperada |
    |---|---:|---|
    | Implementación correcta | 40 % | Dimensiones coherentes, funciones propias, actualización y ciclo completos; coincidencia con la iteración manual. |
    | Explicación matemática | 30 % | Ecuaciones, derivación de gradientes y explicación del papel de cada paso. |
    | Experimentación e interpretación | 20 % | Comparación controlada de tasas, gráficas, tabla y conclusiones sustentadas. |
    | Claridad y reproducibilidad | 10 % | Notebook ordenado, semilla fija, respuestas completas y ejecución sin errores. |

    Revisa tus resultados antes de entregar.
    """)
    return


if __name__ == "__main__":
    app.run()
