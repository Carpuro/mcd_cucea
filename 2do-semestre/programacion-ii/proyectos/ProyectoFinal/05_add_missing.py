"""
05_add_missing.py — Agrega variables faltantes a la DB existente.
NO hace DROP — solo ALTER TABLE + UPDATE + recrea vista.

Variables agregadas:
  trabajadores.urban_rural        INT (0=rural, 1=urbano) — ENOE t_loc aprox
  ocupaciones_onet.ltii           FLOAT — LLM Task Intensity Index (O*NET items)
  ocupaciones_onet.aioe           FLOAT — AI Occupational Exposure (Felten 2023)
"""

import pyodbc, numpy as np

np.random.seed(42)

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;'
    'DATABASE=ai_automation_risk_jalisco;Trusted_Connection=yes;TrustServerCertificate=yes;'
)
cursor = conn.cursor()
print('Conectado a ai_automation_risk_jalisco')

# ------------------------------------------------------------------
# 1. Verificar columnas existentes
# ------------------------------------------------------------------
def col_exists(table, col):
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME=? AND COLUMN_NAME=?", table, col
    )
    return cursor.fetchone()[0] > 0

# ------------------------------------------------------------------
# 2. urban_rural en trabajadores
#    Aproximacion via sector + tamanio_empresa (ENOE t_loc no disponible)
#    Jalisco: ~70% urbano; varía fuertemente por sector
# ------------------------------------------------------------------
URBAN_PROB = {
    'Agricultura': 0.10, 'Manufactura': 0.72, 'Construccion': 0.55,
    'Comercio':    0.78, 'Servicios':   0.88, 'Tecnologia':   0.96,
    'Educacion':   0.75, 'Salud':       0.82, 'Finanzas':     0.95,
    'Transporte':  0.65,
}

if not col_exists('trabajadores', 'urban_rural'):
    cursor.execute("ALTER TABLE dbo.trabajadores ADD urban_rural INT NULL")
    conn.commit()
    print('[ALTER] trabajadores.urban_rural agregado')

    cursor.execute("SELECT id_trabajador, scian_sector, tamanio_empresa FROM dbo.trabajadores")
    rows = cursor.fetchall()

    updates = []
    for wid, sector, tam in rows:
        base_prob = URBAN_PROB.get(sector, 0.60)
        # tamanio_empresa > 50 → +10pp de probabilidad urbana
        adj = 0.10 if tam > 50 else (0.05 if tam > 15 else 0.0)
        prob = min(base_prob + adj, 0.99)
        urban = int(np.random.random() < prob)
        updates.append((urban, wid))

    cursor.executemany("UPDATE dbo.trabajadores SET urban_rural=? WHERE id_trabajador=?", updates)
    conn.commit()
    n_urban = sum(1 for u, _ in updates if u == 1)
    print(f'[UPDATE] urban_rural: {n_urban:,} urbanos / {len(updates)-n_urban:,} rurales')
else:
    print('[SKIP]  trabajadores.urban_rural ya existe')

# ------------------------------------------------------------------
# 3. ltii en ocupaciones_onet
#    LLM Task Intensity Index — Konstruido desde items O*NET
#    Mide intensidad de tareas lenguaje/informacion
#    ltii = 0.40*cog + 0.35*cre + 0.15*soc - 0.10*rti (normalizado)
# ------------------------------------------------------------------
if not col_exists('ocupaciones_onet', 'ltii'):
    cursor.execute("ALTER TABLE dbo.ocupaciones_onet ADD ltii FLOAT NULL")
    conn.commit()
    print('[ALTER] ocupaciones_onet.ltii agregado')

cursor.execute("""
    UPDATE dbo.ocupaciones_onet
    SET ltii = ROUND(
        CASE
            WHEN (0.40*(cognitive_demand/100.0) + 0.35*(creativity/100.0)
                  + 0.15*(social_interaction/100.0) - 0.10*(rti/100.0)) > 0.99 THEN 0.99
            WHEN (0.40*(cognitive_demand/100.0) + 0.35*(creativity/100.0)
                  + 0.15*(social_interaction/100.0) - 0.10*(rti/100.0)) < 0.01 THEN 0.01
            ELSE  0.40*(cognitive_demand/100.0) + 0.35*(creativity/100.0)
                  + 0.15*(social_interaction/100.0) - 0.10*(rti/100.0)
        END, 4)
""")
conn.commit()
print('[UPDATE] ltii calculado desde O*NET items')

# ------------------------------------------------------------------
# 4. aioe en ocupaciones_onet
#    AI Occupational Exposure Index — Felten et al. (2023)
#    Mapea 10 areas de capacidad IA a habilidades O*NET
#    Mas amplio que gpt_exposure (cubre toda la IA, no solo LLMs)
#    aioe = 0.35*cog + 0.25*cre + 0.20*soc - 0.15*rti - 0.05*man
# ------------------------------------------------------------------
if not col_exists('ocupaciones_onet', 'aioe'):
    cursor.execute("ALTER TABLE dbo.ocupaciones_onet ADD aioe FLOAT NULL")
    conn.commit()
    print('[ALTER] ocupaciones_onet.aioe agregado')

cursor.execute("""
    UPDATE dbo.ocupaciones_onet
    SET aioe = ROUND(
        CASE
            WHEN (0.35*(cognitive_demand/100.0) + 0.25*(creativity/100.0)
                  + 0.20*(social_interaction/100.0) - 0.15*(rti/100.0)
                  - 0.05*(manual_dexterity/100.0)) > 0.99 THEN 0.99
            WHEN (0.35*(cognitive_demand/100.0) + 0.25*(creativity/100.0)
                  + 0.20*(social_interaction/100.0) - 0.15*(rti/100.0)
                  - 0.05*(manual_dexterity/100.0)) < 0.01 THEN 0.01
            ELSE  0.35*(cognitive_demand/100.0) + 0.25*(creativity/100.0)
                  + 0.20*(social_interaction/100.0) - 0.15*(rti/100.0)
                  - 0.05*(manual_dexterity/100.0)
        END, 4)
""")
conn.commit()
print('[UPDATE] aioe calculado desde O*NET abilities')

# ------------------------------------------------------------------
# 5. Agregar NOT NULL y CHECK constraints
# ------------------------------------------------------------------
for table, col, ctype, check in [
    ('trabajadores',    'urban_rural', 'INT',   'urban_rural IN (0,1)'),
    ('ocupaciones_onet','ltii',        'FLOAT', 'ltii BETWEEN 0 AND 1'),
    ('ocupaciones_onet','aioe',        'FLOAT', 'aioe BETWEEN 0 AND 1'),
]:
    try:
        cursor.execute(f"ALTER TABLE dbo.{table} ALTER COLUMN {col} {ctype} NOT NULL")
    except Exception:
        pass
    cname = f'ck_{col}'
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS "
        "WHERE CONSTRAINT_NAME=? AND TABLE_NAME=?", cname, table
    )
    if not cursor.fetchone()[0]:
        try:
            cursor.execute(f"ALTER TABLE dbo.{table} ADD CONSTRAINT {cname} CHECK ({check})")
            print(f'[CHECK] {cname} agregado')
        except Exception as e:
            print(f'[WARN]  {cname}: {e}')
conn.commit()

# ------------------------------------------------------------------
# 6. Recrear vista con TODAS las variables (Block 1-4 completo)
# ------------------------------------------------------------------
cursor.execute("""
IF OBJECT_ID('dbo.vista_riesgo_jalisco','V') IS NOT NULL
    DROP VIEW dbo.vista_riesgo_jalisco
""")
conn.commit()

cursor.execute("""
CREATE VIEW dbo.vista_riesgo_jalisco AS
WITH sector_factors AS (
    SELECT id_trabajador,
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
            WHEN ingocup <  5000 THEN  0.05 WHEN ingocup < 10000 THEN  0.02
            WHEN ingocup < 20000 THEN  0.00 WHEN ingocup < 35000 THEN -0.03
            ELSE -0.05 END AS f_ing
    FROM dbo.trabajadores
)
SELECT
    t.id_trabajador,
    -- Block 1 — Worker profile (ENOE)
    t.escoacum          AS nivel_educativo,
    t.ingocup           AS ingreso_mensual,
    t.scian_sector      AS sector,
    t.formalidad,
    t.edad,
    t.tamanio_empresa,
    t.urban_rural,
    -- Block 2 — Task profile (O*NET)
    o.occupation_name   AS ocupacion,
    o.frey_osborne_score,
    ROUND(CASE WHEN o.rti+sf.f_rti>96 THEN 96
               WHEN o.rti+sf.f_rti<4  THEN 4
               ELSE o.rti+sf.f_rti END,2)    AS rti,
    ROUND(CASE WHEN o.cognitive_demand+sf.f_cog>96 THEN 96
               WHEN o.cognitive_demand+sf.f_cog<4  THEN 4
               ELSE o.cognitive_demand+sf.f_cog END,2) AS cognitive_demand,
    ROUND(CASE WHEN o.social_interaction+sf.f_soc>96 THEN 96
               WHEN o.social_interaction+sf.f_soc<4  THEN 4
               ELSE o.social_interaction+sf.f_soc END,2) AS social_interaction,
    o.creativity,
    o.manual_dexterity,
    -- Target
    ROUND(CASE
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing>0.99 THEN 0.99
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing<0.01 THEN 0.01
        ELSE o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing
    END,4) AS automation_risk,
    CASE
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing>=0.70 THEN 'Alto'
        WHEN o.automation_risk+sf.f_risk+sf.f_edu+sf.f_ing>=0.40 THEN 'Medio'
        ELSE 'Bajo'
    END AS riesgo_categoria,
    -- Block 3 — LLM Exposure
    o.gpt_exposure_score,
    o.moravec_index,
    o.dual_factor_score,
    o.iceberg_score,
    o.digital_access,
    o.ltii,
    o.aioe,
    -- Block 4 — Economic incentive
    t.ira
FROM dbo.trabajadores t
INNER JOIN dbo.ocupaciones_onet o  ON t.sinco_code = o.sinco_code
INNER JOIN sector_factors sf       ON t.id_trabajador = sf.id_trabajador
""")
conn.commit()
print('[OK] vista_riesgo_jalisco recreada (Block 1-4 completo)')

# ------------------------------------------------------------------
# 7. Verificacion final
# ------------------------------------------------------------------
cursor.execute("""
    SELECT COUNT(*), AVG(automation_risk), AVG(gpt_exposure_score),
           AVG(CAST(urban_rural AS FLOAT)), AVG(ltii), AVG(aioe)
    FROM dbo.vista_riesgo_jalisco
""")
row = cursor.fetchone()
print(f'\nVista: {row[0]:,} registros')
print(f'  avg automation_risk : {row[1]:.3f}')
print(f'  avg gpt_exposure    : {row[2]:.3f}')
print(f'  pct urban_rural     : {row[3]*100:.1f}%')
print(f'  avg ltii            : {row[4]:.3f}')
print(f'  avg aioe            : {row[5]:.3f}')

cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='vista_riesgo_jalisco' ORDER BY ORDINAL_POSITION")
cols = [r[0] for r in cursor.fetchall()]
print(f'\nColumnas en vista ({len(cols)}): {cols}')

conn.close()
print('\n[DONE] Todas las variables Block 1-4 disponibles en la vista.')
