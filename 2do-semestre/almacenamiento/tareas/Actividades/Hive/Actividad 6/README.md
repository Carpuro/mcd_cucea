# Actividad 6 — Estrategia de Optimización de Data Warehouse

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Alumno:** Carlos Pulido Rosas  
**Tipo:** Propuesta analítica (sin implementación)

## Pregunta central

> ¿Cómo podría implementarse una estrategia de optimización del Data Warehouse para una agencia de investigación sobre calidad de empleo que consume los datos abiertos de asegurados del IMSS 2025?

## Variables de análisis de la agencia

| Dimensión | Descripción | Cardinalidad |
|-----------|-------------|--------------|
| Entidad federativa | 32 estados de la república | 32 valores |
| Sector económico | 1 dígito SCIAN | 11 sectores |
| Rango salarial | Tramos salariales | 10 tramos |
| Sexo | Masculino / Femenino | 2 valores |

## Estrategia propuesta — 4 pilares

### 1. Migración TEXTFILE → ORC + SNAPPY
```sql
CREATE TABLE fact_asegurados (
  cve_entidad    TINYINT,
  sector_1       TINYINT,
  rango_salarial TINYINT,
  sexo           TINYINT,
  asegurados     INT,
  masa_sal_ta    BIGINT
)
PARTITIONED BY (mes TINYINT)
CLUSTERED BY (cve_entidad, sector_1) INTO 32 BUCKETS
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');
```
**Impacto:** −74% volumen en disco · −93% I/O por consulta analítica

### 2. Tablas de agregación pre-calculadas
```sql
-- Tendencia mensual por entidad y sector
CREATE TABLE agg_entidad_sector_mes STORED AS ORC AS
SELECT mes, cve_entidad, sector_1,
       SUM(asegurados) AS total_asegurados,
       SUM(masa_sal_ta) AS masa_salarial
FROM fact_asegurados
GROUP BY mes, cve_entidad, sector_1;
```
**Impacto:** Consultas KPI < 1 segundo (vs 120–180 segundos en tabla base)

### 3. Motor Tez + vectorización
```sql
SET hive.execution.engine               = tez;
SET hive.vectorized.execution.enabled   = true;
SET hive.auto.convert.join              = true;  -- broadcast join automático
```
**Impacto:** −85% latencia en consultas OLAP vs MapReduce

### 4. Esquema estrella
```
fact_asegurados
├── dim_entidad    (32 filas)
├── dim_sector     (11 filas)
├── dim_salario    (10 filas)
├── dim_sexo       (2 filas)
└── dim_tiempo     (6–12 filas/año)
```

## Estimación de impacto

| Métrica | Estado actual | Estado objetivo | Mejora |
|---------|--------------|-----------------|--------|
| Volumen semestral | ~2.3 GB | ~600 MB | −74% |
| I/O por consulta | 100% columnas | ~7% columnas | −93% |
| Latencia por entidad+sector | 60–90 seg | 5–10 seg | −85% |
| Consulta KPI nacional | 120–180 seg | <1 seg | −99% |

## Generación del reporte

```bash
python3 generar_reporte.py
```

## Entregable

`Actividad_DW_Tarea6_CarlosPulidoRosas.pdf`
