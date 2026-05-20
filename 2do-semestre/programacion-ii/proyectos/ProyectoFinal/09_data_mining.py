"""
09_data_mining.py — Mineria de datos completa
  1. Arbol de Decision (CART) — reglas interpretables de clasificacion
  2. Reglas de Asociacion (Apriori) — patrones en variables categoricas
  3. Comparacion de clasificadores (DT / RF / LR / GBM / NB)
  4. Figuras: arbol_decision.png, reglas_asociacion.png, comparacion_clf.png
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine, text
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                              recall_score, roc_auc_score, classification_report)

np.random.seed(42)
BASE  = os.path.dirname(__file__)
NAVY  = '#1F497D'
AMBER = '#D48C00'
sns.set_theme(style='whitegrid')

# ── Cargar datos ──────────────────────────────────────────────────────────────
engine = create_engine(
    'mssql+pyodbc://localhost,1433/ai_automation_risk_jalisco'
    '?driver=ODBC+Driver+17+for+SQL+Server'
    '&trusted_connection=yes&TrustServerCertificate=yes'
)
with engine.connect() as conn:
    df = pd.read_sql(text('SELECT * FROM dbo.vista_riesgo_jalisco'), conn)

le = LabelEncoder()
df['formalidad_enc'] = le.fit_transform(df['formalidad'])
ohe = OneHotEncoder(sparse_output=False, drop='first')
sector_ohe  = ohe.fit_transform(df[['sector']])
sector_cols = [f'sector_{c}' for c in ohe.categories_[0][1:]]
df = pd.concat([df, pd.DataFrame(sector_ohe, columns=sector_cols, index=df.index)], axis=1)

# Features y target
ALL_FEATS = (['nivel_educativo','ingreso_mensual','edad','tamanio_empresa',
              'formalidad_enc'] + sector_cols +
             ['rti','cognitive_demand','social_interaction','creativity'] +
             ['gpt_exposure_score','moravec_index','dual_factor_score',
              'iceberg_score','digital_access','ira'])

X = df[ALL_FEATS]
y = df['riesgo_categoria']

sc = StandardScaler()
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.30,
                                            random_state=42, stratify=y)
X_tr_sc = sc.fit_transform(X_tr)
X_te_sc  = sc.transform(X_te)

print(f'Datos: {len(df):,} | Train: {len(X_tr):,} | Test: {len(X_te):,}')
print(f'Clases: {y.value_counts().to_dict()}')

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ÁRBOL DE DECISION (CART)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n── Arbol de Decision ──')

# Arbol profundo para metricas
dt_full = DecisionTreeClassifier(max_depth=6, min_samples_leaf=20,
                                  class_weight='balanced', random_state=42)
dt_full.fit(X_tr_sc, y_tr)
dt_acc = dt_full.score(X_te_sc, y_te)
dt_f1  = f1_score(y_te, dt_full.predict(X_te_sc), average='weighted')
print(f'DT profundo (depth=6): Accuracy={dt_acc:.4f}  F1={dt_f1:.4f}')

# Arbol simple (depth=4) para visualizar
dt_vis = DecisionTreeClassifier(max_depth=4, min_samples_leaf=30,
                                 class_weight='balanced', random_state=42)
dt_vis.fit(X_tr_sc, y_tr)
print(f'DT visual  (depth=4): Accuracy={dt_vis.score(X_te_sc,y_te):.4f}')

# Feature names legibles
feat_names = []
for f in ALL_FEATS:
    if f.startswith('sector_'): feat_names.append(f.replace('sector_','s_'))
    elif f == 'formalidad_enc': feat_names.append('formal')
    elif f == 'nivel_educativo': feat_names.append('edu')
    elif f == 'ingreso_mensual': feat_names.append('ingreso')
    elif f == 'tamanio_empresa': feat_names.append('tamano')
    elif f == 'gpt_exposure_score': feat_names.append('gpt_exp')
    elif f == 'moravec_index': feat_names.append('moravec')
    elif f == 'dual_factor_score': feat_names.append('dual_f')
    elif f == 'iceberg_score': feat_names.append('iceberg')
    elif f == 'digital_access': feat_names.append('digital')
    elif f == 'cognitive_demand': feat_names.append('cognitivo')
    elif f == 'social_interaction': feat_names.append('social')
    else: feat_names.append(f)

# Reglas de texto
rules_text = export_text(dt_vis, feature_names=feat_names, max_depth=3)
print('\nReglas del arbol (depth=3):')
print(rules_text[:1500])

# Visualizacion del arbol
fig, ax = plt.subplots(figsize=(20, 9))
plot_tree(dt_vis, feature_names=feat_names,
          class_names=dt_vis.classes_,
          filled=True, rounded=True, fontsize=7,
          impurity=True, proportion=True, ax=ax,
          precision=3)
ax.set_title('Arbol de Decision (CART, depth=4) — Clasificacion de Riesgo de Automatizacion\n'
             'Jalisco 2024 | Entrenado con Block 1+2+3',
             fontsize=12, fontweight='bold', color=NAVY)
plt.tight_layout()
out = os.path.join(BASE, 'arbol_decision.png')
plt.savefig(out, dpi=130, bbox_inches='tight')
plt.close()
print(f'[OK] {out}')

# Importancia de features del arbol
dt_imp = pd.DataFrame({
    'Feature': feat_names,
    'Importance': dt_full.feature_importances_
}).sort_values('Importance', ascending=False).head(12)
print('\nTop 12 features en DT:')
print(dt_imp.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(dt_imp['Feature'][::-1], dt_imp['Importance'][::-1],
               color=NAVY, alpha=0.85)
ax.set_xlabel('Importancia (reduccion de Gini ponderada)')
ax.set_title('Importancia de Variables — Arbol de Decision (CART)\nTop 12 features',
             fontsize=11, fontweight='bold', color=NAVY)
plt.tight_layout()
out_imp = os.path.join(BASE, 'arbol_importancia.png')
plt.savefig(out_imp, dpi=150, bbox_inches='tight')
plt.close()
print(f'[OK] {out_imp}')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. REGLAS DE ASOCIACION (Apriori manual sobre variables categoricas)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n── Reglas de Asociacion ──')

# Discretizar variables para Apriori
df_disc = df.copy()

df_disc['edu_cat'] = pd.cut(df['nivel_educativo'],
    bins=[0,2,3,4,6], labels=['Sin_Sec','Secundaria','Prepa','Superior'])

df_disc['ingreso_cat'] = pd.cut(df['ingreso_mensual'],
    bins=[0,5000,10000,20000,99999],
    labels=['Bajo(<5k)','Medio(5-10k)','Alto(10-20k)','Muy_Alto(>20k)'])

df_disc['edad_cat'] = pd.cut(df['edad'],
    bins=[14,30,45,60,100], labels=['Joven(15-30)','Adulto(31-45)','Maduro(46-60)','Senior(61+)'])

df_disc['gpt_cat'] = pd.cut(df['gpt_exposure_score'],
    bins=[0,0.4,0.6,1.0], labels=['LLM_Bajo','LLM_Medio','LLM_Alto'])

cat_cols = ['sector','formalidad','edu_cat','ingreso_cat','edad_cat','gpt_cat','riesgo_categoria']

# Implementar Apriori manual
def apriori_rules(df_cat, cols, min_support=0.05, min_confidence=0.60, min_lift=1.5):
    """Genera reglas de asociacion 2-item desde variables categoricas."""
    records = df_cat[cols].dropna().astype(str)
    n = len(records)

    # Items individuales con su soporte
    item_support = {}
    for col in cols:
        for val in records[col].unique():
            key = f'{col}={val}'
            item_support[key] = (records[col] == val).sum() / n

    # Reglas: antecedente (col_a=val_a) → consecuente (riesgo=X)
    rules = []
    target_col = 'riesgo_categoria'
    for target_val in records[target_col].unique():
        target_mask = records[target_col] == target_val
        for col in [c for c in cols if c != target_col]:
            for val in records[col].unique():
                ant_mask = records[col] == val
                sup_ant  = ant_mask.sum() / n
                sup_both = (ant_mask & target_mask).sum() / n
                if sup_ant < min_support or sup_both < min_support:
                    continue
                confidence = sup_both / sup_ant
                lift = confidence / (target_mask.sum() / n)
                if confidence >= min_confidence and lift >= min_lift:
                    rules.append({
                        'Antecedente': f'{col}={val}',
                        'Consecuente': f'riesgo={target_val}',
                        'Soporte': round(sup_both, 3),
                        'Confianza': round(confidence, 3),
                        'Lift': round(lift, 3),
                        'N': int(sup_both * n),
                    })
    return pd.DataFrame(rules).sort_values('Lift', ascending=False)

rules_df = apriori_rules(df_disc, cat_cols, min_support=0.02,
                          min_confidence=0.40, min_lift=1.2)
print(f'\nReglas encontradas: {len(rules_df)}')
print('\nTop 15 reglas por Lift:')
print(rules_df.head(15).to_string(index=False))

# Visualizacion: scatter soporte vs confianza, coloreado por lift
if len(rules_df) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Reglas de Asociacion — Patrones en Caracteristicas de Trabajadores\n'
                 'Mineria de datos sobre sector, formalidad, educacion, ingreso, edad, LLM exposure y riesgo',
                 fontsize=12, fontweight='bold', color=NAVY)

    # Panel izq: scatter support vs confidence
    risk_colors = {'riesgo=Alto':'#E53935','riesgo=Medio':AMBER,'riesgo=Bajo':'#43A047'}
    for risk_cat, color in risk_colors.items():
        mask = rules_df['Consecuente'] == risk_cat
        sub  = rules_df[mask]
        if len(sub) == 0: continue
        scatter = axes[0].scatter(sub['Soporte'], sub['Confianza'],
                                  c=color, s=sub['Lift']*40, alpha=0.7,
                                  edgecolors='white', linewidths=0.5,
                                  label=risk_cat.replace('riesgo=','Riesgo '))
    axes[0].set_xlabel('Soporte (frecuencia del patron)')
    axes[0].set_ylabel('Confianza (P(riesgo | antecedente))')
    axes[0].set_title('Support vs Confidence\n(tamano del circulo = Lift)')
    axes[0].legend(title='Consecuente', fontsize=9)

    # Panel der: top 15 reglas como barras horizontales
    top15 = rules_df.head(15).copy()
    top15['label'] = top15.apply(
        lambda r: f"{r['Antecedente']} → {r['Consecuente']}", axis=1)
    bar_colors = [risk_colors.get(r['Consecuente'], '#555') for _, r in top15.iterrows()]
    axes[1].barh(top15['label'][::-1], top15['Lift'][::-1],
                 color=bar_colors[::-1], alpha=0.85)
    axes[1].axvline(1.0, color='black', lw=0.8, ls='--', label='Lift=1 (sin asociacion)')
    axes[1].set_xlabel('Lift (fuerza de la asociacion)')
    axes[1].set_title('Top 15 Reglas por Lift')
    axes[1].legend(fontsize=8)
    axes[1].tick_params(axis='y', labelsize=7)

    plt.tight_layout()
    out = os.path.join(BASE, 'reglas_asociacion.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'[OK] {out}')

# ═══════════════════════════════════════════════════════════════════════════════
# 3. COMPARACION DE CLASIFICADORES
# ═══════════════════════════════════════════════════════════════════════════════
print('\n── Comparacion de Clasificadores ──')

classifiers = {
    'Arbol CART':        DecisionTreeClassifier(max_depth=6, min_samples_leaf=20,
                                                 class_weight='balanced', random_state=42),
    'Random Forest':     RandomForestClassifier(n_estimators=200, max_depth=8,
                                                class_weight='balanced', random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, max_depth=4,
                                                     learning_rate=0.1, random_state=42),
    'Regresion Logistica': LogisticRegression(max_iter=1000, random_state=42,
                                               class_weight='balanced'),
    'Naive Bayes':       GaussianNB(),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
comparison = {}

print(f'\n{"Clasificador":<22} {"Acc_test":>10} {"F1_test":>10} {"CV_Acc":>10} {"AUC_Alto":>10}')
print('-'*65)

for name, clf in classifiers.items():
    clf.fit(X_tr_sc, y_tr)
    y_pred = clf.predict(X_te_sc)

    acc  = accuracy_score(y_te, y_pred)
    f1   = f1_score(y_te, y_pred, average='weighted')
    prec = precision_score(y_te, y_pred, average='weighted', zero_division=0)
    rec  = recall_score(y_te, y_pred, average='weighted', zero_division=0)
    cv_acc = cross_val_score(clf, X_tr_sc, y_tr, cv=cv, scoring='accuracy').mean()

    # AUC para clase Alto (one-vs-rest)
    if hasattr(clf, 'predict_proba'):
        classes = list(clf.classes_)
        if 'Alto' in classes:
            y_prob = clf.predict_proba(X_te_sc)[:, classes.index('Alto')]
            auc = roc_auc_score((y_te == 'Alto').astype(int), y_prob)
        else:
            auc = float('nan')
    else:
        auc = float('nan')

    comparison[name] = dict(acc=acc, f1=f1, prec=prec, rec=rec, cv_acc=cv_acc, auc=auc)
    print(f'{name:<22} {acc:>10.4f} {f1:>10.4f} {cv_acc:>10.4f} {auc:>10.4f}')

# Visualizacion comparacion
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Comparacion de Clasificadores — Mineria de Datos\n'
             'Clasificacion de riesgo de automatizacion en Jalisco 2024',
             fontsize=12, fontweight='bold', color=NAVY)

metrics_names  = ['acc', 'f1', 'prec', 'rec', 'cv_acc']
metrics_labels = ['Accuracy', 'F1 ponderado', 'Precision', 'Recall', 'CV Accuracy']
clf_names = list(comparison.keys())
x = np.arange(len(clf_names))

# Panel 1: barras grouped por metrica
w = 0.15
colors_m = [NAVY, AMBER, '#43A047', '#E53935', '#9B59B6']
for i, (metric, label, color) in enumerate(zip(metrics_names, metrics_labels, colors_m)):
    vals = [comparison[c][metric] for c in clf_names]
    axes[0].bar(x + i*w - 2*w, vals, w, label=label, color=color, alpha=0.85)
axes[0].set_xticks(x)
axes[0].set_xticklabels([n.replace(' ','\n') for n in clf_names], fontsize=8)
axes[0].set_ylabel('Valor (0-1)')
axes[0].set_title('Metricas por Clasificador')
axes[0].legend(fontsize=7, ncol=2)
axes[0].set_ylim(0, 1.05)

# Panel 2: radar-style comparison (heatmap)
comp_df = pd.DataFrame(comparison).T[metrics_names]
comp_df.columns = metrics_labels
comp_df.index = [n.replace(' ','\n') for n in clf_names]
sns.heatmap(comp_df, annot=True, fmt='.3f', cmap='YlGn', ax=axes[1],
            vmin=0.5, vmax=1.0, linewidths=0.4,
            cbar_kws={'label': 'Valor (mayor = mejor)'})
axes[1].set_title('Heatmap de Metricas\n(amarillo=bajo, verde=alto)')
axes[1].tick_params(axis='y', labelsize=8)

plt.tight_layout()
out = os.path.join(BASE, 'comparacion_clasificadores.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.close()
print(f'[OK] {out}')

# ── Resumen final ─────────────────────────────────────────────────────────────
print('\n=== RESUMEN MINERIA DE DATOS ===')
best = max(comparison.items(), key=lambda x: x[1]['f1'])
print(f'Mejor clasificador (F1): {best[0]} — F1={best[1]["f1"]:.4f}  Acc={best[1]["acc"]:.4f}')
print(f'Reglas de asociacion encontradas: {len(rules_df)}')
if len(rules_df) > 0:
    top_rule = rules_df.iloc[0]
    print(f'Regla mas fuerte: {top_rule["Antecedente"]} → {top_rule["Consecuente"]} '
          f'(conf={top_rule["Confianza"]:.3f}, lift={top_rule["Lift"]:.3f}, n={top_rule["N"]})')
print('\nFiguras: arbol_decision.png, arbol_importancia.png, reglas_asociacion.png, comparacion_clasificadores.png')
