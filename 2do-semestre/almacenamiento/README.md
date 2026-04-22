# Almacenamiento de Grandes Bases de Datos
**Semestre:** 2do | **Departamento:** DSI | **Créditos:** 7 | **Prerrequisito:** Procesamiento de Grandes Bases de Datos

Almacenamiento y consulta de Big Data usando Hadoop (MapReduce + HDFS) y Apache Hive. La infraestructura corre en Docker en el homelab.

## Tareas (`tareas/`)

### MapReduce
| # | Tarea | Estado |
|---|-------|--------|
| 1 | WordCount — Hadoop MapReduce sobre `warandpeace.txt` | ✅ Entregada |
| 2 | WordCount corregido + nube de palabras | ✅ Entregada |

### Hive
| # | Tarea | Estado |
|---|-------|--------|
| 1 | Instalación y configuración de Hive (ruta HDFS persistente, no /tmp) | ✅ Entregada |
| 2 | Importar archivos IMSS ASG 2025 a HDFS — tabla externa `empleo` | ✅ Entregada |
| 3 | Reorganizar en dos directorios + dos tablas externas (`empleo`, `empleo_enero`) | ✅ Entregada |
| 4 | Análisis de empleo en México — 4 consultas HiveQL + informe PDF | ✅ Entregada |
| 5 | Optimización en Hive — particionar `empleo` por mes (`mes=01` … `mes=06`) | ✅ Entregada |

### Tarea 4 — Consultas respondidas
1. Top 5 sectores económicos (4 dígitos SCIAN) por trabajadores asegurados — enero 2025
2. Top 2 rangos de edad entre asegurados en Jalisco — enero 2025
3. Top 3 entidades por mujeres aseguradas + top 5 sectores por entidad
4. Distribución por tamaño de empresa (Jalisco, Nuevo León, CDMX) con % del total

### Tarea 5 — Particionado
- HDFS reorganizado: 6 archivos planos → `/user/oem/empleo/mes=01/` … `mes=06/`
- Tabla `empleo` reconstruida como `EXTERNAL TABLE` con `PARTITIONED BY (mes STRING)`, delimitador `|`, `skip.header.line.count=1`
- 6 particiones registradas con `MSCK REPAIR TABLE empleo`
- Validación: `SUM(asegurados) GROUP BY cve_entidad WHERE mes='03'` → 32 entidades; CDMX (9) = 4,787,763

## Infraestructura

| Componente | Detalle |
|------------|---------|
| Hadoop | 3.3.6 / YARN · Docker (bde2020) |
| Hive | 2.3.2 + metastore PostgreSQL 9.6 |
| UI HDFS | `http://192.168.100.11:9870` |
| UI YARN | `http://192.168.100.11:8088` |
| HiveServer2 | `192.168.100.11:10000` (accesible vía Tailscale) |

```bash
# Conectar vía beeline
docker exec -i hive-server beeline -u 'jdbc:hive2://localhost:10000' --silent=true 2>/dev/null
```

## Datos en HDFS

| Ruta HDFS | Tabla Hive | Contenido |
|-----------|------------|-----------|
| `/user/oem/empleo/` | `empleo` | Semestre completo, particionado por mes (~25M registros, 6 particiones) |
| `/user/oem/empleo_enero/` | `empleo_enero` | Solo enero 2025 (~4.6M registros) |
| `/data/imss-asg-2025/` | — | Archivos originales — no modificar |

## Herramientas
Apache Hadoop 3.3.6 · Apache Hive 2.3.2 · HiveQL · beeline · Docker · Python (python-docx)
