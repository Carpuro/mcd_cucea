from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter

# --- Configuración ---
CSV_PATH = Path("categorias_de_corredores.csv")     # Ruta al CSV
OUT_DIR = Path("01_histogramas")                    # Carpeta de salida
BINS = 10                                           # Número de bins
# ----------------------

def main():
    # Crear carpeta de salida si no existe
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar CSV
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {CSV_PATH}")

    print(f"📂 Cargando: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, sep=None, engine="python")  # Detecta separador automáticamente
    print(df.head())

    # Detectar columnas numéricas
    numeric_cols = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors="raise")
            numeric_cols.append(col)
        except Exception:
            pass

    if not numeric_cols:
        raise ValueError("No se encontraron columnas numéricas en el CSV.")

    saved = []
    summary_data = []
    timestamp = datetime.now().strftime("%d_%m_%Y")
    colors = cm.tab10.colors

    # Crear histogramas
    for i, col in enumerate(numeric_cols):
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            print(f"[skip] '{col}' está vacío después de dropna().")
            continue

        # Guardar estadísticas
        stats = s.describe().to_dict()
        stats["column"] = col
        summary_data.append(stats)

        # Figura con mejor UX
        plt.figure(figsize=(9, 6))
        plt.hist(
            s,
            bins=BINS,
            edgecolor="black",
            color=colors[i % len(colors)],
            alpha=0.75,
            linewidth=1.2
        )
        plt.title(f"Histograma - {col}", fontsize=16, fontweight="bold", color="#333333")
        plt.xlabel(col, fontsize=14)
        plt.ylabel("Frecuencia", fontsize=14)
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.gca().set_facecolor("#f9f9f9")
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()

        out_file = OUT_DIR / f"hist_{col}_bins{BINS}_{timestamp}.png"
        plt.savefig(out_file, bbox_inches="tight", dpi=120)
        plt.close()
        saved.append(out_file)

    # Guardar resumen
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_path = OUT_DIR / f"resumen_{timestamp}.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"📊 Resumen guardado en: {summary_path}")

    # Mensaje final
    if saved:
        print("✅ Histogramas guardados en:")
        for f in saved:
            print(f" - {f}")

if __name__ == "__main__":
    main()