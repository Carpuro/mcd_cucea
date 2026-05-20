# Almacenamiento de Grandes Bases de Datos

**Materia:** Almacenamiento de Grandes Bases de Datos
**Maestría:** Maestría en Ciencia de Datos (MCD) — CUCEA, Universidad de Guadalajara
**Alumno:** Carlos Pulido Rosas
**Semestre:** 2do | **Créditos:** 7 | **Prerrequisito:** Procesamiento de Grandes Bases de Datos

---

## Resumen de Actividades

| # | Módulo | Tema | Herramienta | Entregable |
|---|--------|------|-------------|------------|
| 1 | Configuración | Descarga de aplicativos para Linux Mint | — | — |
| 2 | Hadoop | Instalación de Hadoop | Docker | — |
| 3 | MapReduce | WordCount sobre *War and Peace* | Hadoop 3.3.6 | PDF + resultado.txt |
| 4 | MapReduce | WordCount corregido + nube de palabras | Hadoop + Python | PDF + nube.webp |
| 5 | Hive | Instalación y configuración de Apache Hive | Docker + Hive 2.3.2 | PDF |
| 6 | Hive | Importar archivos IMSS ASG 2025 a HDFS | HDFS CLI + beeline | — |
| 7 | Hive | Reorganizar archivos IMSS en HDFS | HDFS CLI + HiveQL | — |
| 8 | Hive | Análisis de empleo IMSS 2025 — 4 consultas HiveQL | HiveQL + beeline | PDF |
| 9 | Hive | Optimización: particionado por mes | HiveQL + HDFS | PDF |
| 10 | Hive | Estrategia de optimización de Data Warehouse | Python (python-docx) | PDF |
| 11 | R | Instalación de paquetes `bigmemory` y `ff` | R 4.5.3 + RStudio | PDF |
| 12 | R | Construcción de modelos con BigData (WLS + Logístico) | Python / statsmodels | PDF |

---

## Módulo 1 — Configuración del entorno

### Actividad 1 — Descarga de aplicativos para Linux Mint
**Ruta:** `tareas/Actividad 1/`

Descarga de la imagen ISO de Linux Mint y aplicativos necesarios para montar el entorno base del curso.

### Actividad 2 — Instalación de Hadoop
**Ruta:** `tareas/Actividad 2/`

Instalación y configuración de Apache Hadoop en entorno Docker Compose.
La configuración final vive en el homelab: `~/apps/hadoop/docker-compose.yml` + `hadoop.env`.

**Stack Docker:**
```yaml
hadoop-namenode      # HDFS NameNode — puerto 9870
hadoop-datanode
hadoop-resourcemanager  # YARN — puerto 8088
hadoop-nodemanager
```

---

## Módulo 2 — Analítica con MapReduce

### Actividad 3 — WordCount con Hadoop
**Ruta:** `tareas/Actividad 3/`

WordCount clásico ejecutado sobre el texto completo de *War and Peace* (Tolstói) usando Hadoop MapReduce sobre HDFS. Se documentó el proceso completo: carga del archivo, ejecución del job y lectura de resultados.

- **Archivo de entrada:** `warandpeace.txt`
- **Resultado:** `resultado.txt` — frecuencia de cada palabra en el corpus

### Actividad 4 — WordCount corregido + nube de palabras
**Ruta:** `tareas/Actividad 4/`

Versión corregida del WordCount que filtra stopwords y signos de puntuación, generando un conteo más limpio. Se añadió visualización en forma de nube de palabras con las 100 palabras más frecuentes.

- **Resultado:** `resultado2.txt` + `nube_de_palabras.webp`

---

## Módulo 3 — Apache Hive

### Actividad 5 — Instalación y configuración de Hive
**Ruta:** `tareas/Actividad 5/`

Instalación de Apache Hive 2.3.2 sobre Hadoop 3.3.6 en Docker Compose. Se configuró el metastore con PostgreSQL 9.6, se definió la ruta HDFS persistente `/user/oem/` y se verificó la conexión vía beeline.

**Stack Docker completo:**
```yaml
hive-server           # HiveServer2 — puerto 10000
hive-metastore        # Thrift metastore
hive-metastore-db     # PostgreSQL 9.6
hadoop-namenode       # HDFS NameNode — puerto 9870
hadoop-datanode
hadoop-resourcemanager  # YARN — puerto 8088
hadoop-nodemanager
```

### Actividad 6 — Importar archivos IMSS a HDFS
**Ruta:** `tareas/Actividad 6/`

Carga de los datos abiertos de Asegurados IMSS (ASG 2025) en HDFS.
Tabla externa `empleo_enero` creada en `/user/oem/empleo_enero/` (~4.6M registros, enero 2025).

```sql
CREATE EXTERNAL TABLE empleo_enero (...)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/oem/empleo_enero/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

### Actividad 7 — Reorganizar archivos en HDFS
**Ruta:** `tareas/Actividad 7/`

Reorganización de HDFS en dos directorios con dos tablas externas independientes:

| Ruta HDFS | Tabla Hive | Descripción |
|-----------|------------|-------------|
| `/user/oem/empleo_semestre/` | `empleo_semestre` | Semestre completo (~25M registros) |
| `/user/oem/empleo_enero/` | `empleo_enero` | Solo enero 2025 (~4.6M registros) |

### Actividad 8 — Análisis de empleo IMSS 2025
**Ruta:** `tareas/Actividad 8/`

4 consultas analíticas sobre los datos IMSS enero 2025 (~4.6M registros):

1. Top 5 sectores económicos (4 dígitos SCIAN) por total de asegurados
2. Top 2 rangos de edad con más asegurados en Jalisco (cve_entidad=14)
3. Top 3 entidades por mujeres aseguradas + top 5 sectores por entidad
4. Distribución por tamaño de patrón en Jalisco, Nuevo León y CDMX con % del total

### Actividad 9 — Optimización: particionado por mes
**Ruta:** `tareas/Actividad 9/`

Reorganización de los 6 archivos mensuales (enero–junio 2025, ~2.3 GB) en estructura de particiones HDFS. Tabla reconstruida como `PARTITIONED BY (mes STRING)` para habilitar partition pruning.

**Estructura HDFS resultante:**
```
/user/oem/empleo/
├── mes=01/  asg-2025-01-31.csv  (385 MB)
├── mes=02/  asg-2025-02-28.csv  (382 MB)
├── mes=03/  asg-2025-03-31.csv  (382 MB)
├── mes=04/  asg-2025-04-30.csv  (378 MB)
├── mes=05/  asg-2025-05-31.csv  (383 MB)
└── mes=06/  asg-2025-06-30.csv  (383 MB)
```

**Validación:** CDMX (cve=9): **4,787,763** asegurados en marzo 2025.

### Actividad 10 — Estrategia de optimización de Data Warehouse
**Ruta:** `tareas/Actividad 10/`

Propuesta analítica de estrategia de optimización de DW para una agencia de investigación sobre calidad de empleo que consume datos IMSS (variables: entidad, sector 1 dígito SCIAN, rango salarial, sexo).

| Pilar | Descripción | Beneficio estimado |
|-------|-------------|-------------------|
| ORC + SNAPPY | Migrar de TEXTFILE a formato columnar | −74% volumen · −93% I/O |
| Clustering (32 buckets) | `CLUSTERED BY (cve_entidad, sector_1)` | Bucket pruning en filtros |
| Tablas de agregación | Vistas materializadas pre-calculadas | KPIs < 1 segundo |
| Tez + vectorización | Motor DAG en memoria, bloques de 1,024 filas | −85% latencia vs MapReduce |

**Esquema estrella:** `fact_asegurados` + `dim_entidad`, `dim_sector`, `dim_salario`, `dim_sexo`, `dim_tiempo`.

---

## Módulo 4 — R para Grandes Datos

### Actividad 11 — Instalación de paquetes `bigmemory` y `ff`
**Ruta:** `tareas/Actividad 11/`

Instalación y verificación en R 4.5.3 / RStudio 2025.05.0 sobre Windows 11.

| Paquete | Versión | Estrategia |
|---------|---------|------------|
| `bigmemory` | 4.6.4 | Memoria compartida — matrices fuera del heap, acceso concurrente |
| `ff` | 4.5.2 | Memory-mapped files — datos en disco accedidos como RAM |

```r
install.packages(c("bigmemory", "ff"), repos = "https://cran.rstudio.com/")
```

### Actividad 12 — Construcción de modelos con BigData
**Ruta:** `tareas/Actividad 12/`

Dos modelos de regresión sobre el dataset IMSS ASG abril 2026 (7.4M trabajadores urbanos):

**Modelo 1 — Regresión Lineal Ponderada (WLS)**
- Fórmula: `sal_num ~ edad + edad² + C(entidad) + C(tamano) + edad:C(tamano)`
- R²=0.079 · F=7,433 · Pico salarial a los 49.8 años
- Empresas grandes (S6/S7) valorizan la experiencia más que microempresas

**Modelo 2 — Regresión Logística Ponderada (GLM Binomial)**
- Fórmula: `sal_alto ~ C(entidad) + C(sector) + mujer`  (umbral = W3, percentil 75)
- AUC=0.610 · OR_mujer=0.703 — mujeres con 30% menos odds de salario alto
- Umbral óptimo Youden=0.408 → Sens=39.9%, Spec=75.3%

**Entregables:** `generar_reporte.py` · 6 gráficas · PDF con 9 referencias APA

---

## Infraestructura del Homelab

| Componente | Versión | Acceso |
|------------|---------|--------|
| Hadoop NameNode | 3.3.6 | `http://homelab:9870` |
| YARN ResourceManager | 3.3.6 | `http://homelab:8088` |
| HiveServer2 | 2.3.2 | `homelab:10000` (vía Tailscale) |
| Metastore DB | PostgreSQL 9.6 | Interno Docker |
| R | 4.5.3 (2026-03-11 ucrt) | Windows 11 local |
| RStudio | 2025.05.0 | Windows 11 local |

```bash
# Conectar a Hive vía beeline
docker exec -i hive-server beeline \
  -u 'jdbc:hive2://localhost:10000' \
  --silent=true 2>/dev/null

# SSH al homelab (Tailscale)
ssh carpuro@100.64.0.11
```

## Datos IMSS en HDFS

| Ruta HDFS | Tabla Hive | Descripción |
|-----------|------------|-------------|
| `/user/oem/empleo/mes=NN/` | `empleo` | Semestre completo particionado (~27.7M registros) |
| `/user/oem/empleo_enero/` | `empleo_enero` | Solo enero 2025 (~4.6M registros) |

**Fuente:** [Datos Abiertos IMSS — Asegurados por Grupo de Edad y Sexo 2025](https://datos.imss.gob.mx/)
**Formato:** CSV con delimitador `|`, 29 columnas, encabezado en primera fila
