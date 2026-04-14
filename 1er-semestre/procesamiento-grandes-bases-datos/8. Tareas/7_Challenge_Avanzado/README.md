# Challenge Avanzado: Predicción de Riesgo de Automatización Laboral en Jalisco

## Análisis de Big Data con PySpark y Machine Learning Avanzado

## 📋 Descripción del Proyecto

Este proyecto representa el **Challenge Avanzado** de la materia de Procesamiento de Grandes Bases de Datos y está **directamente relacionado con mi tesis de maestría**: *"Predicción de Riesgo de Automatización Laboral por IA en Jalisco, México (2025-2030)"*.

Utiliza **Apache Spark**, **Spark MLlib** y datos del **Banco Mundial** para construir modelos predictivos que evalúan el riesgo de automatización de diferentes ocupaciones en el estado de Jalisco, México.

## 🎯 Objetivos del Proyecto

### Objetivo General
Desarrollar un sistema de predicción avanzado usando PySpark y Spark MLlib para identificar ocupaciones vulnerables a la automatización por Inteligencia Artificial en Jalisco.

### Objetivos Específicos
1. **Integrar múltiples fuentes de datos** (Banco Mundial, O*NET, ENOE simulado)
2. **Construir modelos de Machine Learning** escalables y distribuidos
3. **Identificar sectores y ocupaciones** más vulnerables a la automatización
4. **Generar recomendaciones** de política pública basadas en datos
5. **Aplicar técnicas avanzadas** de Feature Engineering con PySpark

## 📊 Fuentes de Datos

### 1. Banco Mundial API (Datos Reales)
**Indicadores descargados:**
- Tasa de desempleo (% fuerza laboral)
- Fuerza laboral total
- Tasa de matriculación terciaria y secundaria
- Gasto en I+D (% PIB)
- Usuarios de Internet (% población)
- PIB per cápita (USD)
- Población total
- Empleo por sector (Industria, Servicios, Agricultura)

**Periodo:** 2010-2023  
**País:** México (código ISO: MX)  
**Total de registros:** 154 observaciones

### 2. Dataset Sintético de Ocupaciones
Basado en la estructura de **O*NET Database** y estadísticas de **ENOE México**:
- **50,335 registros** de trabajadores
- **38 ocupaciones** principales en Jalisco
- **12 sectores económicos**
- **Variables:** Salario, educación, habilidades, riesgo, experiencia, edad, etc.

### 3. Sectores Económicos Analizados
1. Tecnología e Informática
2. Manufactura (hub industrial de Jalisco)
3. Comercio y Servicios
4. Salud
5. Educación
6. Transporte y Logística
7. Construcción
8. Administración y Finanzas
9. Agricultura (tequila, agave)
10. Creatividad y Medios
11. Servicios Personales
12. Agricultura especializada

## 🛠️ Tecnologías y Herramientas

### Stack Tecnológico Principal
- **Apache Spark 3.5.6** - Motor de procesamiento distribuido
- **PySpark.Pandas (Koalas)** - API compatible con pandas
- **Spark MLlib** - Machine Learning escalable
- **Python 3.8+** - Lenguaje de programación

### Machine Learning
- **Random Forest Regressor** - Modelo ensemble
- **Gradient Boosting Trees** - Modelo de boosting
- **Linear Regression** - Baseline
- **VectorAssembler** - Ensamblaje de features
- **StandardScaler** - Normalización
- **CrossValidation** - Validación cruzada

### Visualización y Análisis
- **Matplotlib** - Gráficos estáticos
- **Seaborn** - Visualizaciones estadísticas
- **Plotly** - Gráficos interactivos
- **Pandas** - Análisis de datos
- **NumPy** - Operaciones numéricas

### APIs y Descarga de Datos
- **Banco Mundial API** - Indicadores económicos
- **Requests** - Cliente HTTP para APIs

## 🚀 Instalación y Ejecución

### 1. Requisitos Previos
```bash
# Python 3.8 o superior
python --version

# Java 8 o 11 (requerido por Apache Spark)
java -version
```

### 2. Crear Entorno Virtual (Recomendado)
```bash
# Crear entorno
conda create -n ai_automation_thesis python=3.8

# Activar entorno
conda activate ai_automation_thesis
```

### 3. Instalar Dependencias
```bash
# Apache Spark
pip install pyspark==3.5.0

# Librerías de análisis
pip install pandas numpy

# Visualización
pip install matplotlib seaborn plotly

# API y utilidades
pip install requests
```

**O usando requirements.txt:**
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el Notebook
```bash
# Jupyter Notebook
jupyter notebook AI_Automation_Risk_Jalisco.ipynb

# O JupyterLab
jupyter lab AI_Automation_Risk_Jalisco.ipynb

# O VS Code
code AI_Automation_Risk_Jalisco.ipynb
```

### 5. Configuración de Spark (Importante para Windows)

El notebook incluye configuración específica para Windows:
```python
spark = SparkSession.builder \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .master("local[*]") \
    .getOrCreate()
```

## 📈 Resultados del Análisis

### Rendimiento de Modelos

| Modelo | RMSE | MAE | R² Score |
|--------|------|-----|----------|
| **Random Forest** ⭐ | 0.1129 | 0.0903 | **0.7521** |
| Gradient Boosting | 0.1160 | 0.0925 | 0.7383 |
| Linear Regression | 0.1318 | 0.1070 | 0.6624 |

**🏆 Mejor Modelo:** Random Forest con R² = 0.7521

### Features Más Importantes

| Ranking | Feature | Importancia | Interpretación |
|---------|---------|-------------|----------------|
| 1 | **Creatividad** | 34.64% | Trabajos creativos tienen menor riesgo |
| 2 | **Trabajo Manual** | 25.96% | Mayor trabajo físico = mayor riesgo |
| 3 | **Nivel de Educación** | 14.61% | Mayor educación = menor riesgo |
| 4 | Educación × Tecnología | 9.60% | Interacción protectora |
| 5 | Índice de Adaptabilidad | 5.93% | Capacidad de cambio |

### Sectores Más Vulnerables en Jalisco

| Sector | % en Alto Riesgo | Trabajadores Afectados |
|--------|------------------|------------------------|
| **Transporte y Logística** | 61.4% | ~2,945 |
| **Agricultura** | 50.9% | ~1,475 |
| **Comercio** | 49.1% | ~2,367 |
| **Servicios** | 47.9% | ~1,298 |
| **Manufactura** | 42.2% | ~3,092 |
| **Construcción** | 40.1% | ~1,523 |

**Total en Alto Riesgo:** ~12,700 trabajadores en el dataset

### Top 10 Ocupaciones con Mayor Riesgo Predicho

1. **Conductor de Transporte** - Riesgo: 83.2%
2. **Cajero** - Riesgo: 83.0%
3. **Operador de Maquinaria** - Riesgo: 80.8%
4. **Agricultor** - Riesgo: 79.4%
5. **Almacenista** - Riesgo: 79.1%
6. **Mesero** - Riesgo: 79.0%
7. **Ensamblador Electrónico** - Riesgo: 77.9%
8. **Albañil** - Riesgo: 75.5%
9. **Vendedor** - Riesgo: 70.7%
10. **Asistente Administrativo** - Riesgo: 66.4%

### Ocupaciones Más Protegidas

1. **Profesor Universitario** - Riesgo: ~18%
2. **Médico General** - Riesgo: ~15%
3. **Desarrollador de Software** - Riesgo: ~25%
4. **Analista de Datos** - Riesgo: ~30%
5. **Diseñador Gráfico** - Riesgo: ~40%

## 💡 Hallazgos Clave

### 1. Factores de Protección
- ✅ **Educación superior** reduce riesgo en ~45%
- ✅ **Creatividad** es el factor más protector (34.6% importancia)
- ✅ **Capacitación reciente** reduce riesgo en ~25%
- ✅ **Uso de tecnología** mejora empleabilidad futura

### 2. Factores de Riesgo
- ⚠️ **Rutinidad de tareas** aumenta riesgo significativamente
- ⚠️ **Trabajo manual repetitivo** es altamente vulnerable
- ⚠️ **Baja educación** (< 5 años) correlaciona con riesgo >70%
- ⚠️ **Falta de capacitación** en últimos 2 años

### 3. Impacto por Sector
- **Manufactura:** Hub industrial de Jalisco con 7,323 trabajadores analizados
- **Tecnología:** Sector más protegido (solo 0.08% en alto riesgo)
- **Transporte:** Sector más vulnerable (61.4% en riesgo)

### 4. Relación Educación-Riesgo
- **Educación Básica (0-3):** Riesgo promedio 81.2%
- **Educación Media (3-5):** Riesgo promedio 71.7%
- **Educación Media-Superior (5-7):** Riesgo promedio 52.1%
- **Educación Superior (7-10):** Riesgo promedio 35.0%

## 🎯 Recomendaciones de Política Pública

### Para el Gobierno de Jalisco

**1. Programas de Capacitación Prioritarios**
- Habilidades digitales básicas para sectores de alto riesgo
- Programación y análisis de datos para reconversión laboral
- Creatividad y resolución de problemas complejos
- Gestión de tecnologías emergentes (IA, IoT, Automatización)

**2. Inversión en Educación**
- Aumentar matriculación en educación terciaria en áreas STEM
- Fortalecer educación técnica y vocacional
- Programas de educación continua para trabajadores adultos
- Becas para reconversión laboral en ocupaciones vulnerables

**3. Sectores Prioritarios para Intervención**
- **Transporte:** 2,945 trabajadores en riesgo (61.4%)
- **Comercio:** 2,367 trabajadores en riesgo (49.1%)
- **Manufactura:** 3,092 trabajadores en riesgo (42.2%)

**4. Fondo de Transición Laboral**
- Apoyo económico durante reconversión
- Subsidios para capacitación certificada
- Incentivos a empresas que retengan y capaciten empleados

### Para Empresas

1. **Planificar transición tecnológica responsable**
   - No solo automatizar para reducir costos
   - Crear roles híbridos humano-máquina
   
2. **Invertir en reskilling de empleados actuales**
   - Programas de capacitación interna
   - Mentoría y actualización profesional
   
3. **Aprovechar subsidios gubernamentales**
   - Incentivos fiscales por capacitación
   - Apoyo en adopción de tecnología

### Para Trabajadores

1. **Invertir en educación continua**
   - Especialmente en áreas STEM y digitales
   - Cursos en línea (Coursera, edX, Platzi)
   
2. **Desarrollar habilidades complementarias**
   - Creatividad, liderazgo, comunicación
   - Pensamiento crítico y resolución de problemas
   
3. **Adaptarse a tecnologías**
   - Aprender herramientas digitales del sector
   - Familiarizarse con IA y automatización
   
4. **Considerar reconversión si en alto riesgo**
   - Transición a ocupaciones relacionadas pero más protegidas
   - Aprovechar experiencia previa

## 📊 Visualizaciones Generadas

### 1. Riesgo por Sector (viz_1_riesgo_por_sector.png)
Comparación entre riesgo real vs predicho por sector económico.

### 2. Educación vs Riesgo (viz_2_educacion_vs_riesgo.png)
Scatter plot mostrando relación inversa entre educación y riesgo.

### 3. Feature Importance (viz_3_feature_importance.png)
Importancia de cada característica en el modelo Random Forest.

### 4. Comparación de Modelos (viz_4_comparacion_modelos.png)
Métricas de rendimiento (RMSE y R²) de los tres modelos.

### 5. Top Ocupaciones en Riesgo (viz_5_top_ocupaciones_riesgo.html)
Gráfico interactivo con Plotly de las 10 ocupaciones más vulnerables.

## 🔬 Metodología

### 1. Descarga y Preparación de Datos
```python
# API del Banco Mundial
indicadores = ['SL.UEM.TOTL.ZS', 'IT.NET.USER.ZS', ...]
df_bm = descargar_indicador_bm(indicador, pais='MX')

# Dataset sintético basado en O*NET y ENOE
df_ocupaciones = generar_dataset_ocupaciones()
```

### 2. Feature Engineering con PySpark
```python
# Crear features derivados
df_spark.withColumn('indice_tecnologia', ...)
df_spark.withColumn('indice_adaptabilidad', ...)
df_spark.withColumn('empleabilidad_futura', ...)
```

### 3. Pipeline de Machine Learning
```python
# Pipeline de Spark MLlib
pipeline = Pipeline(stages=[
    VectorAssembler(...),
    StandardScaler(...),
    RandomForestRegressor(...)
])
```

### 4. Entrenamiento y Evaluación
- División 80/20 (train/test)
- 3 modelos comparados
- Métricas: RMSE, MAE, R²
- Feature importance analysis

## 📚 Referencias Académicas

### Datasets y Fuentes
1. **Banco Mundial** - Indicadores de Desarrollo Mundial  
   https://data.worldbank.org/

2. **O*NET Database** - Occupational Information Network  
   https://www.onetcenter.org/

3. **ENOE** - Encuesta Nacional de Ocupación y Empleo, INEGI México  
   https://www.inegi.org.mx/programas/enoe/

### Investigación Académica
1. Frey, C. B., & Osborne, M. A. (2013). *The future of employment: How susceptible are jobs to computerisation?*

2. Arntz, M., Gregory, T., & Zierahn, U. (2016). *The risk of automation for jobs in OECD countries*.

3. Autor, D. H., & Dorn, D. (2013). *The growth of low-skill service jobs and the polarization of the US labor market*.

### Documentación Técnica
- **Apache Spark Documentation:** https://spark.apache.org/docs/latest/
- **Spark MLlib Guide:** https://spark.apache.org/docs/latest/ml-guide.html
- **PySpark.Pandas API:** https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/

## 👨‍💻 Autor

**Carlos**
- **Institución:** Universidad de Guadalajara - CUCEA
- **Programa:** Maestría en Data Science
- **Tesis:** Predicción de Riesgo de Automatización Laboral por IA en Jalisco, México (2025-2030)
- **Correo:** [tu correo]
- **GitHub:** [tu usuario]

## 🎓 Contexto Académico

Este proyecto forma parte del **Challenge Avanzado** de la materia de Big Data con Apache Spark y está **directamente relacionado con mi investigación de tesis** sobre el impacto de la Inteligencia Artificial en el mercado laboral de Jalisco.

### Relación con la Tesis

**Tema de Tesis:** *Predicción de Riesgo de Automatización Laboral por IA en Jalisco, México (2025-2030)*

**Aplicaciones del Challenge:**
1. ✅ Metodología de análisis con PySpark escalable
2. ✅ Modelos predictivos de riesgo de automatización
3. ✅ Identificación de ocupaciones y sectores vulnerables
4. ✅ Feature engineering para variables laborales
5. ✅ Visualizaciones para presentación de resultados
6. ✅ Base para recomendaciones de política pública

## 📝 Licencia

Este proyecto es de carácter académico desarrollado para la Maestría en Data Science de la Universidad de Guadalajara.

Los datos del Banco Mundial están bajo licencia **CC BY 4.0**.

## ⚠️ Limitaciones del Estudio

### Datos
- Dataset de ocupaciones es **sintético** (basado en patrones reales pero simulado)
- No incluye datos reales completos de ENOE 2024
- Enfoque específico en Jalisco puede no generalizarse a otros estados

### Metodología
- Modelo asume condiciones relativamente estables
- No incluye factores macroeconómicos cambiantes
- Tecnología evoluciona más rápido que la capacidad predictiva

### Técnicas
- No se implementó Spark Streaming (planeado para tesis)
- Validación cruzada simplificada
- Hyperparameter tuning básico

## 🔮 Trabajo Futuro

### Para la Tesis
1. Integrar datos reales de ENOE 2023-2024
2. Implementar Spark Streaming para análisis en tiempo real
3. Expandir a otros estados de México (comparación regional)
4. Incluir modelos de impacto económico regional
5. Desarrollar dashboard interactivo con Streamlit/Dash

### Mejoras Técnicas
1. CrossValidator con Grid Search más exhaustivo
2. Ensemble methods avanzados (Stacking, Voting)
3. Deep Learning con TensorFlow on Spark
4. Análisis de series temporales para tendencias
5. Integración con APIs de vacantes laborales (Indeed, LinkedIn)

## 📧 Contacto

Para preguntas, comentarios o colaboraciones relacionadas con este proyecto o la tesis:

- **Email:** [tu email]
- **LinkedIn:** [tu perfil]
- **GitHub:** [tu repositorio]

---

**Universidad de Guadalajara - CUCEA**  
**Maestría en Data Science**  
**Challenge Avanzado - Big Data con Apache Spark**

**Fecha de creación:** Noviembre 2025  
**Última actualización:** Noviembre 2025  
**Versión:** 1.0  
---

## 📊 Resumen Ejecutivo
```
====================================================================
PREDICCIÓN DE RIESGO DE AUTOMATIZACIÓN LABORAL EN JALISCO
====================================================================

📊 DATOS PROCESADOS:
  • Total de registros: 50,335
  • Ocupaciones: 38
  • Sectores: 12
  • Features: 12

🤖 MODELOS:
  • Random Forest: R² = 0.7521 ⭐
  • Gradient Boosting: R² = 0.7383
  • Linear Regression: R² = 0.6624

🔑 TOP FEATURES:
  1. Creatividad (34.64%)
  2. Trabajo Manual (25.96%)
  3. Nivel Educación (14.61%)

⚠️ SECTORES VULNERABLES:
  • Transporte: 61.4% en riesgo
  • Agricultura: 50.9% en riesgo
  • Comercio: 49.1% en riesgo

====================================================================
```