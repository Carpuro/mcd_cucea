# Actividad 4 — Análisis de Empleo IMSS 2025 con HiveQL

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Módulo:** Apache Hive  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Apache Hive 2.3.2 · HiveQL · beeline

## Objetivo

Cargar los datos abiertos de Asegurados al IMSS (ASG 2025) en HDFS y responder 4 preguntas analíticas sobre el empleo formal en México usando HiveQL.

## Datos

- **Fuente:** [Datos Abiertos IMSS — ASG 2025](https://datos.imss.gob.mx/)
- **Archivo:** `asg-2025-01-31.csv` — enero 2025
- **Registros:** ~4.6 millones
- **Columnas:** 29 campos separados por `|`
- **Ruta HDFS:** `/user/oem/empleo_enero/`

## Tabla Hive

```sql
CREATE EXTERNAL TABLE empleo_enero (
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
  -- ... 29 columnas total
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/oem/empleo_enero/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

## Consultas y Hallazgos

### Q1 — Top 5 sectores económicos (4 dígitos SCIAN) por asegurados

```sql
SELECT sector_economico_4,
       SUM(CAST(asegurados AS BIGINT)) AS total
FROM empleo_enero
GROUP BY sector_economico_4
ORDER BY total DESC
LIMIT 5;
```

### Q2 — Top 2 rangos de edad en Jalisco (cve_entidad = 14)

```sql
SELECT rango_edad,
       SUM(CAST(asegurados AS BIGINT)) AS total
FROM empleo_enero
WHERE cve_entidad = '14'
GROUP BY rango_edad
ORDER BY total DESC
LIMIT 2;
```

### Q3 — Top 3 entidades por mujeres aseguradas

```sql
SELECT cve_entidad,
       SUM(CAST(asegurados AS BIGINT)) AS total_mujeres
FROM empleo_enero
WHERE sexo = '2'
GROUP BY cve_entidad
ORDER BY total_mujeres DESC
LIMIT 3;
```

### Q4 — Distribución por tamaño de patrón (Jalisco, Nuevo León, CDMX)

```sql
SELECT cve_entidad, tamano_patron,
       SUM(CAST(asegurados AS BIGINT)) AS total,
       ROUND(SUM(CAST(asegurados AS BIGINT)) * 100.0 /
             SUM(SUM(CAST(asegurados AS BIGINT))) OVER (PARTITION BY cve_entidad), 2) AS pct
FROM empleo_enero
WHERE cve_entidad IN ('9','14','19')
GROUP BY cve_entidad, tamano_patron;
```

## Generación del reporte

```bash
python3 generar_reporte.py
```

Genera `Actividad_Hive_Tarea4_CarlosPulidoRosas.docx` usando el template MCD CUCEA y lo convierte a PDF con LibreOffice.

## Entregable

`Actividad_Hive_Tarea4_CarlosPulidoRosas.pdf`
