"""
10_load_all_data.py
Carga todos los datos disponibles a ai_automation_risk_jalisco:
  1. enoe_sdemt_full  — todos los trabajadores Jalisco (13,839)
  2. enoe_coe1_jalisco — condiciones de trabajo (p5f)
  3. onet_task_ratings
  4. onet_technology_skills
  5. onet_task_statements
  6. onet_emerging_tasks
  7. onet_skills
  8. onet_work_context
  9. onet_education_training
 10. onet_work_activities_detail
"""

import os, time, warnings
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

warnings.filterwarnings('ignore')

# ── Rutas ─────────────────────────────────────────────────────────────────────
TESIS   = r'C:\Users\carlo\OneDrive\Documentos\GitHub\ai-automation-risk-jalisco'
ENOE    = os.path.join(TESIS, 'data', 'raw', 'enoe')
ONET    = os.path.join(TESIS, 'data', 'raw', 'onet', 'db_28_3_text')

# ── Conexion SQL Server ───────────────────────────────────────────────────────
engine = create_engine(
    'mssql+pyodbc://localhost,1433/ai_automation_risk_jalisco'
    '?driver=ODBC+Driver+17+for+SQL+Server'
    '&trusted_connection=yes&TrustServerCertificate=yes'
)

ENOE_KEY = ['ent','con','upm','d_sem','n_pro_viv','v_sel',
            'n_hog','h_mud','n_ent','per','n_ren']

def load_table(df, table_name, chunksize=5000, if_exists='replace'):
    t0 = time.time()
    df.to_sql(table_name, engine, if_exists=if_exists,
              index=False, chunksize=chunksize)
    print(f'  [{table_name}] {len(df):,} filas — {time.time()-t0:.1f}s')

def read_onet(filename, sep='\t'):
    path = os.path.join(ONET, filename)
    df = pd.read_csv(path, sep=sep, encoding='latin-1', low_memory=False)
    df.columns = [c.strip().lower().replace(' ','_').replace('-','_')
                  .replace('*','').replace('(','').replace(')','')
                  .replace('/','_') for c in df.columns]
    return df

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ENOE SDEMT — todos los trabajadores Jalisco
# ═══════════════════════════════════════════════════════════════════════════════
print('=== 1. ENOE SDEMT full (Jalisco) ===')
sdemt_cols = ENOE_KEY + [
    'sex','eda','niv_ins','anios_esc','cs_p17',
    'clase1','pos_ocu','seg_soc','c_ocu11c','scian','rama_est2',
    'emple7c','t_tra','ingocup','ing7c','ing_x_hrs','hrsocup',
    't_loc_tri','ur','fac_tri'
]
sdemt_all  = pd.read_csv(os.path.join(ENOE, 'ENOE_SDEMT324.csv'),
                          usecols=sdemt_cols, low_memory=False, encoding='latin-1')
sdemt_jal  = sdemt_all[sdemt_all['ent'] == 14].copy()
print(f'  Jalisco: {len(sdemt_jal):,} registros, {len(sdemt_jal.columns)} columnas')
load_table(sdemt_jal, 'enoe_sdemt_full')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. ENOE COE1 — condiciones de trabajo (p5f)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 2. ENOE COE1 (Jalisco) ===')
coe1_cols = ENOE_KEY + [
    'p1',        # tipo local
    'p2c',       # tipo contrato
    'p3h',       # num trabajadores establecimiento
    'p3i',       # contrato escrito
    'p5b_thrs',  # horas semana
    'p5f1','p5f2','p5f3','p5f4','p5f5','p5f6','p5f7',
    'p5f8','p5f9','p5f10','p5f11','p5f12','p5f13','p5f14','p5f15',
    'p5f99'
]
# Solo cargar columnas que existen en el archivo
coe1_all_cols = pd.read_csv(os.path.join(ENOE,'ENOE_COE1T324.csv'),
                              nrows=0).columns.tolist()
coe1_use = [c for c in coe1_cols if c in coe1_all_cols]
missing   = [c for c in coe1_cols if c not in coe1_all_cols]
if missing:
    print(f'  Columnas no encontradas en COE1: {missing}')

coe1_all = pd.read_csv(os.path.join(ENOE,'ENOE_COE1T324.csv'),
                        usecols=coe1_use, low_memory=False, encoding='latin-1')
coe1_jal = coe1_all[coe1_all['ent'] == 14].copy()

# Renombrar columnas descriptivas
rename_map = {
    'p1':'tipo_local', 'p2c':'tipo_contrato', 'p3h':'tam_establecimiento_n',
    'p3i':'contrato_escrito', 'p5b_thrs':'horas_semana',
    'p5f1':'cond_exterior', 'p5f2':'cond_de_pie', 'p5f3':'cond_peso',
    'p5f4':'cond_repetitivo', 'p5f5':'cond_maquinaria', 'p5f6':'cond_transporte',
    'p5f7':'cond_computadora', 'p5f8':'cond_clientes', 'p5f9':'cond_vigilancia',
    'p5f10':'cond_temperatura', 'p5f11':'cond_peligroso', 'p5f12':'cond_altura',
    'p5f13':'cond_herramientas', 'p5f14':'cond_elaborar', 'p5f15':'cond_reparacion',
    'p5f99':'cond_ninguna'
}
coe1_jal = coe1_jal.rename(columns={k:v for k,v in rename_map.items() if k in coe1_jal.columns})
print(f'  Jalisco: {len(coe1_jal):,} registros, {len(coe1_jal.columns)} columnas')
load_table(coe1_jal, 'enoe_coe1_jalisco')

# ═══════════════════════════════════════════════════════════════════════════════
# 3. O*NET Task Ratings
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 3. O*NET Task Ratings ===')
tr = read_onet('Task Ratings.txt')
print(f'  Columnas: {list(tr.columns)}')
# Renombrar columnas clave
tr = tr.rename(columns={
    'onet_soc_code':'onetsoc_code',
    'task_type':'task_type',
    'scale_id':'scale_id',
    'data_value':'data_value',
    'n':'n_value',
    'standard_error':'standard_error',
    'recommend_suppress':'recommend_suppress',
    'date_updated':'date_updated'
})
load_table(tr, 'onet_task_ratings')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. O*NET Technology Skills
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 4. O*NET Technology Skills ===')
ts = read_onet('Technology Skills.txt')
ts = ts.rename(columns={'onet_soc_code':'onetsoc_code'})
print(f'  Columnas: {list(ts.columns)} — {len(ts):,} filas')
load_table(ts, 'onet_technology_skills')

# ═══════════════════════════════════════════════════════════════════════════════
# 5. O*NET Task Statements
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 5. O*NET Task Statements ===')
tst = read_onet('Task Statements.txt')
tst = tst.rename(columns={'onet_soc_code':'onetsoc_code'})
print(f'  Columnas: {list(tst.columns)} — {len(tst):,} filas')
load_table(tst, 'onet_task_statements')

# ═══════════════════════════════════════════════════════════════════════════════
# 6. O*NET Emerging Tasks
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 6. O*NET Emerging Tasks ===')
et = read_onet('Emerging Tasks.txt')
et = et.rename(columns={'onet_soc_code':'onetsoc_code'})
print(f'  Columnas: {list(et.columns)} — {len(et):,} filas')
load_table(et, 'onet_emerging_tasks')

# ═══════════════════════════════════════════════════════════════════════════════
# 7. O*NET Skills
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 7. O*NET Skills ===')
sk = read_onet('Skills.txt')
sk = sk.rename(columns={'onet_soc_code':'onetsoc_code',
                         'element_id':'element_id',
                         'element_name':'element_name',
                         'scale_id':'scale_id',
                         'data_value':'data_value',
                         'n':'n_value',
                         'standard_error':'standard_error',
                         'recommend_suppress':'recommend_suppress',
                         'date_updated':'date_updated'})
print(f'  Columnas: {list(sk.columns)} — {len(sk):,} filas')
load_table(sk, 'onet_skills')

# ═══════════════════════════════════════════════════════════════════════════════
# 8. O*NET Work Context
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 8. O*NET Work Context ===')
wc = read_onet('Work Context.txt')
wc = wc.rename(columns={'onet_soc_code':'onetsoc_code',
                          'n':'n_value',
                          'standard_error':'standard_error',
                          'recommend_suppress':'recommend_suppress'})
print(f'  Columnas: {list(wc.columns)} — {len(wc):,} filas')
load_table(wc, 'onet_work_context', chunksize=2000)

# ═══════════════════════════════════════════════════════════════════════════════
# 9. O*NET Education, Training & Experience
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 9. O*NET Education, Training & Experience ===')
edu = read_onet('Education, Training, and Experience.txt')
edu = edu.rename(columns={'onet_soc_code':'onetsoc_code',
                            'n':'n_value',
                            'standard_error':'standard_error',
                            'recommend_suppress':'recommend_suppress'})
print(f'  Columnas: {list(edu.columns)} — {len(edu):,} filas')
load_table(edu, 'onet_education_training')

# ═══════════════════════════════════════════════════════════════════════════════
# 10. O*NET Work Activities (detalle)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== 10. O*NET Work Activities (detalle) ===')
wa = read_onet('Work Activities.txt')
wa = wa.rename(columns={'onet_soc_code':'onetsoc_code',
                         'n':'n_value',
                         'standard_error':'standard_error',
                         'recommend_suppress':'recommend_suppress'})
print(f'  Columnas: {list(wa.columns)} — {len(wa):,} filas')
load_table(wa, 'onet_work_activities_detail')

# ═══════════════════════════════════════════════════════════════════════════════
# Verificacion final
# ═══════════════════════════════════════════════════════════════════════════════
print('\n=== Verificacion de tablas ===')
tables = [
    'trabajadores', 'ocupaciones_onet',
    'enoe_sdemt_full', 'enoe_coe1_jalisco',
    'onet_task_ratings', 'onet_technology_skills', 'onet_task_statements',
    'onet_emerging_tasks', 'onet_skills', 'onet_work_context',
    'onet_education_training', 'onet_work_activities_detail'
]
with engine.connect() as conn:
    for t in tables:
        try:
            n = conn.execute(text(f'SELECT COUNT(*) FROM dbo.{t}')).scalar()
            print(f'  {t:<35} {n:>10,} filas')
        except Exception as e:
            print(f'  {t:<35} ERROR: {e}')

print('\n[OK] Carga completa.')
