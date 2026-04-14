# MCD — Almacenamiento de Grandes Bases de Datos

**Universidad de Guadalajara CUCEA · Maestría en Ciencias de los Datos · 2do Semestre 2026**

Stack: Hadoop 3.3.6 + Hive 2.3.2 + YARN — Docker en homelab (`192.168.100.11`)

---

## Actividades — Analítica con MapReduce

| # | Actividad | Descripción | Estado |
|---|---|---|---|
| 1 | WordCount | Implementación básica de WordCount en Hadoop MapReduce sobre `warandpeace.txt` | ✅ Entregada |
| 2 | WordCount Corregido | WordCount mejorado + nube de palabras | ✅ Entregada |

**Datos:** `warandpeace.txt` — War and Peace (Tolstói), usado como corpus para MapReduce.

---

## Tareas — Hive

| # | Tarea | Descripción | Estado |
|---|---|---|---|
| 1 | Instalación Hive | Instalación y configuración de Apache Hive 3.1.3; `hdfs-site.xml` con ruta persistente (no `/tmp`) | ✅ Entregada |
| 2 | Importar archivos IMSS | Archivos de asegurados IMSS 1er semestre 2025 → HDFS `/user/oem/empleo/`; tabla externa `empleo` en Hive | ✅ Entregada |
| 3 | Reorganizar archivos empleo | Dos directorios HDFS (semestre completo + solo enero); dos tablas externas correspondientes | ✅ Entregada |
| 4 | Análisis de Empleo en México | 4 consultas Hive + informe PDF con catálogos de dimensiones | ⏳ Pendiente |

### Tarea 4 — Preguntas

1. ¿Cuáles son los primeros 5 sectores económicos (4 dígitos) con mayor número de asegurados en enero 2025?
2. ¿Cuáles son los 2 primeros rangos de edad con mayor número de asegurados **urbanos en Jalisco** en enero 2025?
3. ¿Cuáles son las 3 entidades con mayor número de **mujeres aseguradas** en enero 2025 y en qué sectores económicos (4 dígitos) laboran?
4. ¿Cuál es el tamaño de empresas con mayor número de asegurados en Jalisco, Nuevo León y CDMX, y qué porcentaje representan del total en cada entidad?

Entregable: informe PDF con resultados y descripciones de los catálogos de cada dimensión.

---

## Infraestructura

| Componente | Detalle |
|---|---|
| Hadoop | 3.3.6 / YARN · Docker (bde2020) |
| Hive | 2.3.2 + PostgreSQL metastore |
| HDFS UI | `http://192.168.100.11:9870` |
| YARN UI | `http://192.168.100.11:8088` |
| HiveServer2 | `192.168.100.11:10000` |
| Config | `~/apps/hadoop/docker-compose.yml` + `hadoop.env` |

### Datos IMSS en HDFS

| Ruta HDFS | Tabla Hive | Contenido |
|---|---|---|
| `/user/oem/empleo/` | `empleo` | Semestre completo (~25M registros, 6 archivos) |
| `/user/oem/empleo_semestre/` | `empleo_semestre` | Semestre completo 2025 |
| `/user/oem/empleo_enero/` | `empleo_enero` | Solo enero 2025 (~4M registros) |

---

## Estructura del repositorio

```
Actividades/
  Analitica con Map Reduce/
    warandpeace.txt
    Actividad 1/   ← WordCount básico
    Actividad 2/   ← WordCount corregido + nube de palabras
  Hive/
    Actividad 3/   ← Instalación Hive (Tarea 1)
```
