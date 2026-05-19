"""
Genera occupations_sample.csv con correlaciones y distribucion disenadas.

Estrategia: generar automation_risk primero (bimodal por sector),
luego derivar variables O*NET como funcion lineal del riesgo + ruido.
Esto garantiza correlaciones controladas y distribucion bimodal.

Targets Block 2 — O*NET (presentacion):
  cognitive_demand   <-> risk : r approx -0.83
  routine_index      <-> risk : r approx +0.71
  social_interaction <-> risk : r approx -0.67
  education_level    <-> risk : r approx -0.66
  avg_salary_mxn     <-> risk : r approx -0.62

Targets Block 3 — LLM Exposure (H1: correlacion NEGATIVA con automation_risk):
  gpt_exposure_score <-> risk : r approx -0.60  (Eloundou 2024 via IDB SINCO crosswalk)
  moravec_index      <-> risk : r approx -0.55  (Arora et al. 2025, arXiv:2510.13369)
  dual_factor_score  <-> risk : r approx -0.45  (arXiv:2604.04464 — tech x (1-compliance))
  iceberg_score      <-> risk : r approx -0.60  (MIT Iceberg Index, arXiv:2510.25137)
  digital_access     <-> risk : r approx -0.50  (ILO/World Bank WP121 2024 — binaria 0/1)

H1 pattern: Servicios/Finanzas tienen HIGH LLM exposure pese a MEDIUM Frey-Osborne risk.
Agricultura/Manufactura tienen HIGH Frey-Osborne risk pero LOW LLM exposure.

Sector ranking Frey-Osborne (mayor a menor riesgo):
  Agricultura > Manufactura > Construccion > Transporte >
  Comercio > Servicios > Tecnologia > Finanzas > Salud > Educacion

Sector ranking LLM exposure (mayor a menor — patron invertido = H1):
  Finanzas > Servicios > Tecnologia > Educacion > Comercio >
  Salud > Transporte > Manufactura > Construccion > Agricultura
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

# ------------------------------------------------------------------
# 1. Definicion de ocupaciones por sector y cluster de riesgo
#    score_range: rango de automation_risk para ese bloque
# ------------------------------------------------------------------
# (sector, risk_cluster, n, score_range)
blocks = [
    # Sector          cluster    n   score_range
    ('Agricultura',   'high',    5, (0.75, 0.90)),
    ('Manufactura',   'high',   14, (0.65, 0.88)),
    ('Manufactura',   'medium',  4, (0.42, 0.62)),
    ('Manufactura',   'low',     2, (0.18, 0.38)),
    ('Construccion',  'high',    5, (0.63, 0.85)),
    ('Construccion',  'medium',  3, (0.40, 0.60)),
    ('Transporte',    'high',    4, (0.60, 0.82)),
    ('Transporte',    'medium',  4, (0.38, 0.58)),
    ('Comercio',      'high',    4, (0.58, 0.80)),
    ('Comercio',      'medium',  5, (0.38, 0.58)),
    ('Comercio',      'low',     3, (0.18, 0.38)),
    ('Servicios',     'high',    3, (0.58, 0.78)),
    ('Servicios',     'medium',  8, (0.36, 0.56)),
    ('Servicios',     'low',     9, (0.12, 0.36)),
    ('Tecnologia',    'high',    1, (0.56, 0.72)),
    ('Tecnologia',    'medium',  3, (0.35, 0.55)),
    ('Tecnologia',    'low',     6, (0.10, 0.35)),
    ('Educacion',     'medium',  1, (0.35, 0.50)),
    ('Educacion',     'low',     6, (0.08, 0.30)),
    ('Salud',         'medium',  1, (0.36, 0.52)),
    ('Salud',         'low',     5, (0.10, 0.32)),
    ('Finanzas',      'medium',  1, (0.38, 0.54)),
    ('Finanzas',      'low',     3, (0.12, 0.34)),
]

occ_names = {
    ('Agricultura', 'high'):    ['Jornalero agricola', 'Operador de cosechadora',
                                  'Recolector de frutas', 'Empacador agricola',
                                  'Trabajador de invernadero'],
    ('Manufactura', 'high'):    ['Operador de maquinaria CNC', 'Ensamblador de linea',
                                  'Soldador industrial', 'Operador de prensa',
                                  'Inspector de calidad linea', 'Trabajador de molde',
                                  'Operador de torno', 'Clasificador de productos',
                                  'Empacador industrial', 'Operador de montacargas',
                                  'Cortador textil', 'Pintador industrial',
                                  'Operador de extrusora', 'Armador de cajas'],
    ('Manufactura', 'medium'):  ['Tecnico de mantenimiento', 'Supervisor de produccion',
                                  'Tecnico de control de calidad', 'Mecanico industrial'],
    ('Manufactura', 'low'):     ['Ingeniero de procesos', 'Ingeniero de manufactura'],
    ('Construccion', 'high'):   ['Albanil', 'Peon de construccion',
                                  'Pintor de inmuebles', 'Colocador de pisos',
                                  'Ayudante general'],
    ('Construccion', 'medium'): ['Plomero', 'Electricista', 'Tecnico en construccion'],
    ('Transporte', 'high'):     ['Chofer de camion de carga', 'Operador de grua',
                                  'Conductor de taxi', 'Repartidor'],
    ('Transporte', 'medium'):   ['Mecanico automotriz', 'Conductor de autobus',
                                  'Tecnico de flotilla', 'Operador logistico'],
    ('Comercio', 'high'):       ['Cajero de tienda', 'Empacador de supermercado',
                                  'Vendedor ambulante', 'Repositor de anaquel'],
    ('Comercio', 'medium'):     ['Vendedor de mostrador', 'Asesor de ventas',
                                  'Ejecutivo de cuentas', 'Agente inmobiliario',
                                  'Coordinador de ventas'],
    ('Comercio', 'low'):        ['Gerente de sucursal', 'Director comercial',
                                  'Especialista en marketing digital'],
    ('Servicios', 'high'):      ['Teleoperador de call center', 'Capturista de datos',
                                  'Archivista'],
    ('Servicios', 'medium'):    ['Asistente administrativo', 'Recepcionista',
                                  'Auxiliar contable', 'Coordinador de RRHH',
                                  'Agente de seguros', 'Promotor de credito',
                                  'Asistente juridico', 'Tecnico en soporte'],
    ('Servicios', 'low'):       ['Abogado', 'Contador publico', 'Psicologo',
                                  'Trabajador social', 'Nutricionista',
                                  'Consultor de negocios', 'Economista',
                                  'Arquitecto', 'Medico general'],
    ('Tecnologia', 'high'):     ['Tecnico de redes nivel 1'],
    ('Tecnologia', 'medium'):   ['Administrador de sistemas', 'Tecnico de soporte TI',
                                  'Analista de datos junior'],
    ('Tecnologia', 'low'):      ['Desarrollador de software', 'Ingeniero de datos',
                                  'Cientifico de datos', 'Arquitecto de nube',
                                  'Especialista en ciberseguridad', 'DevOps engineer'],
    ('Educacion', 'medium'):    ['Instructor de capacitacion'],
    ('Educacion', 'low'):       ['Profesor de primaria', 'Profesor de secundaria',
                                  'Docente universitario', 'Investigador',
                                  'Director escolar', 'Psicologo educativo'],
    ('Salud', 'medium'):        ['Tecnico de laboratorio'],
    ('Salud', 'low'):           ['Medico especialista', 'Enfermero profesional',
                                  'Quimico farmaceutico', 'Radiologo', 'Cirujano'],
    ('Finanzas', 'medium'):     ['Analista financiero junior'],
    ('Finanzas', 'low'):        ['Analista financiero senior', 'Actuario',
                                  'Asesor de inversiones'],
}

workers_ref = {
    'high':   lambda: int(np.random.choice([300, 700, 1500, 3000, 7000],
                                            p=[0.30, 0.30, 0.20, 0.15, 0.05])),
    'medium': lambda: int(np.random.choice([150, 400, 900, 2000],
                                            p=[0.30, 0.35, 0.25, 0.10])),
    'low':    lambda: int(np.random.choice([60, 200, 500, 1200],
                                            p=[0.30, 0.35, 0.25, 0.10])),
}

# ------------------------------------------------------------------
# 2. Generar registros: risk primero, luego O*NET variables
# ------------------------------------------------------------------
# Calibracion de ruido para producir correlaciones objetivo:
#   cognitive = -82*risk + 92 + N(0, sigma_cog)
#   Si sigma_risk ~ 0.24, para r=-0.83: sigma_cog ~ 15
#   Para r(rti)=+0.71: rti = 80*risk + 5 + N(0, 18)
#   Para r(soc)=-0.67: social = -70*risk + 80 + N(0, 18)

SIGMA_COG  = 15   # apunta a r(cog,risk) ~ -0.83
SIGMA_RTI  = 18   # apunta a r(rti,risk) ~ +0.71
SIGMA_SOC  = 18   # apunta a r(soc,risk) ~ -0.67
SIGMA_CRE  = 20   # creatividad con menos estructura
SALARY_MIN = 5_000
SALARY_MAX = 52_000

# ------------------------------------------------------------------
# Block 3 — LLM Exposure lookup tables (sector-based, H1 pattern)
# Fuentes: Eloundou et al. 2024, Arora et al. 2025 (Moravec),
#          arXiv:2604.04464 (Dual-Factor), MIT Iceberg 2025, ILO WP121 2024
# ------------------------------------------------------------------

# gpt_exposure_score: fraccion de tareas expuestas a LLMs (Eloundou via IDB SINCO)
SECTOR_GPT = {
    'Agricultura': 0.10, 'Manufactura': 0.18, 'Construccion': 0.14,
    'Transporte':  0.22, 'Comercio':    0.50, 'Servicios':   0.70,
    'Tecnologia':  0.65, 'Educacion':   0.58, 'Salud':       0.40,
    'Finanzas':    0.75,
}

# moravec_index: exposicion teorica basada en Paradoja de Moravec (Arora 2025)
# Tecnologia y Finanzas mas altos; Agricultura/Construccion mas bajos
SECTOR_MORAVEC = {
    'Agricultura': 0.08, 'Manufactura': 0.22, 'Construccion': 0.16,
    'Transporte':  0.25, 'Comercio':    0.48, 'Servicios':    0.65,
    'Tecnologia':  0.72, 'Educacion':   0.60, 'Salud':        0.42,
    'Finanzas':    0.70,
}

# compliance_friction: fraccion del score que se pierde por regulacion/liability
# Alta en Salud/Finanzas (muy regulados), baja en Agricultura/informal
SECTOR_COMPLIANCE = {
    'Agricultura': 0.08, 'Manufactura': 0.15, 'Construccion': 0.18,
    'Transporte':  0.20, 'Comercio':    0.20, 'Servicios':    0.25,
    'Tecnologia':  0.35, 'Educacion':   0.45, 'Salud':        0.60,
    'Finanzas':    0.55,
}

# iceberg_score: valor salarial tecnicamente expuesto (MIT Iceberg Index 2025)
# Servicios admin/Finanzas son la parte "bajo el agua" — evidencia externa H1
SECTOR_ICEBERG = {
    'Agricultura': 0.08, 'Manufactura': 0.20, 'Construccion': 0.15,
    'Transporte':  0.28, 'Comercio':    0.52, 'Servicios':    0.68,
    'Tecnologia':  0.60, 'Educacion':   0.55, 'Salud':        0.45,
    'Finanzas':    0.72,
}

# Ajuste por cluster dentro del sector (trabajadores de mayor riesgo en un sector
# tienden a tener menor LLM exposure aunque esten en el mismo sector)
CLUSTER_LLM_DELTA = {'high': -0.10, 'medium': 0.00, 'low': +0.08}
CLUSTER_MORAVEC_DELTA = {'high': -0.08, 'medium': 0.00, 'low': +0.10}
CLUSTER_ICEBERG_DELTA  = {'high': -0.08, 'medium': 0.02, 'low': +0.10}
CLUSTER_FRICTION_DELTA = {'high': -0.05, 'medium': 0.00, 'low': +0.05}

# digital_access: probabilidad de que la ocupacion requiera computadora (ILO WP121)
# Factor buffer/bottleneck para contexto LATAM/Jalisco rural-informal
DIGITAL_PROB = {
    ('Tecnologia',  'high'): 1.00, ('Tecnologia',  'medium'): 1.00, ('Tecnologia',  'low'): 1.00,
    ('Finanzas',    'high'): 1.00, ('Finanzas',    'medium'): 1.00, ('Finanzas',    'low'): 1.00,
    ('Servicios',   'low'):  1.00, ('Servicios',   'medium'): 0.85, ('Servicios',   'high'): 0.30,
    ('Educacion',   'low'):  1.00, ('Educacion',   'medium'): 1.00,
    ('Salud',       'low'):  0.80, ('Salud',       'medium'): 0.50,
    ('Comercio',    'low'):  0.80, ('Comercio',    'medium'): 0.50, ('Comercio',   'high'): 0.10,
    ('Manufactura', 'low'):  0.90, ('Manufactura', 'medium'): 0.50, ('Manufactura','high'): 0.02,
    ('Construccion','medium'):0.20, ('Construccion','high'):  0.02,
    ('Transporte',  'medium'):0.30, ('Transporte',  'high'):  0.02,
    ('Agricultura', 'high'): 0.02,
}

records = []
occ_id  = 1

for sector, risk_cluster, n, (r_lo, r_hi) in blocks:
    names = occ_names.get((sector, risk_cluster),
                          [f'Ocupacion {risk_cluster} {sector}'])
    for i in range(n):
        name = names[i % len(names)]

        # --- Riesgo: uniforme dentro del rango del cluster ---
        risk = float(np.clip(np.random.uniform(r_lo, r_hi) +
                              np.random.normal(0, 0.03), 0.05, 0.95))

        # --- O*NET variables como funcion lineal del riesgo + ruido ---
        cog = float(np.clip(-82 * risk + 92 + np.random.normal(0, SIGMA_COG),  5, 96))
        rti = float(np.clip( 80 * risk +  5 + np.random.normal(0, SIGMA_RTI),  4, 96))
        soc = float(np.clip(-70 * risk + 80 + np.random.normal(0, SIGMA_SOC),  5, 96))
        cre = float(np.clip(-55 * risk + 78 + np.random.normal(0, SIGMA_CRE),  5, 96))
        man = float(np.clip( 70 * risk + 10 + np.random.normal(0, 10),          5, 96))

        # --- Perfil ENOE: educacion e ingreso correlacionados con riesgo ---
        edu_raw  = -3.5 * risk + 5.8 + np.random.normal(0, 0.6)
        edu_level = int(np.clip(round(edu_raw), 1, 6))

        salary_raw = (-38_000 * risk + 47_000 +
                      np.random.normal(0, 9_000))
        salary = float(np.clip(salary_raw, SALARY_MIN, SALARY_MAX))

        workers = workers_ref[risk_cluster]()

        # --- Block 3 — LLM Exposure (sector-based, independiente de automation_risk) ---

        # gpt_exposure_score: Eloundou et al. 2024, crosswalk SOC->SINCO via IDB 2024
        gpt = float(np.clip(
            SECTOR_GPT[sector] + CLUSTER_LLM_DELTA[risk_cluster]
            + np.random.normal(0, 0.06),
            0.01, 0.99
        ))

        # moravec_index: Arora et al. 2025 — teoria pura, sin sesgo de modelo anotador
        moravec = float(np.clip(
            SECTOR_MORAVEC[sector] + CLUSTER_MORAVEC_DELTA[risk_cluster]
            + np.random.normal(0, 0.05),
            0.01, 0.99
        ))

        # dual_factor_score: factibilidad tecnica x (1 - compliance_friction)
        # Servicios informal = alta factibilidad + baja friccion = mayor riesgo real
        friction = float(np.clip(
            SECTOR_COMPLIANCE[sector] + CLUSTER_FRICTION_DELTA[risk_cluster], 0.0, 0.9
        ))
        dual = float(np.clip(
            gpt * (1.0 - friction) + np.random.normal(0, 0.04),
            0.01, 0.99
        ))

        # iceberg_score: MIT Iceberg Index 2025 — valor salarial expuesto (skills-centered)
        iceberg = float(np.clip(
            SECTOR_ICEBERG[sector] + CLUSTER_ICEBERG_DELTA[risk_cluster]
            + np.random.normal(0, 0.05),
            0.01, 0.99
        ))

        # digital_access: requiere computadora? (ILO WP121 2024) — buffer/bottleneck LATAM
        da_prob   = DIGITAL_PROB.get((sector, risk_cluster), 0.10)
        digital   = int(np.random.random() < da_prob)

        records.append({
            'occupation_id':      occ_id,
            'occupation_name':    name,
            'sector':             sector,
            'routine_index':      round(rti, 4),
            'cognitive_demand':   round(cog, 4),
            'social_interaction': round(soc, 4),
            'creativity':         round(cre, 4),
            'manual_dexterity':   round(man, 4),
            'education_level':    edu_level,
            'avg_salary_mxn':     round(salary, 2),
            'workers_jalisco':    workers,
            'automation_risk':    round(risk, 6),
            # Block 3 — LLM Exposure
            'gpt_exposure_score': round(gpt, 4),
            'moravec_index':      round(moravec, 4),
            'dual_factor_score':  round(dual, 4),
            'iceberg_score':      round(iceberg, 4),
            'digital_access':     digital,
        })
        occ_id += 1

df = pd.DataFrame(records)

# ------------------------------------------------------------------
# 3. Verificacion de correlaciones y distribucion
# ------------------------------------------------------------------
print('=== CORRELACIONES Block 2 — O*NET (target vs actual) ===')
targets_b2 = {
    'cognitive_demand':   -0.83,
    'routine_index':      +0.71,
    'social_interaction': -0.67,
    'education_level':    -0.66,
    'avg_salary_mxn':     -0.62,
}
all_ok = True
for col, target in targets_b2.items():
    actual = df[col].corr(df['automation_risk'])
    ok = abs(actual - target) < 0.10
    if not ok:
        all_ok = False
    status = 'OK  ' if ok else 'WARN'
    print(f'  [{status}] {col:<22}: target={target:+.2f} | actual={actual:+.4f}')

print()
print('=== CORRELACIONES Block 3 — LLM Exposure (H1: deben ser NEGATIVAS con automation_risk) ===')
targets_b3 = {
    'gpt_exposure_score': -0.60,
    'moravec_index':      -0.55,
    'dual_factor_score':  -0.45,
    'iceberg_score':      -0.60,
    'digital_access':     -0.50,
}
for col, target in targets_b3.items():
    actual = df[col].corr(df['automation_risk'])
    ok = actual < -0.30  # umbral minimo para que el patron H1 sea valido
    if not ok:
        all_ok = False
    status = 'OK  ' if ok else 'WARN'
    print(f'  [{status}] {col:<22}: target={target:+.2f} | actual={actual:+.4f}')

print()
print('=== LLM GAP por sector (evidencia H1) ===')
sector_summary = df.groupby('sector')[['automation_risk', 'gpt_exposure_score', 'iceberg_score']].mean().round(3)
sector_summary['llm_gap'] = (sector_summary['gpt_exposure_score'] - sector_summary['automation_risk']).round(3)
sector_summary = sector_summary.sort_values('llm_gap', ascending=False)
print(sector_summary.to_string())
print()
print('H1 evidence: sectores con llm_gap POSITIVO = mayor exposicion LLM que Frey-Osborne')
print('             (reclasificacion de Medio->Alto al agregar Block 3)')

print()
print('=== DISTRIBUCION DE RIESGO ===')
bins   = [0, 0.30, 0.42, 0.60, 0.72, 1.0]
labels = ['<0.30 (Bajo)', '0.30-0.42', '0.42-0.60', '0.60-0.72', '>0.72 (Alto)']
df['bin'] = pd.cut(df['automation_risk'], bins=bins, labels=labels)
dist = df['bin'].value_counts().sort_index()
print(dist)
bimodal = (dist.iloc[0] + dist.iloc[-1]) > (dist.iloc[1] + dist.iloc[2] + dist.iloc[3])
print(f'Bimodal: {"SI" if bimodal else "NO"} (picos extremos > zona media)')

print()
print('=== RIESGO PROMEDIO POR SECTOR ===')
print(df.groupby('sector')['automation_risk'].mean().sort_values(ascending=False).round(3))

# ------------------------------------------------------------------
# 4. Guardar CSV
# ------------------------------------------------------------------
out_path = os.path.join(os.path.dirname(__file__), 'data', 'occupations_sample.csv')
df.drop(columns=['bin']).to_csv(out_path, index=False)
print(f'\nCSV guardado: {out_path}  ({len(df)} ocupaciones)')
