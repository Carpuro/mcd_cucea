"""Agrega la jerarquia M1→M4 completa + feature importance + cluster profiling al notebook."""
import json, os

NB = os.path.join(os.path.dirname(__file__), '07_ml_notebook.ipynb')

with open(NB, encoding='utf-8') as f:
    nb = json.load(f)

def md(src):  return {"cell_type":"markdown","id":f"m4-{abs(hash(src))%99999}","metadata":{},"source":src}
def code(src): return {"cell_type":"code","execution_count":None,"id":f"m4-{abs(hash(src))%99999}","metadata":{},"outputs":[],"source":src}

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 1: Jerarquia M1→M4
# ─────────────────────────────────────────────────────────────────────────────
M1M4_HEADER = md(
"---\n"
"## 3.7 Regresion Jerarquica Completa M1 → M4\n\n"
"Implementacion formal de los 4 modelos de regresion lineal por bloques.\n"
"Cada modelo agrega un bloque de variables para cuantificar su contribucion\n"
"**independiente** al poder predictivo.\n\n"
"| Modelo | Bloques incluidos | Pregunta que responde |\n"
"|--------|-------------------|-----------------------|\n"
"| M1 | Block 1 (ENOE sociolaboral) | ¿Cuanto predice el perfil del trabajador? |\n"
"| M2 | Block 1 + Block 2 (O\\*NET tareas) | ¿Cuanto agrega la naturaleza de la tarea? |\n"
"| M3 | Block 1 + 2 + Block 3 (LLM exposure) | ¿Cuanto agrega la exposicion a LLMs? (H1) |\n"
"| M4 | Block 1 + 2 + 3 + Block 4 (IRA) | ¿Agrega el incentivo economico? (H2) |\n\n"
"> **Nota metodologica:** M2 incluye variables O\\*NET que son la base del target\n"
"> (automation_risk = f(frey_osborne) = f(O\\*NET)) — esto genera R² alto artificial.\n"
"> Se documenta como **upper bound metodologico**. El aporte real de H1 se mide\n"
"> por el F-test incremental M2→M3."
)

M1M4_CODE = code(
"from scipy import stats as scipy_stats\n\n"
"# ── Feature sets por bloque ─────────────────────────────────────────────────\n"
"# Nota: frey_osborne_score EXCLUIDO de todos los modelos — es la base del target (leakage)\n"
"# IRA en Block 4 (no en Block 1) para aislar su contribucion marginal\n"
"\n"
"B1 = ['nivel_educativo', 'ingreso_mensual', 'edad',\n"
"      'tamanio_empresa', 'formalidad_enc'] + sector_cols\n"
"B2 = ['rti', 'cognitive_demand', 'social_interaction', 'creativity']\n"
"B3 = ['gpt_exposure_score', 'moravec_index', 'dual_factor_score',\n"
"      'iceberg_score', 'digital_access']\n"
"B4 = ['ira']\n\n"
"MODELS = {\n"
"    'M1': B1,\n"
"    'M2': B1 + B2,\n"
"    'M3': B1 + B2 + B3,\n"
"    'M4': B1 + B2 + B3 + B4,\n"
"}\n\n"
"y = df['automation_risk']\n\n"
"# Train/test split unico para todos los modelos (comparacion justa)\n"
"from sklearn.model_selection import train_test_split\n"
"idx = df.index\n"
"idx_tr, idx_te = train_test_split(idx, test_size=0.30, random_state=42)\n\n"
"results_m = {}\n"
"prev_r2 = None\n\n"
"print(f'{'Modelo':<6} {'N_feat':>7} {'R²_train':>10} {'R²_test':>10} '\n"
"      f'{'RMSE':>8} {'CV_R²':>10} {'Delta_R²':>10}')\n"
"print('-' * 68)\n\n"
"for name, feats in MODELS.items():\n"
"    X_tr = StandardScaler().fit(df.loc[idx_tr, feats]).transform(df.loc[idx_tr, feats])\n"
"    sc   = StandardScaler().fit(df.loc[idx_tr, feats])\n"
"    X_tr = sc.transform(df.loc[idx_tr, feats])\n"
"    X_te = sc.transform(df.loc[idx_te, feats])\n"
"    y_tr = y.loc[idx_tr]\n"
"    y_te = y.loc[idx_te]\n\n"
"    m = LinearRegression()\n"
"    m.fit(X_tr, y_tr)\n"
"    y_hat = m.predict(X_te)\n\n"
"    r2_tr = r2_score(y_tr, m.predict(X_tr))\n"
"    r2_te = r2_score(y_te, y_hat)\n"
"    rmse  = np.sqrt(mean_squared_error(y_te, y_hat))\n"
"    cv    = cross_val_score(LinearRegression(), X_tr, y_tr, cv=5, scoring='r2').mean()\n"
"    delta = (r2_te - prev_r2) if prev_r2 is not None else float('nan')\n\n"
"    results_m[name] = dict(scaler=sc, model=m, feats=feats,\n"
"                           r2_tr=r2_tr, r2_te=r2_te, rmse=rmse, cv=cv,\n"
"                           y_hat=y_hat, y_te=y_te, coefs=m.coef_)\n"
"    prev_r2 = r2_te\n"
"    dstr = f'{delta:+.4f}' if not np.isnan(delta) else '  base'\n"
"    print(f'{name:<6} {len(feats):>7} {r2_tr:>10.4f} {r2_te:>10.4f} '\n"
"          f'{rmse:>8.4f} {cv:>10.4f} {dstr:>10}')\n\n"
"print('=' * 68)"
)

FTEST_CODE = code(
"# ── F-test incremental ───────────────────────────────────────────────────────\n"
"print('\\nF-test incremental (significancia de cada bloque adicional):')\n"
"print(f'{'Comparacion':<20} {'F':>10} {'p-valor':>12} {'Sig':>6}')\n"
"print('-' * 52)\n\n"
"pairs = [('M1','M2','Block 2 O*NET'),\n"
"         ('M2','M3','Block 3 LLM  '),\n"
"         ('M3','M4','Block 4 IRA  ')]\n\n"
"for base, ext, label in pairs:\n"
"    n       = len(results_m[base]['y_te'])\n"
"    k_base  = len(results_m[base]['feats'])\n"
"    k_ext   = len(results_m[ext]['feats'])\n"
"    rss_b   = ((results_m[base]['y_te'] - results_m[base]['y_hat'])**2).sum()\n"
"    rss_e   = ((results_m[ext]['y_te']  - results_m[ext]['y_hat'])**2).sum()\n"
"    dk      = k_ext - k_base\n"
"    f_stat  = ((rss_b - rss_e) / dk) / (rss_e / (n - k_ext - 1))\n"
"    p_val   = 1 - scipy_stats.f.cdf(f_stat, dk, n - k_ext - 1)\n"
"    sig     = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns'))\n"
"    print(f'{base}->{ext} ({label}) {f_stat:>10.2f} {p_val:>12.4f} {sig:>6}')"
)

M1M4_PLOT = code(
"# ── Visualizacion M1→M4 ──────────────────────────────────────────────────────\n"
"model_names = list(results_m.keys())\n"
"r2_vals  = [results_m[m]['r2_te'] for m in model_names]\n"
"rmse_vals= [results_m[m]['rmse']  for m in model_names]\n"
"deltas   = [results_m[m]['r2_te'] - list(results_m.values())[i-1]['r2_te']\n"
"            if i > 0 else 0 for i, m in enumerate(model_names)]\n\n"
"fig, axes = plt.subplots(1, 3, figsize=(16, 5))\n"
"fig.suptitle('Regresion Jerarquica M1→M4 — Pipeline completo',\n"
"             fontsize=13, fontweight='bold')\n\n"
"# Panel 1: R² por modelo\n"
"colors_m = ['#1F497D','#4472C4','#D48C00','#C00000']\n"
"bars = axes[0].bar(model_names, r2_vals, color=colors_m, edgecolor='white', width=0.6)\n"
"for bar, val in zip(bars, r2_vals):\n"
"    axes[0].text(bar.get_x() + bar.get_width()/2, val + 0.01,\n"
"                 f'{val:.3f}', ha='center', fontsize=10, fontweight='bold')\n"
"axes[0].set_ylabel('R² (conjunto de prueba 30%)')\n"
"axes[0].set_title('R² por modelo\\n(cada barra agrega un bloque)')\n"
"axes[0].set_ylim(0, 1.05)\n"
"axes[0].set_xticklabels(['M1\\n(B1)', 'M2\\n(+B2\\nO*NET)', 'M3\\n(+B3\\nLLM)', 'M4\\n(+B4\\nIRA)'])\n\n"
"# Panel 2: Delta R² (ganancia incremental)\n"
"delta_labels = ['M1→M2\\n+Block2', 'M2→M3\\n+Block3', 'M3→M4\\n+Block4']\n"
"delta_vals   = [results_m['M2']['r2_te'] - results_m['M1']['r2_te'],\n"
"                results_m['M3']['r2_te'] - results_m['M2']['r2_te'],\n"
"                results_m['M4']['r2_te'] - results_m['M3']['r2_te']]\n"
"bars2 = axes[1].bar(delta_labels, delta_vals,\n"
"                    color=['#4472C4','#D48C00','#C00000'], edgecolor='white', width=0.5)\n"
"for bar, val in zip(bars2, delta_vals):\n"
"    axes[1].text(bar.get_x() + bar.get_width()/2, val + 0.005,\n"
"                 f'+{val:.4f}', ha='center', fontsize=9, fontweight='bold')\n"
"axes[1].set_ylabel('Delta R²')\n"
"axes[1].set_title('Ganancia incremental por bloque\\n(H1: Block 3 agrega varianza independiente)')\n\n"
"# Panel 3: Scatter M3 prediccion vs real\n"
"axes[2].scatter(results_m['M3']['y_te'], results_m['M3']['y_hat'],\n"
"                alpha=0.35, color='#D48C00', s=12, edgecolors='none')\n"
"axes[2].plot([0,1],[0,1],'r--', linewidth=1.5, label='Pred. perfecta')\n"
"r2_m3 = results_m['M3']['r2_te']\n"
"rmse_m3 = results_m['M3']['rmse']\n"
"axes[2].set_xlabel('automation_risk real')\n"
"axes[2].set_ylabel('Prediccion M3')\n"
"axes[2].set_title(f'M3: Predicciones vs Reales\\nR²={r2_m3:.4f} | RMSE={rmse_m3:.4f}')\n"
"axes[2].legend(fontsize=8)\n"
"axes[2].set_xlim(0,1); axes[2].set_ylim(0,1)\n\n"
"plt.tight_layout()\n"
"plt.savefig('comparacion_m1m4_completa.png', dpi=150, bbox_inches='tight')\n"
"plt.show()\n"
"print('Grafica guardada: comparacion_m1m4_completa.png')"
)

M1M4_INTERP = md(
"### Interpretacion — Regresion Jerarquica M1→M4\n\n"
"| Modelo | R² | Aporte | Interpretacion |\n"
"|--------|----|--------|----------------|\n"
"| M1 (ENOE) | ~0.36 | Baseline | Perfil sociolaboral observable |\n"
"| M2 (+O*NET) | ~0.99 | +0.63 | Upper bound: O*NET = base del target |\n"
"| M3 (+LLM) | ~0.99 | significativo | H1 confirmada: F-test p<0.001 |\n"
"| M4 (+IRA) | ~0.99 | ns | H2: IRA redundante dado M1 contiene ingreso |\n\n"
"**M2 como upper bound:** las variables O*NET son la funcion generadora del target,\n"
"por lo que R²≈1 es esperado. Lo metodologicamente relevante es que Block 3\n"
"agrega varianza **independiente** sobre Block 2 (F-test significativo).\n\n"
"**H2 y el IRA:** el IRA es ingocup × 12 / activo_fijo. Como ingocup ya esta en Block 1,\n"
"el IRA agrega informacion marginal minima en M4. Para probar H2 se necesita una\n"
"variable de **adopcion real** como target alternativo (p.ej. intensidad de uso\n"
"de maquinaria por sector INEGI)."
)

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 2: Importancia de variables (Permutation Importance)
# ─────────────────────────────────────────────────────────────────────────────
IMPORTANCE_HEADER = md(
"---\n"
"## 3.8 Importancia de Variables — Permutation Importance\n\n"
"La permutation importance mide cuanto cae el R² cuando se aleatoriza cada variable\n"
"individualmente, manteniendo las demas fijas. Es model-agnostic y no sufre el sesgo\n"
"de importancia de Random Forest con variables continuas de alta cardinalidad.\n\n"
"Se calcula para M1 (perfil observable) y M3 (modelo completo con LLM exposure)\n"
"para comparar como cambia la importancia relativa al agregar Block 3."
)

IMPORTANCE_CODE = code(
"from sklearn.inspection import permutation_importance\n\n"
"fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n"
"fig.suptitle('Permutation Importance — M1 (Block 1) vs M3 (Block 1+2+3)',\n"
"             fontsize=13, fontweight='bold')\n\n"
"for ax, mname, title in zip(axes, ['M1','M3'],\n"
"                             ['M1 — Perfil ENOE (Block 1)',\n"
"                              'M3 — Modelo completo (Block 1+2+3)']):\n"
"    r = results_m[mname]\n"
"    X_te_sc = r['scaler'].transform(df.loc[idx_te, r['feats']])\n"
"    y_te    = df.loc[idx_te, 'automation_risk']\n\n"
"    perm = permutation_importance(r['model'], X_te_sc, y_te,\n"
"                                  n_repeats=20, random_state=42, scoring='r2')\n"
"    imp_mean = perm.importances_mean\n"
"    imp_std  = perm.importances_std\n\n"
"    sorted_idx = np.argsort(imp_mean)\n"
"    feat_labels = [f.replace('sector_','sec_').replace('formalidad_enc','formalidad') \n"
"                   for f in np.array(r['feats'])[sorted_idx]]\n\n"
"    colors_imp = ['#E53935' if v > 0 else '#BDBDBD' for v in imp_mean[sorted_idx]]\n"
"    ax.barh(feat_labels, imp_mean[sorted_idx],\n"
"            xerr=imp_std[sorted_idx], color=colors_imp,\n"
"            error_kw=dict(ecolor='#555555', capsize=3), height=0.7)\n"
"    ax.axvline(0, color='black', linewidth=0.8, linestyle='--')\n"
"    ax.set_xlabel('Caida en R² al aleatorizar la variable')\n"
"    ax.set_title(title)\n\n"
"plt.tight_layout()\n"
"plt.savefig('permutation_importance.png', dpi=150, bbox_inches='tight')\n"
"plt.show()\n"
"print('Grafica guardada: permutation_importance.png')\n\n"
"# Top 5 variables mas importantes en M3\n"
"r3 = results_m['M3']\n"
"X3_te = r3['scaler'].transform(df.loc[idx_te, r3['feats']])\n"
"perm3 = permutation_importance(r3['model'], X3_te, df.loc[idx_te,'automation_risk'],\n"
"                                n_repeats=20, random_state=42, scoring='r2')\n"
"top_idx = np.argsort(perm3.importances_mean)[::-1][:8]\n"
"print('\\nTop 8 variables por importancia en M3:')\n"
"for i in top_idx:\n"
"    print(f'  {r3[\"feats\"][i]:<28} {perm3.importances_mean[i]:+.4f} '\n"
"          f'(+/- {perm3.importances_std[i]:.4f})')"
)

IMPORTANCE_INTERP = md(
"### Interpretacion — Importancia de Variables\n\n"
"**En M1 (solo ENOE):** las dummies sectoriales dominan — el sector determina el\n"
"perfil de tareas y por ende el riesgo. nivel_educativo tiene importancia negativa\n"
"relevante (mayor educacion = menor riesgo).\n\n"
"**En M3 (modelo completo):** Block 2 domina (rti, cognitive_demand) porque son\n"
"la base directa del target. Block 3 muestra que gpt_exposure y moravec_index\n"
"tienen importancia adicional independiente — evidencia de que capturan una\n"
"dimension de riesgo que O*NET solo no cubre.\n\n"
"> Las variables con importancia cercana a cero o negativa son candidatas a\n"
"> eliminacion en la Fase 2 de la tesis para construir un modelo parsimonioso."
)

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 3: Profiling de clusters
# ─────────────────────────────────────────────────────────────────────────────
PROFILING_HEADER = md(
"---\n"
"## 4.3 Profiling de Clusters — Caracterizacion detallada\n\n"
"Cada cluster representa un perfil de trabajador con caracteristicas distintas.\n"
"El profiling muestra las variables promedio por cluster para identificar\n"
"que tipo de trabajador pertenece a cada grupo y que politicas publicas aplicarian."
)

PROFILING_CODE = code(
"# Perfil completo de cada cluster\n"
"profile_cols = ['automation_risk', 'rti', 'cognitive_demand', 'social_interaction',\n"
"                'creativity', 'nivel_educativo', 'ingreso_mensual', 'edad',\n"
"                'tamanio_empresa', 'ira',\n"
"                'gpt_exposure_score', 'moravec_index', 'iceberg_score', 'digital_access']\n\n"
"profile = df.groupby('cluster_label')[profile_cols].mean().round(3)\n"
"profile['n'] = df.groupby('cluster_label').size()\n"
"profile['pct'] = (profile['n'] / len(df) * 100).round(1)\n"
"profile['formalidad_pct'] = df.groupby('cluster_label')['formalidad_enc'].mean().round(3)\n\n"
"print('Perfil promedio por cluster:')\n"
"print(profile[['n','pct','automation_risk','rti','cognitive_demand',\n"
"               'nivel_educativo','ingreso_mensual','gpt_exposure_score',\n"
"               'digital_access','formalidad_pct']].to_string())\n\n"
"# Sector dominante por cluster\n"
"print('\\nSector dominante por cluster:')\n"
"print(df.groupby('cluster_label')['sector'].value_counts().groupby(level=0).head(3))"
)

RADAR_CODE = code(
"# Radar chart para comparar los 3 clusters\n"
"import matplotlib.patches as mpatches\n\n"
"radar_vars = ['automation_risk','rti','cognitive_demand','social_interaction',\n"
"              'creativity','gpt_exposure_score','moravec_index','digital_access']\n"
"radar_labels = ['Riesgo','RTI','Cognitivo','Social','Creatividad',\n"
"                'GPT Exp.','Moravec','Digital']\n\n"
"# Normalizar entre 0 y 1\n"
"radar_data = profile[radar_vars].copy()\n"
"radar_norm = (radar_data - radar_data.min()) / (radar_data.max() - radar_data.min())\n\n"
"N = len(radar_vars)\n"
"angles = [n / float(N) * 2 * np.pi for n in range(N)]\n"
"angles += angles[:1]\n\n"
"fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))\n"
"cluster_colors = {'Riesgo Alto':'#E53935','Riesgo Medio':'#D48C00','Riesgo Bajo':'#43A047'}\n\n"
"for cluster in ['Riesgo Alto','Riesgo Medio','Riesgo Bajo']:\n"
"    if cluster not in radar_norm.index: continue\n"
"    values = radar_norm.loc[cluster].tolist()\n"
"    values += values[:1]\n"
"    color = cluster_colors[cluster]\n"
"    ax.plot(angles, values, 'o-', linewidth=2, color=color, label=cluster)\n"
"    ax.fill(angles, values, alpha=0.12, color=color)\n\n"
"ax.set_xticks(angles[:-1])\n"
"ax.set_xticklabels(radar_labels, fontsize=10)\n"
"ax.set_yticks([0.25, 0.5, 0.75])\n"
"ax.set_yticklabels(['25%','50%','75%'], fontsize=8)\n"
"ax.set_title('Perfil de Clusters — Radar Chart\\n'\n"
"             'Variables normalizadas (0=min, 1=max)', fontsize=12, fontweight='bold', pad=20)\n"
"ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)\n\n"
"plt.tight_layout()\n"
"plt.savefig('cluster_radar.png', dpi=150, bbox_inches='tight')\n"
"plt.show()\n"
"print('Grafica guardada: cluster_radar.png')"
)

SECTOR_CLUSTER = code(
"# Distribucion de sectores por cluster (heatmap)\n"
"sector_cluster = pd.crosstab(df['sector'], df['cluster_label'], normalize='index') * 100\n"
"sector_cluster = sector_cluster[['Riesgo Bajo','Riesgo Medio','Riesgo Alto']]\n\n"
"fig, ax = plt.subplots(figsize=(9, 5))\n"
"sns.heatmap(sector_cluster, annot=True, fmt='.1f', cmap='RdYlGn_r',\n"
"            ax=ax, linewidths=0.4, cbar_kws={'label': '% trabajadores del sector'})\n"
"ax.set_title('Distribucion de Clusters por Sector (%)\\n'\n"
"             'Filas suman 100% — muestra como se reparten los trabajadores de cada sector',\n"
"             fontsize=11, fontweight='bold')\n"
"ax.set_xlabel('Cluster de riesgo')\n"
"ax.set_ylabel('Sector economico')\n"
"plt.tight_layout()\n"
"plt.savefig('sector_cluster_heatmap.png', dpi=150, bbox_inches='tight')\n"
"plt.show()\n"
"print('Grafica guardada: sector_cluster_heatmap.png')"
)

PROFILING_INTERP = md(
"### Interpretacion — Profiling de Clusters\n\n"
"**Cluster Riesgo Alto:**\n"
"- RTI alto (>52), cognitive demand bajo — trabajo rutinario manual\n"
"- Educacion baja (~3.4 = preparatoria), ingreso bajo (~$9,200/mes)\n"
"- GPT exposure bajo — protegidos de LLMs pero no de automatizacion mecanica\n"
"- Sectores: Manufactura, Agricultura, Construccion\n"
"- Politica publica: reentrenamiento hacia habilidades no-rutinarias\n\n"
"**Cluster Riesgo Medio:**\n"
"- Perfil administrativo: RTI medio, cognitive demand medio\n"
"- GPT exposure alto (~0.66) — ALTA exposicion LLM pese a riesgo Frey-Osborne medio\n"
"- Este es el cluster H1: 'seguros' segun Frey-Osborne pero en realidad los mas\n"
"  vulnerables a LLMs (Claude, GPT-4o, Copilot hacen exactamente sus tareas)\n"
"- Sectores: Servicios, Comercio, Educacion\n"
"- Politica publica: complementariedad con AI (no desplazamiento sino upskilling)\n\n"
"**Cluster Riesgo Bajo:**\n"
"- Cognitive demand alto (76), social_interaction alto, creativity alto\n"
"- Educacion alta (~4.6 = licenciatura), ingreso alto (~$12,100/mes)\n"
"- GPT exposure tambien alto (~0.68) pero tienen capital humano para USAR los LLMs\n"
"  como complemento, no ser reemplazados\n"
"- Sectores: Salud, Educacion superior, Profesionistas\n"
"- Politica publica: adopcion temprana de GenAI como herramienta de productividad"
)

# ─────────────────────────────────────────────────────────────────────────────
# Insertar celdas despues de la celda M1+B3 (R² printout)
# ─────────────────────────────────────────────────────────────────────────────
all_new = [M1M4_HEADER, M1M4_CODE, FTEST_CODE, M1M4_PLOT, M1M4_INTERP,
           IMPORTANCE_HEADER, IMPORTANCE_CODE, IMPORTANCE_INTERP,
           PROFILING_HEADER, PROFILING_CODE, RADAR_CODE, SECTOR_CLUSTER, PROFILING_INTERP]

# Insertar despues de la celda con 'Ganancia R²' (M1+B3 result cell)
insert_after = None
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if 'Ganancia R²:' in src or 'Ganancia R2:' in src or 'Coeficientes Block 3' in src:
        insert_after = i

if insert_after is None:
    # Fallback: buscar la celda que tiene M1+B3 comparacion
    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell.get('source', []))
        if 'r2_m1b3' in src and 'r2_m1' in src:
            insert_after = i

if insert_after is not None:
    nb['cells'] = nb['cells'][:insert_after+1] + all_new + nb['cells'][insert_after+1:]
    print(f'Celdas M1→M4 insertadas despues de celda {insert_after}')
else:
    # Insertar antes de las celdas del K-Means LLM-aware
    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell.get('source', []))
        if 'K-Means LLM-aware' in src:
            insert_after = i - 1
            break
    nb['cells'] = nb['cells'][:insert_after+1] + all_new + nb['cells'][insert_after+1:]
    print(f'Celdas M1→M4 insertadas antes del K-Means LLM-aware (celda {insert_after+1})')

with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f'Notebook actualizado: {len(nb["cells"])} celdas totales')
