# Almacenamiento de Grandes Bases de Datos
**Semester:** 2nd | **Department:** DSI | **Credits:** 7 | **Pre-req:** Procesamiento de Grandes Bases de Datos

Big Data storage and querying using Hadoop (MapReduce + HDFS) and Apache Hive. Infrastructure runs on Docker in homelab.

## Tasks (`tareas/`)

### MapReduce
| # | Task | Status |
|---|------|--------|
| 1 | WordCount — Hadoop MapReduce over `warandpeace.txt` | ✅ Done |
| 2 | WordCount corrected + word cloud visualization | ✅ Done |

### Hive
| # | Task | Status |
|---|------|--------|
| 1 | Hive installation and configuration (persistent HDFS path, not /tmp) | ✅ Done |
| 2 | Import IMSS ASG 2025 files to HDFS — external table `empleo` | ✅ Done |
| 3 | Reorganize into two directories + two external tables (`empleo`, `empleo_enero`) | ✅ Done |
| 4 | Employment analysis — 4 HiveQL queries + PDF report (navy/amber template) | ✅ Done |
| 5 | Hive optimization — partition `empleo` by month (`mes=01` … `mes=06`) | ✅ Done |

### Tarea 4 — Queries answered
1. Top 5 economic sectors (4-digit SCIAN) by insured workers — January 2025
2. Top 2 age ranges among insured workers in Jalisco — January 2025
3. Top 3 states by female insured workers + top 5 sectors per state
4. Employer size distribution (Jalisco, Nuevo León, CDMX) with % of total

### Tarea 5 — Partitioning
- Reorganized HDFS: 6 flat files → `/user/oem/empleo/mes=01/` … `mes=06/`
- Rebuilt `empleo` as `EXTERNAL TABLE` with `PARTITIONED BY (mes STRING)`, delimiter `|`, `skip.header.line.count=1`
- 6 partitions registered via `MSCK REPAIR TABLE empleo`
- Validation: `SUM(asegurados) GROUP BY cve_entidad WHERE mes='03'` → 32 entities; CDMX (9) = 4,787,763

## Infrastructure

| Component | Detail |
|-----------|--------|
| Hadoop | 3.3.6 / YARN · Docker (bde2020) |
| Hive | 2.3.2 + PostgreSQL 9.6 metastore |
| HDFS UI | `http://192.168.100.11:9870` |
| YARN UI | `http://192.168.100.11:8088` |
| HiveServer2 | `192.168.100.11:10000` (Tailscale accessible) |

```bash
# Connect via beeline
docker exec -i hive-server beeline -u 'jdbc:hive2://localhost:10000' --silent=true 2>/dev/null
```

## HDFS Data

| HDFS Path | Hive Table | Content |
|-----------|------------|---------|
| `/user/oem/empleo/` | `empleo` | Full semester, partitioned by month (~25M records, 6 partitions) |
| `/user/oem/empleo_enero/` | `empleo_enero` | January 2025 only (~4.6M records) |
| `/data/imss-asg-2025/` | — | Original files — do not modify |

## Tools
Apache Hadoop 3.3.6 · Apache Hive 2.3.2 · HiveQL · beeline · Docker · Python (python-docx)
