# /// script
# requires-python = ">=3.10"
# dependencies = ["marimo>=0.24.0", "matplotlib>=3.8", "numpy>=1.26", "scikit-learn>=1.4"]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.datasets import make_moons

    return make_moons, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Actividad 3 · ¿Qué aprende cada neurona oculta?**

    **Nombre:** Carlos Pulido Rosas
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ¿Qué aprende cada neurona oculta?

    En el tema anterior, se observó la frontera producida por toda la red. Sin embargo, la capa oculta contiene varias neuronas y cada una aprende parámetros diferentes.

    En el notebook anterior observamos la frontera producida por toda la red. Sin
    embargo, la capa oculta contiene varias neuronas y cada una aprende parámetros
    diferentes:

    \[
    z_j^{[1]}=w_{j1}^{[1]}x_1+w_{j2}^{[1]}x_2+b_j^{[1]}
    \]

    donde \(z_j^{[1]}=0\) describe una recta. La activación indica en qué lado de esta recta se encuentra dicha observación.
    """)
    return


@app.cell
def _(mo):
    neuronas = mo.ui.slider(2, 8, value=4, step=1, label="Número de neuronas")
    ruido = mo.ui.slider(0.02, 0.30, value=0.14, step=0.01, label="Ruido")
    iteraciones = mo.ui.slider(500, 8000, value=4000, step=250, label="Iteraciones")
    learning_rate = mo.ui.slider(0.05, 1.5, value=0.8, step=0.05, label="Learning rate")

    mo.vstack([
        mo.md("### Controles del modelo"),
        mo.hstack([neuronas, ruido]),
        mo.hstack([iteraciones, learning_rate]),
    ])
    return iteraciones, learning_rate, neuronas, ruido


@app.cell
def _(make_moons, ruido):
    # Se generan datos ficticios
    muestras, etiquetas = make_moons(
        n_samples=250, noise=ruido.value, random_state=12
    )
    X = muestras.T
    Y = etiquetas.reshape(1, -1)
    return X, Y


@app.cell
def _(np):
    def sigmoid(Z):
        return 1 / (1 + np.exp(-np.clip(Z, -500, 500)))

    def initialize_parameters(n_x, n_h, semilla=5):
        generador = np.random.default_rng(semilla)

        W1 = generador.normal(0, np.sqrt(1 / n_x), (n_h, n_x))
        b1 = np.zeros((n_h, 1))
        W2 = generador.normal(0, np.sqrt(1 / n_h), (1, n_h))
        b2 = np.zeros((1, 1))

        parameters = {
            "W1":W1,
            "b1":b1,
            "W2":W2,
            "b2":b2
        }
    
        return parameters

    def forward_propagation(X, parameters):

        # parametros, pesos y sesgos
        W1 = parameters["W1"]
        b1 = parameters["b1"]
        W2 = parameters["W2"]
        b2 = parameters["b2"]

        Z1 = np.matmul(W1,X) + b1
        A1 = np.tanh(Z1)
        Z2 = np.matmul(W2,A1) + b2
        A2 = sigmoid(Z2) # salida

        cache = {
            "Z1":Z1,
            "A1":A1,
            "Z2":Z2,
            "A2":A2
        }
    
        return A2, cache

    def nn_model(X, Y, n_h, num_iterations, learning_rate):
        """Entrena la red de dos capas utilizando descenso del gradiente."""
        m = X.shape[1]
        parameters = initialize_parameters(X.shape[0], n_h)
        costs = []

        for i in range(num_iterations):
            A2, cache = forward_propagation(X, parameters)
            A2_segura = np.clip(A2, 1e-10, 1 - 1e-10)
            cost = -np.mean(Y * np.log(A2_segura) + (1 - Y) * np.log(1 - A2_segura))

            dZ2 = A2 - Y
            dW2 = np.matmul(dZ2,cache["A1"].T) / m
            db2 = np.sum(dZ2, axis=1, keepdims=True) / m
            dA1 = np.matmul(parameters["W2"].T,dZ2)
            dZ1 = dA1 * (1 - cache["A1"] ** 2)
            dW1 = np.matmul(dZ1, X.T) / m
            db1 = np.sum(dZ1, axis=1, keepdims=True) / m

            parameters["W1"] -= learning_rate * dW1
            parameters["b1"] -= learning_rate * db1
            parameters["W2"] -= learning_rate * dW2
            parameters["b2"] -= learning_rate * db2

            if i % 20 == 0:
                costs.append((i, cost))

        return parameters, costs

    return forward_propagation, nn_model


@app.cell
def _(
    X,
    Y,
    forward_propagation,
    iteraciones,
    learning_rate,
    neuronas,
    nn_model,
    np,
):
    parameters, costs = nn_model(
        X, Y,
        n_h=neuronas.value,
        num_iterations=iteraciones.value,
        learning_rate=learning_rate.value,
    )
    A2, cache = forward_propagation(X, parameters)
    accuracy = float(np.mean((A2 > 0.5) == Y))
    return accuracy, cache, parameters


@app.cell
def _(mo, neuronas):
    neurona = mo.ui.slider(
        1, neuronas.value, value=1, step=1,
        label="Neurona oculta que queremos inspeccionar",
    )
    neurona
    return (neurona,)


@app.cell(hide_code=True)
def _(mo, neurona, parameters):
    indice = neurona.value - 1
    pesos_neurona = parameters["W1"][indice]
    bias_neurona = parameters["b1"][indice, 0]
    peso_salida = parameters["W2"][0, indice]
    mo.md(
        rf"""
        ## Neurona oculta {neurona.value}

        La combinación lineal aprendida por esta neurona es:

        \[
        z_{{{neurona.value}}}^{{[1]}}
        =({pesos_neurona[0]:.3f})x_1
        +({pesos_neurona[1]:.3f})x_2
        +({bias_neurona:.3f})
        \]

        Su peso en la neurona de salida es
        \(w_{{1,{neurona.value}}}^{{[2]}}={peso_salida:.3f}\).
        El signo y la magnitud de este valor indican cómo utiliza la salida final la
        característica construida por esta neurona.

        La combinación final utiliza las activaciones de **todas** las neuronas:

        \[
        z^{{[2]}}=\sum_j w_{{1,j}}^{{[2]}}\tanh(z_j^{{[1]}})+b^{{[2]}},
        \qquad \hat y=\sigma(z^{{[2]}}).
        \]

        La frontera negra corresponde a \(\hat y=0.5\), equivalente a
        \(z^{{[2]}}=0\). El selector cambia la neurona inspeccionada;
        la combinación final siempre utiliza toda la capa oculta.
        """
    )
    return (indice,)


@app.cell
def _(X, Y, forward_propagation, indice, np, parameters, plt):
    eje_x1 = np.linspace(X[0].min() - 0.6, X[0].max() + 0.6, 220)
    eje_x2 = np.linspace(X[1].min() - 0.6, X[1].max() + 0.6, 220)
    malla_x1, malla_x2 = np.meshgrid(eje_x1, eje_x2)
    X_malla = np.vstack((malla_x1.ravel(), malla_x2.ravel()))
    A2_malla, cache_malla = forward_propagation(X_malla, parameters)
    activacion_malla = cache_malla["A1"][indice].reshape(malla_x1.shape)
    Z_neurona = cache_malla["Z1"][indice].reshape(malla_x1.shape)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))
    mapa_activacion = axes[0].contourf(
        malla_x1, malla_x2, activacion_malla,
        levels=np.linspace(-1, 1, 21), cmap="coolwarm",
    )
    axes[0].contour(
        malla_x1, malla_x2, Z_neurona,
        levels=[0], colors="black", linewidths=2,
    )
    axes[0].scatter(X[0], X[1], c=Y.ravel(), cmap="bwr", s=15, edgecolor="white")
    axes[0].set(title="Activación de la neurona", xlabel="$x_1$", ylabel="$x_2$")
    fig.colorbar(mapa_activacion, ax=axes[0], label="$a_j^{[1]}$")

    for indice_linea in range(parameters["W1"].shape[0]):
        Z_linea = cache_malla["Z1"][indice_linea].reshape(malla_x1.shape)
        axes[1].contour(
            malla_x1, malla_x2, Z_linea, levels=[0],
            linewidths=3 if indice_linea == indice else 1.3,
        )
    axes[1].scatter(X[0], X[1], c=Y.ravel(), cmap="bwr", s=20, edgecolor="white")
    axes[1].set(title="Rectas de todas las neuronas", xlabel="$x_1$", ylabel="$x_2$")

    axes[2].contourf(
        malla_x1, malla_x2, A2_malla.reshape(malla_x1.shape),
        levels=np.linspace(0, 1, 21), cmap="RdBu_r", alpha=0.65,
    )
    axes[2].contour(
        malla_x1, malla_x2, A2_malla.reshape(malla_x1.shape),
        levels=[0.5], colors="black", linewidths=2,
    )
    axes[2].scatter(X[0], X[1], c=Y.ravel(), cmap="bwr", s=20, edgecolor="white")
    axes[2].set(title="Combinación final", xlabel="$x_1$", ylabel="$x_2$")
    fig.tight_layout()
    fig
    return


@app.cell
def _(cache, neurona, plt):
    fig_hist, ax_hist = plt.subplots(figsize=(7.5, 3.5))
    valores_neurona = cache["A1"][neurona.value - 1]
    ax_hist.hist(valores_neurona, bins=25, color="mediumpurple", edgecolor="white")
    ax_hist.set(
        title=f"Distribución de activaciones: neurona {neurona.value}",
        xlabel="$a_j^{[1]}$", ylabel="Número de observaciones",
    )
    ax_hist.grid(axis="y", alpha=0.2)
    fig_hist.tight_layout()
    fig_hist
    return


@app.cell(hide_code=True)
def _(accuracy, mo):
    mo.callout(
        mo.md(
            f"""
            **Exactitud de la red: {accuracy:.1%}**

            La neuronas de la capa oculta no deberían interpretarse como clasificadores independientes.
            Cada una contruye una característica intermedia (o virtual).
            La neurona de salida es la que aprende a combinar todas estas características creadas.
            """
        ),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Preguntas

    1. Recorre las neuronas con el control y compara sus rectas y activaciones.
    2. Identifica neuronas con representaciones parecidas. ¿Son todas necesarias?
    3. Aumenta el número de neuronas. ¿La frontera siempre mejora?
    4. Observa el peso de salida de cada neurona. ¿Qué significa un valor negativo?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Respuestas

    El selector de arriba muestra una neurona a la vez. Para poder comparar todas y para que las
    respuestas no cambien si se mueven los controles, en estas celdas entreno la red con los
    valores por defecto del notebook: cuatro neuronas, ruido 0.14, semilla 12 para los datos,
    4000 iteraciones y learning rate 0.8. Uso las mismas funciones `nn_model` y
    `forward_propagation`.
    """)
    return


@app.function
def tabla_md(filas):
    """
    Argumentos:
    filas -- lista de diccionarios (una fila por diccionario)

    Retorna:
    texto de una tabla en markdown, para que se vea igual en marimo, Jupyter y GitHub
    """
    columnas = list(filas[0].keys())
    lineas = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    for f in filas:
        lineas.append("| " + " | ".join(str(f[c]) for c in columnas) + " |")
    return "\n".join(lineas)


@app.cell
def _(forward_propagation, make_moons, nn_model, np):
    _m, _e = make_moons(n_samples=250, noise=0.14, random_state=12)
    X_r, Y_r = _m.T, _e.reshape(1, -1)
    par_r, _costos = nn_model(X_r, Y_r, n_h=4, num_iterations=4000, learning_rate=0.8)
    A2_r, cache_r = forward_propagation(X_r, par_r)
    exactitud_r = float(np.mean((A2_r > 0.5) == Y_r))
    return A2_r, X_r, Y_r, cache_r, exactitud_r, par_r


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1. Rectas y activaciones de cada neurona
    """)
    return


@app.cell
def _(X_r, Y_r, forward_propagation, np, par_r, plt):
    _g1, _g2 = np.meshgrid(np.linspace(X_r[0].min() - 0.6, X_r[0].max() + 0.6, 200),
                           np.linspace(X_r[1].min() - 0.6, X_r[1].max() + 0.6, 200))
    _, _cm = forward_propagation(np.vstack((_g1.ravel(), _g2.ravel())), par_r)
    fig_n, ax_n = plt.subplots(1, 4, figsize=(16, 3.8))
    for _j, _ax in enumerate(ax_n):
        _mapa = _ax.contourf(_g1, _g2, _cm["A1"][_j].reshape(_g1.shape),
                             levels=np.linspace(-1, 1, 21), cmap="coolwarm")
        _ax.contour(_g1, _g2, _cm["Z1"][_j].reshape(_g1.shape), levels=[0], colors="black", linewidths=2)
        _ax.scatter(X_r[0], X_r[1], c=Y_r.ravel(), cmap="bwr", s=10, edgecolor="white", linewidths=0.3)
        _ax.set_title(f"Neurona {_j + 1}: peso de salida {par_r['W2'][0, _j]:+.2f}", fontsize=9)
        _ax.set(xlabel="$x_1$", ylabel="$x_2$")
    fig_n.colorbar(_mapa, ax=list(ax_n), shrink=0.85, label="$a_j^{[1]}$")
    fig_n
    return


@app.cell
def _(mo, par_r):
    mo.md(tabla_md([
        {"Neurona": _j + 1,
         "w1": f"{par_r['W1'][_j, 0]:.3f}",
         "w2": f"{par_r['W1'][_j, 1]:.3f}",
         "b": f"{par_r['b1'][_j, 0]:.3f}",
         "Tamaño del peso, ‖w‖": f"{float((par_r['W1'][_j] ** 2).sum() ** 0.5):.2f}",
         "Peso de salida": f"{par_r['W2'][0, _j]:+.3f}"}
        for _j in range(par_r["W1"].shape[0])
    ]))
    return


@app.cell(hide_code=True)
def _(exactitud_r, mo):
    mo.md(rf"""
    Con estos valores la red clasifica bien el {exactitud_r:.0%} de los puntos. Al comparar las
    cuatro neuronas se ve que cada una parte el plano con una recta distinta, y que de un lado de
    su recta vale cerca de 1 y del otro cerca de −1.

    - Las neuronas 1, 2 y 4 tienen pesos grandes (‖w‖ entre 4.8 y 6.1). Por eso el cambio de −1 a 1
      es brusco y en la gráfica se ven casi solo dos colores, uno de cada lado de la recta.
    - La neurona 3 es distinta. Sus pesos son chicos (‖w‖ ≈ 0.56), así que su activación cambia muy
      despacio: en la gráfica los colores pasan poco a poco de azul a rojo y los puntos quedan en
      tonos claros, sin llegar a −1 ni a 1. Trabaja casi como una función lineal.
    - Las rectas de las neuronas 2, 3 y 4 son casi paralelas, todas inclinadas hacia la derecha,
      pero están en distintas posiciones: la 4 pasa por la izquierda, la 3 por el centro y la 2
      por la derecha. La 1 va en otra dirección. Ninguna separa las lunas por sí sola; la frontera
      curva sale de combinarlas.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2. Neuronas con representaciones parecidas

    Para encontrar neuronas parecidas comparé sus activaciones sobre los 250 puntos con la
    correlación. Para ver si son necesarias, apagué una neurona a la vez (puse su peso de salida
    en cero, sin volver a entrenar) y medí cuánto baja la exactitud.
    """)
    return


@app.cell
def _(X_r, Y_r, cache_r, forward_propagation, mo, np, par_r):
    _corr = np.corrcoef(cache_r["A1"])
    _n = _corr.shape[0]
    _filas_corr = [{"Neurona": _i + 1, **{f"N{_k + 1}": f"{_corr[_i, _k]:+.2f}" for _k in range(_n)}}
                   for _i in range(_n)]
    _filas_abl = []
    for _j in range(_n):
        _q = {_k: _v.copy() for _k, _v in par_r.items()}
        _q["W2"][0, _j] = 0.0
        _a, _ = forward_propagation(X_r, _q)
        _filas_abl.append({"Neurona apagada": _j + 1,
                           "Exactitud sin ella": f"{float(np.mean((_a > 0.5) == Y_r)):.1%}"})
    mo.vstack([
        mo.md("**Correlación entre las activaciones de las neuronas**"),
        mo.md(tabla_md(_filas_corr)),
        mo.md("**Exactitud al apagar cada neurona** (con todas: 100 %)"),
        mo.md(tabla_md(_filas_abl)),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Las neuronas 2 y 3 son las más parecidas (correlación de +0.83), y la 3 y la 4 también lo son
    pero al revés (−0.84): cuando una sube, la otra baja, que en la práctica es la misma
    información con el signo cambiado.

    No todas son necesarias. Al apagar la neurona 3 la exactitud se queda en 100 %, así que lo que
    aporta ya lo cubren las otras. Cuadra con lo que vi en la pregunta 1: es la de pesos
    más chicos y la que menos se "decide". En cambio, sin la neurona 1 la exactitud cae a 77.2 %, y
    sin la 4 o la 2 baja a 94.0 % y 91.6 %. Estas tres son las que cargan con la forma de la
    frontera. En la siguiente pregunta lo confirmo, porque con tres neuronas la red ya llega al
    mismo resultado.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3. ¿Más neuronas siempre mejora la frontera?

    Como con 250 puntos de entrenamiento todo puede verse bien, también generé 1000 puntos nuevos
    de las mismas lunas (mismo ruido, otra semilla) para medir si la red funciona con datos que
    no vio.
    """)
    return


@app.cell
def _(X_r, Y_r, forward_propagation, make_moons, mo, nn_model, np):
    _mt, _et = make_moons(n_samples=1000, noise=0.14, random_state=99)
    _Xt, _Yt = _mt.T, _et.reshape(1, -1)
    filas_3b = []
    for _n in range(2, 9):
        _p, _c = nn_model(X_r, Y_r, n_h=_n, num_iterations=4000, learning_rate=0.8)
        _tr = float(np.mean((forward_propagation(X_r, _p)[0] > 0.5) == Y_r))
        _te = float(np.mean((forward_propagation(_Xt, _p)[0] > 0.5) == _Yt))
        filas_3b.append({"Neuronas": _n, "Exactitud entrenamiento": f"{_tr:.1%}",
                         "Exactitud datos nuevos": f"{_te:.1%}", "Costo final": f"{_c[-1][1]:.4f}"})
    mo.md(tabla_md(filas_3b))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No. De dos a tres neuronas sí hay un salto grande, de 85.2 % a 100 % en entrenamiento y de 86.8 %
    a 98.8 % con datos nuevos, porque con dos neuronas la frontera todavía no puede seguir bien la
    curva. Pero de tres en adelante ya no mejora nada: el entrenamiento se queda en 100 % y los
    datos nuevos entre 98.8 % y 98.9 %. A partir de ahí las neuronas extra no aportan, y como vimos en
    la pregunta 2, terminan repitiendo lo que ya hacen las demás.

    Además, más neuronas no son gratis. Cada una agrega cuatro parámetros (sus dos pesos, su
    sesgo y su peso de salida) que hay que entrenar y,
    con datos más ruidosos o con pocas observaciones, una red más grande puede empezar a ajustarse
    al ruido y doblar la frontera alrededor de puntos sueltos. En este problema eso no llegó a
    pasar, pero la conclusión es la misma: la frontera mejora hasta que la red tiene la capacidad
    que el problema necesita, y después ya no.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4. ¿Qué significa un peso de salida negativo?
    """)
    return


@app.cell
def _(A2_r, X_r, forward_propagation, mo, np, par_r):
    _j = int(np.argmin(par_r["W2"][0]))
    _q = {_k: _v.copy() for _k, _v in par_r.items()}
    # cambio el signo de todos los pesos de esa neurona, de entrada y de salida
    _q["W1"][_j] *= -1
    _q["b1"][_j] *= -1
    _q["W2"][0, _j] *= -1
    _a, _ = forward_propagation(X_r, _q)
    neurona_neg = _j + 1
    mo.md(rf"""
    La neurona con peso de salida negativo es la **{neurona_neg}**
    ($w^{{[2]}}_{{1,{neurona_neg}}} = {par_r["W2"][0, _j]:.3f}$). Le cambié el signo a todos sus pesos,
    los de entrada ($w_1$, $w_2$, $b$) y el de salida, y volví a calcular las predicciones. La diferencia
    máxima contra la red original es de {float(np.abs(_a - A2_r).max()):.1e}, es decir, la red hace
    exactamente lo mismo.
    """)
    return (neurona_neg,)


@app.cell(hide_code=True)
def _(mo, neurona_neg):
    mo.md(rf"""
    Un peso de salida negativo quiere decir que cuando esa neurona se activa (su $a_j$ se acerca a 1)
    empuja la predicción hacia la clase 0, la azul. Con peso positivo pasa lo contrario: activarse
    empuja hacia la clase 1, la roja. El tamaño del peso dice qué tan fuerte es ese empujón.

    Lo que no significa es que la neurona esté "mal" o que estorbe. El experimento de arriba lo
    muestra: como $\tanh(-z) = -\tanh(z)$, voltear el signo de los pesos de entrada de la neurona
    {neurona_neg} y también el de su peso de salida da exactamente la misma red, solo que ahora con
    un peso positivo. Lo que importa es la combinación de los dos signos, no el signo del peso
    de salida por separado. Por eso la neurona {neurona_neg} sigue siendo importante (sin ella la
    exactitud baja a 94.0 %) aunque su peso de salida sea negativo.

    ### Conclusión

    Cada neurona oculta divide el plano con una recta y la activación convierte esa división en una
    nueva variable que vale cerca de 1 de un lado y cerca de −1 del otro. La neurona de salida no
    "elige" una de ellas, las suma con sus pesos, y de esa suma sale la frontera curva. No todas las
    neuronas aportan lo mismo: en esta red una sobra, y agregar más de tres ya no mejora el
    resultado.
    """)
    return


if __name__ == "__main__":
    app.run()
