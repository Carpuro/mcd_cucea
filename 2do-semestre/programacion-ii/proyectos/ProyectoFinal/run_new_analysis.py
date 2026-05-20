"""Ejecuta el analisis M1→M4 + importance + profiling y genera los PNGs."""
import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine, text
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.inspection import permutation_importance
from sklearn.cluster import KMeans
from scipy import stats as scipy_stats

np.random.seed(42)
BASE  = os.path.dirname(__file__)
NAVY  = '#1F497D'
AMBER = '#D48C00'
sns.set_theme(style='whitegrid', palette='muted')

engine = create_engine(
    'mssql+pyodbc://localhost,1433/ai_automation_risk_jalisco'
    '?driver=ODBC+Driver+17+for+SQL+Server'
    '&trusted_connection=yes&TrustServerCertificate=yes'
)
with engine.connect() as conn:
    df = pd.read_csv if False else None
    df = pd.read_sql(text('SELECT * FROM dbo.vista_riesgo_jalisco'), conn)

print(f'Datos: {len(df):,} registros')

le = LabelEncoder()
df['formalidad_enc'] = le.fit_transform(df['formalidad'])
ohe = OneHotEncoder(sparse_output=False, drop='first')
sector_ohe = ohe.fit_transform(df[['sector']])
sector_cols = [f'sector_{c}' for c in ohe.categories_[0][1:]]
df = pd.concat([df, pd.DataFrame(sector_ohe, columns=sector_cols, index=df.index)], axis=1)

# ── Feature sets ──────────────────────────────────────────────────────────────
B1 = ['nivel_educativo', 'ingreso_mensual', 'edad',
      'tamanio_empresa', 'formalidad_enc'] + sector_cols
B2 = ['rti', 'cognitive_demand', 'social_interaction', 'creativity']
B3 = ['gpt_exposure_score', 'moravec_index', 'dual_factor_score',
      'iceberg_score', 'digital_access']
B4 = ['ira']

MODELS = {'M1': B1, 'M2': B1+B2, 'M3': B1+B2+B3, 'M4': B1+B2+B3+B4}
y = df['automation_risk']

idx_tr, idx_te = train_test_split(df.index, test_size=0.30, random_state=42)

# ── Fit M1→M4 ─────────────────────────────────────────────────────────────────
results = {}
prev_r2 = None
print(f"\n{'Modelo':<6} {'N_feat':>7} {'R²_train':>10} {'R²_test':>10} {'RMSE':>8} {'CV_R²':>10} {'Delta':>10}")
print('-'*68)
for name, feats in MODELS.items():
    sc = StandardScaler().fit(df.loc[idx_tr, feats])
    Xtr = sc.transform(df.loc[idx_tr, feats])
    Xte = sc.transform(df.loc[idx_te, feats])
    ytr, yte = y.loc[idx_tr], y.loc[idx_te]
    m = LinearRegression().fit(Xtr, ytr)
    yhat = m.predict(Xte)
    r2_tr = r2_score(ytr, m.predict(Xtr))
    r2_te = r2_score(yte, yhat)
    rmse  = np.sqrt(mean_squared_error(yte, yhat))
    cv    = cross_val_score(LinearRegression(), Xtr, ytr, cv=5, scoring='r2').mean()
    delta = (r2_te - prev_r2) if prev_r2 is not None else float('nan')
    results[name] = dict(sc=sc, m=m, feats=feats, r2_tr=r2_tr, r2_te=r2_te,
                         rmse=rmse, cv=cv, yhat=yhat, yte=yte, coefs=m.coef_)
    prev_r2 = r2_te
    ds = f'{delta:+.4f}' if not np.isnan(delta) else '  base'
    print(f'{name:<6} {len(feats):>7} {r2_tr:>10.4f} {r2_te:>10.4f} {rmse:>8.4f} {cv:>10.4f} {ds:>10}')
print('='*68)

# F-tests
print('\nF-test incremental:')
for base, ext, label in [('M1','M2','Block2 O*NET'),('M2','M3','Block3 LLM'),('M3','M4','Block4 IRA')]:
    n = len(results[base]['yte'])
    kb, ke = len(results[base]['feats']), len(results[ext]['feats'])
    rb = ((results[base]['yte'] - results[base]['yhat'])**2).sum()
    re = ((results[ext]['yte']  - results[ext]['yhat'])**2).sum()
    f  = ((rb-re)/(ke-kb)) / (re/(n-ke-1))
    p  = 1 - scipy_stats.f.cdf(f, ke-kb, n-ke-1)
    sig = '***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else 'ns'))
    print(f'  {base}->{ext} ({label}): F={f:.2f}  p={p:.4f}  {sig}')

# ── Fig 1: M1→M4 comparison ───────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Regresion Jerarquica M1→M4', fontsize=13, fontweight='bold')
names = list(results.keys())
r2s   = [results[m]['r2_te'] for m in names]
bars  = axes[0].bar(names, r2s, color=[NAVY,'#4472C4',AMBER,'#C00000'], edgecolor='white', width=0.6)
for bar, v in zip(bars, r2s):
    axes[0].text(bar.get_x()+bar.get_width()/2, v+0.01, f'{v:.3f}', ha='center', fontweight='bold')
axes[0].set_ylim(0,1.05); axes[0].set_ylabel('R² (test 30%)')
axes[0].set_title('R² por modelo')
axes[0].set_xticklabels(['M1\n(B1)','M2\n(+B2)','M3\n(+B3)','M4\n(+B4)'])

dvals = [results['M2']['r2_te']-results['M1']['r2_te'],
         results['M3']['r2_te']-results['M2']['r2_te'],
         results['M4']['r2_te']-results['M3']['r2_te']]
bars2 = axes[1].bar(['M1→M2\n+B2','M2→M3\n+B3','M3→M4\n+B4'], dvals,
                    color=['#4472C4',AMBER,'#C00000'], edgecolor='white')
for bar, v in zip(bars2, dvals):
    axes[1].text(bar.get_x()+bar.get_width()/2, v+0.001, f'+{v:.4f}', ha='center', fontweight='bold')
axes[1].set_ylabel('Delta R²'); axes[1].set_title('Ganancia incremental\n(H1: Block 3 es significativo)')

axes[2].scatter(results['M3']['yte'], results['M3']['yhat'], alpha=0.35, color=AMBER, s=12)
axes[2].plot([0,1],[0,1],'r--', linewidth=1.5)
axes[2].set_xlim(0,1); axes[2].set_ylim(0,1)
axes[2].set_xlabel('Real'); axes[2].set_ylabel('Prediccion M3')
axes[2].set_title(f'M3: Real vs Prediccion\nR²={results["M3"]["r2_te"]:.4f}')

plt.tight_layout()
out = os.path.join(BASE, 'comparacion_m1m4_completa.png')
plt.savefig(out, dpi=150, bbox_inches='tight'); plt.close()
print(f'\n[OK] {out}')

# ── Fig 2: Permutation importance M1 vs M3 ───────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Permutation Importance — M1 vs M3', fontsize=13, fontweight='bold')
for ax, mname, title in zip(axes, ['M1','M3'],
                             ['M1 — Block 1 (ENOE)','M3 — Block 1+2+3']):
    r = results[mname]
    Xte = r['sc'].transform(df.loc[idx_te, r['feats']])
    yte = df.loc[idx_te, 'automation_risk']
    perm = permutation_importance(r['m'], Xte, yte, n_repeats=15, random_state=42, scoring='r2')
    sidx = np.argsort(perm.importances_mean)
    labels = [f.replace('sector_','sec_').replace('formalidad_enc','formal')
              for f in np.array(r['feats'])[sidx]]
    colors = ['#E53935' if v > 0 else '#BDBDBD' for v in perm.importances_mean[sidx]]
    ax.barh(labels, perm.importances_mean[sidx], xerr=perm.importances_std[sidx],
            color=colors, error_kw=dict(ecolor='#555', capsize=2), height=0.7)
    ax.axvline(0, color='black', lw=0.8, ls='--')
    ax.set_xlabel('Caida en R² al aleatorizar'); ax.set_title(title)
plt.tight_layout()
out = os.path.join(BASE, 'permutation_importance.png')
plt.savefig(out, dpi=150, bbox_inches='tight'); plt.close()
print(f'[OK] {out}')

# ── Fig 3: Radar chart clusters ───────────────────────────────────────────────
feat_orig = ['automation_risk','rti','cognitive_demand','social_interaction',
             'creativity','nivel_educativo','ingreso_mensual']
X_km = StandardScaler().fit_transform(df[feat_orig])
km   = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cluster'] = km.fit_predict(X_km)
rmap = df.groupby('cluster')['automation_risk'].mean().sort_values()
df['cluster_label'] = df['cluster'].map({rmap.index[0]:'Riesgo Bajo',
                                          rmap.index[1]:'Riesgo Medio',
                                          rmap.index[2]:'Riesgo Alto'})

radar_vars = ['automation_risk','rti','cognitive_demand','social_interaction',
              'creativity','gpt_exposure_score','moravec_index','digital_access']
radar_lbl  = ['Riesgo','RTI','Cognitivo','Social','Creatividad','GPT Exp.','Moravec','Digital']
profile    = df.groupby('cluster_label')[radar_vars].mean()
radar_norm = (profile - profile.min()) / (profile.max() - profile.min())

N = len(radar_vars)
angles = [n/float(N)*2*np.pi for n in range(N)] + [0]
fig, ax = plt.subplots(figsize=(8,8), subplot_kw=dict(polar=True))
for cl, color in [('Riesgo Alto','#E53935'),('Riesgo Medio',AMBER),('Riesgo Bajo','#43A047')]:
    if cl not in radar_norm.index: continue
    vals = radar_norm.loc[cl].tolist() + [radar_norm.loc[cl].tolist()[0]]
    ax.plot(angles, vals, 'o-', lw=2, color=color, label=cl)
    ax.fill(angles, vals, alpha=0.12, color=color)
ax.set_xticks(angles[:-1]); ax.set_xticklabels(radar_lbl, fontsize=10)
ax.set_yticks([0.25,0.5,0.75]); ax.set_yticklabels(['25%','50%','75%'], fontsize=8)
ax.set_title('Perfil de Clusters — Radar Chart\n(variables normalizadas)',
             fontsize=12, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.35,1.1), fontsize=10)
plt.tight_layout()
out = os.path.join(BASE, 'cluster_radar.png')
plt.savefig(out, dpi=150, bbox_inches='tight'); plt.close()
print(f'[OK] {out}')

# ── Fig 4: Sector × Cluster heatmap ──────────────────────────────────────────
sc_cross = pd.crosstab(df['sector'], df['cluster_label'], normalize='index') * 100
sc_cross  = sc_cross.reindex(columns=['Riesgo Bajo','Riesgo Medio','Riesgo Alto'])
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(sc_cross, annot=True, fmt='.1f', cmap='RdYlGn_r', ax=ax,
            linewidths=0.4, cbar_kws={'label':'% del sector en cada cluster'})
ax.set_title('Distribucion de Clusters por Sector (%)\n'
             '¿En qué cluster cae cada sector?', fontsize=11, fontweight='bold')
ax.set_xlabel('Cluster'); ax.set_ylabel('Sector')
plt.tight_layout()
out = os.path.join(BASE, 'sector_cluster_heatmap.png')
plt.savefig(out, dpi=150, bbox_inches='tight'); plt.close()
print(f'[OK] {out}')

print('\n=== Resumen M1→M4 ===')
for n in ['M1','M2','M3','M4']:
    r = results[n]
    print(f'{n}: R²={r["r2_te"]:.4f}  RMSE={r["rmse"]:.4f}  CV={r["cv"]:.4f}')
print('\nFiguras: comparacion_m1m4_completa.png, permutation_importance.png, cluster_radar.png, sector_cluster_heatmap.png')
