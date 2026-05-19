"""
06_run_models.py — Regresion jerarquica M1 → M4.

M1: Block 1 (ENOE sociolaboral)
M2: Block 1 + Block 2 (O*NET task profile)
M3: Block 1 + Block 2 + Block 3 (LLM Exposure)
M4: Block 1 + Block 2 + Block 3 + Block 4 (IRA — incentivo economico)

Genera: comparacion_modelos.png, shap_block3.png
Imprime todos los metricas para actualizar el reporte.

Nota metodologica: M2/M3/M4 incluyen variables O*NET que son la base del
target (automation_risk = f(frey_osborne) = f(O*NET)). Esto genera R² alto
artificial en M2. Se documenta como referencia y upper-bound metodologico.
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine, text
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score

np.random.seed(42)
BASE = os.path.dirname(__file__)
NAVY, AMBER = '#1F497D', '#D48C00'

# ==================================================================
# 1. Cargar datos desde la vista completa
# ==================================================================
engine = create_engine(
    'mssql+pyodbc://localhost,1433/ai_automation_risk_jalisco'
    '?driver=ODBC+Driver+17+for+SQL+Server'
    '&trusted_connection=yes&TrustServerCertificate=yes'
)
with engine.connect() as conn:
    df = pd.read_sql(text('SELECT * FROM dbo.vista_riesgo_jalisco'), conn)

print(f'Datos cargados: {len(df):,} registros | {len(df.columns)} columnas')
print(f'Columnas: {list(df.columns)}')
print(f'\nTarget automation_risk: mean={df.automation_risk.mean():.3f} std={df.automation_risk.std():.3f}')
print(f'Riesgo_categoria: {df.riesgo_categoria.value_counts().to_dict()}')

# ==================================================================
# 2. Preprocesamiento
# ==================================================================
le = LabelEncoder()
df['formalidad_enc'] = le.fit_transform(df['formalidad'])

ohe = OneHotEncoder(sparse_output=False, drop='first')
sector_ohe  = ohe.fit_transform(df[['sector']])
sector_cols = [f'sector_{c}' for c in ohe.categories_[0][1:]]
df_ohe = pd.DataFrame(sector_ohe, columns=sector_cols, index=df.index)
df = pd.concat([df, df_ohe], axis=1)

print(f'\nSectores OHE ({len(sector_cols)} dummies, ref={ohe.categories_[0][0]}): {sector_cols}')
print(f'urban_rural: {df.urban_rural.sum()} urbanos / {(1-df.urban_rural).sum()} rurales')
print(f'ltii mean={df.ltii.mean():.3f} | aioe mean={df.aioe.mean():.3f}')

# ==================================================================
# 3. Definir feature sets por bloque
# ==================================================================
y = df['automation_risk']

BLOCK1 = ['nivel_educativo', 'ingreso_mensual', 'edad',
           'tamanio_empresa', 'formalidad_enc', 'urban_rural'] + sector_cols

BLOCK2 = ['rti', 'cognitive_demand', 'social_interaction',
           'creativity', 'manual_dexterity']
# Nota: frey_osborne_score excluido (= base del target — leakage directo)

BLOCK3 = ['gpt_exposure_score', 'moravec_index', 'dual_factor_score',
           'iceberg_score', 'digital_access', 'ltii', 'aioe']

BLOCK4 = ['ira']

FEATURES = {
    'M1': BLOCK1,
    'M2': BLOCK1 + BLOCK2,
    'M3': BLOCK1 + BLOCK2 + BLOCK3,
    'M4': BLOCK1 + BLOCK2 + BLOCK3 + BLOCK4,
}

print('\nFeature counts por modelo:')
for m, f in FEATURES.items():
    print(f'  {m}: {len(f):>2} features  {f}')

# ==================================================================
# 4. Train/test split (70/30, random_state=42)
# ==================================================================
_, _, y_train, y_test = train_test_split(df[BLOCK1], y, test_size=0.30, random_state=42)
idx_train = y_train.index
idx_test  = y_test.index

# ==================================================================
# 5. Entrenar y evaluar M1 → M4
# ==================================================================
results = {}

print('\n' + '='*72)
print(f'{"Modelo":<6} {"N_feat":>7} {"R²_train":>10} {"R²_test":>10} '
      f'{"RMSE":>8} {"CV_R²":>10} {"Delta_R²":>10}')
print('-'*72)

prev_r2 = None
for model_name, features in FEATURES.items():
    X = df[features]
    X_train = X.loc[idx_train]
    X_test  = X.loc[idx_test]

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_sc, y_train)

    y_pred_train = model.predict(X_train_sc)
    y_pred_test  = model.predict(X_test_sc)

    r2_train = r2_score(y_train, y_pred_train)
    r2_test  = r2_score(y_test,  y_pred_test)
    rmse     = np.sqrt(mean_squared_error(y_test, y_pred_test))
    cv_r2    = cross_val_score(LinearRegression(), X_train_sc, y_train,
                                cv=5, scoring='r2').mean()
    delta    = (r2_test - prev_r2) if prev_r2 is not None else float('nan')

    results[model_name] = {
        'model': model, 'scaler': scaler, 'features': features,
        'r2_train': r2_train, 'r2_test': r2_test,
        'rmse': rmse, 'cv_r2': cv_r2, 'delta': delta,
        'y_pred': y_pred_test, 'coefs': model.coef_,
    }

    delta_str = f'{delta:+.4f}' if not np.isnan(delta) else '  base'
    print(f'{model_name:<6} {len(features):>7} {r2_train:>10.4f} {r2_test:>10.4f} '
          f'{rmse:>8.4f} {cv_r2:>10.4f} {delta_str:>10}')
    prev_r2 = r2_test

print('='*72)

# F-test incremental (M1 vs M2, M2 vs M3, M3 vs M4)
print('\nF-test incremental (significancia de cada bloque adicional):')
model_pairs = [('M1','M2','Block 2 O*NET'), ('M2','M3','Block 3 LLM'),
               ('M3','M4','Block 4 IRA')]
for m_base, m_ext, label in model_pairs:
    n      = len(y_test)
    k_base = len(results[m_base]['features'])
    k_ext  = len(results[m_ext]['features'])
    rss_base = ((y_test - results[m_base]['y_pred'])**2).sum()
    rss_ext  = ((y_test - results[m_ext]['y_pred'])**2).sum()
    delta_k  = k_ext - k_base
    f_stat   = ((rss_base - rss_ext) / delta_k) / (rss_ext / (n - k_ext - 1))
    p_val    = 1 - stats.f.cdf(f_stat, delta_k, n - k_ext - 1)
    sig      = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns'))
    print(f'  {m_base}->{m_ext} ({label}): F={f_stat:.2f}  p={p_val:.4f} {sig}')

# Coeficientes Block 3 en M3
print('\nCoeficientes Block 3 en M3 (estandarizados):')
m3 = results['M3']
b3_names = BLOCK3
b3_idx   = [m3['features'].index(b) for b in b3_names]
b3_coefs = m3['coefs'][b3_idx]
for n, c in sorted(zip(b3_names, b3_coefs), key=lambda x: x[1]):
    print(f'  {n:<25} {c:+.4f}')

# Coeficientes Block 4 en M4
print('\nCoeficiente Block 4 en M4:')
m4 = results['M4']
b4_idx  = m4['features'].index('ira')
print(f'  ira  {m4["coefs"][b4_idx]:+.4f}')

# ==================================================================
# 6. Figura — Comparacion R² M1→M4
# ==================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Regresion Jerarquica M1→M4 — Riesgo de Automatizacion Jalisco',
             fontsize=13, fontweight='bold')

# Panel 1: R² progression
model_names = list(results.keys())
r2_vals = [results[m]['r2_test'] for m in model_names]
colors_bar = [NAVY, '#4472C4', AMBER, '#C00000']
bars = axes[0].bar(model_names, r2_vals, color=colors_bar, edgecolor='white', width=0.6)
for bar, val in zip(bars, r2_vals):
    axes[0].text(bar.get_x() + bar.get_width()/2, val + 0.01,
                 f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
axes[0].set_ylabel('R² (test set 30%)')
axes[0].set_title('R² por modelo\n(cada barra agrega un bloque)')
axes[0].set_ylim(0, 1.05)
axes[0].axhline(1.0, color='gray', linestyle='--', alpha=0.5)

labels_bl = ['M1\n(Block1)', 'M2\n(+Block2\nO*NET)', 'M3\n(+Block3\nLLM)', 'M4\n(+Block4\nIRA)']
axes[0].set_xticklabels(labels_bl)

# Panel 2: Delta R²
deltas = [results[m]['delta'] for m in model_names]
delta_names  = model_names[1:]
delta_vals   = [d for d in deltas[1:]]
axes[1].bar(delta_names, delta_vals,
            color=['#4472C4', AMBER, '#C00000'], edgecolor='white', width=0.5)
for i, (name, val) in enumerate(zip(delta_names, delta_vals)):
    axes[1].text(i, val + 0.005, f'+{val:.3f}', ha='center', fontsize=10, fontweight='bold')
axes[1].set_ylabel('Delta R² (ganancia incremental)')
axes[1].set_title('Ganancia de R² por bloque adicional\n(H1: Block 3 agrega mayor ganancia)')
axes[1].set_xticklabels(['M1→M2\nBlock2', 'M2→M3\nBlock3', 'M3→M4\nBlock4'])

# Panel 3: Scatter M3 predicciones vs reales
axes[2].scatter(y_test, results['M3']['y_pred'],
                alpha=0.35, color=AMBER, s=12, edgecolors='none')
axes[2].plot([0,1],[0,1],'r--', linewidth=1.5, label='Prediccion perfecta')
axes[2].set_xlabel('automation_risk real')
axes[2].set_ylabel('Prediccion M3')
axes[2].set_title(f'M3: Predicciones vs Reales\nR²={results["M3"]["r2_test"]:.4f} | RMSE={results["M3"]["rmse"]:.4f}')
axes[2].set_xlim(0,1); axes[2].set_ylim(0,1)
axes[2].legend()

plt.tight_layout()
plt.savefig(os.path.join(BASE, 'comparacion_modelos.png'), dpi=150, bbox_inches='tight')
plt.close()
print('\n[OK] comparacion_modelos.png')

# ==================================================================
# 7. Figura — Coeficientes Block 3 en M3 (H1 evidencia)
# ==================================================================
b3_df = pd.DataFrame({'Variable': b3_names, 'Coeficiente': b3_coefs}).sort_values('Coeficiente')
fig, ax = plt.subplots(figsize=(9, 4))
colors = ['#E53935' if c > 0 else '#1E88E5' for c in b3_df['Coeficiente']]
ax.barh(b3_df['Variable'], b3_df['Coeficiente'], color=colors)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
ax.set_title('Coeficientes Block 3 en M3 (estandarizados)\n'
             'Rojo=aumenta riesgo | Azul=reduce riesgo (H1: LLM exposure → mayor riesgo)')
ax.set_xlabel('Coeficiente estandarizado')
plt.tight_layout()
plt.savefig(os.path.join(BASE, 'coeficientes_block3.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] coeficientes_block3.png')

# ==================================================================
# 8. Resumen final
# ==================================================================
print('\n' + '='*60)
print('METRICAS FINALES — actualizar en build_report.py')
print('='*60)
for m in model_names:
    r = results[m]
    delta_str = f'({r["delta"]:+.4f})' if not np.isnan(r['delta']) else '(baseline)'
    print(f'{m}: R²={r["r2_test"]:.4f}  RMSE={r["rmse"]:.4f}  '
          f'CV={r["cv_r2"]:.4f}  {delta_str}  n_feat={len(r["features"])}')
print()
print(f'urban_rural: {df.urban_rural.sum():,} urbanos ({df.urban_rural.mean()*100:.1f}%) '
      f'/ {(~df.urban_rural.astype(bool)).sum():,} rurales')
print(f'ltii mean={df.ltii.mean():.3f} | aioe mean={df.aioe.mean():.3f}')
print('='*60)
print('\nFiguras: comparacion_modelos.png, coeficientes_block3.png')
