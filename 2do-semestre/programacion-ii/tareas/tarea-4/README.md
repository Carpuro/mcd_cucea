# Practica Power BI — Acceso a la Salud en Mexico

**Materia:** Programacion II  
**Maestria:** Maestria en Ciencia de Datos (MCD) — CUCEA, Universidad de Guadalajara  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Microsoft Power BI (formato PBIP)  

---

## Historia de Uso de Datos

### Pregunta central

> **¿Que tan desigual es el acceso a servicios de salud en Mexico, y que factores sociodemograficos se asocian con la falta de cobertura?**

### Fuente de datos

Los datos provienen de la base de datos relacional **`Defunciones_2000`** (SQL Server local), que contiene informacion sociodemografica y de afiliacion a servicios de salud de la poblacion mexicana. Las tablas utilizadas cubren:

- Cobertura por institucion (IMSS, ISSSTE, PEMEX, sin derechohabiencia)
- Distribucion geografica por estado
- Factores sociales: escolaridad, grupo de edad, poblacion indigena y tipo de localidad (urbana/rural)

### Hallazgos principales

| Indicador | Valor |
|-----------|-------|
| Poblacion total analizada | ~10 millones de personas |
| Sin cobertura de salud | **~65.6%** |
| Con IMSS | ~26.4% |
| Edad promedio de la muestra | ~25.9 anos |

**El dato mas critico:** dos de cada tres personas en la muestra no cuentan con ningun tipo de derechohabiencia, lo que representa una brecha enorme de acceso a la salud formal.

### Narrativa del dashboard

El reporte sigue un flujo de cinco paginas que lleva al lector desde lo general hasta lo especifico:

1. **Portada / KPIs** — Panorama inmediato: cifras clave de poblacion y cobertura, mas la distribucion entre tipos de servicio (IMSS, Sin derechohabiencia, Otro).

2. **Analisis Geografico** — ¿Donde esta el problema? Ranking de estados por porcentaje sin cobertura, con filtro interactivo por entidad y tabla de detalle.

3. **Factores Sociodemograficos** — ¿A quien le afecta mas? Cruce de la falta de cobertura con:
   - Nivel educativo (a menor escolaridad, mayor desproteccion)
   - Grupo de edad (jovenes y adultos mayores mas vulnerables)
   - Poblacion indigena hablante (brecha significativamente mayor)
   - Tipo de localidad — urbana vs. rural

4. **Distribucion por Servicio** — ¿Como se distribuye la cobertura existente? Comparativa entre instituciones y estados con mayor proporcion de afiliados al IMSS.

5. **Conclusiones** — Resumen ejecutivo con los estados mas criticos, la distribucion final de cobertura y los KPIs globales del analisis.

---

## Estructura del Proyecto

```
tarea-4/
├── presentacion.pbip              # Archivo principal Power BI Project
├── presentacion.Report/           # Definicion del reporte (JSON / PBIP)
│   ├── definition/
│   │   ├── report.json            # Configuracion global + tema aplicado
│   │   └── pages/
│   │       ├── c6c0d7e312295e1f0013/   # Portada | KPIs
│   │       ├── geo2analisisestados01/  # Analisis Geografico
│   │       ├── socio3factores000001/   # Factores Sociodemograficos
│   │       ├── comp4servicio000001/    # Distribucion por Servicio
│   │       └── concl5conclusiones01/  # Conclusiones
│   └── StaticResources/
│       └── RegisteredResources/
│           └── PresentacionTheme.json # Tema oscuro personalizado
└── presentacion.SemanticModel/    # Modelo semantico (tablas y medidas)
    └── definition/tables/
        ├── tbl_kpis.tmdl
        ├── tbl_estados_resumen.tmdl
        ├── tbl_acceso_resumen.tmdl
        ├── tbl_escolaridad_resumen.tmdl
        ├── tbl_grupos_edad_resumen.tmdl
        ├── tbl_indigena_resumen.tmdl
        └── tbl_urbano_resumen.tmdl
```

---

## Modelo de Datos

El modelo utiliza 7 tablas importadas desde SQL Server, sin relaciones explicitas entre ellas (cada tabla es un resumen pre-agregado independiente):

| Tabla | Descripcion | Columnas clave |
|-------|-------------|----------------|
| `tbl_kpis` | KPIs globales de la muestra | total_poblacion, pct_imss, pct_sin_derechohabiencia, edad_promedio |
| `tbl_estados_resumen` | Cobertura por estado | nombre_estado, con_imss, sin_derechohabiencia, total_poblacion |
| `tbl_acceso_resumen` | Distribucion por tipo de servicio | tipo_servicio, total |
| `tbl_escolaridad_resumen` | Cobertura segun nivel educativo | nivel_educativo, con_imss, sin_derechohabiencia, total |
| `tbl_grupos_edad_resumen` | Cobertura por grupo de edad | grupo_edad, con_imss, sin_derechohabiencia |
| `tbl_indigena_resumen` | Cobertura en poblacion indigena | habla_indigena, con_imss, sin_derechohabiencia, total |
| `tbl_urbano_resumen` | Cobertura urbana vs. rural | tipo_localidad, con_imss, sin_derechohabiencia, total |

### Medidas DAX creadas

```dax
% Sin Cobertura General =
DIVIDE(
    CALCULATE(SUM(tbl_acceso_resumen[total]),
        tbl_acceso_resumen[tipo_servicio] = "Sin derechohabiencia"),
    SUM(tbl_acceso_resumen[total])
) * 100

% Sin Cobertura Estado =
DIVIDE(SUM(tbl_estados_resumen[sin_derechohabiencia]),
       SUM(tbl_estados_resumen[total_poblacion])) * 100

% Sin Cobertura Escolaridad =
DIVIDE(SUM(tbl_escolaridad_resumen[sin_derechohabiencia]),
       SUM(tbl_escolaridad_resumen[total])) * 100

% Sin Cobertura Indígena =
DIVIDE(SUM(tbl_indigena_resumen[sin_derechohabiencia]),
       SUM(tbl_indigena_resumen[total])) * 100

% Sin Cobertura Urbano =
DIVIDE(SUM(tbl_urbano_resumen[sin_derechohabiencia]),
       SUM(tbl_urbano_resumen[total])) * 100
```

---

## Visualizaciones por Pagina

### Pagina 1 — Portada | KPIs
- 4 tarjetas KPI: Poblacion total, % sin derechohabiencia, % IMSS, Edad promedio
- Grafico de dona: distribucion por tipo de servicio (Sin derechohabiencia / IMSS / Otro)

### Pagina 2 — Analisis Geografico
- Segmentador (slicer) por estado
- Grafico de barras: ranking de estados por cobertura
- Tabla detallada por estado

### Pagina 3 — Factores Sociodemograficos
- Barras por nivel educativo vs. sin cobertura
- Barras por grupo de edad vs. sin cobertura
- Barras por poblacion indigena vs. sin cobertura
- Barras por tipo de localidad (urbana/rural) vs. sin cobertura

### Pagina 4 — Distribucion por Servicio
- Barras: estados con mayor poblacion sin cobertura
- Barras: top estados con IMSS
- Tabla comparativa por tipo de servicio

### Pagina 5 — Conclusiones
- 4 tarjetas KPI de resumen global
- Grafico de dona resumen
- Barras: top estados criticos

---

## Tema Visual

El reporte utiliza un tema oscuro personalizado (`PresentacionTheme`) con la siguiente paleta:

| Rol | Color |
|-----|-------|
| Fondo del canvas | `#0F1923` |
| Fondo de visuales | `#1A2535` |
| Bordes | `#2A3B52` |
| Acento principal (teal) | `#00C9A7` |
| Indicador neutro | `#F4A261` |
| Indicador negativo | `#E63946` |
| Texto secundario | `#94A3B8` |

---

## Como Abrir el Proyecto

1. Tener instalado **Power BI Desktop** (version febrero 2026 o superior con soporte PBIP)
2. Contar con SQL Server local con la base de datos `Defunciones_2000`
3. Abrir el archivo `presentacion.pbip` desde Power BI Desktop
4. Actualizar los datos para conectar con la fuente SQL

> Si no se tiene acceso al SQL Server local, los datos en cache (`cache.abf`) permiten visualizar el reporte sin conexion activa.
