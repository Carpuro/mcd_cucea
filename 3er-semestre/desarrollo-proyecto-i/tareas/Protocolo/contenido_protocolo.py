# -*- coding: utf-8 -*-
"""
Protocol content. Every factual statement is supported by an external, citable source (APA 7).
Unpublished thesis results are NOT used as evidence (professor's instruction, 2026-10-07).
Sources verified against the documents saved in ./fuentes and ../Actividad_Referencias/referencias.
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
    "riesgo de que el trabajo sea sustituido por tecnología. Con qué herramientas: un modelo "
    "construido con métodos de ciencia de datos que integra índices de exposición ocupacional, "
    "modelos estadísticos y escenarios de adopción tecnológica. Dónde se aplicará: en la industria "
    "manufacturera del estado de Jalisco.")

# ---------------------------------------------------------------- II
seccion("Planteamiento del problema")
sub("Contexto")
par("La automatización es el proceso mediante el cual el capital reemplaza al trabajo en tareas que "
    "antes realizaban las personas; su efecto inmediato es desplazar trabajo, aunque puede "
    "compensarse con la creación de tareas nuevas (Acemoglu y Restrepo, 2019). Durante décadas, este "
    "proceso se asoció sobre todo con tareas rutinarias, es decir, con actividades que siguen reglas "
    "explícitas y que por ello pueden programarse en una computadora (Autor et al., 2003).")
par("En los últimos años la automatización se extendió en dos direcciones. Por un lado, los modelos "
    "de lenguaje de gran escala, que se definen formalmente en el marco teórico, ampliaron la "
    "capacidad de las máquinas para realizar tareas cognitivas como redactar, resumir o analizar "
    "información. Eloundou et al. (2023) estiman que cerca de 80 % de los trabajadores de Estados "
    "Unidos podría tener al menos 10 % de sus tareas afectadas por estos modelos, y que alrededor de "
    "19 % podría ver afectada la mitad o más de sus tareas. Para México, Azuara et al. (2024) "
    "estiman que 74 % de los empleos tiene más de 10 % de sus tareas expuestas, y Benítez-Rueda y "
    "Parrado (2024) calculan que alrededor de 16 millones de empleos mexicanos están muy expuestos a "
    "la inteligencia artificial en un horizonte de un año.")
par("Por otro lado, la robótica industrial sigue extendiéndose sobre las tareas físicas. México "
    "instaló 5,594 robots industriales en 2024 y es el segundo mercado de robots de América, después "
    "de Estados Unidos (International Federation of Robotics [IFR], 2025). La evidencia sobre su "
    "efecto en el empleo mexicano no es concluyente. Faber (2020) encuentra que los robots instalados "
    "en Estados Unidos reducen el empleo en los mercados laborales mexicanos, con mayor efecto en "
    "operadores de maquinaria de baja escolaridad de la manufactura, y Artuc et al. (2019) estiman "
    "que un robot adicional por cada mil trabajadores en Estados Unidos reduce 6.7 % el crecimiento "
    "de las exportaciones por trabajador de México hacia ese país. En sentido contrario, Márquez "
    "Stone y Sandoval Cabrera (2024) encuentran una correlación positiva entre la adopción de robots "
    "y el empleo y los salarios en la industria automotriz de 14 estados entre 2013 y 2022, y Maloney "
    "y Molina (2019) documentan que en los países en desarrollo el empleo de operadores y "
    "ensambladores ha crecido, aunque con indicios de polarización en México.")
par("La industria manufacturera de Jalisco se ubica en el cruce de ambas tendencias. En el cuarto "
    "trimestre de 2024 empleaba a 698,147 personas, 17.9 % de los 4.0 millones de ocupados del "
    "estado, y la tasa de informalidad laboral estatal era de 46.5 % (Instituto Nacional de "
    "Estadística y Geografía [INEGI], 2025). A ello se suma la relocalización de empresas hacia "
    "México, conocida como nearshoring: según el Banco de México (2022), 16 % de las empresas con más "
    "de 100 trabajadores reportó beneficios de este fenómeno, concentrados en la región norte y en la "
    "manufactura integrada a cadenas globales de valor. Sin embargo, el efecto en Jalisco no es "
    "lineal: en 2024 el estado recibió 1,100 millones de dólares de inversión extranjera directa, "
    "3 % del total nacional, y pasó del cuarto al noveno lugar entre las entidades (Secretaría de "
    "Economía [SE], 2025).")
sub("Definición del problema")
par("Las medidas disponibles no permiten saber qué ocupaciones de la manufactura jalisciense enfrentan "
    "qué tipo de riesgo. La estimación más difundida, la de Frey y Osborne (2017), se construyó a "
    "partir de 70 ocupaciones etiquetadas de forma subjetiva por un grupo de investigadores y se "
    "extrapoló al resto con datos de Estados Unidos, por lo que es estática y depende del juicio "
    "experto. Los índices posteriores miden por separado cada tecnología: unos la exposición a la IA "
    "cognitiva (Eloundou et al., 2023; Felten et al., 2021, 2023) y otros la exposición a robots "
    "(Acemoglu y Restrepo, 2020; Webb, 2020), aun cuando Webb (2020) muestra que ambas tecnologías "
    "se dirigen a tareas distintas. Además, la exposición técnica no basta para que la sustitución "
    "ocurra, pues automatizar solo resulta conveniente cuando el costo del capital es menor que el "
    "del trabajo que reemplaza (Acemoglu y Restrepo, 2018).")
par("En consecuencia, el problema de investigación es la falta de un instrumento que permita evaluar, "
    "con datos de México, el riesgo de sustitución laboral que enfrentan las ocupaciones de la "
    "industria manufacturera de Jalisco ante dos tecnologías diferentes, la inteligencia artificial "
    "cognitiva y la robótica, considerando además si la sustitución es económicamente rentable para "
    "las empresas. Sin ese instrumento, las autoridades, las cámaras industriales y los centros de "
    "capacitación no cuentan con un diagnóstico para anticipar qué trabajadores necesitarán apoyo ni "
    "de qué tipo.")
sub("Preguntas de investigación")
par("Pregunta general: ¿cómo se distribuye el riesgo de sustitución laboral por inteligencia "
    "artificial cognitiva y por robótica entre las ocupaciones y ramas de la industria manufacturera "
    "de Jalisco, y en qué medida la rentabilidad de automatizar determina que ese riesgo se "
    "materialice?")
item("1. ¿Qué ocupaciones manufactureras de Jalisco están más expuestas a la IA cognitiva y cuáles a "
     "la robótica?")
item("2. ¿Las ramas manufactureras donde automatizar es más rentable sustituyen más trabajo por "
     "capital?")
item("3. ¿Qué presión de sustitución podría enfrentar el sector hacia 2030 bajo distintos escenarios "
     "de adopción tecnológica?")

# ---------------------------------------------------------------- III
seccion("Justificación")
par("Relevancia social. La manufactura emplea a casi una de cada cinco personas ocupadas en Jalisco y "
    "casi la mitad de los ocupados del estado trabaja en la informalidad (INEGI, 2025), es decir, en "
    "condiciones de vulnerabilidad laboral y, en muchos casos, sin seguridad social. Si la "
    "automatización desplaza trabajadores en este sector, una parte importante de ellos carecería de "
    "protección. La evidencia para México apunta a que los más afectados por la robótica son los "
    "operadores de maquinaria con baja escolaridad (Faber, 2020), un grupo con pocas opciones de "
    "reconversión laboral.")
par("Relevancia práctica. Como los estudios disponibles llegan a conclusiones opuestas para México "
    "(Artuc et al., 2019; Faber, 2020; Márquez Stone y Sandoval Cabrera, 2024), hace falta un "
    "diagnóstico local que distinga ocupaciones, ramas y tecnologías. Ese diagnóstico permitiría a las "
    "instancias de desarrollo económico, trabajo y capacitación del estado orientar sus programas "
    "hacia las ocupaciones con mayor riesgo antes de que el desplazamiento ocurra. La literatura "
    "sobre la adopción de tecnologías de propósito general sugiere que sus efectos tardan en aparecer "
    "en las estadísticas (Brynjolfsson et al., 2021), lo que abre un margen de tiempo para actuar.")
par("Aportación a la ciencia. El proyecto propone construir dos índices de exposición ocupacional con "
    "la misma metodología, uno para la IA cognitiva y otro para la robótica, y combinarlos con una "
    "medida de rentabilidad de la automatización. El índice cognitivo partirá del índice de "
    "exposición a la IA de Felten et al. (2021), al que se agregará una dimensión temporal a partir "
    "de la evolución del desempeño de los modelos de lenguaje, y ambos índices se validarán contra "
    "medidas publicadas, como la exposición a robots de Webb (2020) y el uso observado de la IA de "
    "Handa et al. (2025).")
par("Viabilidad. Todas las fuentes de información son públicas y gratuitas: la ENOE, los Censos "
    "Económicos y la clasificación de ocupaciones del INEGI, la base O*NET, las estadísticas de la "
    "Federación Internacional de Robótica y las bases de datos que acompañan a los estudios citados.")

# ---------------------------------------------------------------- IV
seccion("Objetivos")
sub("Objetivo general")
par("Evaluar el riesgo de sustitución laboral en la industria manufacturera de Jalisco frente a la "
    "inteligencia artificial cognitiva y la robótica, mediante un modelo de ciencia de datos que "
    "integre la exposición ocupacional, la rentabilidad de automatizar y escenarios de adopción "
    "tecnológica para el periodo 2025-2030.")
sub("Objetivos específicos")
item("1. Identificar y caracterizar las ocupaciones y ramas de la industria manufacturera de Jalisco, "
     "así como su composición de empleo, a partir de la ENOE, los Censos Económicos y los registros "
     "del IMSS.")
item("2. Construir y validar dos índices de exposición ocupacional, uno cognitivo y uno físico, y "
     "aplicarlos a la estructura ocupacional de la manufactura.")
item("3. Desarrollar modelos que relacionen la exposición con el uso observado de la IA y con la "
     "sustitución de trabajo por capital en función de la rentabilidad de automatizar.")
item("4. Evaluar y comparar el desempeño de los modelos y la robustez de sus resultados mediante "
     "validación externa, validación cruzada e inferencia por permutación.")
item("5. Proyectar la presión de sustitución hacia 2030 en tres escenarios de adopción y presentar los "
     "resultados en un tablero de visualización por rama, ocupación y municipio.")

# ---------------------------------------------------------------- V
seccion("Hipótesis")
par("H1. Dentro de la industria manufacturera de Jalisco, la exposición a la IA cognitiva y la "
    "exposición a la robótica recaen en ocupaciones distintas: los operadores y trabajadores de "
    "producción concentran la exposición física, mientras que las ocupaciones administrativas, "
    "técnicas y de supervisión concentran la exposición cognitiva. Esta hipótesis se deriva de la "
    "evidencia de Webb (2020) sobre la orientación distinta de ambas tecnologías y se contrastará con "
    "análisis factorial exploratorio y confirmatorio sobre los índices de exposición.")
par("H2. Las ramas manufactureras con mayor rentabilidad de automatizar presentan mayor "
    "profundización de capital y menor participación del trabajo en el valor agregado. Esta hipótesis "
    "se deriva de la condición de rentabilidad de Acemoglu y Restrepo (2018) y se contrastará con un "
    "panel de los Censos Económicos con efectos fijos e inferencia por permutación.")

# ---------------------------------------------------------------- VI
seccion("Antecedentes")
par("Los antecedentes se presentan en orden cronológico. Autor et al. (2003) establecieron el enfoque "
    "de tareas: la tecnología sustituye tareas y no ocupaciones completas, y las tareas rutinarias "
    "son las más fáciles de automatizar. Frey y Osborne (2017) estimaron, con un clasificador de "
    "procesos gaussianos aplicado a 702 ocupaciones, que 47 % del empleo de Estados Unidos enfrentaba "
    "un riesgo alto de automatización. Acemoglu y Restrepo (2018) formalizaron el proceso como una "
    "carrera entre el desplazamiento del trabajo y la creación de tareas nuevas, e incorporaron la "
    "condición de que automatizar solo ocurre cuando es más barato que pagar salarios.")
par("Sobre la robótica, Graetz y Michaels (2018) encontraron, con datos de 17 países entre 1993 y "
    "2007, que los robots industriales elevaron la productividad laboral, el valor agregado y los "
    "salarios, sin un efecto significativo en las horas totales trabajadas. Acemoglu y Restrepo "
    "(2019) atribuyeron el menor crecimiento del empleo en Estados Unidos durante tres décadas a un "
    "desplazamiento más rápido, sobre todo en la manufactura, y a una creación de tareas nuevas más "
    "débil. Acemoglu y Restrepo (2020) estimaron que cada robot adicional por cada mil trabajadores "
    "redujo la razón empleo-población entre 0.18 y 0.34 puntos porcentuales en las zonas laborales de "
    "ese país.")
par("Para México y los países en desarrollo, Artuc et al. (2019) encontraron que la automatización en "
    "Estados Unidos reduce el crecimiento de las exportaciones mexicanas y el empleo manufacturero en "
    "los municipios con ocupaciones más automatizables. Maloney y Molina (2019) no hallaron, en "
    "cambio, desplazamiento en los países en desarrollo, donde el empleo de operadores y ensambladores "
    "aumentó, aunque con indicios de polarización en México y Brasil. Faber (2020) mostró que los "
    "robots de Estados Unidos reducen el empleo en los mercados laborales mexicanos, sobre todo el de "
    "operadores de maquinaria de baja escolaridad, y Webb (2020) documentó, con el texto de las "
    "patentes, que a diferencia del software y los robots la IA se dirige a tareas de alta "
    "calificación.")
par("La llegada de los modelos de lenguaje abrió una nueva línea. Brynjolfsson et al. (2021) "
    "explicaron por qué los efectos de las tecnologías de propósito general tardan en aparecer en las "
    "estadísticas. Eloundou et al. (2023) midieron la exposición de las ocupaciones a estos modelos, "
    "Felten et al. (2023) adaptaron su índice de exposición a la IA a los modelos de lenguaje y "
    "Gmyrek et al. (2023) concluyeron para la Organización Internacional del Trabajo que el efecto "
    "dominante será complementar más que automatizar. En América Latina, Azuara et al. (2024) y "
    "Benítez-Rueda y Parrado (2024) estimaron la exposición del empleo mexicano. Márquez Stone y "
    "Sandoval Cabrera (2024) analizaron la adopción de robots en la industria automotriz de 14 estados "
    "del país, y Handa et al. (2025) midieron por primera vez el uso real de la IA por ocupación a "
    "partir de millones de conversaciones con un asistente.")

# ---------------------------------------------------------------- VII
seccion("Marco teórico")
sub("Conceptos y definiciones")
par("Automatización y sustitución laboral. La automatización permite que el capital reemplace al "
    "trabajo en tareas que antes realizaban las personas, lo que produce un efecto de desplazamiento; "
    "la creación de tareas nuevas genera, en sentido contrario, un efecto de reinstalación del trabajo "
    "(Acemoglu y Restrepo, 2019). En este protocolo, el riesgo de sustitución laboral se entiende como "
    "la posibilidad de que ocurra ese desplazamiento en las tareas de una ocupación.")
par("Modelos de lenguaje de gran escala. Se trata de modelos de lenguaje basados en la arquitectura "
    "Transformer que contienen cientos de miles de millones de parámetros o más, se entrenan con "
    "grandes volúmenes de texto y muestran una fuerte capacidad para comprender el lenguaje natural y "
    "resolver tareas complejas mediante la generación de texto; ejemplos de ellos son GPT-3, PaLM y "
    "LLaMA (Zhao et al., 2023). La arquitectura Transformer, en la que se basan, es una red neuronal "
    "que se apoya únicamente en mecanismos de atención (Vaswani et al., 2017).")
par("Robot industrial. La Federación Internacional de Robótica define un robot industrial como una "
    "máquina controlada automáticamente, reprogramable y multipropósito (IFR, 2014, como se citó en "
    "Acemoglu y Restrepo, 2020).")
par("Nearshoring. Es la relocalización de actividades productivas hacia países más cercanos al lugar "
    "de consumo, a diferencia del reshoring, que consiste en regresar la producción al país de origen "
    "(Banco de México, 2022). En la literatura de gestión de operaciones se le define como la "
    "reubicación de la producción hacia la región de origen de la empresa (Merino et al., 2021). Para "
    "México, la cercanía geográfica con Estados Unidos y el T-MEC lo convierten en un candidato natural "
    "para la relocalización de empresas que abastecen al mercado estadounidense (Banco de México, "
    "2022).")
par("Informalidad laboral. Comprende a las personas ocupadas que son laboralmente vulnerables por la "
    "naturaleza de la unidad económica para la que trabajan, o cuyo vínculo laboral no es reconocido "
    "por su fuente de trabajo; incluye a quienes trabajan en micronegocios no registrados y a quienes "
    "laboran sin seguridad social en unidades económicas registradas (INEGI, 2025).")
sub("Teoría de tareas y condición de rentabilidad")
par("El fundamento teórico del proyecto es el enfoque de tareas (Autor et al., 2003), según el cual la "
    "tecnología no sustituye ocupaciones completas, sino tareas específicas. Acemoglu y Restrepo "
    "(2018, 2019) desarrollan este enfoque como una carrera entre el desplazamiento que genera la "
    "automatización y la reinstalación que generan las tareas nuevas, y establecen que la sustitución "
    "solo se materializa cuando el costo del capital es menor que el salario. La teoría de la curva J "
    "de Brynjolfsson et al. (2021) complementa este marco al explicar por qué el efecto de las "
    "tecnologías de propósito general puede tardar varios años en observarse.")
sub("Dos fronteras de la automatización")
par("En este protocolo se denomina frontera cognitiva al conjunto de tareas que pueden automatizarse "
    "con modelos de lenguaje, y frontera física al conjunto de tareas que pueden automatizarse con "
    "robots. La distinción se sustenta en la clasificación de tareas cognitivas y manuales de Autor "
    "et al. (2003) y en la evidencia de Webb (2020), quien encuentra que, a diferencia del software y "
    "los robots, la inteligencia artificial se dirige a tareas de alta calificación. Si ambas "
    "tecnologías se dirigen a tareas distintas, es de esperar que una misma industria, como la "
    "manufacturera, enfrente riesgos diferentes en sus áreas de producción y en sus áreas "
    "administrativas y técnicas, lo que da origen a la primera hipótesis.")
sub("Elección del método")
par("El enfoque es cuantitativo porque el riesgo se expresa en magnitudes comparables entre "
    "ocupaciones, ramas y territorios. Siguiendo a la literatura de referencia (Eloundou et al., 2023; "
    "Felten et al., 2021; Webb, 2020), la exposición se mide a partir de los descriptores de tareas y "
    "habilidades de O*NET. Los modelos estadísticos permiten contrastar las hipótesis con inferencia "
    "formal, y los modelos de aprendizaje automático aportan capacidad predictiva y medidas de "
    "importancia de las variables. La proyección por escenarios, en lugar de un pronóstico, responde a "
    "que no existe un registro histórico de automatización observada para Jalisco.")

# ---------------------------------------------------------------- VIII
seccion("Metodología")
par("Tipo de estudio. Investigación cuantitativa, no experimental, que combina un análisis transversal "
    "de la exposición ocupacional con un análisis longitudinal de la sustitución de trabajo por "
    "capital y una proyección por escenarios.")
par("Población y unidades de análisis. Trabajadores ocupados en la industria manufacturera de Jalisco, "
    "sectores 31 a 33 del Sistema de Clasificación Industrial de América del Norte. Las unidades de "
    "análisis son la ocupación, clasificada según el Sistema Nacional de Clasificación de Ocupaciones "
    "(INEGI, 2011), el trabajador, la rama manufacturera y el municipio.")
par("Fuentes de datos. Se integrarán en una base de datos SQL Server las siguientes fuentes públicas: "
    "la ENOE y los Censos Económicos (INEGI, 2025, s.f.), la base de ocupaciones O*NET (National "
    "Center for O*NET Development, 2024), el índice de exposición a la IA y sus datos de "
    "habilidades (Felten et al., 2021), los resultados de los modelos de lenguaje en pruebas de "
    "referencia (Epoch AI, s.f.), las estadísticas de robots industriales (IFR, 2025), la inversión "
    "extranjera directa (SE, 2025) y el uso observado de la IA por ocupación (Handa et al., 2025).")
par("Procedimiento. El trabajo se organiza en seis pasos alineados con los objetivos específicos:")
item("1. Integración y depuración de las fuentes, y delimitación de la población manufacturera por rama "
     "y ocupación.")
item("2. Construcción de los índices de exposición cognitiva y física a partir de O*NET, su validación "
     "contra índices publicados (Felten et al., 2021; Webb, 2020) y su traslado a las ocupaciones "
     "mexicanas mediante las tablas de correspondencia del INEGI.")
item("3. Análisis de la estructura de la exposición con análisis factorial exploratorio y "
     "confirmatorio, para contrastar H1, y descripción del perfil de exposición del sector ponderado "
     "por empleo.")
item("4. Modelación de la exposición frente al uso observado de la IA con un modelo de dos partes "
     "(hurdle), complementado con modelos de aprendizaje supervisado, como bosques aleatorios y "
     "gradient boosting, con validación cruzada e interpretación mediante valores SHAP.")
item("5. Contraste de H2 con un panel de los Censos Económicos con efectos fijos de periodo, usando un "
     "índice de rentabilidad de la automatización rezagado e inferencia por permutación, desagregado a "
     "nivel de rama manufacturera.")
item("6. Proyección 2025-2030 en tres escenarios (conservador, base y acelerado) que combinan la "
     "exposición, la rentabilidad y la evolución de la capacidad de la IA y de la adopción de robots, "
     "para dimensionar la presión de sustitución en el sector, y elaboración del tablero de "
     "visualización.")
par("Herramientas de análisis. Python (pandas, NumPy, statsmodels, scikit-learn, factor_analyzer y "
    "Matplotlib), SQL Server para la integración de datos y GitHub para el control de versiones y la "
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
par("El cronograma reproduce el plan registrado en el avance de protocolo de la tesis, con la "
    "actividad de reenfoque a la industria manufacturera añadida y el estado de cada etapa a octubre "
    "de 2026.")
caption_table(1, "Cronograma de actividades del proyecto de tesis")
table([
    ["Etapa / actividad", "2025B", "2026A", "2026B", "2027A", "Estado"],
    ["Revisión de literatura y antecedentes", "Ago-Sep", "", "", "", "Concluida"],
    ["Corrección del marco teórico y definición metodológica", "Sep-Oct", "", "", "", "Concluida"],
    ["Obtención y limpieza de datos (INEGI, O*NET)", "Oct-Nov", "", "", "", "Concluida"],
    ["Mapeo y normalización de ocupaciones", "Nov-Dic", "Ene", "", "", "Concluida"],
    ["Cálculo de índices", "", "Feb-Mar", "", "", "Concluida"],
    ["Incorporación de indicadores emergentes de IA", "", "Mar-Abr", "", "", "Concluida"],
    ["Desarrollo y entrenamiento de modelos", "", "May-Jul", "Ago-Sep", "", "Concluida"],
    ["Reenfoque a la industria manufacturera", "", "", "Ago-Oct", "", "En curso"],
    ["Evaluación y validación del modelo", "", "", "Sep-Nov", "", "En curso"],
    ["Visualización y desarrollo del tablero", "", "", "Nov-Dic", "Ene", "Pendiente"],
    ["Redacción de resultados y análisis de impacto", "", "", "Dic", "Feb-Mar", "En curso"],
    ["Escritura y revisión del documento final", "", "", "", "Mar-Jun", "Pendiente"],
    ["Presentación y defensa del trabajo de tesis", "", "", "", "Jul 2027", "Pendiente"],
], [3300, 900, 900, 900, 1000, 1100])
note("Nota. Elaboración propia con base en el plan del avance de protocolo de la tesis.")

# ---------------------------------------------------------------- XI
seccion("Referencias bibliográficas")
for a in [
 "Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. American Economic Review, 108(6), 1488-1542. https://doi.org/10.1257/aer.20160696",
 "Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. Journal of Economic Perspectives, 33(2), 3-30. https://doi.org/10.1257/jep.33.2.3",
 "Acemoglu, D., & Restrepo, P. (2020). Robots and jobs: Evidence from US labor markets. Journal of Political Economy, 128(6), 2188-2244. https://doi.org/10.1086/705716",
 "Artuc, E., Christiaensen, L., & Winkler, H. (2019). Does automation in rich countries hurt developing ones? Evidence from the U.S. and Mexico (Policy Research Working Paper 8741). Banco Mundial.",
 "Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. The Quarterly Journal of Economics, 118(4), 1279-1333. https://doi.org/10.1162/003355303322552801",
 "Azuara, O., Ripani, L., & Torres, E. (2024). AI and the increase of productivity and labor inequality in Latin America: Potential impact of large language models on Latin American workforce (IDB Discussion Paper 01076). Banco Interamericano de Desarrollo.",
 "Banco de México. (2022). Opinión empresarial sobre la relocalización de las empresas hacia México (Recuadro 2). En Reporte sobre las economías regionales, abril-junio 2022 (pp. 16-21). https://www.banxico.org.mx/publicaciones-y-prensa/reportes-sobre-las-economias-regionales/recuadros/%7BE243D1D1-63F5-6C86-38F0-28BD3CF33CE6%7D.pdf",
 "Benítez-Rueda, M., & Parrado, E. (2024). “Mirror, mirror on the wall: Which jobs will AI replace after all?”: A new index of occupational exposure (IDB Working Paper 1624). Banco Interamericano de Desarrollo.",
 "Brynjolfsson, E., Rock, D., & Syverson, C. (2021). The productivity J-curve: How intangibles complement general purpose technologies. American Economic Journal: Macroeconomics, 13(1), 333-372. https://doi.org/10.1257/mac.20180386",
 "Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. arXiv. https://arxiv.org/abs/2303.10130",
 "Epoch AI. (s.f.). Datos sobre el desempeño de modelos de inteligencia artificial en pruebas de referencia [Base de datos]. https://epoch.ai/data",
 "Faber, M. (2020). Robots and reshoring: Evidence from Mexican labor markets. Journal of International Economics, 127, 103384. https://doi.org/10.1016/j.jinteco.2020.103384",
 "Felten, E., Raj, M., & Seamans, R. (2021). Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses. Strategic Management Journal, 42(12), 2195-2217. https://doi.org/10.1002/smj.3286",
 "Felten, E., Raj, M., & Seamans, R. (2023). How will language modelers like ChatGPT affect occupations and industries? arXiv. https://arxiv.org/abs/2303.01157",
 "Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019",
 "Gmyrek, P., Berg, J., & Bescond, D. (2023). Generative AI and jobs: A global analysis of potential effects on job quantity and quality (ILO Working Paper 96). Organización Internacional del Trabajo. https://doi.org/10.54394/FHEM8239",
 "Graetz, G., & Michaels, G. (2018). Robots at work. The Review of Economics and Statistics, 100(5), 753-768. https://doi.org/10.1162/rest_a_00754",
 "Handa, K., Tamkin, A., McCain, M., Huang, S., Durmus, E., Heck, S., Mueller, J., Hong, J., Ritchie, S., Belonax, T., Troy, K. K., Amodei, D., Kaplan, J., Clark, J., & Ganguli, D. (2025). Which economic tasks are performed with AI? Evidence from millions of Claude conversations. arXiv. https://arxiv.org/abs/2503.04761",
 "Instituto Nacional de Estadística y Geografía. (2011). Sistema Nacional de Clasificación de Ocupaciones (SINCO). INEGI.",
 "Instituto Nacional de Estadística y Geografía. (2025). Encuesta Nacional de Ocupación y Empleo (ENOE), Jalisco: Cuarto trimestre de 2024 (Boletín de indicador 110/25). https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/enoe/enoe2025_02_Jal.pdf",
 "Instituto Nacional de Estadística y Geografía. (s.f.). Censos Económicos [Programa de información]. https://www.inegi.org.mx/programas/ce/",
 "International Federation of Robotics. (2025). World Robotics 2025: Industrial robots [Resumen ejecutivo]. IFR.",
 "Maloney, W. F., & Molina, C. (2019). Is automation labor-displacing in the developing countries, too? Robots, polarization, and jobs (Policy Research Working Paper). Banco Mundial. https://doi.org/10.1596/33301",
 "Márquez Stone, V., & Sandoval Cabrera, S. V. (2024). Effects of automation on Mexican automotive employment: 2013-2022. The Indian Journal of Labour Economics. https://doi.org/10.1007/s41027-024-00505-5",
 "Merino, F., Di Stefano, C., & Fratocchi, L. (2021). Back-shoring vs near-shoring: A comparative exploratory study in the footwear industry. Operations Management Research, 14(1-2), 17-37. https://doi.org/10.1007/s12063-020-00173-w",
 "National Center for O*NET Development. (2024). O*NET 28.3 Database [Base de datos]. U.S. Department of Labor. https://www.onetcenter.org/database.html",
 "Secretaría de Economía. (2025). Inversión extranjera directa en México: Cuarto trimestre de 2024 [Informe]. Gobierno de México. https://www.gob.mx/cms/uploads/attachment/file/980231/20250225_IED_4T_2024_Versi_n_p_blica_VF.pdf",
 "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1706.03762",
 "Webb, M. (2020). The impact of artificial intelligence on the labor market [Documento de trabajo]. Stanford University. https://www.michaelwebb.co/webb_ai.pdf",
 "Zhao, W. X., Zhou, K., Li, J., Tang, T., Wang, X., Hou, Y., Min, Y., Zhang, B., Zhang, J., Dong, Z., Du, Y., Yang, C., Chen, Y., Chen, Z., Jiang, J., Ren, R., Li, Y., Tang, X., Liu, Z., . . . Wen, J.-R. (2023). A survey of large language models. arXiv. https://arxiv.org/abs/2303.18223",
]:
    ref(a)
