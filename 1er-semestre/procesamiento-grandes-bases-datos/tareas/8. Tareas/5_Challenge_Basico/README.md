# Challenge Básico: Análisis Global de Terrorismo con PySpark.Pandas

## 📋 Descripción

Este proyecto realiza un **análisis exploratorio exhaustivo** de la **Global Terrorism Database (GTD)** utilizando **PySpark.Pandas (Koalas API)** para procesar más de 180,000 registros de ataques terroristas desde 1970 hasta 2017.

## 🎯 Objetivos

- Familiarizarse con **PySpark.Pandas (Koalas)** para Big Data
- Analizar patrones temporales y geográficos del terrorismo global
- Identificar grupos terroristas más activos y tipos de ataques
- Generar visualizaciones significativas sobre tendencias globales
- Practicar manipulación de grandes datasets con sintaxis pandas

## 📊 Dataset

**Fuente:** [Global Terrorism Database (GTD)](https://www.kaggle.com/datasets/START-UMD/gtd)  
**Institución:** START - University of Maryland

**Características:**
- **181,691+ registros** de ataques terroristas (1970-2017)
- **135 columnas** con información detallada
- **Cobertura global:** Todos los continentes
- **Tamaño:** ~155 MB
- **Variables:** Fecha, ubicación, tipo de ataque, armas, víctimas, grupos responsables, objetivos

## 🛠️ Tecnologías Utilizadas

### Frameworks Core
- **Apache Spark 3.5+** - Motor de procesamiento distribuido
- **PySpark.Pandas (Koalas)** - API compatible con pandas para Spark
- **KaggleHub** - Descarga automatizada de datasets

### Visualización
- **Matplotlib** - Gráficos estáticos
- **Seaborn** - Visualizaciones estadísticas
- **Pandas** - Conversión para display


## 🚀 Instalación y Uso

### 1. Requisitos Previos
```bash
# Python 3.8 o superior
python --version

# Java 8 o 11 (requerido por Apache Spark)
java -version
```

### 2. Instalar Dependencias
```bash
# Instalar PySpark
pip install pyspark==3.5.0

# Instalar librerías de visualización
pip install pandas matplotlib seaborn

# Instalar KaggleHub para descarga de datos
pip install kagglehub

# Otras dependencias
pip install numpy
```

### 3. Configurar Kaggle (Opcional)

Si usas la API de Kaggle en lugar de KaggleHub:
```bash
pip install kaggle

# Colocar kaggle.json en:
# Linux/Mac: ~/.kaggle/kaggle.json
# Windows: C:\Users\<usuario>\.kaggle\kaggle.json
```

### 4. Ejecutar el Notebook
```bash
jupyter notebook GTD_Analysis_Koalas.ipynb
```

**O con JupyterLab:**
```bash
jupyter lab GTD_Analysis_Koalas.ipynb
```

## 📈 Análisis Realizados

### 1. Análisis Temporal
- Evolución de ataques año por año (1970-2017)
- Identificación de años con mayor actividad terrorista
- Tendencias de víctimas a lo largo del tiempo
- Análisis por décadas

### 2. Análisis Geográfico
- Distribución de ataques por región mundial
- Top 20 países más afectados
- Heatmap de ataques por década y región
- Patrones geográficos de terrorismo

### 3. Análisis de Tipos de Ataque
- Distribución de métodos de ataque
- Tipos de objetivos más comunes
- Armas más utilizadas
- Letalidad promedio por tipo de arma

### 4. Análisis de Grupos Terroristas
- Top 20 grupos más activos
- Total de víctimas por grupo
- Patrones de actividad por grupo

### 5. Análisis de Características
- Tasa de éxito de ataques
- Comparación ataques suicidas vs no suicidas
- Impacto en víctimas

## 📊 Hallazgos Principales

### Evolución Temporal
- **Incremento dramático** post-2000, especialmente 2011-2017
- **Años más violentos:** 2014-2017 (conflictos en Medio Oriente)
- **Brecha de datos:** 1993 no tiene registros

### Distribución Geográfica
- **Regiones más afectadas:**
  1. Medio Oriente y Norte de África (~50,000 ataques)
  2. Sur de Asia (~40,000 ataques)
  3. América del Sur (~15,000 ataques)

- **Países más afectados:**
  1. Iraq (~25,000 ataques)
  2. Afganistán (~15,000 ataques)
  3. Pakistán (~14,000 ataques)

### Tipos de Ataque
- **Bombardeos/Explosivos:** ~50% de todos los ataques
- **Ataques armados:** ~30% de ataques
- **Ataques suicidas:** Más letales en promedio

### Grupos Terroristas
- **Más activos:** Taliban, ISIS, Boko Haram, FMLN, Shining Path
- Muchos ataques sin atribución definitiva (~40%)

## 🎨 Visualizaciones Generadas

### 1. Evolución Temporal (Dual)
- Gráfico de línea: Número de ataques por año
- Gráfico de línea: Víctimas totales por año

### 2. Top 15 Países
- Gráfico de barras horizontales con conteo de ataques

### 3. Tipos de Ataque
- Pie chart con distribución porcentual

### 4. Ataques por Región
- Gráfico de barras con totales por región

### 5. Top 15 Grupos Terroristas
- Barras horizontales dual (ataques + víctimas)

### 6. Heatmap Década-Región
- Mapa de calor mostrando intensidad de ataques

### 7. Letalidad por Arma
- Barras horizontales con promedio de víctimas

## 💻 Uso de PySpark.Pandas (Koalas)

### ¿Qué es Koalas?
**PySpark.Pandas** (anteriormente Koalas) es una API que permite usar **sintaxis de pandas** con el **poder distribuido de Apache Spark**.

### Ventajas
- ✅ Sintaxis familiar de pandas
- ✅ Procesamiento distribuido automático
- ✅ Escalable a datasets de TB
- ✅ Conversión fácil entre pandas y Spark

### Ejemplo de Uso
```python
import pyspark.pandas as ps

# Cargar datos (distribuido)
df = ps.read_csv('globalterrorismdb.csv')

# Operaciones familiares de pandas
df.groupby('region_txt').agg({
    'eventid': 'count',
    'nkill': 'sum'
}).sort_values('eventid', ascending=False)

# Convertir a pandas cuando sea necesario
df_pandas = df.to_pandas()
```

## 🔍 Código de Ejemplo

### Análisis de Ataques por Año
```python
# Usando PySpark.Pandas (Koalas)
ataques_por_año = df_clean.groupby('iyear').agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum',
    'total_casualties': 'sum'
}).rename(columns={
    'eventid': 'num_ataques',
    'nkill': 'total_muertos',
    'nwound': 'total_heridos',
    'total_casualties': 'total_victimas'
}).sort_index()

# Mostrar resultados
print(ataques_por_año.head(10).to_pandas())
```

## 📚 Referencias

- **GTD Official Website:** https://www.start.umd.edu/gtd/
- **Dataset en Kaggle:** https://www.kaggle.com/datasets/START-UMD/gtd
- **Documentación PySpark.Pandas:** https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/
- **Codebook GTD:** https://www.start.umd.edu/gtd/downloads/Codebook.pdf

## 👨‍💻 Autor

**Carlos Pulido Rosas**
- Maestría en Data Science - Universidad de Guadalajara (CUCEA)
- Challenge Básico - Procesamiento de Grandes Bases de Datos

## 📝 Licencia

El Global Terrorism Database (GTD) es mantenido por el National Consortium for the Study of Terrorism and Responses to Terrorism (START) en la University of Maryland.

**Citación:**
> National Consortium for the Study of Terrorism and Responses to Terrorism (START). (2018). Global Terrorism Database [Data file]. Retrieved from https://www.start.umd.edu/gtd

## ⚠️ Notas Importantes

### Limitaciones del Dataset
- Brecha de datos en 1993
- Criterios de inclusión específicos (violencia con objetivo político)
- No incluye actos de terrorismo de estado
- Puede tener sesgos de reporte geográfico

### Consideraciones Técnicas

**Para Windows:**
- Configurar `HADOOP_HOME` si es necesario
- Usar `.to_pandas()` antes de mostrar resultados
- El notebook incluye configuración específica para Windows

**Memoria:**
- Dataset completo ~155MB, cabe en memoria
- PySpark.Pandas útil para practicar Big Data
- Para datasets >10GB, usar cluster de Spark



## 🐛 Troubleshooting

### Error: Py4JJavaError
**Causa:** Problemas con workers de Spark en Windows  
**Solución:** Usar `.to_pandas()` antes de mostrar DataFrames

### Error: KeyError en columnas
**Causa:** Ejecutar celdas fuera de orden  
**Solución:** Ejecutar celdas secuencialmente desde el inicio

### Error: Memory issues
**Causa:** Intentar cargar todo el dataset en memoria  
**Solución:** Usar operaciones lazy de Koalas, evitar `.to_pandas()` prematuro

## 📧 Contacto

Preguntas o comentarios: Abrir issue en el repositorio de GitHub

---

**Fecha de creación:** Noviembre 2025  
**Última actualización:** Noviembre 2025  
**Versión:** 1.0  