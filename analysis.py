import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

from utils.database import crear_base_de_datos, obtener_climas_por_rango, obtener_traficos_por_rango


def load_data_last_years(years=2):
    end = datetime.utcnow()
    start = end - timedelta(days=365 * years)
    start_iso = start.isoformat()
    end_iso = end.isoformat()
    crear_base_de_datos()

    climas = pd.DataFrame(obtener_climas_por_rango(start_iso, end_iso))
    traficos = pd.DataFrame(obtener_traficos_por_rango(start_iso, end_iso))

    if climas.empty or traficos.empty:
        print("No hay datos suficientes para el periodo solicitado.")
        return None

    climas["created_at"] = pd.to_datetime(climas["created_at"], errors="coerce")
    traficos["created_at"] = pd.to_datetime(traficos["created_at"], errors="coerce")
    climas = climas.dropna(subset=["created_at"]) 
    traficos = traficos.dropna(subset=["created_at"]) 
    climas["created_at"] = climas["created_at"].dt.round("s")
    traficos["created_at"] = traficos["created_at"].dt.round("s")

    df = pd.merge(climas, traficos, on=["ciudad", "created_at"] , how="inner")
    # Normalizar nombres
    df = df.rename(columns={
        "temperatura": "temperatura",
        "humedad": "humedad",
        "viento": "viento",
        "congestion": "congestion",
        "descripcion": "descripcion"
    })

    return df


def analyze(df):
    out_dir = os.path.join("analysis_results")
    os.makedirs(out_dir, exist_ok=True)

    numeric = df[["congestion", "temperatura", "humedad", "viento", "precipitation"]].apply(pd.to_numeric, errors="coerce")
    corr = numeric.corr()["congestion"].sort_values(ascending=False)
    print("Correlación con congestión:\n", corr)

    # promedio por descripción
    by_desc = df.groupby("descripcion")["congestion"].agg(["mean", "count"]).sort_values("mean", ascending=False)
    print("\nMedia de congestión por condición meteorológica:\n", by_desc)

    # scatter temperatura vs congestion
    plt.figure(figsize=(8, 5))
    plt.scatter(df["temperatura"], df["congestion"], alpha=0.4)
    plt.xlabel("Temperatura (°C)")
    plt.ylabel("Congestión")
    plt.title("Temperatura vs Congestión")
    plt.grid(True)
    plt.tight_layout()
    temp_plot = os.path.join(out_dir, "temp_vs_congestion.png")
    plt.savefig(temp_plot)
    print(f"Guardado: {temp_plot}")

    # scatter humedad vs congestion
    plt.figure(figsize=(8, 5))
    plt.scatter(df["humedad"], df["congestion"], alpha=0.4, color="orange")
    plt.xlabel("Humedad (%)")
    plt.ylabel("Congestión")
    plt.title("Humedad vs Congestión")
    plt.grid(True)
    plt.tight_layout()
    hum_plot = os.path.join(out_dir, "hum_vs_congestion.png")
    plt.savefig(hum_plot)
    print(f"Guardado: {hum_plot}")

    # scatter precipitación vs congestion
    plt.figure(figsize=(8, 5))
    plt.scatter(df["precipitation"].fillna(0), df["congestion"], alpha=0.4, color="blue")
    plt.xlabel("Precipitación (mm)")
    plt.ylabel("Congestión")
    plt.title("Precipitación vs Congestión")
    plt.grid(True)
    plt.tight_layout()
    precip_plot = os.path.join(out_dir, "precip_vs_congestion.png")
    plt.savefig(precip_plot)
    print(f"Guardado: {precip_plot}")

    # guardar CSV con muestra
    sample_csv = os.path.join(out_dir, "merged_sample.csv")
    df.to_csv(sample_csv, index=False)
    print(f"Guardado CSV: {sample_csv}")

    return {
        "corr": corr.to_dict(),
        "by_description": by_desc.reset_index().to_dict(orient="records"),
        "plots": [temp_plot, hum_plot, precip_plot],
        "csv": sample_csv
    }


if __name__ == "__main__":
    df = load_data_last_years(2)
    if df is None:
        print("No hay datos para analizar. Ejecuta el backfill primero.")
    else:
        res = analyze(df)
        print("Análisis completado. Resumen:")
        print(res)
