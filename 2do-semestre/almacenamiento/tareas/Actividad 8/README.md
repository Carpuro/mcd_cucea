# Actividad 8 — Construccion de Modelos e Interpretacion con BigData

**Materia:** Almacenamiento de Grandes Bases de Datos
**Alumno:** Carlos Pulido Rosas
**Herramientas:** Python 3.13 · statsmodels · scikit-learn · pandas

## Objetivo

Construir y validar dos modelos de regresion sobre el dataset de asegurados IMSS abril 2026,
e interpretar la influencia de la edad, entidad y tamano de empresa sobre el salario, y
cuantificar la brecha salarial de genero por sector y entidad.

## Modelos

| Modelo | Tipo | Variable dependiente | Predictores |
|--------|------|---------------------|-------------|
| 1 | WLS (ponderado por trabajadores) | Rango salarial W1-W10 | Edad + Edad² + Entidad + Tamano + Edad×Tamano |
| 2 | Logistica GLM Binomial | Salario alto (W3+, percentil 75) | Entidad + Sector + Sexo |

## Resultados clave

- **Modelo 1:** R²=0.0790, F=7,433, p≈0. Pico salarial estimado a los 49.8 anos.
  Empresas medianas/grandes (S4+) valorizan la experiencia sistematicamente mas que microempresas.
- **Modelo 2:** AUC=0.6105, OR mujer=0.7033 (p≈0). Las mujeres tienen 30% menos odds
  de salario alto que los hombres, controlando por entidad y sector.
  Umbral optimo Youden: 0.408 → Sens=39.9%, Spec=75.3%.

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `generar_reporte.py` | Script principal: carga datos, ajusta modelos, genera graficas y reporte |
| `charts/` | 6 figuras generadas (PNG) |
| `Actividad8_AlmacenamientoGBD_CarlosPulidoRosas.docx` | Reporte en Word |
| `Actividad8_AlmacenamientoGBD_CarlosPulidoRosas.pdf` | Entregable final |

## Ejecucion

```bash
conda activate MCD
python generar_reporte.py
```

## Datos

`../../datos/asg-abr-2026.csv` — Asegurados IMSS por Grupo, abril 2026 (IMSS datos abiertos).
1,416,930 filas · 18 columnas · 7.4M trabajadores urbanos tras filtrado.
