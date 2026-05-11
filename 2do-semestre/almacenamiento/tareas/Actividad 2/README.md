# Actividad 2 — WordCount Corregido + Nube de Palabras

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Módulo:** Analítica con MapReduce  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Apache Hadoop 3.3.6 · Python (wordcloud)

## Objetivo

Versión mejorada del WordCount que filtra stopwords y signos de puntuación, produciendo un conteo semánticamente útil. Se genera además una nube de palabras con las 100 términos más frecuentes.

## Mejoras respecto a Actividad 1

| Aspecto | Actividad 1 | Actividad 2 |
|---------|-------------|-------------|
| Stopwords | No filtradas | Eliminadas (the, and, of…) |
| Puntuación | Incluida como tokens | Eliminada |
| Visualización | Solo texto | Nube de palabras |

## Proceso

1. Ejecutar WordCount corregido con filtrado de stopwords en Hadoop
2. Exportar frecuencias limpias a `resultado2.txt`
3. Generar nube de palabras con Python (`wordcloud` + `matplotlib`)

## Resultado

- **`resultado2.txt`** — frecuencias sin stopwords ni puntuación
- **`nube_de_palabras.webp`** — visualización de las 100 palabras más frecuentes

## Entregable

`Actividad_WordCount_Corregido_NubePalabras_CarlosPulidoRosas.pdf`
