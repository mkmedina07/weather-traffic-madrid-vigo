import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def prepare_dataset(relacion_df: pd.DataFrame):
    df = relacion_df.copy()
    df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")
    df["humedad"] = pd.to_numeric(df["humedad"], errors="coerce")
    df["viento"] = pd.to_numeric(df["viento"], errors="coerce")
    df["precipitation"] = pd.to_numeric(df["precipitation"], errors="coerce").fillna(0)
    df["congestion"] = pd.to_numeric(df["congestion"], errors="coerce")
    df = df.dropna(subset=["temperatura", "humedad", "viento", "precipitation", "congestion"])
    return df


def aggregate_by_year_and_month(df: pd.DataFrame):
    df = prepare_dataset(df)
    df["year"] = pd.to_datetime(df["created_at"]).dt.year
    df["month"] = pd.to_datetime(df["created_at"]).dt.month

    yearly = df.groupby(["ciudad", "year"]).agg(
        avg_temp=("temperatura", "mean"),
        avg_precip=("precipitation", "mean"),
        avg_wind=("viento", "mean"),
        avg_humidity=("humedad", "mean"),
        avg_congestion=("congestion", "mean"),
    ).reset_index()

    monthly = df.groupby(["ciudad", "month"]).agg(
        avg_temp=("temperatura", "mean"),
        avg_precip=("precipitation", "mean"),
        avg_wind=("viento", "mean"),
        avg_humidity=("humedad", "mean"),
        avg_congestion=("congestion", "mean"),
    ).reset_index()

    return yearly, monthly


def train_congestion_model(df: pd.DataFrame, features=None):
    if features is None:
        features = ["viento", "precipitation", "temperatura", "humedad"]

    df = prepare_dataset(df)
    X = df[features]
    y = df["congestion"]

    if X.empty:
        return None, None, None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        "r2": round(r2_score(y_test, y_pred), 4),
        "rmse": round(mean_squared_error(y_test, y_pred, squared=False), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    importances = dict(sorted(zip(features, model.feature_importances_), key=lambda x: x[1], reverse=True))
    return model, metrics, importances


def predict_congestion(model, temperatura, humedad, viento, precipitation):
    X = pd.DataFrame([
        {
            "temperatura": temperatura,
            "humedad": humedad,
            "viento": viento,
            "precipitation": precipitation,
        }
    ])
    return float(model.predict(X)[0])
