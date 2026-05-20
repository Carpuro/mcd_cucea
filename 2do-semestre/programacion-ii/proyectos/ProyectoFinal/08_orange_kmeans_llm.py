"""
08_orange_kmeans_llm.py
Genera 4 figuras:
  orange_flow1_dist.png  — distribuciones (equivalente Orange Flujo 1)
  orange_flow2_corr.png  — correlaciones (equivalente Orange Flujo 2)
  orange_flow3_clf.png   — clasificacion RF + LR (equivalente Orange Flujo 3)
  kmeans_llm_shift.png   — cluster shift al agregar Block 3 (H1 computacional)
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.metrics import (confusion_matrix, classification_report,
                             roc_curve, auc, ConfusionMatrixDisplay)
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score

np.random.seed(42)
BASE  = os.path.dirname(__file__)
NAVY  = '#1F497D'
AMBER = '#D48C00'
sns.set_theme(style='whitegrid', palette='muted')

# ── Cargar datos ──────────────────────────────────────────────────────────────
engine = create_engine(
    'mssql+pyodbc://localhost,1433/ai_automation_risk_jalisco'
    '?driver=ODBC+Driver+17+for+SQL+Server'
    '&trusted_connection=yes&TrustServerCertificate=yes'
)
with engine.connect() as conn:
    df = pd.read_sql(text('SELECT * FROM dbo.vista_riesgo_jalisco'), conn)

print(f'Datos: {len(df):,} registros | {len(df.columns)} columnas')

# Preprocesamiento básico
le = LabelEncoder()
df['formalidad_enc'] = le.fit_transform(df['formalidad'])

ohe = OneHotEncoder(sparse_output=False, drop='first')
sector_ohe = ohe.fit_transform(df[['sector']])
sector_cols = [f'sector_{c}' for c in ohe.categories_[0][1:]]
df_ohe = pd.DataFrame(sector_ohe, columns=sector_cols, index=df.index)
df = pd.concat([df, df_ohe], axis=1)

EDU_LABELS = {1:'Sin escolaridad',2:'Primaria',3:'Secundaria',
              4:'Preparatoria',5:'Licenciatura',6:'Posgrado'}

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURA 1 — Orange Flujo 1: Distribuciones
# ═══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Flujo 1 — Análisis Exploratorio y Distribuciones',
             fontsize=13, fontweight='bold', color=NAVY)

# Panel 1: Histograma automation_risk por categoría
colors_cat = {'Alto': '#E53935', 'Medio': AMBER, 'Bajo': '#43A047'}
for cat, color in colors_cat.items():
    subset = df[df['riesgo_categoria'] == cat]['automation_risk']
    axes[0].hist(subset, bins=20, alpha=0.65, color=color, label=cat, edgecolor='white')
axes[0].set_xlabel('automation_risk (Frey-Osborne ajustado)')
axes[0].set_ylabel('Frecuencia')
axes[0].set_title('Distribución de Riesgo\npor Categoría')
axes[0].legend(title='Categoría')

# Panel 2: Box plot por nivel educativo
edu_order = sorted(df['nivel_educativo'].unique())
edu_data  = [df[df['nivel_educativo'] == e]['automation_risk'].values for e in edu_order]
bp = axes[1].boxplot(edu_data, patch_artist=True, notch=False,
                     medianprops=dict(color='white', linewidth=2))
for i, patch in enumerate(bp['boxes']):
    patch.set_facecolor(NAVY if i < 3 else AMBER)
    patch.set_alpha(0.75)
axes[1].set_xticklabels([EDU_LABELS.get(e, str(e)) for e in edu_order],
                         rotation=20, ha='right', fontsize=8)
axes[1].set_ylabel('automation_risk')
axes[1].set_title('Riesgo por Nivel Educativo\n(educación como factor protector)')

# Panel 3: Scatter ingreso vs riesgo
scatter_colors = df['riesgo_categoria'].map(colors_cat)
axes[2].scatter(df['ingreso_mensual'], df['automation_risk'],
                c=scatter_colors, alpha=0.35, s=12, edgecolors='none')
axes[2].set_xlabel('Ingreso mensual (MXN)')
axes[2].set_ylabel('automation_risk')
axes[2].set_title('Ingreso vs Riesgo\n(relación inversa)')
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=v, label=k) for k, v in colors_cat.items()]
axes[2].legend(handles=legend_elements, fontsize=8)

plt.tight_layout()
out1 = os.path.join(BASE, 'orange_flow1_dist.png')
plt.savefig(out1, dpi=150, bbox_inches='tight')
plt.close()
print(f'[OK] {out1}')

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURA 2 — Orange Flujo 2: Correlaciones y Mosaico
# ═══════════════════════════════════════════════════════════════════════════════
corr_cols = ['automation_risk', 'rti', 'cognitive_demand', 'social_interaction',
             'creativity', 'nivel_educativo', 'ingreso_mensual', 'ira',
             'gpt_exposure_score', 'moravec_index', 'dual_factor_score',
             'iceberg_score', 'digital_access']
corr_labels = {
    'automation_risk': 'Riesgo (target)',
    'rti': 'RTI',
    'cognitive_demand': 'Cognitivo',
    'social_interaction': 'Interacción',
    'creativity': 'Creatividad',
    'nivel_educativo': 'Educación',
    'ingreso_mensual': 'Ingreso',
    'ira': 'IRA',
    'gpt_exposure_score': 'GPT Exposure',
    'moravec_index': 'Moravec',
    'dual_factor_score': 'Dual-Factor',
    'iceberg_score': 'Iceberg',
    'digital_access': 'Digital Access',
}

corr_matrix = df[corr_cols].corr()
corr_matrix.index   = [corr_labels[c] for c in corr_cols]
corr_matrix.columns = [corr_labels[c] for c in corr_cols]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Flujo 2 — Correlaciones Block 2 + Block 3 y Formalidad × Riesgo',
             fontsize=13, fontweight='bold', color=NAVY)

# Panel 1: Heatmap
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, ax=axes[0], mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, vmin=-1, vmax=1,
            annot_kws={'size': 7}, linewidths=0.4)
axes[0].set_title('Mapa de Correlaciones\n(Block 2 O*NET + Block 3 LLM Exposure)')
axes[0].tick_params(axis='x', rotation=30, labelsize=8)
axes[0].tick_params(axis='y', rotation=0, labelsize=8)

# Panel 2: Box plot formalidad × riesgo (equivalente Mosaic Display)
formal_data = {
    label: df[df['formalidad'] == label]['automation_risk'].values
    for label in ['Formal', 'Informal']
}
bp2 = axes[1].boxplot(formal_data.values(), patch_artist=True,
                      labels=formal_data.keys(),
                      medianprops=dict(color='white', linewidth=2.5),
                      notch=True)
bp2['boxes'][0].set_facecolor(NAVY)
bp2['boxes'][0].set_alpha(0.8)
bp2['boxes'][1].set_facecolor(AMBER)
bp2['boxes'][1].set_alpha(0.8)

for cat, color in [('Alto','#E53935'),('Medio',AMBER),('Bajo','#43A047')]:
    for form in ['Formal', 'Informal']:
        sub = df[(df['formalidad'] == form) & (df['riesgo_categoria'] == cat)]['automation_risk']
        x_pos = 1 if form == 'Formal' else 2
        axes[1].scatter(np.full(len(sub), x_pos) + np.random.uniform(-0.12, 0.12, len(sub)),
                        sub, alpha=0.25, s=6, color=color, edgecolors='none')
n_formal   = (df['formalidad'] == 'Formal').sum()
n_informal = (df['formalidad'] == 'Informal').sum()
axes[1].set_xticklabels([f'Formal\n(n={n_formal:,})', f'Informal\n(n={n_informal:,})'])
axes[1].set_ylabel('automation_risk')
axes[1].set_title('Formalidad × Distribución de Riesgo\n(informal amplifica riesgo LLM real)')

plt.tight_layout()
out2 = os.path.join(BASE, 'orange_flow2_corr.png')
plt.savefig(out2, dpi=150, bbox_inches='tight')
plt.close()
print(f'[OK] {out2}')

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURA 3 — Orange Flujo 3: Clasificacion (Random Forest + Logistic Regression)
# ═══════════════════════════════════════════════════════════════════════════════
features_clf = ['nivel_educativo', 'ingreso_mensual', 'edad', 'tamanio_empresa',
                'formalidad_enc', 'ira', 'rti', 'cognitive_demand',
                'social_interaction', 'creativity',
                'gpt_exposure_score', 'moravec_index',
                'dual_factor_score', 'iceberg_score', 'digital_access'] + sector_cols
y_cat = df['riesgo_categoria']

X_clf = df[features_clf]
X_tr, X_te, y_tr, y_te = train_test_split(X_clf, y_cat, test_size=0.30,
                                            random_state=42, stratify=y_cat)
scaler_clf = StandardScaler()
X_tr_sc = scaler_clf.fit_transform(X_tr)
X_te_sc  = scaler_clf.transform(X_te)

rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
lr = LogisticRegression(max_iter=1000, random_state=42)

rf.fit(X_tr_sc, y_tr)
lr.fit(X_tr_sc, y_tr)

rf_acc = rf.score(X_te_sc, y_te)
lr_acc = lr.score(X_te_sc, y_te)

rf_cv = cross_val_score(rf, X_tr_sc, y_tr, cv=5, scoring='accuracy').mean()
lr_cv = cross_val_score(lr, X_tr_sc, y_tr, cv=5, scoring='accuracy').mean()

print(f'\nRandom Forest  — Accuracy: {rf_acc:.4f}  CV-5: {rf_cv:.4f}')
print(f'Logistic Regr. — Accuracy: {lr_acc:.4f}  CV-5: {lr_cv:.4f}')
print('\nRF Classification Report:')
print(classification_report(y_te, rf.predict(X_te_sc)))

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Flujo 3 — Modelo Predictivo: Random Forest vs Regresión Logística',
             fontsize=13, fontweight='bold', color=NAVY)

# Panel 1: Accuracy comparison
models = ['Random\nForest', 'Regresion\nLogistica']
accs   = [rf_acc, lr_acc]
cv_accs = [rf_cv, lr_cv]
x = np.arange(2)
w = 0.35
bars1 = axes[0].bar(x - w/2, accs,   w, label='Test (30%)', color=NAVY,  alpha=0.85)
bars2 = axes[0].bar(x + w/2, cv_accs, w, label='CV-5',      color=AMBER, alpha=0.85)
for bar, val in zip(list(bars1) + list(bars2), accs + cv_accs):
    axes[0].text(bar.get_x() + bar.get_width()/2, val + 0.005,
                 f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(models, fontsize=10)
axes[0].set_ylabel('Accuracy')
axes[0].set_ylim(0, 1.05)
axes[0].set_title(f'Comparacion de Accuracy\nRF={rf_acc:.3f} | LR={lr_acc:.3f}')
axes[0].legend()

# Panel 2: Confusion Matrix RF
classes = ['Alto', 'Bajo', 'Medio']
cm_rf = confusion_matrix(y_te, rf.predict(X_te_sc), labels=classes)
disp = ConfusionMatrixDisplay(confusion_matrix=cm_rf, display_labels=classes)
disp.plot(ax=axes[1], colorbar=False, cmap='Blues')
axes[1].set_title('Matriz de Confusion — Random Forest')

# Panel 3: ROC curves (one-vs-rest)
colors_roc = {'Alto': '#E53935', 'Bajo': '#43A047', 'Medio': AMBER}
for cls, color in colors_roc.items():
    y_bin  = (y_te == cls).astype(int)
    y_prob = rf.predict_proba(X_te_sc)[:, list(rf.classes_).index(cls)]
    fpr, tpr, _ = roc_curve(y_bin, y_prob)
    roc_auc     = auc(fpr, tpr)
    axes[2].plot(fpr, tpr, color=color, linewidth=2,
                 label=f'{cls} (AUC={roc_auc:.3f})')
axes[2].plot([0,1],[0,1],'k--', linewidth=1, alpha=0.5, label='Azar')
axes[2].set_xlabel('Tasa Falsos Positivos')
axes[2].set_ylabel('Tasa Verdaderos Positivos (Sensibilidad)')
axes[2].set_title('Curva ROC — Random Forest\n(One-vs-Rest por categoría)')
axes[2].legend(fontsize=9)

plt.tight_layout()
out3 = os.path.join(BASE, 'orange_flow3_clf.png')
plt.savefig(out3, dpi=150, bbox_inches='tight')
plt.close()
print(f'[OK] {out3}')

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURA 4 — K-Means LLM-aware vs original (H1 computacional)
# ═══════════════════════════════════════════════════════════════════════════════

# K-Means original (sin Block 3)
feat_orig = ['automation_risk', 'rti', 'cognitive_demand',
             'social_interaction', 'creativity',
             'nivel_educativo', 'ingreso_mensual']
X_orig = StandardScaler().fit_transform(df[feat_orig])
km_orig = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cl_orig'] = km_orig.fit_predict(X_orig)
rmap_orig = df.groupby('cl_orig')['automation_risk'].mean().sort_values()
df['cl_orig_label'] = df['cl_orig'].map(
    {rmap_orig.index[0]:'Riesgo Bajo',
     rmap_orig.index[1]:'Riesgo Medio',
     rmap_orig.index[2]:'Riesgo Alto'})

# K-Means LLM-aware (con Block 3)
feat_llm = feat_orig + ['gpt_exposure_score', 'moravec_index', 'iceberg_score']
X_llm = StandardScaler().fit_transform(df[feat_llm])
km_llm = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cl_llm'] = km_llm.fit_predict(X_llm)
rmap_llm = df.groupby('cl_llm')['automation_risk'].mean().sort_values()
df['cl_llm_label'] = df['cl_llm'].map(
    {rmap_llm.index[0]:'Riesgo Bajo',
     rmap_llm.index[1]:'Riesgo Medio',
     rmap_llm.index[2]:'Riesgo Alto'})

ari = adjusted_rand_score(df['cl_orig_label'], df['cl_llm_label'])
print(f'\nAdjusted Rand Index (cluster shift): {ari:.4f}')

cross = pd.crosstab(df['cl_orig_label'], df['cl_llm_label'],
                    rownames=['Sin Block3'], colnames=['Con Block3 (LLM-aware)'])
print('Matriz de reasignacion:')
print(cross)

# Cuantificar el cluster shift: trabajadores que cambian de Medio → Alto
orig_medio = set(df[df['cl_orig_label'] == 'Riesgo Medio'].index)
llm_alto   = set(df[df['cl_llm_label']  == 'Riesgo Alto'].index)
shift_medio_to_alto = len(orig_medio & llm_alto)
pct_shift = shift_medio_to_alto / len(orig_medio) * 100
print(f'\nCluster shift H1: {shift_medio_to_alto:,} trabajadores '
      f'({pct_shift:.1f}% del Cluster Medio) reclasifican a Riesgo Alto al agregar Block 3')

# Visualizacion PCA comparativa
pca = PCA(n_components=2, random_state=42)
X_pca_orig = pca.fit_transform(X_orig)
X_pca_llm  = pca.transform(StandardScaler().fit_transform(df[feat_orig]))

colores_cl = {'Riesgo Alto': '#E53935', 'Riesgo Medio': AMBER, 'Riesgo Bajo': '#43A047'}

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('K-Means LLM-aware vs Original — Evidencia Computacional H1\n'
             '(Cluster Medio migra hacia Riesgo Alto al incluir gpt_exposure + moravec + iceberg)',
             fontsize=12, fontweight='bold', color=NAVY)

# Panel 1: K-Means sin Block 3
for label, color in colores_cl.items():
    mask = df['cl_orig_label'] == label
    n    = mask.sum()
    axes[0].scatter(X_pca_orig[mask, 0], X_pca_orig[mask, 1],
                    c=color, label=f'{label} (n={n:,})',
                    alpha=0.5, s=15, edgecolors='none')
axes[0].set_title(f'K-Means Original (Block 2 only)\nARI vs LLM-aware: {ari:.3f}')
axes[0].set_xlabel('PC1'); axes[0].set_ylabel('PC2')
axes[0].legend(fontsize=8, markerscale=1.5)

# Panel 2: K-Means con Block 3
for label, color in colores_cl.items():
    mask = df['cl_llm_label'] == label
    n    = mask.sum()
    axes[1].scatter(X_pca_orig[mask, 0], X_pca_orig[mask, 1],
                    c=color, label=f'{label} (n={n:,})',
                    alpha=0.5, s=15, edgecolors='none')
axes[1].set_title('K-Means LLM-aware (Block 2 + Block 3)\ngpt_exposure + moravec + iceberg')
axes[1].set_xlabel('PC1'); axes[1].set_ylabel('PC2')
axes[1].legend(fontsize=8, markerscale=1.5)

# Panel 3: Sankey-style bar chart del shift
cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
cross_pct.plot(kind='bar', ax=axes[2], color=['#E53935', AMBER, '#43A047'],
               edgecolor='white', alpha=0.85)
axes[2].set_title(f'Reasignación de Clusters (H1)\n'
                  f'{shift_medio_to_alto:,} del Cluster Medio → Alto ({pct_shift:.1f}%)')
axes[2].set_xlabel('Cluster original (sin Block 3)')
axes[2].set_ylabel('% reasignado al nuevo cluster')
axes[2].set_xticklabels(cross_pct.index, rotation=15)
axes[2].legend(title='Cluster LLM-aware', fontsize=8)

plt.tight_layout()
out4 = os.path.join(BASE, 'kmeans_llm_shift.png')
plt.savefig(out4, dpi=150, bbox_inches='tight')
plt.close()
print(f'[OK] {out4}')

print('\n=== Resumen ===')
print(f'RF Accuracy: {rf_acc:.4f} | AUC Alto: ', end='')
y_bin_alto = (y_te == 'Alto').astype(int)
y_prob_alto = rf.predict_proba(X_te_sc)[:, list(rf.classes_).index('Alto')]
fpr_a, tpr_a, _ = roc_curve(y_bin_alto, y_prob_alto)
print(f'{auc(fpr_a, tpr_a):.4f}')
print(f'LR Accuracy: {lr_acc:.4f}')
print(f'Cluster shift: {shift_medio_to_alto:,} ({pct_shift:.1f}%) Medio → Alto con Block 3')
print(f'\nFiguras generadas: orange_flow1_dist.png, orange_flow2_corr.png, '
      f'orange_flow3_clf.png, kmeans_llm_shift.png')
