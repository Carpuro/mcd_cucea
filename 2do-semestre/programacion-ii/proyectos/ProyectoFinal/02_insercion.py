"""
Proyecto Final — Programacion II | MCD CUCEA 2026-A
Autor: Carlos Pulido Rosas
Descripcion: Carga masiva de datos en Defunciones_2000 (SQL Server).
             - ocupaciones_onet: desde CSV derivado de O*NET 28.3
             - trabajadores: generados a partir del perfil ENOE Jalisco
"""

import pandas as pd
import numpy as np
import pyodbc
import os

np.random.seed(42)

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
# 2. Cargar CSV de ocupaciones (O*NET 28.3 via SINCO)
# ------------------------------------------------------------------
csv_path = os.path.join(os.path.dirname(__file__), 'data', 'occupations_sample.csv')
df_occ = pd.read_csv(csv_path)

print(f'Ocupaciones cargadas del CSV: {len(df_occ)} registros')

# ------------------------------------------------------------------
# 3. Insertar ocupaciones_onet
# ------------------------------------------------------------------
cursor.execute("DELETE FROM dbo.trabajadores")
cursor.execute("DELETE FROM dbo.ocupaciones_onet")
conn.commit()

insert_occ = """
    INSERT INTO dbo.ocupaciones_onet
        (sinco_code, occupation_name, sector, frey_osborne_score,
         rti, cognitive_demand, social_interaction, creativity,
         manual_dexterity, automation_risk)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

sector_map = {
    'Agricultura': 'Agricultura', 'Manufactura': 'Manufactura',
    'Construccion': 'Construccion', 'Construcción': 'Construccion',
    'Comercio': 'Comercio', 'Servicios': 'Servicios',
    'Tecnologia': 'Tecnologia', 'Tecnología': 'Tecnologia',
    'Educacion': 'Educacion', 'Educación': 'Educacion',
    'Salud': 'Salud', 'Finanzas': 'Finanzas', 'Transporte': 'Transporte'
}

rows_occ = []
for _, row in df_occ.iterrows():
    sector_clean = sector_map.get(row['sector'], 'Servicios')
    manual_dex = max(0.0, min(100.0, 100.0 - row['cognitive_demand'] * 0.6))
    rows_occ.append((
        int(row['occupation_id']),
        str(row['occupation_name'])[:100],
        sector_clean,
        float(row['automation_risk']),
        float(row['routine_index']),
        float(row['cognitive_demand']),
        float(row['social_interaction']),
        float(row['creativity']),
        round(manual_dex, 4),
        float(row['automation_risk']),
    ))

cursor.executemany(insert_occ, rows_occ)
conn.commit()
print(f'ocupaciones_onet: {len(rows_occ)} registros insertados')

# ------------------------------------------------------------------
# 4. Generar e insertar trabajadores (perfil ENOE Jalisco)
#    ~5 trabajadores por ocupacion = ~500 registros
# ------------------------------------------------------------------
insert_trab = """
    INSERT INTO dbo.trabajadores
        (sinco_code, escoacum, ingocup, scian_sector,
         formalidad, edad, tamanio_empresa, ira)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

sector_to_scian = {
    'Agricultura': 'Agricultura', 'Manufactura': 'Manufactura',
    'Construccion': 'Construccion', 'Comercio': 'Comercio',
    'Servicios': 'Servicios', 'Tecnologia': 'Tecnologia',
    'Educacion': 'Educacion', 'Salud': 'Salud',
    'Finanzas': 'Finanzas', 'Transporte': 'Transporte'
}

# Activo fijo amortizado a 5 anios por trabajador y sector (MXN/anio)
# Fuente de referencia: Censos Economicos INEGI 2019
# IRA = ingocup_anual / activo_fijo_amortizado → IRA > 1 = incentivo economico
activo_fijo_sector = {
    'Agricultura':  18_000,   # Baja mecanizacion por hect; terreno explica por que sigue manual
    'Manufactura':  95_000,   # Alta inversion en maquinaria CNC, robots industriales
    'Construccion': 45_000,   # Equipo pesado amortizado
    'Comercio':     38_000,   # Terminales POS, software ERP
    'Servicios':    28_000,   # Capital bajo; labor-intensive
    'Tecnologia':   72_000,   # Infraestructura TI, licencias
    'Educacion':    22_000,   # Bajo capital fisico por docente
    'Salud':       110_000,   # Equipo medico de alto costo
    'Finanzas':     85_000,   # Software, centros de datos
    'Transporte':   98_000,   # Vehiculos, flotillas
}

informal_sectors = {'Agricultura', 'Construccion', 'Comercio'}

rows_trab = []
for _, row in df_occ.iterrows():
    sinco = int(row['occupation_id'])
    sector_clean = sector_map.get(row['sector'], 'Servicios')
    base_salary = float(row['avg_salary_mxn'])
    edu_level = int(row['education_level'])
    n_workers = max(3, min(10, int(np.log1p(row['workers_jalisco']))))

    for _ in range(n_workers):
        ingocup = max(0.0, np.random.normal(base_salary, base_salary * 0.2))
        escoacum = int(np.clip(
            np.random.normal(edu_level, 1), 1, 6
        ))
        edad = int(np.random.randint(18, 66))
        formalidad = 'Informal' if sector_clean in informal_sectors \
                     else ('Formal' if np.random.random() > 0.35 else 'Informal')
        tamanio = int(np.random.choice([1, 5, 15, 50, 150, 250],
                      p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05]))

        activo_fijo = activo_fijo_sector.get(sector_clean, 28_000)
        ira = round((ingocup * 12) / activo_fijo, 4)

        rows_trab.append((
            sinco,
            escoacum,
            round(ingocup, 2),
            sector_to_scian.get(sector_clean, 'Servicios'),
            formalidad,
            edad,
            tamanio,
            ira,
        ))

cursor.executemany(insert_trab, rows_trab)
conn.commit()
print(f'trabajadores: {len(rows_trab)} registros insertados')

# ------------------------------------------------------------------
# 5. Verificacion final
# ------------------------------------------------------------------
cursor.execute("SELECT COUNT(*) FROM dbo.ocupaciones_onet")
n_occ = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM dbo.trabajadores")
n_trab = cursor.fetchone()[0]

print(f'\nVerificacion final:')
print(f'  ocupaciones_onet : {n_occ} registros')
print(f'  trabajadores     : {n_trab} registros')

conn.close()
print('\nCarga masiva completada exitosamente.')
