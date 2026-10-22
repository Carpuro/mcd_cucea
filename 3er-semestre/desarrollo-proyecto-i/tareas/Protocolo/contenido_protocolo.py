# -*- coding: utf-8 -*-
"""
Protocol content, occupational mobility focus (2026-10-21).
The protocol states the problem and the plan only: no results of our own are reported.
Every factual statement is supported by an external, citable source (APA 7) and every figure is
explained in plain terms. Sources verified against abstracts (OpenAlex), the PDFs in
../Actividad_Referencias/referencias and ./fuentes, and the INEGI ENOE metadata catalog.
Executed from build_protocolo.py with the formatting helpers in scope.
"""

titulo("Protocolo de investigación")

# ---------------------------------------------------------------- I
seccion("Datos de identificación y título")
par(f"Título: {TITULO}.")
par("Alumno: Carlos Pulido Rosas. Programa: Maestría en Ciencia de los Datos, Centro Universitario "
    "de Ciencias Económico Administrativas, Universidad de Guadalajara. Generación 2025-2027, "
    "modalidad ejecutiva. Unidad de aprendizaje: Desarrollo de Proyecto I, impartida por la "
    "Dra. Ana Rosa Jiménez Meza. Director de tesis: por designar. Línea de generación y "
    "aplicación del conocimiento: Smart Data (LGAC 2), por el uso de técnicas de aprendizaje "
    "automatizado y analítica de datos.")
par("El título responde a las tres preguntas que pide la guía. Qué se pretende hacer: evaluar el "
    "riesgo de movilidad laboral que generan los modelos de inteligencia artificial, es decir, la "
    "probabilidad de que un trabajador cambie de ocupación, quede desocupado o salga del mercado de "
    "trabajo como consecuencia de esa tecnología. Con qué herramientas: un modelo de ciencia de "
    "datos que combina medidas de exposición de las tareas a la inteligencia artificial con el "
    "seguimiento de las trayectorias laborales de los trabajadores. En dónde: en las ocupaciones de "
    "ingeniería informática en México.")

# ---------------------------------------------------------------- II
seccion("Planteamiento del problema")
sub("Contexto")
par("Los modelos de lenguaje de gran escala, que se definen formalmente en el marco teórico, son "
    "sistemas de inteligencia artificial capaces de comprender y generar texto y código. Su "
    "difusión a partir de 2022 reabrió la pregunta de qué ocurre con el empleo cuando una "
    "tecnología puede realizar tareas cognitivas que antes solo hacían las personas. Eloundou et al. "
    "(2023) estimaron que alrededor del 80 % de los trabajadores de Estados Unidos podría ver "
    "afectado al menos el 10 % de sus tareas por estos modelos, y que cerca del 19 % podría ver "
    "afectada al menos la mitad. En otras palabras, la exposición no se limita a unas cuantas "
    "ocupaciones, pero solo en una de cada cinco alcanza a la mayor parte del trabajo.")
par("Las ocupaciones relacionadas con la informática están entre las más involucradas. En el "
    "análisis de millones de conversaciones con el asistente Claude, las ocupaciones de computación "
    "y matemáticas concentraron el 37.2 % de todas las consultas, la proporción más alta de cualquier "
    "grupo ocupacional, y el 57 % de los usos mostró un patrón de aumento de las capacidades humanas "
    "más que de automatización (Handa et al., 2025). Es decir, más de un tercio del uso observado "
    "de esta herramienta proviene de tareas propias de la informática, y en la mayoría de los casos "
    "el modelo trabaja junto con la persona en lugar de reemplazarla. En la misma línea, Gao y "
    "Huang (2026) calcularon un índice relativo de automatización ocupacional para Estados Unidos y "
    "encontraron que los puestos cognitivos no rutinarios que dependen de la manipulación de "
    "símbolos son los más vulnerables; los científicos de datos encabezan el índice, con un valor "
    "cercano a 0.70.")
par("Sin embargo, una exposición alta no se ha traducido en pérdidas generales de empleo. Acemoglu "
    "et al. (2022) encontraron, con las vacantes publicadas en línea en Estados Unidos desde 2010, "
    "que los establecimientos que adoptan inteligencia artificial reducen sus contrataciones en "
    "puestos no relacionados con ella y cambian los requisitos de habilidades de las vacantes que "
    "mantienen, aunque el efecto todavía es demasiado pequeño para observarse en el empleo agregado. "
    "Broady et al. (2026) mostraron que, entre 2019 y 2024, las ocupaciones con mayor aplicabilidad "
    "de la inteligencia artificial aumentaron su empleo y sus salarios, por lo que proponen leer la "
    "exposición como un indicador de reestructuración de las ocupaciones y no como un pronóstico de "
    "pérdida de empleo.")
par("Donde sí aparece un cambio es en la entrada al mercado de trabajo. Con registros de nómina de "
    "millones de trabajadores de Estados Unidos, Brynjolfsson et al. (2026) encontraron que el empleo "
    "de los jóvenes de 22 a 25 años en ocupaciones expuestas a la inteligencia artificial se "
    "encuentra 19 % por debajo de donde estaría si hubiera crecido al mismo ritmo que el de sus pares "
    "en ocupaciones menos expuestas, sin una brecha comparable entre los trabajadores con más "
    "experiencia. Los autores precisan que la diferencia se explica sobre todo por menos "
    "contrataciones de jóvenes y no por más despidos, y analizan el desarrollo de software como uno "
    "de sus casos de estudio. Este resultado sugiere que el efecto de la tecnología se manifiesta en "
    "quién entra, quién sale y hacia dónde se mueven los trabajadores, más que en la desaparición "
    "de las ocupaciones.")
sub("Definición del problema")
par("La mayoría de los estudios sobre inteligencia artificial y empleo miden la exposición de cada "
    "ocupación en un momento dado, pero no siguen a los trabajadores. Frank et al. (2025) mostraron, "
    "con datos mensuales de desempleo por ocupación de cada estado de Estados Unidos entre 2010 y "
    "2020, que ningún índice de exposición por sí solo predice bien el riesgo de desempleo; solo al "
    "combinarlos se explica un 18 % adicional de la variación del riesgo de desempleo entre "
    "ocupaciones, estados y periodos, respecto a un modelo que ya considera la escolaridad, las "
    "habilidades, la estacionalidad y la región. Dicho de otro modo, saber que una ocupación está "
    "expuesta no basta para saber qué les pasará a quienes trabajan en ella.")
par("Del Rio-Chanona et al. (2021) plantean el problema desde otro ángulo: cuando la automatización "
    "afecta a una ocupación, el resultado para sus trabajadores depende de cuántas ocupaciones "
    "cercanas existen hacia donde puedan moverse. Con un modelo de red de movilidad ocupacional, "
    "encontraron que las ocupaciones ubicadas en zonas de la red con pocas opciones de transición "
    "tienen más riesgo de desempleo de largo plazo. Por su parte, Georgieff y Hyee (2022) "
    "encontraron, para 23 países de la OCDE, que en las ocupaciones con uso intensivo de "
    "computadora una mayor exposición a la inteligencia artificial se asocia con un mayor "
    "crecimiento del empleo, y Chen et al. (2022) mostraron, con 701 ocupaciones de Estados Unidos, "
    "que las habilidades digitales moderan el efecto negativo del riesgo de desplazamiento sobre "
    "los salarios y el empleo.")
par("Estos trabajos coinciden en que el riesgo relevante no es solo el de perder el empleo, sino el "
    "de verse obligado a cambiar de ocupación, de empleador o de condición laboral, y en que ese "
    "riesgo depende de las habilidades del trabajador y de las rutas de transición disponibles. "
    "Sin embargo, se basan en datos de Estados Unidos o de países de la OCDE. En México no se ha "
    "medido cómo se mueven los trabajadores de las ocupaciones de ingeniería informática desde la "
    "llegada de los modelos de lenguaje, ni si esa movilidad es distinta para quienes empiezan su "
    "carrera.")
par("En consecuencia, el problema de investigación es la falta de un modelo que permita evaluar, con "
    "datos de México, el riesgo de movilidad laboral que enfrentan los trabajadores de las "
    "ocupaciones de ingeniería informática ante los modelos de inteligencia artificial, es decir, "
    "con qué probabilidad cambian de ocupación, quedan desocupados o salen del mercado de trabajo, "
    "hacia qué ocupaciones se mueven y qué características del trabajador aumentan o reducen ese "
    "riesgo.")
sub("Preguntas de investigación")
par("Pregunta general: ¿cómo se relaciona la exposición a los modelos de inteligencia artificial con "
    "la movilidad laboral de los trabajadores de las ocupaciones de ingeniería informática en México?")
item("1. ¿Qué tareas de las ocupaciones de ingeniería informática están más expuestas a los modelos "
     "de inteligencia artificial?")
item("2. ¿Con qué frecuencia cambian de ocupación, quedan desocupados o salen del mercado de trabajo "
     "estos trabajadores, hacia qué ocupaciones se mueven y cómo cambió esa movilidad después de 2022?")
item("3. ¿Qué características del trabajador, como la edad, la experiencia, la escolaridad y el tipo "
     "de ocupación, se asocian con un mayor riesgo de movilidad?")

# ---------------------------------------------------------------- III
seccion("Justificación")
par("Relevancia social. Si el efecto de la inteligencia artificial se concentra en la entrada al "
    "mercado de trabajo, como sugieren Brynjolfsson et al. (2026), quienes más lo resentirían serían "
    "los egresados recientes de carreras de informática, que buscan su primer empleo en las "
    "ocupaciones más expuestas. Conocer ese riesgo permite anticiparlo en la formación universitaria "
    "y en las políticas de empleo.")
par("Relevancia práctica. Los resultados permitirán identificar qué ocupaciones de destino reciben a "
    "los trabajadores que salen de la ingeniería informática y qué habilidades facilitan esas "
    "transiciones. Paolillo et al. (2022) mostraron que es posible identificar, para cada ocupación, "
    "alternativas que reducen el riesgo de automatización con un esfuerzo de reentrenamiento "
    "moderado; un análisis similar con datos mexicanos serviría a universidades, empleadores y "
    "trabajadores para orientar la capacitación.")
par("Aportación a la ciencia. El proyecto propone medir la movilidad laboral asociada a la "
    "inteligencia artificial siguiendo a los mismos trabajadores en el tiempo, en lugar de comparar "
    "fotografías de la exposición en distintos años. Frank et al. (2025) muestran que la exposición "
    "por sí sola es un mal predictor de lo que ocurre con el empleo, por lo que observar las "
    "transiciones reales de los trabajadores aporta una medida más directa del riesgo.")
par("Viabilidad. Las fuentes de información son públicas y gratuitas. La Encuesta Nacional de "
    "Ocupación y Empleo (ENOE) del INEGI tiene un diseño de panel rotatorio: la muestra se divide en "
    "cinco paneles y cada vivienda permanece en la encuesta durante cinco trimestres, de modo que en "
    "cada trimestre se mantiene el 80 % de la muestra (INEGI, 2025). Esto significa que una misma "
    "persona se entrevista hasta cinco veces seguidas, lo que permite observar si cambió de "
    "ocupación o de condición laboral entre un trimestre y otro. La ocupación se registra con el "
    "Sistema Nacional de Clasificación de Ocupaciones (INEGI, 2019), y las tareas de cada ocupación "
    "pueden obtenerse de la base O*NET (National Center for O*NET Development, 2024).")

# ---------------------------------------------------------------- IV
seccion("Objetivos")
sub("Objetivo general")
par("Evaluar el riesgo de movilidad laboral de los trabajadores de las ocupaciones de ingeniería "
    "informática en México frente a los modelos de inteligencia artificial, mediante un modelo de "
    "ciencia de datos que relacione la exposición de sus tareas con las transiciones laborales "
    "observadas.")
sub("Objetivos específicos")
item("1. Delimitar las ocupaciones de ingeniería informática en el Sistema Nacional de Clasificación "
     "de Ocupaciones y caracterizar a sus trabajadores con la ENOE.")
item("2. Medir la exposición de las tareas de esas ocupaciones a los modelos de inteligencia "
     "artificial a partir de O*NET y de índices de exposición publicados.")
item("3. Construir las trayectorias trimestrales de los trabajadores con el panel de la ENOE y "
     "estimar matrices de transición entre ocupaciones y condiciones laborales, antes y después "
     "de 2022.")
item("4. Estimar modelos que expliquen el riesgo de movilidad en función de la exposición y de las "
     "características del trabajador, y evaluar su desempeño y robustez.")
item("5. Identificar las ocupaciones de destino de quienes salen de la ingeniería informática y "
     "presentar los resultados en un tablero de visualización.")

# ---------------------------------------------------------------- V
seccion("Hipótesis")
par("H1. Después de la difusión de los modelos de lenguaje en 2022, los trabajadores jóvenes de las "
    "ocupaciones de ingeniería informática presentan un riesgo de movilidad mayor que los "
    "trabajadores con más experiencia. La hipótesis se sustenta en la caída relativa del empleo de "
    "los jóvenes en ocupaciones expuestas, explicada por menos contrataciones (Brynjolfsson et al., "
    "2026), y en la reducción de contrataciones en puestos no relacionados con la inteligencia "
    "artificial dentro de los establecimientos que la adoptan (Acemoglu et al., 2022).")
par("H2. Quienes salen de las ocupaciones de ingeniería informática se mueven principalmente hacia "
    "ocupaciones cercanas en habilidades, y no hacia la desocupación, porque sus habilidades "
    "digitales son transferibles. La hipótesis se basa en el papel de la red de movilidad "
    "ocupacional en las opciones de transición (del Rio-Chanona et al., 2021) y en la protección que "
    "las habilidades digitales ofrecen frente al riesgo de desplazamiento (Chen et al., 2022; "
    "Georgieff y Hyee, 2022).")

# ---------------------------------------------------------------- VI
seccion("Antecedentes")
par("Los antecedentes se presentan en orden cronológico. Autor et al. (2003) establecieron el enfoque "
    "de tareas, según el cual la tecnología sustituye tareas y no ocupaciones completas. Kambourov y "
    "Manovskii (2008) documentaron el aumento de la movilidad ocupacional en Estados Unidos entre 1968 "
    "y 1997 y destacaron su importancia porque buena parte del capital humano de los trabajadores es "
    "específico de su ocupación, de modo que cambiar de ocupación implica perder parte de ese "
    "capital. Frey y Osborne (2017) estimaron la probabilidad de automatización de 702 ocupaciones, "
    "y Acemoglu y Restrepo (2019) formalizaron la idea de que la automatización desplaza trabajo de "
    "unas tareas mientras la creación de tareas nuevas lo reinstala en otras.")
par("Sobre la movilidad, Meng et al. (2019) propusieron una red neuronal jerárquica con mecanismos de "
    "atención que aprende de las trayectorias laborales para predecir el siguiente empleador de una "
    "persona y cuánto tiempo permanecerá en el nuevo puesto. Del Rio-Chanona et al. (2021) "
    "construyeron una red empírica de movilidad ocupacional y simularon cómo se mueven los "
    "trabajadores ante distintos escenarios de automatización. Paolillo et al. (2022) calcularon el "
    "riesgo de automatización de casi 1,000 ocupaciones y propusieron un método para encontrar, para "
    "cada una, alternativas que reduzcan ese riesgo con el menor esfuerzo de reentrenamiento.")
par("Con la llegada de los modelos de lenguaje, Eloundou et al. (2023) midieron la exposición de las "
    "tareas a estos modelos, y Acemoglu et al. (2022) documentaron cambios en las contrataciones y en "
    "los requisitos de las vacantes de los establecimientos que adoptan inteligencia artificial. "
    "Georgieff y Hyee (2022) y Chen et al. (2022) mostraron que el uso de computadora y las "
    "habilidades digitales cambian el signo o moderan el efecto de la exposición. Dahlin (2024) "
    "encontró, con una encuesta en Estados Unidos, que los trabajadores de cuello blanco y con "
    "experiencia técnica son quienes más reportan haber sido desplazados por la inteligencia "
    "artificial. Más recientemente, Frank et al. (2025) relacionaron la exposición con el riesgo de "
    "desempleo, Handa et al. (2025) midieron el uso real de un modelo de lenguaje por tarea, Broady "
    "et al. (2026) compararon la exposición con la evolución del empleo entre 2019 y 2024, Gao y Huang "
    "(2026) separaron la factibilidad técnica del riesgo comercial de automatizar cada actividad, y "
    "Brynjolfsson et al. (2026) documentaron la caída relativa del empleo de los trabajadores jóvenes "
    "en ocupaciones expuestas.")

# ---------------------------------------------------------------- VII
seccion("Marco teórico")
sub("Conceptos y definiciones")
par("Movilidad laboral. Se refiere a los cambios en la situación laboral de un trabajador entre dos "
    "momentos. En este protocolo incluye tres tipos de transición: el cambio de ocupación, que "
    "Kambourov y Manovskii (2008) miden como el paso de un trabajador de una ocupación a otra entre "
    "dos periodos; el paso del empleo a la desocupación; y la salida de la fuerza de trabajo. El "
    "riesgo de movilidad laboral es la probabilidad de que ocurra alguna de esas transiciones en un "
    "periodo determinado.")
par("Desplazamiento y reinstalación. La automatización permite que el capital realice tareas que "
    "antes hacían las personas, lo que produce un efecto de desplazamiento del trabajo; la creación "
    "de tareas nuevas genera, en sentido contrario, un efecto de reinstalación (Acemoglu y Restrepo, "
    "2019). La movilidad laboral es la forma en que estos dos efectos se observan en los "
    "trabajadores: unos dejan las tareas que se automatizan y otros se mueven hacia las tareas nuevas.")
par("Modelos de lenguaje de gran escala. Se trata de modelos de lenguaje basados en la arquitectura "
    "Transformer que contienen cientos de miles de millones de parámetros o más, se entrenan con "
    "grandes volúmenes de texto y muestran una fuerte capacidad para comprender el lenguaje natural y "
    "resolver tareas complejas mediante la generación de texto; ejemplos de ellos son GPT-3, PaLM y "
    "LLaMA (Zhao et al., 2023). La arquitectura Transformer es una red neuronal que se apoya "
    "únicamente en mecanismos de atención (Vaswani et al., 2017).")
par("Ocupaciones de ingeniería informática. En el Sistema Nacional de Clasificación de Ocupaciones "
    "2019 corresponden al subgrupo 227, Investigadores y profesionistas en sistemas computacionales, "
    "que comprende a los desarrolladores y analistas de software y multimedia (2271) y a los "
    "administradores de bases de datos y redes de computadora (2272) (INEGI, 2019). Como posibles "
    "ocupaciones de destino cercanas se considerarán, entre otras, los técnicos en la instalación y "
    "reparación de redes, equipos y sistemas computacionales (2651) y los directores y coordinadores "
    "de informática (1321 y 1621).")
par("Exposición a la inteligencia artificial. Es el grado en que las tareas de una ocupación pueden "
    "ser realizadas o asistidas por un sistema de inteligencia artificial. Eloundou et al. (2023) "
    "consideran que una tarea está expuesta cuando usar un modelo de lenguaje puede reducir al menos "
    "a la mitad el tiempo necesario para completarla con la misma calidad. La exposición no implica sustitución: puede traducirse en automatización o en aumento "
    "de las capacidades del trabajador (Handa et al., 2025).")
sub("Teoría de tareas y movilidad")
par("El fundamento teórico es el enfoque de tareas (Autor et al., 2003), según el cual la tecnología "
    "no sustituye ocupaciones completas, sino tareas específicas, y la teoría del desplazamiento y la "
    "reinstalación de Acemoglu y Restrepo (2019). Si la inteligencia artificial absorbe algunas tareas "
    "de una ocupación, la demanda de trabajo se reorganiza: los trabajadores cuyas tareas se "
    "automatizan pueden cambiar de funciones dentro de la ocupación, moverse a otra ocupación o "
    "quedar sin empleo. Qué tan costoso es ese ajuste depende de cuánto capital humano específico se "
    "pierde al cambiar de ocupación (Kambourov y Manovskii, 2008) y de cuántas ocupaciones cercanas "
    "existen para recibir al trabajador (del Rio-Chanona et al., 2021).")
sub("Elección del método")
par("El enfoque es cuantitativo porque el riesgo se expresa como una probabilidad comparable entre "
    "grupos de trabajadores y periodos. El panel rotatorio de la ENOE permite construir trayectorias "
    "individuales de hasta cinco trimestres, lo que hace posible estimar matrices de transición, en "
    "las que cada celda indica la proporción de trabajadores que pasa de una situación laboral a "
    "otra entre dos trimestres. Para explicar esas transiciones se usarán modelos estadísticos con "
    "inferencia formal y modelos de aprendizaje automático, en línea con los trabajos que modelan la "
    "movilidad con redes ocupacionales (del Rio-Chanona et al., 2021) y con redes neuronales "
    "(Meng et al., 2019).")

# ---------------------------------------------------------------- VIII
seccion("Metodología")
par("Tipo de estudio. Investigación cuantitativa, no experimental y longitudinal, basada en el "
    "seguimiento de trabajadores en el panel de la ENOE.")
par("Población y unidades de análisis. Personas ocupadas en las ocupaciones de ingeniería "
    "informática (subgrupo 227 del Sistema Nacional de Clasificación de Ocupaciones 2019) en México. "
    "Jalisco se analizará como caso estatal en la medida en que el tamaño de la muestra lo permita. "
    "Las unidades de análisis son el trabajador, observado trimestre a trimestre, y la ocupación.")
par("Fuentes de datos. La ENOE (INEGI, 2025) para las trayectorias laborales y las características "
    "de los trabajadores; el Sistema Nacional de Clasificación de Ocupaciones (INEGI, 2019) para "
    "delimitar las ocupaciones; la base O*NET (National Center for O*NET Development, 2024) para las "
    "tareas de cada ocupación; e índices publicados de exposición a la inteligencia artificial "
    "(Eloundou et al., 2023; Felten et al., 2023) y de uso observado (Handa et al., 2025).")
par("Procedimiento. El trabajo se organiza en cinco pasos alineados con los objetivos específicos:")
item("1. Delimitación de las ocupaciones de ingeniería informática y de sus posibles ocupaciones de "
     "destino, y depuración de los trimestres de la ENOE disponibles antes y después de 2022.")
item("2. Asignación de las tareas de O*NET a las ocupaciones mexicanas mediante tablas de "
     "correspondencia y cálculo de su exposición a los modelos de inteligencia artificial.")
item("3. Enlace de los registros de cada persona entre trimestres y construcción de matrices de "
     "transición entre ocupaciones, desocupación e inactividad, comparando el periodo anterior y el "
     "posterior a 2022.")
item("4. Estimación de modelos de la probabilidad de transición, como regresiones logísticas "
     "multinomiales y modelos de diferencias en diferencias que comparen a jóvenes y a trabajadores "
     "con experiencia antes y después de 2022, complementados con modelos de aprendizaje automático "
     "con validación cruzada, para contrastar H1.")
item("5. Construcción de una red de movilidad con las ocupaciones de destino observadas, para "
     "contrastar H2, y elaboración del tablero de visualización.")
par("Herramientas de análisis. Python (pandas, NumPy, statsmodels, scikit-learn y Matplotlib), "
    "SQL Server para la integración de datos y GitHub para el control de versiones y la "
    "reproducibilidad del análisis.")

# ---------------------------------------------------------------- IX
seccion("Recursos")
par("Recursos humanos. El tesista, responsable del desarrollo del proyecto; el director de tesis, por "
    "designar; y la profesora de la unidad de aprendizaje Desarrollo de Proyecto I, que da "
    "seguimiento al protocolo.")
par("Recursos materiales. Equipo de cómputo personal, un servidor local con SQL Server para la base de "
    "datos del proyecto, software libre para el análisis (Python y sus bibliotecas) y un repositorio "
    "en GitHub. Las fuentes de información son públicas y gratuitas.")
par("Recursos económicos. El proyecto no requiere la compra de datos ni de licencias de software. Los "
    "costos se limitan al uso del equipo propio y a la conexión a internet, cubiertos por el tesista.")

# ---------------------------------------------------------------- X
seccion("Cronograma")
par("El cronograma parte del plan registrado en el avance de protocolo de la tesis e incorpora el "
    "reenfoque hacia la movilidad laboral en las ocupaciones de ingeniería informática, con el "
    "estado de cada etapa a octubre de 2026.")
caption_table(1, "Cronograma de actividades del proyecto de tesis")
table([
    ["Etapa / actividad", "2025B", "2026A", "2026B", "2027A", "Estado"],
    ["Revisión de literatura y antecedentes", "Ago-Sep", "", "Oct", "", "En curso"],
    ["Reenfoque a movilidad laboral en ingeniería informática", "", "", "Oct-Nov", "", "En curso"],
    ["Obtención y depuración del panel de la ENOE", "", "", "Nov-Dic", "", "Pendiente"],
    ["Mapeo de ocupaciones y tareas (SINCO, O*NET)", "", "", "Nov-Dic", "", "Pendiente"],
    ["Cálculo de la exposición de las tareas", "", "", "Dic", "Ene", "Pendiente"],
    ["Construcción de trayectorias y matrices de transición", "", "", "", "Ene-Feb", "Pendiente"],
    ["Estimación y validación de modelos", "", "", "", "Feb-Abr", "Pendiente"],
    ["Red de movilidad y tablero de visualización", "", "", "", "Abr-May", "Pendiente"],
    ["Escritura y revisión del documento final", "", "", "", "May-Jun", "Pendiente"],
    ["Presentación y defensa del trabajo de tesis", "", "", "", "Jul 2027", "Pendiente"],
], [3300, 900, 900, 900, 1000, 1100])
note("Nota. Elaboración propia con base en el plan del avance de protocolo de la tesis.")

# ---------------------------------------------------------------- XI
seccion("Referencias bibliográficas")
for a in [
 "Acemoglu, D., Autor, D., Hazell, J., & Restrepo, P. (2022). Artificial intelligence and jobs: Evidence from online vacancies. Journal of Labor Economics, 40(S1), S293-S340. https://doi.org/10.1086/718327",
 "Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. Journal of Economic Perspectives, 33(2), 3-30. https://doi.org/10.1257/jep.33.2.3",
 "Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. The Quarterly Journal of Economics, 118(4), 1279-1333. https://doi.org/10.1162/003355303322552801",
 "Broady, K. E., Dunson, C., & Barr, A. (2026). Rethinking automation risk: AI applicability and occupational outcomes, 2019-24 (Working Paper 2026-12). Federal Reserve Bank of Chicago. https://doi.org/10.21033/wp-2026-12",
 "Brynjolfsson, E., Chandar, B., & Chen, R. (2026). Canaries in the coal mine? Six facts about the recent employment effects of artificial intelligence [Documento de trabajo, versión de agosto de 2026]. Stanford Digital Economy Lab. https://digitaleconomy.stanford.edu/publications/canaries-in-the-coal-mine/",
 "Chen, N., Li, Z., & Tang, B. (2022). Can digital skill protect against job displacement risk caused by artificial intelligence? Empirical evidence from 701 detailed occupations. PLOS ONE, 17(11), e0277280. https://doi.org/10.1371/journal.pone.0277280",
 "Dahlin, E. (2024). Who says artificial intelligence is stealing our jobs? Socius, 10. https://doi.org/10.1177/23780231241259672",
 "del Rio-Chanona, R. M., Mealy, P., Beguerisse-Díaz, M., Lafond, F., & Farmer, J. D. (2021). Occupational mobility and automation: A data-driven network model. Journal of the Royal Society Interface, 18(174), 20200898. https://doi.org/10.1098/rsif.2020.0898",
 "Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. arXiv. https://arxiv.org/abs/2303.10130",
 "Felten, E., Raj, M., & Seamans, R. (2023). How will language modelers like ChatGPT affect occupations and industries? arXiv. https://arxiv.org/abs/2303.01157",
 "Frank, M. R., Ahn, Y.-Y., & Moro, E. (2025). AI exposure predicts unemployment risk: A new approach to technology-driven job loss. PNAS Nexus, 4(4), pgaf107. https://doi.org/10.1093/pnasnexus/pgaf107",
 "Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019",
 "Gao, S., & Huang, M. (2026). Bounded by risk, not capability: Quantifying AI occupational substitution rates via a tech-risk dual-factor model. arXiv. https://doi.org/10.48550/arXiv.2604.04464",
 "Georgieff, A., & Hyee, R. (2022). Artificial intelligence and employment: New cross-country evidence. Frontiers in Artificial Intelligence, 5, 832736. https://doi.org/10.3389/frai.2022.832736",
 "Handa, K., Tamkin, A., McCain, M., Huang, S., Durmus, E., Heck, S., Mueller, J., Hong, J., Ritchie, S., Belonax, T., Troy, K. K., Amodei, D., Kaplan, J., Clark, J., & Ganguli, D. (2025). Which economic tasks are performed with AI? Evidence from millions of Claude conversations. arXiv. https://arxiv.org/abs/2503.04761",
 "Instituto Nacional de Estadística y Geografía. (2019). Sistema Nacional de Clasificación de Ocupaciones (SINCO) 2019. INEGI.",
 "Instituto Nacional de Estadística y Geografía. (2025). Encuesta Nacional de Ocupación y Empleo 2025, cuestionario ampliado, primer trimestre [Metadatos y bases de datos]. Red Nacional de Metadatos. https://www.inegi.org.mx/rnm/index.php/catalog/1104",
 "Kambourov, G., & Manovskii, I. (2008). Rising occupational and industry mobility in the United States: 1968-97. International Economic Review, 49(1), 41-79. https://doi.org/10.1111/j.1468-2354.2008.00473.x",
 "Meng, Q., Zhu, H., Xiao, K., Zhang, L., & Xiong, H. (2019). A hierarchical career-path-aware neural network for job mobility prediction. En Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 14-24). ACM. https://doi.org/10.1145/3292500.3330969",
 "National Center for O*NET Development. (2024). O*NET 28.3 Database [Base de datos]. U.S. Department of Labor. https://www.onetcenter.org/database.html",
 "Paolillo, A., Colella, F., Nosengo, N., Schiano, F., Stewart, W., Zambrano, D., Chappuis, I., Lalive, R., & Floreano, D. (2022). How to compete with robots by assessing job automation risks and resilient alternatives. Science Robotics, 7(65), eabg5561. https://doi.org/10.1126/scirobotics.abg5561",
 "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1706.03762",
 "Zhao, W. X., Zhou, K., Li, J., Tang, T., Wang, X., Hou, Y., Min, Y., Zhang, B., Zhang, J., Dong, Z., Du, Y., Yang, C., Chen, Y., Chen, Z., Jiang, J., Ren, R., Li, Y., Tang, X., Liu, Z., . . . Wen, J.-R. (2023). A survey of large language models. arXiv. https://arxiv.org/abs/2303.18223",
]:
    ref(a)
