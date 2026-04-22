# Tópicos Selectos de Grandes Bases de Datos I
**Semestre:** 2do | **Departamento:** DSI | **Créditos:** 7

En la práctica, el curso cubrió dos bloques independientes: (1) diseño y análisis de comportamiento de agentes de IA, y (2) teoría de decisiones bajo incertidumbre aplicada a inversión agrícola.

## Criterios de evaluación

| Rubro | Peso |
|-------|------|
| Tareas | 35% |
| Trabajo en clase | 35% |
| Exámenes / Proyecto | 30% |

### Puntos extra disponibles
| Actividad | Puntos extra |
|-----------|-------------|
| Asistencia perfecta | +5% |
| Actividad de voluntariado (hasta 2) | +5% c/u (máx. 10%) |
| Participar en eventos de ciencia de datos | +10% |
| Dar una clase | +10% |

## Actividades (`tareas/actividades/`)

### Bloque 1 — Agentes de IA y toma de decisiones
| # | Actividad | Calificación | Estado |
|---|-----------|--------------|--------|
| 1 | Examen diagnóstico | 100/100 | ✅ Entregada |
| 2 | Diseño de agente de IA — Guerrero Maestro de Batalla Drow (identidad, rasgos, moral) | 75/100 | ✅ Entregada |
| 3 | Evaluación de coherencia y decisión — predecir vs. ejecutar vs. analizar (escenario Strahd) | 100/100 | ✅ Entregada |
| 4 | Inventario del agente — armas, riqueza, estado persistente | 100/100 | ✅ Entregada |
| 5 | Autopercepción del agente — el agente se describe a sí mismo según sus parámetros | 100/100 | ✅ Entregada |

### Bloque 2 — Teoría de decisiones bajo incertidumbre
| # | Actividad | Calificación | Estado |
|---|-----------|--------------|--------|
| 6 | Árbol de decisión + simulación Monte Carlo — inversión en riego para productor de caña, Pánuco | 100/100 | ✅ Entregada |
| 7 | Condiciones de viabilidad para la inversión — perspectiva del vendedor, presentación 5 slides | 100/100 | ✅ Entregada |

## Resultados clave — Actividades 6 y 7

| Métrica | Temporal (sin riego) | Riego precio lista | Riego con 30% de descuento |
|---------|----------------------|--------------------|----------------------------|
| Rendimiento esperado (ton/ha/año) | 47.0 | 88.7 | 88.7 |
| Utilidad anual esperada | −$4,902 MXN | +$860,851 MXN | +$860,851 MXN |
| Utilidad neta acumulada (7 años) | −$34,316 MXN | −$1,974,042 MXN | **+$425,958 MXN** |
| Punto de recuperación | — | 9.2 años | **6.5 años** |
| Precio de indiferencia (7 años) | — | $873.48 MXN/ton | **$791.27 MXN/ton** |
| P(riego > temporal) — Monte Carlo | — | 35.3% | 44.5% |

## Glosario

### Agentes de IA
| Término | Definición |
|---------|------------|
| **Agente de IA** | Sistema autónomo con identidad definida, reglas internas y capacidad de tomar decisiones en contexto |
| **Estado persistente** | Memoria del agente (inventario, atributos, historial) que sobrevive entre interacciones |
| **Alineación** | Grado en que el comportamiento real de un agente corresponde a los valores e intenciones de su diseñador |
| **Coherencia** | Consistencia entre la identidad/valores del agente y sus decisiones reales ante entradas ambiguas |
| **Razonamiento explicable** | Capacidad de justificar una decisión en términos de la propia identidad, contexto y evidencia del agente |
| **Predicción vs. resultado** | Marco de evaluación central: qué se esperaba que hiciera el agente vs. qué hizo realmente — análogo al análisis de error de un modelo |

### Teoría de decisiones
| Término | Definición |
|---------|------------|
| **Árbol de decisión** | Modelo gráfico que mapea alternativas, eventos probabilísticos y sus resultados para apoyar decisiones estructuradas |
| **Utilidad esperada** | Promedio ponderado por probabilidad de los resultados en todos los escenarios; criterio estándar para decisiones bajo incertidumbre |
| **Simulación de Monte Carlo** | Método para estimar una distribución corriendo miles de escenarios aleatorios independientes |
| **Precio de indiferencia** | Nivel de precio al que dos alternativas producen igual utilidad acumulada; por debajo gana una, por encima la otra |
| **Punto de recuperación** | Número de años necesarios para que la utilidad acumulada de una inversión iguale a la mejor alternativa |
| **Aversión a la pérdida** | Sesgo psicológico donde las pérdidas se ponderan más que las ganancias equivalentes — usado en el pitch de ventas de la Act. 7 |
| **Distribución asimétrica** | Cuando la media de un resultado difiere significativamente de su mediana por eventos raros pero extremos (ej. años con 200 ton/ha que elevan la media del riego aunque haya menos escenarios ganadores) |

## Herramientas
Python 3.13 · NumPy · python-docx · LibreOffice headless · Jupyter · conda env `MCD`
