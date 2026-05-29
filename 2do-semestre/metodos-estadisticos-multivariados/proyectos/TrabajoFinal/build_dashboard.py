# -*- coding: utf-8 -*-
"""Interactive HTML dashboard — Municipal Marginalization PCA 2020."""
import json, os, re, unicodedata, warnings, zipfile
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

warnings.filterwarnings("ignore")
os.makedirs("output", exist_ok=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
PCA_VARS = ["ANALF","SBASC","OVSDE","OVSEE","OVSAE","OVPT","VHAC","PL5000","PO2SM"]
VAR_SHORT = ["Analfabeta","Sin educ.","Sin drenaje","Sin elect.","Sin agua",
             "Piso tierra","Hacinamiento","Loc.<5k","Ingr.<2SM"]
GRADE_LABELS = ["Muy bajo","Bajo","Medio","Alto","Muy alto"]
GRADE_COLORS_LIST = ["#2ecc71","#a9d86e","#f1c40f","#e67e22","#e74c3c"]
GRADE_COLORS = dict(zip(GRADE_LABELS, GRADE_COLORS_LIST))
ZMG_NAMES = ["Guadalajara","Zapopan","San Pedro Tlaquepaque","Tonala",
             "Tlajomulco de Zuniga","El Salto","Ixtlahuacan de los Membrillos",
             "Juanacatlan","Zapotlanejo"]
ZMG_CENTER = {"lat":20.62,"lon":-103.37}
FONT = dict(family="Inter, Arial, sans-serif", size=13)
TPL  = "plotly_white"

def norm(s):
    s = unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode()
    return re.sub(r"\s+","",s).lower()

# ─── LOAD + ANALYSIS ──────────────────────────────────────────────────────────
print("Loading data and running analysis...")
df = pd.read_excel("data/IMM_2020.xls", sheet_name="IMM_2020")
df["CVEGEO"] = df["CVE_MUN"].astype(str).str.zfill(5)
df = df.rename(columns={"PL.5000":"PL5000"}).reset_index(drop=True)

cidx = df[PCA_VARS].dropna().index
Xraw = df.loc[cidx, PCA_VARS].values
n_obs = len(cidx)

kmo_items, kmo_total = calculate_kmo(Xraw)
chi2_stat, p_val     = calculate_bartlett_sphericity(Xraw)

scaler = StandardScaler()
Xs = scaler.fit_transform(Xraw)
pca_full = PCA(n_components=len(PCA_VARS), random_state=42)
pca_full.fit(Xs)
scores = pca_full.transform(Xs)
eigvals   = pca_full.explained_variance_
var_ratio = pca_full.explained_variance_ratio_
cum_var   = np.cumsum(var_ratio)
n_kaiser  = int(np.sum(eigvals > 1))

pc1 = scores[:,0].copy(); lpc1 = pca_full.components_[0].copy()
if lpc1.mean() < 0: pc1 = -pc1; lpc1 = -lpc1

sk = scores[:,:n_kaiser].copy(); lk = pca_full.components_[:n_kaiser].T.copy()
for j in range(n_kaiser):
    if lk[:,j].mean() < 0: lk[:,j]=-lk[:,j]; sk[:,j]=-sk[:,j]

np.random.seed(42)
km = KMeans(n_clusters=5, random_state=42, n_init=25)
raw_cls = km.fit_predict(pc1.reshape(-1,1))
centers = km.cluster_centers_.flatten()
lmap = {o:n for n,o in enumerate(np.argsort(centers))}
cls = np.array([lmap[c] for c in raw_cls])

dw = df.loc[cidx].copy().reset_index(drop=True)
dw["INDEX_PCA"] = pc1
dw["GRADO_PCA"] = pd.Categorical([GRADE_LABELS[c] for c in cls], GRADE_LABELS, ordered=True)
for j in range(n_kaiser): dw[f"COMP{j+1}"] = sk[:,j]
dw["norm"] = dw["NOM_MUN"].apply(norm)
r_conapo = np.corrcoef(dw["INDEX_PCA"], dw["IM_2020"])[0,1]
ct = pd.crosstab(dw["GRADO_PCA"], dw["GM_2020"])
pct_match = sum(ct.loc[g,g] for g in GRADE_LABELS if g in ct.columns and g in ct.index) / n_obs * 100

# ─── INTERPRETATION STATS ─────────────────────────────────────────────────────
_corr_df = pd.DataFrame(Xraw, columns=PCA_VARS).corr()
_mask    = np.triu(np.ones(_corr_df.shape, dtype=bool), k=1)
_upper   = _corr_df.where(_mask)
avg_off_corr  = float(_upper.stack().mean())
_mi, _mj      = np.unravel_index(_upper.fillna(0).values.argmax(), _corr_df.shape)
max_corr_v1   = VAR_SHORT[_mi]; max_corr_v2 = VAR_SHORT[_mj]
max_corr_val  = float(_upper.iloc[_mi, _mj])
max_load_idx  = int(np.argmax(lpc1))
max_load_var  = VAR_SHORT[max_load_idx]
max_load_val  = float(lpc1[max_load_idx])
grade_counts  = dw["GRADO_PCA"].value_counts().reindex(GRADE_LABELS)
most_common_grade = grade_counts.idxmax()
most_common_n     = int(grade_counts.max())
discordance_pct   = 100.0 - pct_match

# CP2 loadings for biplot
lpc2 = pca_full.components_[1].copy()
if lpc2[np.argmax(np.abs(lpc2))] < 0: lpc2 = -lpc2

# Radar: mean variable profile per grade (0–1 normalised)
_raw_r = pd.DataFrame(Xraw, columns=PCA_VARS)
_raw_r["GRADO_PCA"] = dw["GRADO_PCA"].values
radar_means  = _raw_r.groupby("GRADO_PCA")[PCA_VARS].mean().reindex(GRADE_LABELS)
radar_norm_df = (radar_means - radar_means.min()) / (radar_means.max() - radar_means.min())

# National centroids from GADM
dw["norm_ent"] = dw["NOM_ENT"].apply(norm)
dw["norm_mun"] = dw["NOM_MUN"].apply(norm)

# ─── ZMG GEO ──────────────────────────────────────────────────────────────────
print("Loading shapefile...")
with zipfile.ZipFile("data/gadm41_MEX_2.json.zip") as z:
    with z.open(z.namelist()[0]) as f:
        mex = gpd.read_file(f)
jal = mex[mex["NAME_1"]=="Jalisco"].copy()
jal["norm"] = jal["NAME_2"].apply(norm)
zmg_geo = jal[jal["norm"].isin([norm(n) for n in ZMG_NAMES])].copy()
zmg = zmg_geo.merge(dw[["norm","INDEX_PCA","GRADO_PCA","IM_2020","GM_2020","NOM_MUN"]], on="norm", how="left")
zmg["grado_ord"] = zmg["GRADO_PCA"].map({g:i for i,g in enumerate(GRADE_LABELS)}).fillna(0)
zmg["conapo_ord"]= zmg["GM_2020"].map({g:i for i,g in enumerate(GRADE_LABELS)}).fillna(0)
zmg["GRADO_STR"] = zmg["GRADO_PCA"].astype(str)
geojson_dict = json.loads(zmg[["norm","geometry"]].to_json())
for feat in geojson_dict["features"]:
    feat["id"] = feat["properties"]["norm"]

# ─── NATIONAL CENTROIDS ──────────────────────────────────────────────────────
mex_c = mex.copy()
mex_c["geometry"] = mex_c.geometry.centroid
mex_c["lat"] = mex_c.geometry.y
mex_c["lon"] = mex_c.geometry.x
mex_c["norm_ent"] = mex_c["NAME_1"].apply(norm)
mex_c["norm_mun"] = mex_c["NAME_2"].apply(norm)
nat = mex_c.merge(dw, on=["norm_ent","norm_mun"], how="inner")
nat_match = len(nat)
nat["logpop"] = np.log10(nat["POB_TOT"].clip(lower=1))
_szmin = nat["logpop"].min(); _szmax = nat["logpop"].max()
nat["msize"] = 5 + 16 * (nat["logpop"] - _szmin) / (_szmax - _szmin)

national_json = json.dumps([
    {"g": str(row["GRADO_PCA"]), "lat": round(float(row["lat"]),4),
     "lon": round(float(row["lon"]),4), "m": row["NOM_MUN"],
     "e": row["NOM_ENT"], "pca": round(float(row["INDEX_PCA"]),3),
     "conapo": str(row["GM_2020"]), "pop": int(row["POB_TOT"]),
     "sz": round(float(row["msize"]),1),
     "analf": round(float(row["ANALF"]),1),
     "sbasc": round(float(row["SBASC"]),1),
     "ovsae": round(float(row["OVSAE"]),1),
     "po2sm": round(float(row["PO2SM"]),1)}
    for _, row in nat.iterrows()
], ensure_ascii=False)
nat_states_list = sorted(nat["NOM_ENT"].unique().tolist())

# ─── DISCRETE COLORSCALE (for Plotly choropleth) ──────────────────────────────
def discrete_cs():
    cs = []
    for i, c in enumerate(GRADE_COLORS_LIST):
        cs += [[i/5, c], [(i+1)/5, c]]
    return cs

pca_z  = zmg["INDEX_PCA"].fillna(0).values
km_z   = zmg["grado_ord"].values.astype(float)
cn_z   = zmg["conapo_ord"].values.astype(float)
custom = zmg[["NOM_MUN","GRADO_STR","GM_2020","INDEX_PCA","IM_2020"]].values

# ─── FIGURE HELPERS ───────────────────────────────────────────────────────────
def fdiv(fig, div_id=None, h=None):
    kwargs = dict(full_html=False, include_plotlyjs=False,
                  config={"responsive":True,"displayModeBar":True,
                          "modeBarButtonsToRemove":["select2d","lasso2d"]})
    if div_id: kwargs["div_id"] = div_id
    return fig.to_html(**kwargs)

# ─────────────────────────────────────────────────────────────────────────────
print("Building charts...")

# ── 1. CORRELATION HEATMAP ────────────────────────────────────────────────────
corr = pd.DataFrame(Xraw, columns=PCA_VARS).corr().round(3)
fig_corr = go.Figure(go.Heatmap(
    z=corr.values, x=VAR_SHORT, y=VAR_SHORT,
    colorscale="RdYlGn_r", zmid=0, zmin=-1, zmax=1,
    text=corr.values.round(2), texttemplate="%{text}",
    colorbar=dict(title="r", thickness=12),
))
fig_corr.update_layout(title="Matriz de correlaciones", template=TPL, font=FONT,
                       height=460, margin=dict(l=5,r=5,t=45,b=5))

# ── 2. PCA LOADINGS ───────────────────────────────────────────────────────────
load_df = sorted(zip(VAR_SHORT, lpc1), key=lambda x: x[1])
fig_loads = go.Figure(go.Bar(
    x=[v[1] for v in load_df], y=[v[0] for v in load_df],
    orientation="h",
    marker=dict(
        color=[v[1] for v in load_df],
        colorscale=[[0,"#3498db"],[0.5,"#ecf0f1"],[1,"#e74c3c"]],
        cmin=-0.5, cmax=0.5, showscale=False,
    ),
    hovertemplate="%{y}: %{x:.4f}<extra></extra>",
))
fig_loads.add_vline(x=0, line_dash="dash", line_color="#888", line_width=1)
fig_loads.update_layout(
    title=f"Cargas factoriales CP1 &mdash; {var_ratio[0]*100:.1f}% varianza  |  Eigenvalor: {eigvals[0]:.3f}",
    template=TPL, font=FONT, height=360,
    margin=dict(l=5,r=5,t=50,b=5),
    xaxis=dict(title="Carga factorial"),
)

# ── 3. SCREE PLOT ─────────────────────────────────────────────────────────────
fig_scree = make_subplots(specs=[[{"secondary_y":True}]])
fig_scree.add_trace(go.Bar(
    x=[f"CP{i+1}" for i in range(len(PCA_VARS))], y=var_ratio*100,
    name="Var. individual (%)", marker_color="#3498db", opacity=0.7,
))
fig_scree.add_trace(go.Scatter(
    x=[f"CP{i+1}" for i in range(len(PCA_VARS))], y=cum_var*100,
    name="Var. acumulada (%)", mode="lines+markers",
    line=dict(color="#e74c3c",width=2), marker=dict(size=7),
), secondary_y=True)
fig_scree.add_trace(go.Scatter(
    x=[f"CP{i+1}" for i in range(len(PCA_VARS))], y=eigvals,
    name="Eigenvalor", mode="lines+markers",
    line=dict(color="#2c3e50",width=2,dash="dot"), marker=dict(size=7),
))
fig_scree.add_hline(y=1, line_dash="dash", line_color="#e74c3c",
                    annotation_text="Kaiser", annotation_position="top right")
fig_scree.update_layout(
    title=f"Scree plot &mdash; Criterio Kaiser: {n_kaiser} componentes retenidos",
    template=TPL, font=FONT, height=380,
    legend=dict(orientation="h", y=-0.25),
    margin=dict(l=5,r=5,t=50,b=5),
)
fig_scree.update_yaxes(title_text="Eigenvalor / Var. (%)", secondary_y=False)
fig_scree.update_yaxes(title_text="Var. acumulada (%)", secondary_y=True)

# Kaiser summary table (text trace)
k_tbl = pd.DataFrame({
    "CP": [f"CP{i+1}" for i in range(len(PCA_VARS))],
    "Eigenvalor": eigvals.round(3),
    "Var (%)": (var_ratio*100).round(1),
    "Acum (%)": (cum_var*100).round(1),
    "Kaiser": ["Retener" if e>1 else "-" for e in eigvals],
})
fig_ktable = go.Figure(go.Table(
    header=dict(values=list(k_tbl.columns),
                fill_color="#1F497D", font=dict(color="white",size=12),
                align="center"),
    cells=dict(values=[k_tbl[c] for c in k_tbl.columns],
               fill_color=[["#f8f9fc","white"]*5],
               align="center", height=28),
))
fig_ktable.update_layout(template=TPL, font=FONT, height=320,
                         margin=dict(l=5,r=5,t=20,b=5))

# ── 4. KAISER LOADINGS HEATMAP ────────────────────────────────────────────────
fig_kaiser = go.Figure(go.Heatmap(
    z=lk.round(3), x=[f"CP{j+1}" for j in range(n_kaiser)], y=VAR_SHORT,
    colorscale="RdBu_r", zmid=0, zmin=-1, zmax=1,
    text=lk.round(2), texttemplate="%{text}",
    colorbar=dict(title="Carga", thickness=12),
))
fig_kaiser.update_layout(
    title=f"Cargas factoriales &mdash; {n_kaiser} componentes Kaiser",
    template=TPL, font=FONT, height=400, margin=dict(l=5,r=5,t=50,b=5),
)

# ── 5. K-MEANS FREQUENCY ─────────────────────────────────────────────────────
freq = dw["GRADO_PCA"].value_counts().reindex(GRADE_LABELS)
fig_freq = go.Figure(go.Bar(
    x=GRADE_LABELS, y=freq.values, text=freq.values,
    textposition="outside",
    marker_color=GRADE_COLORS_LIST,
    hovertemplate="%{x}: %{y} municipios<extra></extra>",
))
fig_freq.update_layout(title="Municipios por grado K-means", template=TPL, font=FONT,
                       height=360, showlegend=False, margin=dict(l=5,r=5,t=50,b=5),
                       yaxis_title="Municipios")

# ── 6. BOXPLOT BY GRADE ───────────────────────────────────────────────────────
fig_box = go.Figure()
for g, c in zip(GRADE_LABELS, GRADE_COLORS_LIST):
    vals = dw.loc[dw["GRADO_PCA"]==g, "INDEX_PCA"].values
    fig_box.add_trace(go.Box(y=vals, name=g, marker_color=c, boxmean=True,
                             hovertemplate="%{y:.3f}<extra>"+g+"</extra>"))
fig_box.update_layout(title="Distribucion del indice PCA por grado", template=TPL,
                      font=FONT, height=380, showlegend=False,
                      yaxis_title="Indice PCA", margin=dict(l=5,r=5,t=50,b=5))

# ── 6b. RADAR ────────────────────────────────────────────────────────────────
theta = VAR_SHORT + [VAR_SHORT[0]]
fig_radar = go.Figure()
for g, c in zip(GRADE_LABELS, GRADE_COLORS_LIST):
    vals = radar_norm_df.loc[g].tolist()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=theta, name=g,
        fill="toself", fillcolor=c, line=dict(color=c, width=2), opacity=0.55,
    ))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0,1],
               tickfont=dict(size=9), gridcolor="#e0e0e0"),
               angularaxis=dict(tickfont=dict(size=10))),
    showlegend=True, template=TPL, font=FONT, height=480,
    title="Perfil promedio de variables por grado (valores normalizados 0–1)",
    legend=dict(orientation="h", y=-0.08),
    margin=dict(l=20,r=20,t=60,b=20),
)

# ── 6c. BIPLOT ────────────────────────────────────────────────────────────────
fig_biplot = go.Figure()
for g, c in zip(GRADE_LABELS, GRADE_COLORS_LIST):
    sub = dw[dw["GRADO_PCA"]==g]
    c2  = sub["COMP2"].tolist() if "COMP2" in dw.columns else [0]*len(sub)
    fig_biplot.add_trace(go.Scatter(
        x=sub["COMP1"].tolist(), y=c2,
        mode="markers", name=g,
        marker=dict(color=c, size=4, opacity=0.45),
        customdata=sub[["NOM_MUN","NOM_ENT"]].values.tolist(),
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<extra>"+g+"</extra>",
    ))
_scale = 3.5
for _v, _l1, _l2 in zip(VAR_SHORT, lpc1, lpc2):
    fig_biplot.add_annotation(
        x=float(_l1)*_scale, y=float(_l2)*_scale, ax=0, ay=0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor="#1a1a2e",
    )
    fig_biplot.add_annotation(
        x=float(_l1)*_scale*1.18, y=float(_l2)*_scale*1.12,
        text=_v, showarrow=False, font=dict(size=11, color="#1a1a2e"),
    )
fig_biplot.add_vline(x=0, line_dash="dash", line_color="#bbb", line_width=1)
fig_biplot.add_hline(y=0, line_dash="dash", line_color="#bbb", line_width=1)
fig_biplot.update_layout(
    title=f"Biplot PCA &mdash; CP1 ({var_ratio[0]*100:.1f}%) vs CP2 ({var_ratio[1]*100:.1f}%)",
    template=TPL, font=FONT, height=520,
    xaxis_title=f"CP1 ({var_ratio[0]*100:.1f}% varianza)",
    yaxis_title=f"CP2 ({var_ratio[1]*100:.1f}% varianza)",
    legend=dict(orientation="h", y=-0.16),
    margin=dict(l=5,r=5,t=55,b=5),
)

# ── 6d. NATIONAL MAP ──────────────────────────────────────────────────────────
fig_national = go.Figure()
for g, c in zip(GRADE_LABELS, GRADE_COLORS_LIST):
    sub = nat[nat["GRADO_PCA"]==g]
    fig_national.add_trace(go.Scattermapbox(
        lat=sub["lat"].tolist(), lon=sub["lon"].tolist(),
        mode="markers", name=g,
        marker=dict(size=sub["msize"].tolist(), color=c, opacity=0.72,
                    sizemode="diameter"),
        customdata=sub[["NOM_MUN","NOM_ENT","INDEX_PCA","GRADO_PCA","GM_2020",
                         "POB_TOT","ANALF","SBASC","OVSAE","PO2SM"]].values.tolist(),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "<i>%{customdata[1]}</i><br>"
            "<b>Indice PCA:</b> %{customdata[2]:.3f} &nbsp; Grado: %{customdata[3]}<br>"
            "<b>CONAPO DP2:</b> %{customdata[4]}<br>"
            "<b>Poblacion:</b> %{customdata[5]:,}<br>"
            "<b>Analfabetismo:</b> %{customdata[6]:.1f}%<br>"
            "<b>Sin educ. basica:</b> %{customdata[7]:.1f}%<br>"
            "<b>Sin agua entubada:</b> %{customdata[8]:.1f}%<br>"
            "<b>Ingreso &lt; 2 SM:</b> %{customdata[9]:.1f}%"
            "<extra></extra>"
        ),
    ))
fig_national.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=4.2, mapbox_center={"lat":23.5,"lon":-102.5},
    height=600, font=FONT,
    legend=dict(orientation="h", yanchor="bottom", y=0.01,
                xanchor="right", x=0.99,
                bgcolor="rgba(255,255,255,0.88)", bordercolor="#ccc", borderwidth=1),
    margin=dict(l=0,r=0,t=10,b=0),
    uirevision="national",
)

# ── 7. MAP (single figure, 3-option dropdown) ─────────────────────────────────
fig_map = go.Figure(go.Choroplethmapbox(
    geojson=geojson_dict,
    locations=zmg["norm"].tolist(),
    z=pca_z.tolist(),
    colorscale="RdYlGn_r",
    zmin=float(pca_z.min()), zmax=float(pca_z.max()),
    marker_opacity=0.82, marker_line_width=1.5, marker_line_color="white",
    colorbar=dict(title=dict(text="Indice PCA",side="right"), thickness=14, len=0.65),
    customdata=custom,
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Indice PCA: %{z:.3f}<br>"
        "Grado K-means: %{customdata[1]}<br>"
        "Grado CONAPO: %{customdata[2]}"
        "<extra></extra>"
    ),
))

_tvals = [0.4,1.2,2.0,2.8,3.6]
_ttxt  = GRADE_LABELS

fig_map.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=9.5, mapbox_center=ZMG_CENTER,
    height=540, font=FONT, template=TPL,
    margin=dict(l=0,r=0,t=90,b=0),
    title=dict(text="ZMG &mdash; Indice de Marginacion PCA", x=0.5, xanchor="center"),
    updatemenus=[dict(
        type="buttons", direction="right",
        buttons=[
            dict(label="Indice PCA (continuo)", method="restyle",
                 args=[{"z":[pca_z.tolist()],
                        "colorscale":"RdYlGn_r",
                        "zmin":float(pca_z.min()),"zmax":float(pca_z.max()),
                        "colorbar.title.text":"Indice PCA",
                        "colorbar.tickvals":None,"colorbar.ticktext":None,
                        "hovertemplate":("<b>%{customdata[0]}</b><br>"
                            "Indice PCA: %{z:.3f}<br>"
                            "Grado K-means: %{customdata[1]}<br>"
                            "Grado CONAPO: %{customdata[2]}<extra></extra>")}]),
            dict(label="Grado K-means", method="restyle",
                 args=[{"z":[km_z.tolist()],
                        "colorscale":discrete_cs(),
                        "zmin":0,"zmax":4,
                        "colorbar.title.text":"Grado K-means",
                        "colorbar.tickvals":_tvals,"colorbar.ticktext":_ttxt,
                        "hovertemplate":("<b>%{customdata[0]}</b><br>"
                            "Grado K-means: %{customdata[1]}<br>"
                            "Indice PCA: %{customdata[3]:.3f}<br>"
                            "Grado CONAPO: %{customdata[2]}<extra></extra>")}]),
            dict(label="Grado CONAPO DP2", method="restyle",
                 args=[{"z":[cn_z.tolist()],
                        "colorscale":discrete_cs(),
                        "zmin":0,"zmax":4,
                        "colorbar.title.text":"Grado CONAPO",
                        "colorbar.tickvals":_tvals,"colorbar.ticktext":_ttxt,
                        "hovertemplate":("<b>%{customdata[0]}</b><br>"
                            "Grado CONAPO: %{customdata[2]}<br>"
                            "Indice CONAPO DP2: %{customdata[4]:.3f}<br>"
                            "Grado K-means: %{customdata[1]}<extra></extra>")}]),
        ],
        showactive=True, x=0.01, y=1.01,
        xanchor="left", yanchor="bottom",
        bgcolor="white", bordercolor="#dde3ec",
        font=dict(size=12), pad=dict(l=4,r=4,t=4,b=4),
    )],
)

# ── 8. SCATTER PCA vs CONAPO (5 grade traces + trendline) ────────────────────
fig_scatter = go.Figure()
for g, c in zip(GRADE_LABELS, GRADE_COLORS_LIST):
    sub = dw[dw["GRADO_PCA"]==g]
    fig_scatter.add_trace(go.Scatter(
        x=sub["IM_2020"].tolist(), y=sub["INDEX_PCA"].tolist(),
        mode="markers", name=g,
        marker=dict(color=c, size=5, opacity=0.6),
        customdata=sub[["NOM_MUN","NOM_ENT","IM_2020","INDEX_PCA"]].values.tolist(),
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
            "CONAPO DP2: %{x:.3f}<br>Indice PCA: %{y:.3f}"
            "<extra>"+g+"</extra>"
        ),
    ))
z = np.polyfit(dw["IM_2020"], dw["INDEX_PCA"], 1)
xl = np.linspace(dw["IM_2020"].min(), dw["IM_2020"].max(), 150)
fig_scatter.add_trace(go.Scatter(
    x=xl.tolist(), y=np.polyval(z,xl).tolist(),
    mode="lines", name=f"Tendencia (r={r_conapo:.3f})",
    line=dict(color="#2c3e50",width=1.5,dash="dash"),
))
fig_scatter.update_layout(
    title=f"Indice PCA vs. CONAPO DP2 &mdash; r = {r_conapo:.4f} &nbsp; (n = {n_obs:,})",
    template=TPL, font=FONT, height=460,
    legend=dict(orientation="h", y=-0.25),
    xaxis_title="Indice CONAPO DP2",
    yaxis_title="Indice PCA (CP1)",
    margin=dict(l=5,r=5,t=50,b=5),
)

# ─── JSON DATA FOR JS INTERACTIVITY ──────────────────────────────────────────
states_list = sorted(dw["NOM_ENT"].unique().tolist())

scatter_json = json.dumps([
    {"g": row["GRADO_PCA"], "x": round(float(row["IM_2020"]),4),
     "y": round(float(row["INDEX_PCA"]),4),
     "m": row["NOM_MUN"], "e": row["NOM_ENT"]}
    for _, row in dw.iterrows()
], ensure_ascii=False)

table_json = json.dumps([
    {"mun": row["NOM_MUN"], "ent": row["NOM_ENT"],
     "pca": round(float(row["INDEX_PCA"]),3),
     "grado": row["GRADO_PCA"],
     "conapo": row["GM_2020"],
     "pop": int(row["POB_TOT"]),
     "cvegeo": row["CVEGEO"]}
    for _, row in dw.sort_values("INDEX_PCA", ascending=False).iterrows()
], ensure_ascii=False)

# Cross-tab HTML
ct_full = pd.crosstab(dw["GRADO_PCA"], dw["GM_2020"], margins=True, margins_name="Total")
ct_full = ct_full.reindex(
    index=GRADE_LABELS+["Total"],
    columns=[g for g in GRADE_LABELS if g in ct_full.columns]+["Total"],
    fill_value=0)
ct_html = ct_full.to_html(classes="ct-table", border=0)

# Summary cards data
kmo_lbl = next(l for t,l in [(0.9,"Excelente"),(0.8,"Muy bueno"),(0.7,"Aceptable"),(0,"Regular")] if kmo_total>=t)
CARDS = [
    ("#3498db", f"{n_obs:,}", "Municipios", "con datos completos"),
    ("#2ecc71", f"{kmo_total:.4f}", "KMO global", kmo_lbl+" &mdash; adecuado para PCA"),
    ("#9b59b6", f"{var_ratio[0]*100:.1f}%", "Varianza CP1", f"Eigenvalor: {eigvals[0]:.3f}"),
    ("#e67e22", str(n_kaiser), "Componentes Kaiser", f"Varianza acum.: {cum_var[n_kaiser-1]*100:.1f}%"),
    ("#1abc9c", f"r = {r_conapo:.4f}", "Correlacion c/ CONAPO", "Indice PCA vs. DP2"),
    ("#e74c3c", f"{pct_match:.1f}%", "Concordancia grados", "Mismo grado K-means vs CONAPO"),
]
cards_html = "".join(
    f'<div class="card"><div class="cv" style="color:{c}">{v}</div>'
    f'<div class="cl">{l}</div><div class="cs">{s}</div></div>'
    for c,v,l,s in CARDS
)

# ─── HTML ─────────────────────────────────────────────────────────────────────
print("Assembling HTML...")

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Marginacion Municipal PCA 2020</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{{--navy:#1F497D;--amber:#D48C00;--bg:#f2f4f8;--white:#fff;--border:#dde3ec;--text:#2c3e50;--sidebar:220px}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"Inter",Arial,sans-serif;background:var(--bg);color:var(--text);display:flex;min-height:100vh}}

/* ── Sidebar ── */
#sidebar{{width:var(--sidebar);min-height:100vh;background:var(--navy);
  display:flex;flex-direction:column;position:fixed;top:0;left:0;z-index:100;
  border-right:3px solid var(--amber)}}
#sidebar .logo{{padding:16px 18px 14px;border-bottom:1px solid rgba(255,255,255,.12)}}
#sidebar .logo h2{{color:#fff;font-size:.95rem;font-weight:700;line-height:1.3;margin-top:6px}}
#sidebar .logo p{{color:rgba(255,255,255,.6);font-size:.72rem;margin-top:3px}}
.back-link{{display:inline-flex;align-items:center;gap:5px;color:rgba(255,255,255,.55);
  font-size:.72rem;font-weight:600;text-decoration:none;letter-spacing:.03em;
  transition:color .15s}}
.back-link:hover{{color:#fff}}
#sidebar nav{{flex:1;padding:10px 0}}
#sidebar nav a{{display:flex;align-items:center;gap:9px;padding:10px 18px;
  color:rgba(255,255,255,.72);font-size:.82rem;cursor:pointer;
  border-left:3px solid transparent;transition:all .15s;text-decoration:none;
  white-space:nowrap;overflow:hidden}}
#sidebar nav a:hover{{color:#fff;background:rgba(255,255,255,.07)}}
#sidebar nav a.active{{color:#fff;background:rgba(255,255,255,.12);
  border-left-color:var(--amber);font-weight:600}}
#sidebar nav .nav-icon{{font-size:1rem;flex-shrink:0}}
#sidebar .footer{{padding:12px 18px;font-size:.68rem;color:rgba(255,255,255,.35);
  border-top:1px solid rgba(255,255,255,.1)}}

/* ── Main ── */
#main{{margin-left:var(--sidebar);flex:1;display:flex;flex-direction:column;min-height:100vh}}
.topbar{{background:var(--navy);color:#fff;padding:16px 28px 12px;
  border-bottom:3px solid var(--amber)}}
.topbar h1{{font-size:1.4rem;font-weight:700}}
.topbar p{{font-size:.8rem;opacity:.7;margin-top:3px}}

/* ── Sections ── */
.section{{display:none;padding:24px 28px;animation:fadeIn .2s ease}}
.section.active{{display:block}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
.sec-title{{font-size:1.05rem;font-weight:700;color:var(--navy);
  border-left:4px solid var(--amber);padding-left:10px;margin:0 0 18px}}
.sec-sub{{font-size:.9rem;font-weight:600;color:var(--navy);margin:20px 0 10px}}

/* ── Cards ── */
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin-bottom:20px}}
.card{{background:var(--white);border-radius:9px;border:1px solid var(--border);
  padding:14px 16px;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.cv{{font-size:1.55rem;font-weight:800;line-height:1.1}}
.cl{{font-size:.72rem;font-weight:700;color:#666;margin-top:4px;text-transform:uppercase;letter-spacing:.04em}}
.cs{{font-size:.7rem;color:#999;margin-top:2px}}

/* ── Panels ── */
.panel{{background:var(--white);border-radius:9px;border:1px solid var(--border);
  padding:6px;box-shadow:0 1px 4px rgba(0,0,0,.06);margin-bottom:14px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px}}
@media(max-width:960px){{.grid2,.grid3{{grid-template-columns:1fr}}}}

/* ── Info box ── */
.infobox{{background:#eef6ff;border:1px solid #c5ddf5;border-radius:8px;
  padding:12px 16px;font-size:.82rem;line-height:1.6;margin-bottom:14px;color:#1a3a65}}

/* ── Scatter controls ── */
.ctrl-bar{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}}
.ctrl-bar label{{font-size:.82rem;font-weight:600;color:#555}}
.ctrl-bar select{{padding:6px 12px;border:1px solid var(--border);border-radius:6px;
  font-size:.82rem;background:var(--white);cursor:pointer;min-width:180px}}

/* ── Grade filter buttons ── */
.grade-btns{{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:12px}}
.grade-btn{{padding:5px 14px;border-radius:20px;border:1px solid var(--border);
  font-size:.78rem;font-weight:600;cursor:pointer;background:var(--white);
  transition:all .15s}}
.grade-btn.active{{color:#fff;border-color:transparent}}

/* ── Download button ── */
.btn-download{{display:inline-flex;align-items:center;gap:7px;padding:7px 16px;
  background:var(--navy);color:#fff;border:none;border-radius:7px;font-size:.82rem;
  font-weight:600;cursor:pointer;transition:opacity .15s;margin-bottom:12px}}
.btn-download:hover{{opacity:.82}}

/* ── Municipality table ── */
.mun-table-wrap{{overflow-x:auto;max-height:420px;overflow-y:auto;
  border:1px solid var(--border);border-radius:8px}}
.mun-table{{width:100%;border-collapse:collapse;font-size:.8rem}}
.mun-table th{{background:var(--navy);color:#fff;padding:8px 12px;
  text-align:left;position:sticky;top:0;z-index:2;font-weight:600;white-space:nowrap}}
.mun-table th.sortable{{cursor:pointer;user-select:none}}
.mun-table th.sortable:hover{{background:#1a3a65}}
.mun-table td{{padding:6px 12px;border-bottom:1px solid var(--border)}}
.mun-table tr:hover td{{background:#f4f7fc}}
.badge{{padding:2px 8px;border-radius:12px;font-size:.72rem;font-weight:700;color:#fff;white-space:nowrap}}
.mun-count{{font-size:.78rem;color:#888;margin-bottom:6px}}
.search-box{{padding:7px 12px;border:1px solid var(--border);border-radius:6px;
  font-size:.82rem;width:260px;margin-bottom:10px}}

/* ── Crosstab ── */
.ct-table{{width:100%;border-collapse:collapse;font-size:.8rem}}
.ct-table th,.ct-table td{{padding:7px 12px;border:1px solid var(--border);text-align:center}}
.ct-table th{{background:var(--navy);color:#fff;font-weight:600}}
.ct-table tr:nth-child(even) td{{background:#f8f9fc}}
.ct-table tr:last-child td,.ct-table tr:last-child th{{font-weight:700;background:#eef2f7}}

/* ── Scrollbar ── */
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:#f0f0f0}}
::-webkit-scrollbar-thumb{{background:#bbb;border-radius:3px}}
</style>
</head>
<body>

<!-- ── SIDEBAR ───────────────────────────────────────────────────────────── -->
<div id="sidebar">
  <div class="logo">
    <a href="https://carpuro.ai" class="back-link">&#8592; carpuro.ai</a>
    <h2>Marginacion Municipal PCA</h2>
    <p>MCD CUCEA &mdash; Metodos Multivariados</p>
  </div>
  <nav>
    <a class="nav-item active" onclick="showSec('resumen',this)">Resumen</a>
    <a class="nav-item" onclick="showSec('eda',this)">Exploratorio</a>
    <a class="nav-item" onclick="showSec('pca',this)">PCA &mdash; 1 Componente</a>
    <a class="nav-item" onclick="showSec('kaiser',this)">Kaiser</a>
    <a class="nav-item" onclick="showSec('biplot',this)">Biplot</a>
    <a class="nav-item" onclick="showSec('kmeans',this)">K-means</a>
    <a class="nav-item" onclick="showSec('nacional',this)">Mapa Nacional</a>
    <a class="nav-item" onclick="showSec('mapas',this)">Mapas ZMG</a>
    <a class="nav-item" onclick="showSec('conapo',this)">Comparacion CONAPO</a>
  </nav>
  <div class="footer">Carlos Pulido Rosas &bull; Mayo 2026</div>
</div>

<!-- ── MAIN ──────────────────────────────────────────────────────────────── -->
<div id="main">
<div class="topbar">
  <h1>Indice de Marginacion Municipal mediante PCA</h1>
  <p>Censo de Poblacion y Vivienda 2020 &bull; CONAPO &bull; {n_obs:,} municipios analizados</p>
</div>

<!-- ── SECTION: RESUMEN ──────────────────────────────────────────────────── -->
<section id="sec-resumen" class="section active">
  <div class="sec-title">Resumen del analisis</div>
  <div class="cards">{cards_html}</div>
  <div class="infobox">
    <strong>Metodologia:</strong> Se aplicaron PCA y K-means sobre 9 variables del Censo 2020 para construir un
    indice sintetico de marginacion a nivel municipal. El primer componente principal (CP1) explica
    <strong>{var_ratio[0]*100:.1f}%</strong> de la varianza total y se usa como indice de marginacion.
    Los municipios se clasificaron en 5 grados mediante K-means. El indice resultante correlaciona
    <strong>r = {r_conapo:.4f}</strong> con el indice oficial CONAPO DP2.
  </div>
  <div class="sec-sub">KMO = {kmo_total:.4f} ({kmo_lbl}) &nbsp;|&nbsp; Bartlett p-valor = {p_val:.2e} &nbsp;|&nbsp; Componentes Kaiser retenidos: {n_kaiser}</div>
</section>

<!-- ── SECTION: EDA ───────────────────────────────────────────────────────── -->
<section id="sec-eda" class="section">
  <div class="sec-title">Analisis Exploratorio</div>
  <div class="infobox">
    La matriz de correlaciones muestra correlaciones positivas fuertes entre las 9 variables
    (promedio r&nbsp;=&nbsp;<strong>{avg_off_corr:.3f}</strong>). El par mas correlacionado es
    <strong>{max_corr_v1}</strong> &mdash; <strong>{max_corr_v2}</strong>
    (r&nbsp;=&nbsp;<strong>{max_corr_val:.3f}</strong>), lo que refleja que la carencia de
    servicios basicos tiende a co-ocurrir. Esta colinealidad justifica el uso de PCA:
    existe suficiente redundancia de informacion para reducir las 9 variables a unos pocos
    componentes sin perdida significativa. El test de Bartlett rechaza la hipotesis de
    independencia (&chi;&sup2;&nbsp;=&nbsp;<strong>{chi2_stat:.0f}</strong>,
    p&nbsp;&lt;&nbsp;0.001), y el KMO&nbsp;=&nbsp;<strong>{kmo_total:.4f}</strong>
    confirma que los datos son <strong>{kmo_lbl}s</strong> para PCA.
  </div>
  <div class="panel">{fdiv(fig_corr,"fig-corr")}</div>
</section>

<!-- ── SECTION: PCA ───────────────────────────────────────────────────────── -->
<section id="sec-pca" class="section">
  <div class="sec-title">PCA &mdash; Indice de marginacion (1 componente)</div>
  <div class="infobox">
    CP1 captura el <strong>{var_ratio[0]*100:.1f}%</strong> de la varianza total con un
    eigenvalor de <strong>{eigvals[0]:.3f}</strong>. Todas las cargas son positivas, lo
    que confirma que CP1 es un <em>indice general de marginacion</em>: un municipio con
    mayor puntaje en CP1 tiene mas carencias en todas las dimensiones simultaneamente.
    La variable con mayor carga es <strong>{max_load_var}</strong>
    ({max_load_val:.4f}), indicando que es la dimension mas representativa de la
    marginacion en Mexico 2020. Al invertir el signo del componente (convencion: media
    de cargas positiva), los valores mas altos corresponden a mayor marginacion.
  </div>
  <div class="panel">{fdiv(fig_loads,"fig-loads")}</div>
</section>

<!-- ── SECTION: KAISER ────────────────────────────────────────────────────── -->
<section id="sec-kaiser" class="section">
  <div class="sec-title">PCA &mdash; Criterio de Kaiser ({n_kaiser} componentes)</div>
  <div class="infobox">
    El criterio de Kaiser retiene <strong>{n_kaiser} componentes</strong> (eigenvalor&nbsp;&gt;&nbsp;1),
    que explican en conjunto el <strong>{cum_var[n_kaiser-1]*100:.1f}%</strong> de la varianza total.
    CP1 domina claramente con el <strong>{var_ratio[0]*100:.1f}%</strong>; CP2 aporta
    <strong>{var_ratio[1]*100:.1f}%</strong> adicional y captura diferencias secundarias
    entre las dimensiones de carencia. El scree plot muestra un codo pronunciado despues
    de CP1, lo que refuerza usar un unico componente como indice sintetico de marginacion.
  </div>
  <div class="grid2">
    <div class="panel">{fdiv(fig_scree,"fig-scree")}</div>
    <div class="panel">{fdiv(fig_ktable,"fig-ktable")}</div>
  </div>
  <div class="panel">{fdiv(fig_kaiser,"fig-kaiser")}</div>
</section>

<!-- ── SECTION: BIPLOT ────────────────────────────────────────────────────── -->
<section id="sec-biplot" class="section">
  <div class="sec-title">Biplot PCA &mdash; CP1 vs CP2</div>
  <div class="infobox">
    El biplot proyecta simultaneamente los <strong>{n_obs:,} municipios</strong> y las
    <strong>9 variables</strong> en el espacio CP1&ndash;CP2. Las flechas indican la
    direccion y magnitud de cada variable en ese espacio. Variables en la misma
    direccion estan positivamente correlacionadas. En el eje horizontal (CP1, indice de
    marginacion), los municipios de grado <em>Muy alto</em> aparecen a la derecha
    mientras los de grado <em>Muy bajo</em> quedan a la izquierda. CP2 (eje vertical)
    separa dimensiones secundarias: por ejemplo, <em>Ingr.&lt;2SM</em> puede diferir
    de las carencias de vivienda en municipios de ingreso bajo pero urbanizados.
  </div>
  <div class="panel">{fdiv(fig_biplot,"fig-biplot")}</div>
</section>

<!-- ── SECTION: K-MEANS ───────────────────────────────────────────────────── -->
<section id="sec-kmeans" class="section">
  <div class="sec-title">Clasificacion K-means (5 grupos)</div>
  <div class="infobox">
    K-means (k&nbsp;=&nbsp;5, 25 inicializaciones) clasifico los municipios en 5 grupos
    ordenados de <em>Muy bajo</em> a <em>Muy alto</em> segun el valor del indice PCA (CP1).
    El grado mas frecuente es <strong>{most_common_grade}</strong> con
    <strong>{most_common_n:,} municipios</strong>
    ({most_common_n/n_obs*100:.1f}%). El radar chart inferior permite comparar el
    perfil promedio de las 9 variables en cada grado: los municipios de grado
    <em>Muy alto</em> presentan valores maximos en casi todas las dimensiones
    simultaneamente, mientras que los de grado <em>Muy bajo</em> se acercan a cero
    en todas ellas.
  </div>
  <div class="grid2">
    <div class="panel">{fdiv(fig_freq,"fig-freq")}</div>
    <div class="panel">{fdiv(fig_box,"fig-box")}</div>
  </div>
  <div class="panel">{fdiv(fig_radar,"fig-radar")}</div>

  <div class="sec-sub">Tabla de municipios</div>
  <button class="btn-download" onclick="downloadCSV()">&#8659; Descargar CSV</button>
  <div class="grade-btns" id="grade-btns">
    <button class="grade-btn active" style="background:#555;border-color:#555;color:#fff"
            onclick="filterTable('Todos',this)">Todos</button>
    {''.join(f'<button class="grade-btn" style="--gc:{c}" onclick="filterTable(\'{g}\',this)">{g}</button>'
             for g,c in zip(GRADE_LABELS, GRADE_COLORS_LIST))}
  </div>
  <input class="search-box" type="text" id="mun-search" placeholder="Buscar municipio o estado..." oninput="filterTable(currentGrade,null)">
  <div class="mun-count" id="mun-count"></div>
  <div class="mun-table-wrap">
    <table class="mun-table">
      <thead><tr>
        <th class="sortable" onclick="sortTable('pca')">Indice PCA &#8597;</th>
        <th>Municipio</th>
        <th>Estado</th>
        <th>Grado K-means</th>
        <th>Grado CONAPO</th>
        <th>Poblacion</th>
      </tr></thead>
      <tbody id="mun-tbody"></tbody>
    </table>
  </div>
</section>

<!-- ── SECTION: MAPA NACIONAL ─────────────────────────────────────────────── -->
<section id="sec-nacional" class="section">
  <div class="sec-title">Mapa Nacional de Marginacion</div>
  <div class="infobox">
    Distribucion geografica del indice de marginacion PCA para <strong>{nat_match:,} municipios</strong>
    con cobertura en el Censo 2020. El tamano de cada punto es proporcional a la poblacion
    del municipio. Usa los filtros para explorar por estado o grado, y el scroll del raton
    para hacer zoom. El hover muestra indice PCA, grado CONAPO y cuatro indicadores clave.
  </div>
  <div class="ctrl-bar" style="flex-wrap:wrap;gap:10px;margin-bottom:8px">
    <div style="display:flex;align-items:center;gap:8px">
      <label style="font-size:.82rem;font-weight:600;color:#555">Estado:</label>
      <select id="nat-state-sel" onchange="filterNational()"
              style="padding:5px 10px;border:1px solid #dde3ec;border-radius:6px;font-size:.82rem">
        <option value="all">Todos</option>
        {''.join(f'<option value="{s}">{s}</option>' for s in nat_states_list)}
      </select>
    </div>
    <div style="display:flex;align-items:center;gap:8px">
      <label style="font-size:.82rem;font-weight:600;color:#555">Tamano:</label>
      <select id="nat-size-sel" onchange="filterNational()"
              style="padding:5px 10px;border:1px solid #dde3ec;border-radius:6px;font-size:.82rem">
        <option value="pop">Proporcional a poblacion</option>
        <option value="fixed">Uniforme</option>
      </select>
    </div>
    <span id="nat-count" style="font-size:.78rem;color:#888;align-self:center"></span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px" id="nat-grade-btns">
    {''.join(f'<button class="grade-btn active" style="background:{c};color:#fff;border-color:{c}" '
             f'onclick="toggleNatGrade(\'{g}\',this)">{g}</button>'
             for g,c in zip(GRADE_LABELS, GRADE_COLORS_LIST))}
  </div>
  <div class="panel" style="padding:4px">{fdiv(fig_national,"fig-national")}</div>
</section>

<!-- ── SECTION: MAPAS ─────────────────────────────────────────────────────── -->
<section id="sec-mapas" class="section">
  <div class="sec-title">Mapas &mdash; Zona Metropolitana de Guadalajara</div>
  <div class="infobox">
    Usa el selector <strong>"Seleccionar estadistica"</strong> dentro del mapa para cambiar entre
    el indice PCA continuo, los grados K-means y los grados oficiales CONAPO.
    Pasa el cursor sobre cada municipio para ver los valores detallados.
  </div>
  <div class="panel">{fdiv(fig_map,"fig-map")}</div>
</section>

<!-- ── SECTION: CONAPO ───────────────────────────────────────────────────── -->
<section id="sec-conapo" class="section">
  <div class="sec-title">Comparacion con CONAPO DP2</div>
  <div class="infobox">
    La correlacion <strong>r&nbsp;=&nbsp;{r_conapo:.4f}</strong> entre el indice PCA (CP1)
    y el indice DP2 oficial de CONAPO confirma que ambos metodos capturan el mismo fenomeno
    subyacente con alta fidelidad. La concordancia exacta de grados es
    <strong>{pct_match:.1f}%</strong> ({discordance_pct:.1f}% de municipios difieren en
    un grado). Las discordancias ocurren principalmente en la frontera entre grados
    adyacentes y reflejan diferencias metodologicas: el DP2 usa distancias ponderadas
    iterativas, mientras que PCA asigna el mismo peso implicitamente a traves de la
    varianza comun. La alta correlacion valida el enfoque PCA como alternativa reproducible
    y transparente al indice oficial.
  </div>

  <div class="ctrl-bar">
    <label>Filtrar por estado:</label>
    <select id="state-sel" onchange="filterScatter()">
      <option value="all">Todos los estados</option>
      {''.join(f'<option value="{s}">{s}</option>' for s in states_list)}
    </select>
    <span id="scatter-count" style="font-size:.78rem;color:#888"></span>
  </div>
  <div class="panel">{fdiv(fig_scatter,"fig-scatter")}</div>

  <div class="sec-sub">Tabla cruzada: Grado PCA vs. Grado CONAPO</div>
  <div class="panel" style="padding:16px;overflow-x:auto">
    <p style="font-size:.8rem;color:#666;margin-bottom:10px">
      Filas = grado K-means &nbsp;|&nbsp; Columnas = grado CONAPO DP2 &nbsp;|&nbsp;
      <strong>Concordancia exacta: {pct_match:.1f}%</strong>
    </p>
    {ct_html}
  </div>
</section>

</div><!-- /main -->

<!-- ── EMBEDDED DATA ──────────────────────────────────────────────────────── -->
<script>
const SCATTER_DATA  = {scatter_json};
const TABLE_DATA    = {table_json};
const NAT_DATA      = {national_json};
const GRADE_COLORS  = {json.dumps(GRADE_COLORS)};
const GRADE_LABELS  = {json.dumps(GRADE_LABELS)};
const N_GRADE_TRACES = {len(GRADE_LABELS)};

// ── Navigation ──────────────────────────────────────────────────────────────
function showSec(name, el) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(a => a.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  if (el) el.classList.add('active');
  setTimeout(() => window.dispatchEvent(new Event('resize')), 80);
}}

// ── Municipalities table ──────────────────────────────────────────────────
let currentGrade = 'Todos';
let sortDir = -1;  // -1 = descending

function filterTable(grade, btn) {{
  currentGrade = grade;
  if (btn) {{
    document.querySelectorAll('.grade-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (grade !== 'Todos') btn.style.background = GRADE_COLORS[grade] || '#555';
    else {{ btn.style.background = '#555'; btn.style.borderColor = '#555'; }}
  }}
  renderTable();
}}

function sortTable(field) {{
  sortDir *= -1;
  renderTable();
}}

function renderTable() {{
  const q = document.getElementById('mun-search').value.toLowerCase();
  let data = TABLE_DATA.filter(r => {{
    const matchGrade = currentGrade === 'Todos' || r.grado === currentGrade;
    const matchQ = !q || r.mun.toLowerCase().includes(q) || r.ent.toLowerCase().includes(q);
    return matchGrade && matchQ;
  }});
  data.sort((a,b) => sortDir * (a.pca - b.pca));
  document.getElementById('mun-count').textContent = data.length + ' municipios';
  const rows = data.slice(0, 200).map(r => {{
    const bg = GRADE_COLORS[r.grado] || '#888';
    return `<tr>
      <td style="text-align:right;font-weight:600">${{r.pca.toFixed(3)}}</td>
      <td>${{r.mun}}</td>
      <td style="color:#888;font-size:.76rem">${{r.ent}}</td>
      <td><span class="badge" style="background:${{bg}}">${{r.grado}}</span></td>
      <td><span class="badge" style="background:${{GRADE_COLORS[r.conapo]||'#888'}}">${{r.conapo}}</span></td>
      <td style="text-align:right;color:#888">${{r.pop.toLocaleString()}}</td>
    </tr>`;
  }}).join('');
  document.getElementById('mun-tbody').innerHTML = rows || '<tr><td colspan="6" style="text-align:center;color:#aaa;padding:20px">Sin resultados</td></tr>';
}}

// ── Scatter state filter ─────────────────────────────────────────────────
function filterScatter() {{
  const state = document.getElementById('state-sel').value;
  const filtered = state === 'all' ? SCATTER_DATA : SCATTER_DATA.filter(r => r.e === state);

  const updates = [];
  const indices = [];
  GRADE_LABELS.forEach((grade, i) => {{
    const sub = filtered.filter(r => r.g === grade);
    updates.push({{
      x: [sub.map(r => r.x)],
      y: [sub.map(r => r.y)],
      customdata: [sub.map(r => [r.m, r.e, r.x, r.y])],
    }});
    indices.push(i);
  }});

  // Update each grade trace
  const div = document.getElementById('fig-scatter');
  if (!div) return;
  GRADE_LABELS.forEach((grade, i) => {{
    Plotly.restyle(div, updates[i], [i]);
  }});

  const cnt = filtered.length;
  document.getElementById('scatter-count').textContent =
    cnt === SCATTER_DATA.length ? '' : cnt + ' municipios';
}}

// ── National map filter ───────────────────────────────────────────────────
const _natVisible = {{}};
GRADE_LABELS.forEach(g => _natVisible[g] = true);

function filterNational() {{
  const state   = document.getElementById('nat-state-sel').value;
  const szMode  = document.getElementById('nat-size-sel').value;
  const src     = state === 'all' ? NAT_DATA : NAT_DATA.filter(r => r.e === state);
  const div     = document.getElementById('fig-national');
  if (!div) return;
  GRADE_LABELS.forEach((grade, i) => {{
    const sub   = src.filter(r => r.g === grade);
    const sizes = szMode === 'pop' ? sub.map(r => r.sz) : sub.map(() => 7);
    Plotly.restyle(div, {{
      lat:          [sub.map(r => r.lat)],
      lon:          [sub.map(r => r.lon)],
      'marker.size':[sizes],
      customdata:   [sub.map(r => [r.m, r.e, r.pca, r.g, r.conapo, r.pop,
                                   r.analf, r.sbasc, r.ovsae, r.po2sm])],
    }}, [i]);
  }});
  const cnt = src.length;
  document.getElementById('nat-count').textContent =
    state === 'all' ? cnt + ' municipios' : cnt + ' municipios en ' + state;
  if (state !== 'all') {{
    const lats = src.map(r => r.lat), lons = src.map(r => r.lon);
    const clat = (Math.min(...lats)+Math.max(...lats))/2;
    const clon = (Math.min(...lons)+Math.max(...lons))/2;
    Plotly.relayout(div, {{'mapbox.center':{{'lat':clat,'lon':clon}}, 'mapbox.zoom':6}});
  }} else {{
    Plotly.relayout(div, {{'mapbox.center':{{'lat':23.5,'lon':-102.5}}, 'mapbox.zoom':4.2}});
  }}
}}

function toggleNatGrade(grade, btn) {{
  const div = document.getElementById('fig-national');
  if (!div) return;
  const i = GRADE_LABELS.indexOf(grade);
  _natVisible[grade] = !_natVisible[grade];
  Plotly.restyle(div, {{visible: [_natVisible[grade]]}}, [i]);
  btn.style.opacity = _natVisible[grade] ? '1' : '0.3';
}}

// ── Download CSV ─────────────────────────────────────────────────────────
function downloadCSV() {{
  const headers = ['CVEGEO','Municipio','Estado','Indice_PCA','Grado_PCA','Grado_CONAPO','Poblacion'];
  const rows = TABLE_DATA.map(r => [
    r.cvegeo, '"'+r.mun.replace(/"/g,'""')+'"',
    '"'+r.ent.replace(/"/g,'""')+'"',
    r.pca, r.grado, r.conapo, r.pop
  ]);
  const csv = [headers, ...rows].map(r => r.join(',')).join('\\r\\n');
  const blob = new Blob(['\\ufeff', csv], {{type:'text/csv;charset=utf-8'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'marginacion_pca_2020.csv'; a.click();
}}

// ── Init ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {{
  renderTable();
  filterScatter();
  filterNational();
}});
</script>

</body>
</html>
"""

out = "output/dashboard_marginacion_pca.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"\nDashboard generado: {out}  ({os.path.getsize(out)/1024:,.0f} KB)")
