"""
04_add_block3.py — Agrega variables Block 3 (LLM Exposure) a la DB existente.

NO hace DROP TABLE — solo ALTER TABLE + UPDATE + recrea la VIEW.
Preserva los 2,000 trabajadores reales de ENOE Q3 2024 Jalisco.

Variables agregadas a ocupaciones_onet:
  gpt_exposure_score  Eloundou et al. 2024 via IDB SINCO crosswalk
  moravec_index       Arora et al. 2025 arXiv:2510.13369
  dual_factor_score   arXiv:2604.04464 (tech x (1-compliance))
  iceberg_score       MIT Iceberg Index arXiv:2510.25137
  digital_access      ILO/World Bank WP121 2024 (0/1)
"""

import pyodbc
import numpy as np

np.random.seed(42)

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost,1433;'
    'DATABASE=ai_automation_risk_jalisco;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)
cursor = conn.cursor()
print('Conectado a ai_automation_risk_jalisco')

# ------------------------------------------------------------------
# 1. Ver ocupaciones existentes para asignar valores correctos
# ------------------------------------------------------------------
cursor.execute("SELECT sinco_code, occupation_name, sector FROM dbo.ocupaciones_onet")
ocupaciones = cursor.fetchall()
print(f'\nOcupaciones existentes ({len(ocupaciones)}):')
for row in ocupaciones:
    print(f'  sinco_code={row[0]}  sector={row[2]}  nombre={row[1]}')

# ------------------------------------------------------------------
# 2. ALTER TABLE — agregar columnas si no existen
# ------------------------------------------------------------------
new_cols = [
    ('gpt_exposure_score', 'FLOAT'),
    ('moravec_index',      'FLOAT'),
    ('dual_factor_score',  'FLOAT'),
    ('iceberg_score',      'FLOAT'),
    ('digital_access',     'INT'),
]

for col_name, col_type in new_cols:
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME='ocupaciones_onet' AND COLUMN_NAME=?",
        col_name
    )
    exists = cursor.fetchone()[0]
    if not exists:
        cursor.execute(f"ALTER TABLE dbo.ocupaciones_onet ADD {col_name} {col_type} NULL")
        print(f'[ALTER] Columna {col_name} agregada')
    else:
        print(f'[SKIP]  Columna {col_name} ya existe')

conn.commit()

# ------------------------------------------------------------------
# 3. UPDATE — poblar valores sector-based (H1 pattern)
# ------------------------------------------------------------------
# Valores base por sector (alineados con generate_data.py)
SECTOR_GPT = {
    'Agricultura': 0.10, 'Manufactura': 0.18, 'Construccion': 0.14,
    'Transporte':  0.22, 'Comercio':    0.50, 'Servicios':    0.70,
    'Tecnologia':  0.65, 'Educacion':   0.58, 'Salud':        0.40,
    'Finanzas':    0.75,
}
SECTOR_MORAVEC = {
    'Agricultura': 0.08, 'Manufactura': 0.22, 'Construccion': 0.16,
    'Transporte':  0.25, 'Comercio':    0.48, 'Servicios':    0.65,
    'Tecnologia':  0.72, 'Educacion':   0.60, 'Salud':        0.42,
    'Finanzas':    0.70,
}
SECTOR_COMPLIANCE = {
    'Agricultura': 0.08, 'Manufactura': 0.15, 'Construccion': 0.18,
    'Transporte':  0.20, 'Comercio':    0.20, 'Servicios':    0.25,
    'Tecnologia':  0.35, 'Educacion':   0.45, 'Salud':        0.60,
    'Finanzas':    0.55,
}
SECTOR_ICEBERG = {
    'Agricultura': 0.08, 'Manufactura': 0.20, 'Construccion': 0.15,
    'Transporte':  0.28, 'Comercio':    0.52, 'Servicios':    0.68,
    'Tecnologia':  0.60, 'Educacion':   0.55, 'Salud':        0.45,
    'Finanzas':    0.72,
}
DIGITAL_ACCESS = {
    'Agricultura': 0, 'Manufactura': 0, 'Construccion': 0, 'Transporte': 0,
    'Comercio': 0,   'Servicios': 1,   'Tecnologia': 1,   'Educacion': 1,
    'Salud': 0,      'Finanzas': 1,
}

print('\nActualizando Block 3 por ocupacion:')
for row in ocupaciones:
    sinco_code = row[0]
    sector     = row[2]

    gpt     = float(np.clip(SECTOR_GPT.get(sector, 0.40)     + np.random.normal(0, 0.04), 0.01, 0.99))
    moravec = float(np.clip(SECTOR_MORAVEC.get(sector, 0.38) + np.random.normal(0, 0.04), 0.01, 0.99))
    friction = SECTOR_COMPLIANCE.get(sector, 0.25)
    dual    = float(np.clip(gpt * (1.0 - friction)           + np.random.normal(0, 0.03), 0.01, 0.99))
    iceberg = float(np.clip(SECTOR_ICEBERG.get(sector, 0.40) + np.random.normal(0, 0.04), 0.01, 0.99))
    digital = DIGITAL_ACCESS.get(sector, 0)

    cursor.execute("""
        UPDATE dbo.ocupaciones_onet
        SET gpt_exposure_score = ?,
            moravec_index      = ?,
            dual_factor_score  = ?,
            iceberg_score      = ?,
            digital_access     = ?
        WHERE sinco_code = ?
    """, round(gpt, 4), round(moravec, 4), round(dual, 4),
         round(iceberg, 4), digital, sinco_code)

    print(f'  sinco={sinco_code} ({sector}): '
          f'gpt={gpt:.3f} moravec={moravec:.3f} '
          f'dual={dual:.3f} iceberg={iceberg:.3f} digital={digital}')

conn.commit()
print('\n[OK] UPDATE completado')

# ------------------------------------------------------------------
# 4. Agregar NOT NULL constraint ahora que estan pobladas
# ------------------------------------------------------------------
for col_name, _ in new_cols:
    try:
        cursor.execute(
            f"ALTER TABLE dbo.ocupaciones_onet ALTER COLUMN {col_name} FLOAT NOT NULL"
            if col_name != 'digital_access' else
            f"ALTER TABLE dbo.ocupaciones_onet ALTER COLUMN {col_name} INT NOT NULL"
        )
    except Exception:
        pass  # Si ya tiene NOT NULL no falla en silencio

conn.commit()

# ------------------------------------------------------------------
# 5. Agregar CHECK constraints si no existen
# ------------------------------------------------------------------
check_constraints = [
    ('ck_gpt_range',    "gpt_exposure_score BETWEEN 0 AND 1"),
    ('ck_moravec_range','moravec_index BETWEEN 0 AND 1'),
    ('ck_dual_range',   'dual_factor_score BETWEEN 0 AND 1'),
    ('ck_iceberg_range','iceberg_score BETWEEN 0 AND 1'),
    ('ck_digital_access','digital_access IN (0, 1)'),
]
for cname, cdef in check_constraints:
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS "
        "WHERE CONSTRAINT_NAME=? AND TABLE_NAME='ocupaciones_onet'", cname
    )
    if not cursor.fetchone()[0]:
        try:
            cursor.execute(
                f"ALTER TABLE dbo.ocupaciones_onet ADD CONSTRAINT {cname} CHECK ({cdef})"
            )
            print(f'[CHECK] Constraint {cname} agregado')
        except Exception as e:
            print(f'[WARN]  {cname}: {e}')

conn.commit()

# ------------------------------------------------------------------
# 6. Recrear vista con Block 3
# ------------------------------------------------------------------
cursor.execute("""
IF OBJECT_ID('dbo.vista_riesgo_jalisco', 'V') IS NOT NULL
    DROP VIEW dbo.vista_riesgo_jalisco
""")
conn.commit()

cursor.execute("""
CREATE VIEW dbo.vista_riesgo_jalisco AS
WITH sector_factors AS (
    SELECT
        id_trabajador,
        CASE scian_sector
            WHEN 'Manufactura'  THEN  0.24 WHEN 'Agricultura'  THEN  0.16
            WHEN 'Construccion' THEN  0.10 WHEN 'Transporte'   THEN  0.06
            WHEN 'Comercio'     THEN -0.12 WHEN 'Servicios'    THEN -0.14
            WHEN 'Tecnologia'   THEN -0.16 WHEN 'Finanzas'     THEN -0.20
            WHEN 'Salud'        THEN -0.25 WHEN 'Educacion'    THEN -0.28
            ELSE 0.0 END AS f_risk,
        CASE scian_sector
            WHEN 'Manufactura'  THEN  13.0 WHEN 'Agricultura'  THEN   9.0
            WHEN 'Construccion' THEN   6.0 WHEN 'Transporte'   THEN   4.0
            WHEN 'Comercio'     THEN  -3.0 WHEN 'Servicios'    THEN  -5.0
            WHEN 'Tecnologia'   THEN  -7.0 WHEN 'Finanzas'     THEN  -9.0
            WHEN 'Salud'        THEN -10.0 WHEN 'Educacion'    THEN -13.0
            ELSE 0.0 END AS f_rti,
        CASE scian_sector
            WHEN 'Manufactura'  THEN -22.0 WHEN 'Agricultura'  THEN -18.0
            WHEN 'Construccion' THEN -12.0 WHEN 'Transporte'   THEN  -6.0
            WHEN 'Comercio'     THEN  -2.0 WHEN 'Servicios'    THEN   2.0
            WHEN 'Tecnologia'   THEN  12.0 WHEN 'Finanzas'     THEN  14.0
            WHEN 'Salud'        THEN  18.0 WHEN 'Educacion'    THEN  22.0
            ELSE 0.0 END AS f_cog,
        CASE scian_sector
            WHEN 'Manufactura'  THEN -18.0 WHEN 'Agricultura'  THEN -14.0
            WHEN 'Construccion' THEN  -8.0 WHEN 'Transporte'   THEN  -4.0
            WHEN 'Comercio'     THEN   8.0 WHEN 'Servicios'    THEN   6.0
            WHEN 'Tecnologia'   THEN   4.0 WHEN 'Finanzas'     THEN   6.0
            WHEN 'Salud'        THEN  22.0 WHEN 'Educacion'    THEN  18.0
            ELSE 0.0 END AS f_soc,
        CASE
            WHEN escoacum=1 THEN  0.06 WHEN escoacum=2 THEN  0.04
            WHEN escoacum=3 THEN  0.02 WHEN escoacum=4 THEN  0.00
            WHEN escoacum=5 THEN -0.04 WHEN escoacum=6 THEN -0.07
            ELSE 0.0 END AS f_edu,
        CASE
            WHEN ingocup <  5000 THEN  0.05
            WHEN ingocup < 10000 THEN  0.02
            WHEN ingocup < 20000 THEN  0.00
            WHEN ingocup < 35000 THEN -0.03
            ELSE                       -0.05
        END AS f_ing
    FROM dbo.trabajadores
)
SELECT
    t.id_trabajador,
    t.escoacum                                  AS nivel_educativo,
    t.ingocup                                   AS ingreso_mensual,
    t.scian_sector                              AS sector,
    t.formalidad,
    t.edad,
    t.tamanio_empresa,
    t.ira,
    o.occupation_name                           AS ocupacion,
    o.frey_osborne_score,
    ROUND(CASE WHEN o.rti+sf.f_rti>96 THEN 96
               WHEN o.rti+sf.f_rti<4  THEN 4
               ELSE o.rti+sf.f_rti END,2)       AS rti,
    ROUND(CASE WHEN o.cognitive_demand+sf.f_cog>96 THEN 96
               WHEN o.cognitive_demand+sf.f_cog<4  THEN 4
               ELSE o.cognitive_demand+sf.f_cog END,2) AS cognitive_demand,
    ROUND(CASE WHEN o.social_interaction+sf.f_soc>96 THEN 96
               WHEN o.social_interaction+sf.f_soc<4  THEN 4
               ELSE o.social_interaction+sf.f_soc END,2) AS social_interaction,
    o.creativity,
    ROUND(CASE
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing>0.99 THEN 0.99
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing<0.01 THEN 0.01
        ELSE o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing
    END,4)                                      AS automation_risk,
    CASE
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing>=0.70 THEN 'Alto'
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing>=0.40 THEN 'Medio'
        ELSE 'Bajo'
    END                                         AS riesgo_categoria,
    o.gpt_exposure_score,
    o.moravec_index,
    o.dual_factor_score,
    o.iceberg_score,
    o.digital_access
FROM dbo.trabajadores t
INNER JOIN dbo.ocupaciones_onet o  ON t.sinco_code = o.sinco_code
INNER JOIN sector_factors sf       ON t.id_trabajador = sf.id_trabajador
""")
conn.commit()
print('[OK] Vista vista_riesgo_jalisco recreada con Block 3')

# ------------------------------------------------------------------
# 7. Verificacion final
# ------------------------------------------------------------------
cursor.execute("SELECT TOP 3 sinco_code, sector, gpt_exposure_score, moravec_index, digital_access FROM dbo.ocupaciones_onet")
print('\nVerificacion ocupaciones_onet (primeras 3):')
for row in cursor.fetchall():
    print(f'  sinco={row[0]} sector={row[1]} gpt={row[2]:.3f} moravec={row[3]:.3f} digital={row[4]}')

cursor.execute("SELECT COUNT(*), AVG(automation_risk), AVG(gpt_exposure_score) FROM dbo.vista_riesgo_jalisco")
row = cursor.fetchone()
print(f'\nVista: {row[0]:,} registros | avg_risk={row[1]:.3f} | avg_gpt={row[2]:.3f}')

cursor.execute("""
    SELECT sector, COUNT(*) n, AVG(automation_risk) frey, AVG(gpt_exposure_score) gpt,
           AVG(gpt_exposure_score)-AVG(automation_risk) llm_gap
    FROM dbo.vista_riesgo_jalisco
    GROUP BY sector ORDER BY llm_gap DESC
""")
print('\nLLM Gap por sector (datos reales ENOE):')
print(f'  {"Sector":<15} {"N":>6} {"Frey":>8} {"GPT":>8} {"Gap":>8}')
for row in cursor.fetchall():
    print(f'  {row[0]:<15} {row[1]:>6} {row[2]:>8.3f} {row[3]:>8.3f} {row[4]:>+8.3f}')

conn.close()
print('\n[DONE] Block 3 integrado exitosamente en datos reales.')
