# Challenge Intermedio: Predicción de Calidad de Vino con Spark MLlib

## 📋 Descripción

Este proyecto implementa un sistema completo de **Machine Learning distribuido** utilizando **Apache Spark MLlib** para predecir la calidad del vino basándose en características fisicoquímicas. El análisis utiliza el **Wine Quality Dataset** del UCI Machine Learning Repository.

## 🎯 Objetivos

- Descargar y procesar datos usando **PySpark.Pandas (Koalas)**
- Implementar y comparar **3 modelos de clasificación** con Spark MLlib
- Evaluar rendimiento con múltiples métricas
- Identificar las características más importantes para la calidad del vino
- Documentar y visualizar resultados de forma profesional

## 📊 Dataset

**Fuente:** [UCI ML Repository - Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality)

**Características:**
- **6,497 muestras** de vino (4,898 blancos + 1,599 tintos)
- **11 features fisicoquímicas:** acidez, azúcar residual, cloruros, sulfatos, pH, alcohol, etc.
- **Variable objetivo:** Calidad del vino (escala 0-10)
- **Clasificación:** 3 categorías (Baja: 3-5, Media: 6, Alta: 7-9)

## 🛠️ Tecnologías Utilizadas

### Frameworks y Librerías
- **Apache Spark 3.5+** - Procesamiento distribuido
- **PySpark.Pandas (Koalas)** - Manipulación de datos con sintaxis pandas
- **Spark MLlib** - Machine Learning distribuido
- **ucimlrepo** - API para descargar datasets de UCI

### Visualización y Análisis
- **Matplotlib & Seaborn** - Visualizaciones
- **Pandas** - Análisis exploratorio
- **NumPy** - Operaciones numéricas


## 🚀 Instalación y Uso

### 1. Requisitos Previos
```bash
# Python 3.8+
python --version

# Java 8 o 11 (requerido por Spark)
java -version
```

### 2. Instalar Dependencias
```bash
pip install pyspark==3.5.0
pip install pandas matplotlib seaborn
pip install ucimlrepo
pip install numpy
```

### 3. Ejecutar el Notebook
```bash
jupyter notebook Wine_Quality_ML.ipynb
```

**O usar VS Code / JupyterLab:**
```bash
code Wine_Quality_ML.ipynb
```

### 4. Ejecutar Celdas Secuencialmente

⚠️ **Importante:** Ejecutar las celdas en orden para evitar errores de dependencias.

## 🤖 Modelos Implementados

### 1. Regresión Logística
- **Tipo:** Clasificación lineal multiclase
- **Parámetros:** maxIter=100, regParam=0.01
- **Ventajas:** Interpretable, rápido
- **Desventajas:** Asume relaciones lineales

### 2. Random Forest
- **Tipo:** Ensemble de árboles de decisión
- **Parámetros:** numTrees=100, maxDepth=10
- **Ventajas:** Alta precisión, maneja no-linealidad
- **Desventajas:** Más lento, menos interpretable

### 3. Decision Tree
- **Tipo:** Árbol de decisión único
- **Parámetros:** maxDepth=10
- **Ventajas:** Muy interpretable, rápido
- **Desventajas:** Propenso a overfitting

## 📈 Resultados Esperados

### Métricas de Rendimiento

| Modelo | Accuracy | F1-Score | Precision | Recall |
|--------|----------|----------|-----------|--------|
| Regresión Logística | ~0.56 | ~0.56 | ~0.57 | ~0.56 |
| Random Forest | ~0.66 | ~0.66 | ~0.67 | ~0.66 |
| Decision Tree | ~0.58 | ~0.58 | ~0.58 | ~0.58 |

*Nota: Resultados pueden variar debido a la división aleatoria train/test*

### Top 3 Features Más Importantes

1. **Alcohol** (~19%) - Mayor contenido de alcohol → Mayor calidad
2. **Volatile Acidity** (~12%) - Menor acidez volátil → Mayor calidad
3. **Density** (~8%) - Menor densidad → Mayor calidad

## 📊 Visualizaciones Generadas

1. **Distribución de Calidad** - Histograma de clases
2. **Matriz de Correlación** - Relaciones entre features
3. **Features vs Quality** - Boxplots comparativos
4. **Comparación de Modelos** - Métricas de rendimiento
5. **Feature Importance** - Importancia de características

## 🔍 Proceso de Machine Learning

### 1. Descarga de Datos
```python
from ucimlrepo import fetch_ucirepo
wine_quality = fetch_ucirepo(id=186)
```

### 2. Preprocesamiento
- Conversión a PySpark.Pandas
- Limpieza de valores nulos
- Creación de categorías de calidad
- Normalización de features

### 3. Pipeline de Spark MLlib
```
StringIndexer → VectorAssembler → StandardScaler → Classifier
```

### 4. Entrenamiento y Evaluación
- División 80/20 (train/test)
- Entrenamiento de 3 modelos
- Evaluación con métricas múltiples
- Comparación de resultados

## 💡 Conclusiones Clave

### Hallazgos Principales
- **Alcohol** es el predictor más importante de calidad
- **Random Forest** logra mejor rendimiento (~67% accuracy)
- Dataset desbalanceado: mayoría de vinos son calidad "Media"
- Características fisicoquímicas pueden predecir calidad razonablemente bien

### Recomendaciones para Mejorar

**Modelo:**
- Implementar balanceo de clases (SMOTE)
- Usar CrossValidator para hyperparameter tuning
- Crear features de interacción (ej: alcohol × sulphates)
- Probar ensemble methods

**Producción:**
- Guardar modelo con `model.save()`
- Implementar monitoreo de drift
- Validar con datos de otras regiones

**Negocio:**
- Productores deben controlar alcohol y acidez volátil
- Modelo puede ahorrar tiempo en evaluación sensorial
- Identificar vinos problemáticos temprano

## 📚 Referencias

- **Dataset:** Cortez et al. (2009). Modeling wine preferences by data mining from physicochemical properties. Decision Support Systems.
- **Documentación Spark MLlib:** https://spark.apache.org/docs/latest/ml-guide.html
- **UCI ML Repository:** https://archive.ics.uci.edu/

## 👨‍💻 Autor

**Carlos Pulido Rosas**
- Maestría en Ciencia de los Datos - Universidad de Guadalajara (CUCEA)
- Challenge Intermedio - Procesamiento de Grandes Bases de Datos

## 📝 Licencia

Este proyecto utiliza el Wine Quality Dataset bajo licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

## ⚠️ Notas Importantes

### Para Usuarios de Windows
- Asegúrate de tener Java instalado correctamente
- Configura `JAVA_HOME` en variables de entorno
- El notebook incluye configuración específica para Windows

### Troubleshooting Común

**Error: Py4JJavaError**
- Solución: Verificar instalación de Java y configuración de Spark

**Error: Module 'ucimlrepo' not found**
- Solución: `pip install ucimlrepo`

**Error: Pandas display en Koalas**
- Solución: Usar `.to_pandas()` antes de mostrar DataFrames

## 📧 Contacto

Para preguntas o comentarios sobre este proyecto, contactar a través del repositorio de GitHub.

---

**Fecha de creación:** Noviembre 2025  
**Última actualización:** Noviembre 2025  
**Versión:** 1.0