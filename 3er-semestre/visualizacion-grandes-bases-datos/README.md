# Visualización de Grandes Bases de Datos
**Semestre:** 3ro | **Departamento:** DSI | **Créditos:** 7
**Profesor:** Mtro. Carlos Fernando Ruiz Chávez | **NRC:** 176458 | **Día:** jueves (en línea)

Análisis exploratorio y visualización de la base horaria de calidad del aire 2024 del SIMAJ (Jalisco):
distribuciones, valores atípicos, series de tiempo, correlación, regresión, imputación y K-medias.

## Datos

- `datos/BD_2024_calidad_aire.xlsx`: hoja `Data` con lecturas horarias por estación y hoja `Param`
  con los metadatos y coordenadas de las estaciones.
- La columna `DATE` ya incluye la hora.
- **Country (COU):** la más cercana a casa; solo mide CO en septiembre y no mide NO₂ (tareas 1.0 a 1.2).
- **Centro (CEN):** cobertura anual de O₃, CO y partículas; NO₂, NO y NOx solo de septiembre a
  diciembre de 2024 (tareas 1.3 en adelante). Ninguna estación de la red mide NO₂ antes de agosto.

## Tareas (`tareas/`)

Cada tarea tiene su carpeta con el DOCX y el PDF entregado, y un script `build_tarea*.py` en
`tareas/` que genera las figuras, llena la plantilla del informe y exporta el PDF con LibreOffice.

| # | Tarea | Contenido | Estación |
|---|-------|-----------|----------|
| 1.0 | Diagrama de caja | Boxplot del CO y valores atípicos con RIC | Country |
| 1.1 | Cuartiles | Cuartiles de Tukey contra interpolación lineal | Country |
| 1.2 | Histograma | Histograma del CO contra la norma IMECA | Country |
| 1.3 | Series de tiempo | Serie horaria, medias móviles, boxplots por hora y por mes | Centro |
| 1.4 | Correlación con NO₂ | Covarianza, Pearson, dispersión, linealidad, regresión logística | Centro |
| 1.5 | Ajustes a la correlación | Corpus homogéneo, atípicos de Tukey, recta por el origen, mapas de calor | Centro |
| 1.6 | NO₂ con PM10 y PM2.5 | Imputación del NO₂ con CO, regresión múltiple, colinealidad, fracción fina y gruesa | Centro |
| 1.7 | Modelo refinado | Regresión múltiple por el origen contra la 1.6, residuales, K-medias | Centro |

Los scripts `build_tarea16.py` y `build_tarea17.py` comparten la preparación de datos: el segundo
importa al primero.

## Notas (`notas/`)

Diapositivas de clase `VGBD_Sesion_01.pdf` a `VGBD_Sesion_09.pdf` (falta la sesión 5).

## Herramientas

Python · pandas · NumPy · Matplotlib · statsmodels · scikit-learn · python-docx · LibreOffice
