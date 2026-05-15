"""
Proyecto Final — Programacion II | MCD CUCEA 2026-A
Autor: Carlos Pulido Rosas

Carga masiva de datos REALES en Defunciones_2000 (SQL Server):
  - ocupaciones_onet : scores reales O*NET 28.3 por grupo SINCO
  - trabajadores     : muestra ENOE Q3 2024 Jalisco (entidad 14)

Fuentes:
  O*NET 28.3   → onet_scores.csv (procesado de Work Activities + Abilities)
  ENOE Q3 2024 → enoe_jalisco.csv (filtrado entidad=14, 2000 trabajadores)
  Crosswalk    → sinco_group_scores.csv (SINCO -> ISCO-08 -> SOC -> O*NET)
"""

import pandas as pd
import numpy as np
import pyodbc
import os

np.random.seed(42)

REPO = r'C:\Users\carlo\OneDrive\Documentos\GitHub\ai-automation-risk-jalisco'
PROC = os.path.join(REPO, 'data', 'processed')

# ------------------------------------------------------------------
# 1. Conexion a SQL Server (Windows Authentication)
# ------------------------------------------------------------------
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost,1433;'
    'DATABASE=Defunciones_2000;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)
cursor = conn.cursor()
print('Conexion exitosa a Defunciones_2000')

# ------------------------------------------------------------------
# 2. Limpiar tablas existentes
# ------------------------------------------------------------------
cursor.execute("DELETE FROM dbo.trabajadores")
cursor.execute("DELETE FROM dbo.ocupaciones_onet")
conn.commit()

# ------------------------------------------------------------------
# 3. Cargar datos procesados
# ------------------------------------------------------------------
enoe = pd.read_csv(os.path.join(PROC, 'enoe_jalisco.csv'))
sinco_scores = pd.read_csv(os.path.join(PROC, 'sinco_group_scores.csv'))
sinco_scores['sinco_major'] = sinco_scores['sinco_major'].astype(str)

print(f'ENOE Jalisco cargado: {len(enoe):,} trabajadores')
print(f'SINCO group scores: {len(sinco_scores)} grupos')

# ------------------------------------------------------------------
# 4. Construir tabla ocupaciones_onet
#    Una fila por codigo SINCO unico en los datos ENOE
#    Scores O*NET asignados por grupo SINCO mayor
# ------------------------------------------------------------------

# Ocupaciones reales de Jalisco (SINCO codes unicos en ENOE)
occ_jalisco = enoe.groupby('sinco_code').agg(
    n_trabajadores=('ingocup', 'count'),
    ingreso_prom=('ingocup', 'mean'),
    edu_prom=('escoacum', 'mean'),
    sector_principal=('scian_sector', lambda x: x.mode()[0])
).reset_index()

occ_jalisco['sinco_major'] = occ_jalisco['sinco_code'].astype(str).str[0]

# Nombres de ocupacion por grupo SINCO (basados en SINCO 2011)
SINCO_NAMES = {
    '1': 'Directivo o gerente',
    '2': 'Profesionista o cientifico',
    '3': 'Tecnico o profesional asociado',
    '4': 'Trabajador de apoyo administrativo',
    '5': 'Comerciante o vendedor',
    '6': 'Trabajador en servicios personales',
    '7': 'Trabajador agropecuario',
    '8': 'Artesano o trabajador en industria',
    '9': 'Operador de maquinaria o transporte',
    '0': 'Trabajador en ocupacion elemental',
}

occ_jalisco['occupation_name'] = occ_jalisco['sinco_major'].map(SINCO_NAMES).fillna('Ocupacion no clasificada')

# Merge con scores O*NET reales
occ_jalisco = occ_jalisco.merge(
    sinco_scores[['sinco_major', 'cognitive_demand', 'social_interaction',
                  'creativity', 'manual_dexterity', 'rti',
                  'automation_risk', 'frey_osborne_score']],
    on='sinco_major', how='left'
)

# Pequeno ruido para diferenciar ocupaciones dentro del mismo grupo
np.random.seed(42)
for col in ['cognitive_demand', 'social_interaction', 'creativity',
            'manual_dexterity', 'rti', 'automation_risk']:
    noise = np.random.normal(0, 2, len(occ_jalisco))
    occ_jalisco[col] = (occ_jalisco[col] + noise).clip(0, 100)

occ_jalisco['automation_risk'] = occ_jalisco['automation_risk'].clip(0, 1)
occ_jalisco['frey_osborne_score'] = occ_jalisco['automation_risk']

print(f'Ocupaciones unicas ENOE Jalisco: {len(occ_jalisco)}')

# ------------------------------------------------------------------
# 5. Insertar ocupaciones_onet
# ------------------------------------------------------------------
insert_occ = """
    INSERT INTO dbo.ocupaciones_onet
        (sinco_code, occupation_name, sector, frey_osborne_score,
         rti, cognitive_demand, social_interaction, creativity,
         manual_dexterity, automation_risk)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

SECTOR_MAP = {
    'Agricultura': 'Agricultura', 'Manufactura': 'Manufactura',
    'Construccion': 'Construccion', 'Comercio': 'Comercio',
    'Servicios': 'Servicios', 'Tecnologia': 'Tecnologia',
    'Educacion': 'Educacion', 'Salud': 'Salud',
    'Finanzas': 'Finanzas', 'Transporte': 'Transporte',
}

rows_occ = []
for _, row in occ_jalisco.iterrows():
    sector = SECTOR_MAP.get(str(row['sector_principal']), 'Servicios')
    rows_occ.append((
        int(row['sinco_code']),
        str(row['occupation_name'])[:100],
        sector,
        round(float(row['frey_osborne_score']), 6),
        round(float(row['rti']), 4),
        round(float(row['cognitive_demand']), 4),
        round(float(row['social_interaction']), 4),
        round(float(row['creativity']), 4),
        round(float(row['manual_dexterity']), 4),
        round(float(row['automation_risk']), 6),
    ))

cursor.executemany(insert_occ, rows_occ)
conn.commit()
print(f'ocupaciones_onet: {len(rows_occ)} registros insertados (datos reales O*NET)')

# ------------------------------------------------------------------
# 6. Insertar trabajadores desde ENOE Q3 2024 Jalisco
# ------------------------------------------------------------------
insert_trab = """
    INSERT INTO dbo.trabajadores
        (sinco_code, escoacum, ingocup, scian_sector,
         formalidad, edad, tamanio_empresa, ira)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

# IRA por sector
ACTIVO_FIJO = {
    'Agricultura': 18_000, 'Manufactura': 95_000, 'Construccion': 45_000,
    'Comercio': 38_000, 'Servicios': 28_000, 'Tecnologia': 72_000,
    'Educacion': 22_000, 'Salud': 110_000, 'Finanzas': 85_000, 'Transporte': 98_000,
}

# Solo insertar trabajadores cuyo sinco_code existe en ocupaciones_onet
valid_sincos = set(occ_jalisco['sinco_code'].astype(int).tolist())
enoe_valid = enoe[enoe['sinco_code'].isin(valid_sincos)].copy()

rows_trab = []
for _, row in enoe_valid.iterrows():
    sector = SECTOR_MAP.get(str(row['scian_sector']), 'Servicios')
    activo = ACTIVO_FIJO.get(sector, 28_000)
    ingocup = max(500.0, float(row['ingocup']))
    ira = round((ingocup * 12) / activo, 4)

    rows_trab.append((
        int(row['sinco_code']),
        int(row['escoacum']),
        round(ingocup, 2),
        sector,
        str(row['formalidad']),
        int(row['edad']),
        int(row['tamanio_empresa']),
        ira,
    ))

cursor.executemany(insert_trab, rows_trab)
conn.commit()
print(f'trabajadores: {len(rows_trab)} registros insertados (datos reales ENOE Q3 2024 Jalisco)')

# ------------------------------------------------------------------
# 7. Verificacion final
# ------------------------------------------------------------------
cursor.execute("SELECT COUNT(*) FROM dbo.ocupaciones_onet")
n_occ = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM dbo.trabajadores")
n_trab = cursor.fetchone()[0]
cursor.execute("SELECT AVG(ingocup), AVG(ira), AVG(automation_risk) FROM dbo.vista_riesgo_jalisco")
row = cursor.fetchone()

print(f'\nVerificacion SQL Server:')
print(f'  ocupaciones_onet       : {n_occ} registros')
print(f'  trabajadores           : {n_trab} registros')
print(f'  Ingreso promedio       : ${row[0]:,.0f} MXN/mes')
print(f'  IRA promedio           : {row[1]:.3f}')
print(f'  Riesgo promedio        : {row[2]:.3f}')

conn.close()
print('\nCarga masiva REAL completada.')
