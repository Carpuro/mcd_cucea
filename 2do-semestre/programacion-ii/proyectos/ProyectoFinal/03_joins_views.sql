-- ============================================================
-- Proyecto Final — Programacion II | MCD CUCEA 2026-A
-- Autor: Carlos Pulido Rosas
-- Descripcion: Consultas JOIN y creacion de VIEW analitica
--              sobre el riesgo de automatizacion en Jalisco
-- Base de datos: Defunciones_2000 (SQL Server)
-- ============================================================

USE Defunciones_2000;
GO

-- ============================================================
-- JOIN 1 — INNER JOIN
-- Pregunta de tesis: ¿Que porcentaje de trabajadores en Jalisco
-- tiene datos de tareas O*NET disponibles (crosswalk completo)?
-- Se usa INNER JOIN porque solo nos interesan los registros con
-- coincidencia en ambas tablas (trabajadores CON ocupacion mapeada).
-- ============================================================
SELECT
    o.occupation_name                           AS ocupacion,
    o.sector,
    o.frey_osborne_score                        AS riesgo_frey_osborne,
    t.escoacum                                  AS nivel_educativo,
    t.ingocup                                   AS ingreso_mensual,
    t.formalidad,
    t.edad
FROM dbo.trabajadores t
INNER JOIN dbo.ocupaciones_onet o
    ON t.sinco_code = o.sinco_code
ORDER BY o.frey_osborne_score DESC;
GO

-- ============================================================
-- JOIN 2 — LEFT JOIN
-- Pregunta de tesis: ¿Que ocupaciones quedan sin cobertura O*NET
-- (sin crosswalk SOC→SINCO completo)?
-- Se usa LEFT JOIN para conservar TODOS los trabajadores, incluso
-- los que no tienen ocupacion mapeada en O*NET — precisamente
-- los mas vulnerables del sector informal y agropecuario.
-- ============================================================
SELECT
    t.id_trabajador,
    t.sinco_code,
    t.scian_sector,
    t.formalidad,
    o.occupation_name                           AS ocupacion_onet,
    o.frey_osborne_score                        AS riesgo,
    CASE
        WHEN o.sinco_code IS NULL THEN 'Sin crosswalk O*NET'
        ELSE 'Mapeado'
    END                                         AS estado_cobertura
FROM dbo.trabajadores t
LEFT JOIN dbo.ocupaciones_onet o
    ON t.sinco_code = o.sinco_code
ORDER BY estado_cobertura, t.scian_sector;
GO

-- ============================================================
-- JOIN 3 — INNER JOIN + GROUP BY + HAVING
-- Pregunta de tesis: ¿Que sectores economicos concentran el mayor
-- riesgo promedio de automatizacion en Jalisco?
-- Se agrega GROUP BY para consolidar por sector y HAVING para
-- filtrar solo sectores con muestra representativa (>= 20 trab).
-- ============================================================
SELECT
    o.sector,
    COUNT(t.id_trabajador)                      AS total_trabajadores,
    ROUND(AVG(o.frey_osborne_score), 4)         AS riesgo_promedio,
    ROUND(AVG(t.ingocup), 2)                    AS ingreso_promedio,
    ROUND(AVG(CAST(t.escoacum AS FLOAT)), 2)    AS educacion_promedio,
    SUM(CASE WHEN t.formalidad = 'Informal'
             THEN 1 ELSE 0 END)                 AS trabajadores_informales
FROM dbo.trabajadores t
INNER JOIN dbo.ocupaciones_onet o
    ON t.sinco_code = o.sinco_code
GROUP BY o.sector
HAVING COUNT(t.id_trabajador) >= 20
ORDER BY riesgo_promedio DESC;
GO

-- ============================================================
-- VIEW: vista_riesgo_jalisco
-- Consolida el perfil completo del trabajador (variables
-- socioeconomicas ENOE + descriptores de tareas O*NET) en una
-- sola consulta lista para Orange y Python.
-- Incluye campo calculado riesgo_categoria (CASE WHEN).
-- ============================================================
IF OBJECT_ID('dbo.vista_riesgo_jalisco', 'V') IS NOT NULL
    DROP VIEW dbo.vista_riesgo_jalisco;
GO

CREATE VIEW dbo.vista_riesgo_jalisco AS
SELECT
    t.id_trabajador,
    t.escoacum                                  AS nivel_educativo,
    t.ingocup                                   AS ingreso_mensual,
    t.scian_sector                              AS sector,
    t.formalidad,
    t.edad,
    t.tamanio_empresa,
    -- IRA: Indice de Rentabilidad de la Automatizacion (Acemoglu & Restrepo 2018)
    -- IRA = ingocup_anual / activo_fijo_amortizado_5_anios por sector
    -- IRA > 1 → salario supera costo de automatizar → incentivo economico real
    t.ira,
    o.occupation_name                           AS ocupacion,
    o.frey_osborne_score,
    o.rti,
    o.cognitive_demand,
    o.social_interaction,
    o.creativity,
    o.automation_risk,
    CASE
        WHEN o.frey_osborne_score >= 0.7 THEN 'Alto'
        WHEN o.frey_osborne_score >= 0.4 THEN 'Medio'
        ELSE 'Bajo'
    END                                         AS riesgo_categoria
FROM dbo.trabajadores t
INNER JOIN dbo.ocupaciones_onet o
    ON t.sinco_code = o.sinco_code;
GO

-- Verificar la vista
SELECT TOP 10 * FROM dbo.vista_riesgo_jalisco ORDER BY frey_osborne_score DESC;
GO

PRINT 'JOINs y VIEW creados exitosamente';
GO
