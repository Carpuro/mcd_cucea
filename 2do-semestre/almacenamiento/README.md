# Almacenamiento de Grandes Bases de Datos

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Maestría:** Maestría en Ciencia de Datos (MCD) — CUCEA, Universidad de Guadalajara  
**Alumno:** Carlos Pulido Rosas  
**Semestre:** 2do | **Créditos:** 7 | **Prerrequisito:** Procesamiento de Grandes Bases de Datos

---

## Resumen de Actividades

| # | Módulo | Tema | Herramienta | Entregable | Estado |
|---|--------|------|-------------|------------|--------|
| 1 | MapReduce | WordCount sobre *War and Peace* | Hadoop 3.3.6 | PDF + resultado.txt | ✅ |
| 2 | MapReduce | WordCount corregido + nube de palabras | Hadoop + Python | PDF + nube.webp | ✅ |
| 3 | Hive | Instalación y configuración de Apache Hive | Docker + Hive 2.3.2 | PDF | ✅ |
| 4 | Hive | Análisis de empleo IMSS 2025 — 4 consultas HiveQL | HiveQL + beeline | PDF | ✅ |
| 5 | Hive | Optimización: particionado por mes (`mes=01`…`mes=06`) | HiveQL + HDFS | PDF | ✅ |
| 6 | Hive | Estrategia de optimización de Data Warehouse (análisis) | Python (docx) | PDF | ✅ |
| 7 | R | Instalación de paquetes `bigmemory` y `ff` | R 4.5.3 + RStudio | PDF | ✅ |

---

## Módulo 1 — Analítica con MapReduce

### Actividad 1 — WordCount con Hadoop
**Ruta:** `tareas/Actividades/Analitica con Map Reduce/Actividad 1/`

WordCount clásico ejecutado sobre el texto completo de *War and Peace* (Tolstói) usando Hadoop MapReduce sobre HDFS. Se documentó el proceso completo: carga del archivo, ejecución del job y lectura de resultados.

- **Archivo de entrada:** `warandpeace.txt`
- **Resultado:** `resultado.txt` — frecuencia de cada palabra en el corpus

### Actividad 2 — WordCount corregido + nube de palabras
**Ruta:** `tareas/Actividades/Analitica con Map Reduce/Actividad 2/`

Versión corregida del WordCount que filtra stopwords y signos de puntuación, generando un conteo más limpio. Se añadió visualización en forma de nube de palabras con las 100 palabras más frecuentes.

- **Resultado:** `resultado2.txt` + `nube_de_palabras.webp`

---

## Módulo 2 — Apache Hive

### Actividad 3 — Instalación y configuración de Hive
**Ruta:** `tareas/Actividades/Hive/Actividad 3/`

Instalación de Apache Hive 2.3.2 sobre Hadoop 3.3.6 en Docker Compose. Se configuró el metastore con PostgreSQL 9.6, se definió la ruta HDFS persistente `/user/oem/` y se verificó la conexión vía beeline.

**Stack Docker:**
```yaml
hive-server      # HiveServer2 — puerto 10000
hive-metastore   # Thrift metastore
hive-metastore-db  # PostgreSQL 9.6
hadoop-namenode  # HDFS NameNode — puerto 9870
hadoop-datanode
hadoop-resourcemanager  # YARN — puerto 8088
hadoop-nodemanager
```

### Actividad 4 — Análisis de empleo IMSS 2025
**Ruta:** `tareas/Actividades/Hive/Actividad 4/`

Carga de los datos abiertos de Asegurados IMSS (ASG 2025) en HDFS y ejecución de 4 consultas analíticas sobre ~4.6M registros de enero 2025. Los datos tienen 29 columnas delimitadas por pipe `|`.

**Consultas ejecutadas:**
1. Top 5 sectores económicos (4 dígitos SCIAN) por total de asegurados — enero 2025
2. Top 2 rangos de edad con más asegurados en Jalisco (cve_entidad = 14)
3. Top 3 entidades por mujeres aseguradas + top 5 sectores por entidad
4. Distribución por tamaño de patrón en Jalisco, Nuevo León y CDMX con % del total

**Tabla Hive:**
```sql
CREATE EXTERNAL TABLE empleo_enero (...)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/oem/empleo_enero/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

### Actividad 5 — Optimización: particionado por mes
**Ruta:** `tareas/Actividades/Hive/Actividad 5/`

Reorganización de los 6 archivos mensuales (enero–junio 2025, ~2.3 GB total) en estructura de particiones HDFS. La tabla se reconstruyó como `PARTITIONED BY (mes STRING)` para habilitar partition pruning.

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

**Validación:** `SUM(asegurados) GROUP BY cve_entidad WHERE mes='03'` → 32 entidades correctas.  
CDMX (cve=9): **4,787,763** asegurados en marzo 2025.

### Actividad 6 — Estrategia de optimización de Data Warehouse
**Ruta:** `tareas/Actividades/Hive/Actividad 6/`

Propuesta analítica (sin implementación) de una estrategia de optimización de DW para una agencia de investigación sobre calidad de empleo que consume datos IMSS. Las variables de análisis son: entidad federativa, sector económico (1 dígito SCIAN), rango salarial y sexo.

**Pilares de la estrategia:**
| Pilar | Descripción | Beneficio estimado |
|-------|-------------|-------------------|
| ORC + SNAPPY | Migrar de TEXTFILE a formato columnar | −74% volumen · −93% I/O por consulta |
| Clustering (32 buckets) | `CLUSTERED BY (cve_entidad, sector_1)` | Bucket pruning en filtros por entidad |
| Tablas de agregación | 3 vistas materializadas pre-calculadas | Consultas KPI < 1 segundo |
| Tez + vectorización | Motor DAG en memoria, bloques de 1,024 filas | −85% latencia vs MapReduce |

**Esquema estrella propuesto:** `fact_asegurados` + `dim_entidad`, `dim_sector`, `dim_salario`, `dim_sexo`, `dim_tiempo`.

---

## Módulo 3 — R para Grandes Datos

### Actividad 7 — Instalación de paquetes `bigmemory` y `ff`
**Ruta:** `tareas/Actividades/R/Actividad 7/`

Instalación y verificación de los dos principales paquetes de R para procesamiento de grandes volúmenes de datos en equipo local, usando **RStudio 2025.05.0** sobre R 4.5.3.

| Paquete | Versión | Estrategia | Descripción |
|---------|---------|------------|-------------|
| `bigmemory` | 4.6.4 | Memoria compartida | Matrices fuera del heap — acceso concurrente entre procesos R |
| `ff` | 4.5.2 | Memory-mapped files | Datos en disco accedidos como RAM vía paginación del SO |

**Instalación:**
```r
install.packages(c("bigmemory", "ff"), repos = "https://cran.rstudio.com/")
```

**Dependencias instaladas automáticamente:** `bigmemory.sri`, `Rcpp`, `uuid`, `BH`, `bit`

**Ejemplos verificados:**
```r
# bigmemory — matriz en memoria compartida
library(bigmemory)
bm <- big.matrix(nrow=1000, ncol=5, type="double", init=0)
# → Clase: big.matrix | Dimensiones: 1000 x 5

# ff — vector mapeado a disco
library(ff)
ffv <- ff(1:10000, filename=tempfile(fileext=".ff"), vmode="integer")
# → Longitud: 10000 | Tamaño en disco: 40,000 bytes (4 bytes × 10,000 enteros)
```

---

## Infraestructura del Homelab

| Componente | Versión | Acceso |
|------------|---------|--------|
| Hadoop NameNode | 3.3.6 | `http://homelab:9870` |
| YARN ResourceManager | 3.3.6 | `http://homelab:8088` |
| HiveServer2 | 2.3.2 | `homelab:10000` (vía Tailscale) |
| Metastore DB | PostgreSQL 9.6 | Interno Docker |
| Equipo | ThinkPad T14 Gen 4 | Docker Compose |
| R | 4.5.3 (2026-03-11 ucrt) | Windows 11 local |
| RStudio | 2025.05.0-496 | Windows 11 local |

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
| `/user/oem/empleo/mes=NN/` | `empleo` | Semestre completo particionado (~27.7M registros, 6 particiones) |
| `/user/oem/empleo_enero/` | `empleo_enero` | Solo enero 2025 (~4.6M registros) |

**Fuente:** [Datos Abiertos IMSS — Asegurados por Grupo de Edad y Sexo 2025](https://datos.imss.gob.mx/)  
**Formato:** CSV con delimitador `|`, 29 columnas, encabezado en primera fila
