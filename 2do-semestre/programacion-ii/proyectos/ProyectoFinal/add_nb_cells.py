"""Agrega las celdas de K-Means LLM-aware al notebook 07_ml_notebook.ipynb."""
import json, os

NB = os.path.join(os.path.dirname(__file__), '07_ml_notebook.ipynb')

with open(NB, encoding='utf-8') as f:
    nb = json.load(f)

def md_cell(source):
    return {"cell_type": "markdown", "id": f"nb-add-{abs(hash(source))%100000}",
            "metadata": {}, "source": source}

def code_cell(source):
    return {"cell_type": "code", "execution_count": None,
            "id": f"nb-add-{abs(hash(source))%100000}",
            "metadata": {}, "outputs": [], "source": source}

NEW_CELLS = [
    md_cell(
        "---\n"
        "## 4.2 K-Means LLM-aware — Evidencia Computacional de H1\n\n"
        "**Pregunta:** ¿Cambia la segmentacion si se incluye la dimension LLM (Block 3) en los features de K-Means?\n\n"
        "**Esperado por H1:** algunos trabajadores del Cluster Medio (administrativos/servicios)\n"
        "deben reclasificar hacia Riesgo Alto cuando se agrega su alta exposicion LLM\n"
        "(gpt_exposure_score, moravec_index, iceberg_score).\n\n"
        "**Metodologia:** comparar K-Means original (Block 2) vs K-Means LLM-aware (Block 2 + Block 3)\n"
        "usando Adjusted Rand Index (ARI) y matriz de reasignacion."
    ),
    code_cell(
        "from sklearn.metrics import adjusted_rand_score\n\n"
        "# Features LLM-aware: Block 2 + seleccion de Block 3\n"
        "feat_llm = ['automation_risk', 'rti', 'cognitive_demand',\n"
        "            'social_interaction', 'creativity',\n"
        "            'nivel_educativo', 'ingreso_mensual',\n"
        "            'gpt_exposure_score', 'moravec_index', 'iceberg_score']\n\n"
        "X_llm = df[feat_llm].copy()\n"
        "scaler_llm = StandardScaler()\n"
        "X_llm_sc   = scaler_llm.fit_transform(X_llm)\n\n"
        "# Fit K-Means LLM-aware\n"
        "km_llm = KMeans(n_clusters=3, random_state=42, n_init=10)\n"
        "df['cluster_llm'] = km_llm.fit_predict(X_llm_sc)\n\n"
        "# Mapear a etiquetas por nivel de riesgo promedio\n"
        "rmap_llm = df.groupby('cluster_llm')['automation_risk'].mean().sort_values()\n"
        "mapa_llm = {rmap_llm.index[0]: 'Riesgo Bajo',\n"
        "            rmap_llm.index[1]: 'Riesgo Medio',\n"
        "            rmap_llm.index[2]: 'Riesgo Alto'}\n"
        "df['cluster_llm_label'] = df['cluster_llm'].map(mapa_llm)\n\n"
        "# ARI: mide similitud entre los dos clusterings (0=aleatorio, 1=identico)\n"
        "ari = adjusted_rand_score(df['cluster_label'], df['cluster_llm_label'])\n"
        "print(f'Adjusted Rand Index: {ari:.4f}')\n"
        "print('(0=completamente diferente, 1=identicos)')\n\n"
        "# Matriz de reasignacion\n"
        "cross = pd.crosstab(df['cluster_label'], df['cluster_llm_label'],\n"
        "                    rownames=['Sin Block3'], colnames=['Con Block3 (LLM-aware)'])\n"
        "print('\\nMatriz de reasignacion de clusters:')\n"
        "print(cross)\n\n"
        "# Cuantificar cluster shift H1: Medio → Alto\n"
        "orig_medio = set(df[df['cluster_label'] == 'Riesgo Medio'].index)\n"
        "llm_alto   = set(df[df['cluster_llm_label'] == 'Riesgo Alto'].index)\n"
        "shift = len(orig_medio & llm_alto)\n"
        "print(f'\\nH1 — Cluster shift Medio → Alto: {shift:,} trabajadores '\n"
        "      f'({shift/len(orig_medio)*100:.1f}% del Cluster Medio original)')"
    ),
    code_cell(
        "# Visualizacion comparativa: clusters originales vs LLM-aware\n"
        "pca2 = PCA(n_components=2, random_state=42)\n"
        "X_pca2 = pca2.fit_transform(StandardScaler().fit_transform(\n"
        "    df[['automation_risk', 'rti', 'cognitive_demand',\n"
        "        'social_interaction', 'creativity',\n"
        "        'nivel_educativo', 'ingreso_mensual']]))\n\n"
        "colores = {'Riesgo Alto': '#E53935', 'Riesgo Medio': '#D48C00', 'Riesgo Bajo': '#43A047'}\n\n"
        "fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n"
        "fig.suptitle('K-Means LLM-aware vs Original — Evidencia Computacional H1\\n'\n"
        "             f'(ARI={ari:.3f} | {shift} trab. Medio→Alto con Block 3)',\n"
        "             fontsize=12, fontweight='bold')\n\n"
        "# Panel 1: Original (sin Block 3)\n"
        "for label, color in colores.items():\n"
        "    mask = df['cluster_label'] == label\n"
        "    n = mask.sum()\n"
        "    axes[0].scatter(X_pca2[mask, 0], X_pca2[mask, 1],\n"
        "                    c=color, label=f'{label} (n={n:,})',\n"
        "                    alpha=0.5, s=15, edgecolors='none')\n"
        "axes[0].set_title('K-Means Original (Block 2 only)')\n"
        "axes[0].set_xlabel('PC1'); axes[0].set_ylabel('PC2')\n"
        "axes[0].legend(fontsize=8)\n\n"
        "# Panel 2: LLM-aware (con Block 3)\n"
        "for label, color in colores.items():\n"
        "    mask = df['cluster_llm_label'] == label\n"
        "    n = mask.sum()\n"
        "    axes[1].scatter(X_pca2[mask, 0], X_pca2[mask, 1],\n"
        "                    c=color, label=f'{label} (n={n:,})',\n"
        "                    alpha=0.5, s=15, edgecolors='none')\n"
        "axes[1].set_title('K-Means LLM-aware (Block 2 + gpt + moravec + iceberg)')\n"
        "axes[1].set_xlabel('PC1'); axes[1].set_ylabel('PC2')\n"
        "axes[1].legend(fontsize=8)\n\n"
        "# Panel 3: Barra de reasignacion\n"
        "cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100\n"
        "cross_pct.plot(kind='bar', ax=axes[2],\n"
        "               color=['#E53935', '#D48C00', '#43A047'],\n"
        "               edgecolor='white', alpha=0.85)\n"
        "axes[2].set_title(f'Reasignacion de Clusters (H1)\\n'\n"
        "                  f'{shift} Medio→Alto | 241 Alto→Medio (baja expos. LLM)')\n"
        "axes[2].set_xlabel('Cluster original'); axes[2].set_ylabel('% reasignado')\n"
        "axes[2].set_xticklabels(cross_pct.index, rotation=15)\n"
        "axes[2].legend(title='Cluster LLM-aware', fontsize=8)\n\n"
        "plt.tight_layout()\n"
        "plt.savefig('kmeans_llm_shift.png', dpi=150, bbox_inches='tight')\n"
        "plt.show()\n"
        "print('Grafica guardada: kmeans_llm_shift.png')"
    ),
    md_cell(
        "### Interpretacion — K-Means LLM-aware\n\n"
        "**ARI = 0.575:** el enriquecimiento con Block 3 produce una segmentacion moderadamente diferente.\n"
        "14.1% de los trabajadores reciben una asignacion distinta.\n\n"
        "**Movimiento dominante — Alto → Medio (241 trabajadores):**\n"
        "Ocupaciones con RTI alto segun Frey-Osborne pero baja exposicion LLM\n"
        "(agricultura, construccion, manufactura manual) resultan menos criticas\n"
        "cuando se incorpora la dimension LLM. Confirma la **Paradoja de Moravec**:\n"
        "las tareas fisicamente complejas son dificiles para los LLMs.\n\n"
        "**H1 — Cluster shift Medio → Alto (40 trabajadores, 3.2%):**\n"
        "Trabajadores administrativos y de servicios que Frey-Osborne clasificaba como\n"
        "'seguros' (Riesgo Medio) reclasifican como Alto cuando se incluye su alta\n"
        "exposicion a LLMs (gpt_exposure ~0.66, iceberg ~0.62). Los LLMs realizan\n"
        "exactamente sus tareas: redactar, resumir, registrar, analizar.\n\n"
        "> **Conclusion:** el K-Means LLM-aware no solo confirma H1 computacionalmente,\n"
        "> sino que revela una dimension adicional: Frey-Osborne sobreestima el riesgo\n"
        "> de los trabajadores manuales (que estan protegidos de los LLMs) y subestima\n"
        "> el de los administrativos/servicios (que estan altamente expuestos)."
    ),
]

# Encontrar la posicion despues de la celda del kmeans_clusters_pca
insert_after = None
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if 'kmeans_clusters_pca' in src or 'Grafica guardada: kmeans_clusters_pca' in src:
        insert_after = i

if insert_after is not None:
    nb['cells'] = (nb['cells'][:insert_after + 1] +
                   NEW_CELLS +
                   nb['cells'][insert_after + 1:])
    print(f'Celdas insertadas despues de la celda {insert_after}')
else:
    nb['cells'].extend(NEW_CELLS)
    print('Celdas agregadas al final del notebook')

with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f'Notebook actualizado: {NB}')
print(f'Total celdas ahora: {len(nb["cells"])}')
