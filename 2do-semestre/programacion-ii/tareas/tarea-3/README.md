# Practica Orange — Historia de Datos: Acceso a la Salud en Mexico

**Materia:** Programacion II  
**Maestria:** Maestria en Ciencia de Datos (MCD) — CUCEA, Universidad de Guadalajara  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Orange Data Mining (via Anaconda, entorno `MCD`)  
**Archivo:** `Actividad_IMSS.ows`  

---

## Pregunta central

> **¿Que patrones existen en el acceso a la salud en Mexico, y es posible predecir o agrupar a la poblacion segun su nivel de cobertura?**

---

## Conexion a datos

Todos los flujos se conectan a la base de datos **`Defunciones_2000`** en SQL Server local usando `pyodbc` dentro de nodos **Python Script**:

```python
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Defunciones_2000;'
    'Trusted_Connection=yes;'
)
```

Los datos se convierten a objetos `Orange.data.Table` con `Domain` definido manualmente para que Orange los reconozca como variables continuas, discretas o de texto (metas).

---

## Flujo del Workflow

El archivo `.ows` contiene **4 historias de datos** independientes ejecutadas en paralelo:

---

### Historia 1 — Distribucion por Tipo de Servicio

**Nodos:** Python Script → Data Table → Bar Plot

**Tabla:** `tbl_acceso_resumen`  
**SQL:** `SELECT tipo_servicio, total FROM tbl_acceso_resumen`

**Que hace:**
- Calcula el porcentaje de cada tipo de servicio sobre el total
- Variables creadas: `total`, `porcentaje`, `tipo_servicio`
- Etiqueta legible por registro: `"7.0M\n65.7%"`

**Visualizacion:** Bar Plot con `total` en eje Y, agrupado por `tipo_servicio`

**Hallazgo:** El tipo "Sin derechohabiencia" concentra la mayor parte de la poblacion (~65%), confirmando la brecha de cobertura.

---

### Historia 2 — Cobertura por Estado y Region

**Nodos:** Python Script → Data Table → Bar Plot  
**Ademas:** Python Script → Distances (Euclidiana) → Hierarchical Clustering

**Tabla:** `tbl_estados_resumen`  
**SQL:** `SELECT nombre_estado, con_imss, sin_derechohabiencia, total_poblacion FROM tbl_estados_resumen`

**Que hace:**
- Calcula `pct_sin_cobertura` y `pct_con_imss` por estado
- Asigna una region geografica a cada estado (Noroeste, Noreste, Occidente, Centro-Norte, Centro, Golfo, Suroeste, Sureste)
- Ordena estados de mayor a menor porcentaje sin cobertura
- El nombre del estado va como `StringVariable` en metas para usarlo como etiqueta/anotacion

**Visualizaciones:**
- **Bar Plot**: estados en eje X, `pct_sin_cobertura` en eje Y, coloreado por region
- **Hierarchical Clustering**: agrupa estados por similitud en sus porcentajes de cobertura usando distancia Euclidiana

**Hallazgo:** Los estados del Suroeste (Chiapas, Oaxaca, Guerrero) presentan los porcentajes mas altos de poblacion sin cobertura; los del Noroeste y Centro tienen mayor cobertura IMSS.

---

### Historia 3 — Brecha Urbana vs. Rural

**Nodos:** Python Script → Data Table → Bar Plot

**Tabla:** `tbl_urbano_resumen`  
**SQL:** `SELECT tipo_localidad, con_imss, sin_derechohabiencia, total FROM tbl_urbano_resumen WHERE tipo_localidad NOT LIKE '%especificado%'`

**Que hace:**
- Filtra localidades sin clasificacion valida
- Calcula `pct_sin_cobertura` y `pct_con_imss` por tipo de localidad (rural / urbana / mixta)
- `tipo_localidad` como variable discreta

**Visualizacion:** Bar Plot comparando porcentajes entre tipos de localidad

**Hallazgo:** Las localidades rurales tienen significativamente menor cobertura que las urbanas, evidenciando la brecha de acceso por tipo de localidad.

---

### Historia 4 — Machine Learning: Clustering y Arbol de Decision

Esta historia aplica dos tecnicas de aprendizaje automatico:

#### 4a. K-Means Clustering de Estados

**Nodos:** Python Script → k-Means (k=3) → Box Plot + Scatter Plot + Data Table

**Tabla:** `tbl_estados_resumen`  
**Variables:** `pct_imss`, `pct_sin_cobertura`, `estado`

**Configuracion de k-Means:**
- k = 3 clusters
- Normalizacion activada
- max_iterations = 300, n_init = 10

**Visualizaciones:**
- **Box Plot**: distribucion de `pct_sin_cobertura` por cluster
- **Scatter Plot**: eje X = `pct_imss`, eje Y = `pct_sin_cobertura`, coloreado por cluster, etiquetado por estado
- **Data Table**: tabla con asignacion de cluster y silhouette por estado

**Hallazgo:** Los estados se agrupan en 3 perfiles bien diferenciados:
- Cluster 1: alta cobertura IMSS, baja sin cobertura (norte industrial)
- Cluster 2: cobertura media (estados del centro)
- Cluster 3: muy baja cobertura, alta sin derechohabiencia (sur/suroeste)

#### 4b. Arbol de Decision (Prediccion de Cobertura)

**Nodos:** Python Script → Tree (max_depth=3) → Tree Viewer

**Tabla:** `defunciones` (tabla original, 100,000 registros)  
**SQL:**
```sql
SELECT TOP 100000
    CAST(ENT AS INT) AS ENT,
    CAST(SEXO AS INT) AS SEXO,
    CAST(EDAD AS INT) AS EDAD,
    NOTIEDER
FROM defunciones
WHERE EDAD NOT IN ('999', '')
  AND SEXO IN ('1', '2')
  AND ENT IS NOT NULL
```

**Variables:**
- Features: `estado` (ENT), `sexo`, `edad`
- Target: `cobertura` — `'Sin cobertura'` si NOTIEDER = '5', `'Con cobertura'` en otro caso

**Configuracion del arbol:**
- Profundidad maxima: 3
- Min. hoja: 2 instancias
- Min. nodo interno: 5 instancias
- Mayoria suficiente: 95%

**Visualizacion:** Tree Viewer — arbol interactivo con nodos coloreados por clase

**Hallazgo:** El modelo de arbol de decision logra separar los grupos usando principalmente la edad y el estado como variables predictoras de la cobertura medica.

---

## Resumen del Workflow

| Historia | Datos | Tecnica | Visualizacion |
|----------|-------|---------|---------------|
| 1. Distribucion por servicio | `tbl_acceso_resumen` | Agregacion | Bar Plot |
| 2. Cobertura por estado | `tbl_estados_resumen` | Clustering jerarquico | Bar Plot + Dendrograma |
| 3. Brecha urbana-rural | `tbl_urbano_resumen` | Comparacion | Bar Plot |
| 4a. Perfiles de estados | `tbl_estados_resumen` | K-Means (k=3) | Scatter Plot + Box Plot |
| 4b. Prediccion de cobertura | `defunciones` (100k rows) | Arbol de decision | Tree Viewer |

---

## Como Ejecutar

1. Tener **Orange** instalado en el entorno `MCD` de Anaconda:
   ```
   conda activate MCD
   orange-canvas
   ```
2. Abrir `Actividad_IMSS.ows` desde Orange
3. Tener SQL Server local con la base `Defunciones_2000` activa
4. Ejecutar cada nodo Python Script — los demas se actualizan automaticamente

---

## Conclusion de la Historia

El analisis en Orange revela que la falta de derechohabiencia en Mexico no es uniforme: tiene una dimension **geografica** (sur vs. norte), **territorial** (rural vs. urbano) y **demografica** (edad, sexo). Mediante clustering se identifican 3 perfiles de estados con patrones de cobertura distintos, y mediante un arbol de decision se puede predecir con cierta precision si una persona tiene o no cobertura medica a partir de su estado, edad y sexo.
