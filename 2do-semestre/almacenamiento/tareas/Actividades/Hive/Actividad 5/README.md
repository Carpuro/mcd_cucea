# Actividad 5 — Optimización en Hive: Particionado por Mes

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Apache Hive 2.3.2 · HDFS · HiveQL

## Objetivo

Reorganizar los 6 archivos mensuales IMSS ASG 2025 en HDFS con la convención de directorios `mes=NN` que Hive utiliza para partition pruning, y reconstruir la tabla `empleo` como tabla externa particionada.

## Estructura HDFS

**Antes:**
```
/user/oem/empleo/
├── asg-2025-01-31.csv  (385 MB)
├── asg-2025-02-28.csv  (382 MB)
├── asg-2025-03-31.csv  (382 MB)
├── asg-2025-04-30.csv  (378 MB)
├── asg-2025-05-31.csv  (383 MB)
└── asg-2025-06-30.csv  (383 MB)
```

**Después:**
```
/user/oem/empleo/
├── mes=01/  asg-2025-01-31.csv  (385 MB)
├── mes=02/  asg-2025-02-28.csv  (382 MB)
├── mes=03/  asg-2025-03-31.csv  (382 MB)
├── mes=04/  asg-2025-04-30.csv  (378 MB)
├── mes=05/  asg-2025-05-31.csv  (383 MB)
└── mes=06/  asg-2025-06-30.csv  (383 MB)
```

**Total:** ~2.3 GB · ~27.7 millones de registros · 6 particiones

## Comandos HDFS

```bash
# Crear directorios de partición
for mes in 01 02 03 04 05 06; do
  docker exec hadoop-namenode hdfs dfs -mkdir -p /user/oem/empleo/mes=${mes}
done

# Mover archivos
docker exec hadoop-namenode hdfs dfs \
  -mv /user/oem/empleo/asg-2025-01-31.csv /user/oem/empleo/mes=01/
# ... repetir para cada mes
```

## DDL Hive

```sql
DROP TABLE IF EXISTS empleo;

CREATE EXTERNAL TABLE empleo (
  cve_delegacion     STRING,
  cve_subdelegacion  STRING,
  cve_entidad        STRING,
  sector_economico_1 STRING,
  sector_economico_4 STRING,
  tamano_patron      STRING,
  sexo               STRING,
  rango_edad         STRING,
  rango_salarial     STRING,
  asegurados         STRING,
  masa_sal_ta        STRING
  -- ... 29 columnas
)
PARTITIONED BY (mes STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/oem/empleo/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Registrar particiones detectadas en HDFS
MSCK REPAIR TABLE empleo;
```

## Validación

```sql
-- Verificar 6 particiones registradas
SHOW PARTITIONS empleo;
-- mes=01, mes=02, mes=03, mes=04, mes=05, mes=06

-- Consulta de prueba con partition pruning
SELECT cve_entidad,
       SUM(CAST(asegurados AS BIGINT)) AS total_asegurados
FROM empleo
WHERE mes = '03'
GROUP BY cve_entidad
ORDER BY total_asegurados DESC;
-- → 32 filas (una por entidad federativa)
-- → CDMX (9): 4,787,763 asegurados en marzo 2025
```

## Beneficio del particionado

Al filtrar `WHERE mes='03'`, Hive lee **únicamente** los 382 MB de marzo en lugar de los 2.3 GB del semestre completo — reducción del 83% en datos leídos.

## Generación del reporte

```bash
python3 generar_reporte.py
```

## Entregable

`Actividad_Hive_Tarea5_CarlosPulidoRosas.pdf`
