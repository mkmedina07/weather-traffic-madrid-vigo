from pathlib import Path
import pandas as pd
from datetime import datetime

from utils.database import obtener_climas_por_rango, obtener_traficos_por_rango, DB_PATH
from utils.ml_utils import aggregate_by_year_and_month, train_congestion_model
import matplotlib.pyplot as plt


def predict_remaining_2026(out_path: str | Path | None = None):
    """Train on available data and predict congestion for remaining months of 2026.

    Saves CSV to `out_path` (defaults to db/predictions_2026_remaining.csv) and
    returns the resulting DataFrame.
    """
    if out_path is None:
        out_path = Path(DB_PATH).parent / "predictions_2026_remaining.csv"
    out_path = Path(out_path)

    end = datetime.utcnow()
    start = end.replace(year=end.year - 2)

    climas = pd.DataFrame(obtener_climas_por_rango(start.isoformat(), end.isoformat()))
    traficos = pd.DataFrame(obtener_traficos_por_rango(start.isoformat(), end.isoformat()))
    if climas.empty or traficos.empty:
        raise RuntimeError("Not enough historical data to build predictions")

    climas["created_at"] = pd.to_datetime(climas["created_at"], errors="coerce").dt.round("s")
    traficos["created_at"] = pd.to_datetime(traficos["created_at"], errors="coerce").dt.round("s")
    climas = climas.dropna(subset=["created_at"]) 
    traficos = traficos.dropna(subset=["created_at"]) 
    relacion_df = pd.merge(climas, traficos, on=["ciudad", "created_at"], how="inner")

    # Train model
    features = ["viento", "precipitation", "temperatura", "humedad"]
    model, metrics, importances = train_congestion_model(relacion_df, features=features)
    if model is None:
        raise RuntimeError("Model training failed - insufficient data")

    # Build monthly averages
    _, monthly = aggregate_by_year_and_month(relacion_df)
    monthly_map = {}
    for _, row in monthly.iterrows():
        monthly_map[(row["ciudad"], int(row["month"]))] = {
            "temperatura": float(row["avg_temp"]),
            "precipitation": float(row["avg_precip"]),
            "viento": float(row["avg_wind"]),
            "humedad": float(row["avg_humidity"]),
        }

    now = datetime.utcnow()
    start_month = now.month
    months = list(range(start_month, 13))

    cities = sorted({c for (c, m) in monthly_map.keys()})
    results = []
    for city in cities:
        for m in months:
            key = (city, m)
            if key in monthly_map:
                vals = monthly_map[key]
            else:
                city_rows = [v for (c, mm), v in monthly_map.items() if c == city]
                if city_rows:
                    avg = {
                        "temperatura": sum(r["temperatura"] for r in city_rows) / len(city_rows),
                        "precipitation": sum(r["precipitation"] for r in city_rows) / len(city_rows),
                        "viento": sum(r["viento"] for r in city_rows) / len(city_rows),
                        "humedad": sum(r["humedad"] for r in city_rows) / len(city_rows),
                    }
                    vals = avg
                else:
                    vals = {"temperatura": 0.0, "precipitation": 0.0, "viento": 0.0, "humedad": 0.0}

            X = pd.DataFrame([{
                "viento": vals["viento"],
                "precipitation": vals["precipitation"],
                "temperatura": vals["temperatura"],
                "humedad": vals["humedad"],
            }])
            pred = float(model.predict(X)[0])
            results.append({
                "ciudad": city,
                "year": 2026,
                "month": m,
                "pred_congestion": round(pred, 2),
                "temp": round(vals["temperatura"], 2),
                "precip_mm": round(vals["precipitation"], 4),
                "wind_m_s": round(vals["viento"], 2),
                "humidity_pct": round(vals["humedad"], 2),
            })

    df_res = pd.DataFrame(results)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_res.to_csv(out_path, index=False)
    # Save a bar chart of predicted congestion by month for each city
    try:
        fig_path = out_path.with_suffix('.png')
        pivot = df_res.pivot(index='month', columns='ciudad', values='pred_congestion')
        ax = pivot.plot(kind='bar', figsize=(10, 5))
        ax.set_title('Predicción de congestión (meses restantes 2026)')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Predicción congestión (%)')
        plt.tight_layout()
        fig = ax.get_figure()
        fig.savefig(fig_path)
        plt.close(fig)
    except Exception:
        # non-fatal: if plotting fails, continue without saving image
        pass
    return df_res


if __name__ == "__main__":
    df = predict_remaining_2026()
    print(df.to_string(index=False))
