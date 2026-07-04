import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def train_congestion_model(df: pd.DataFrame, features=None):
    if features is None:
        features = ["viento", "temperatura", "humedad", "precipitation"]

    X = df[features].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df["congestion"], errors="coerce")
    mask = X.notna().all(axis=1) & y.notna()
    X = X[mask]
    y = y[mask]

    if X.empty:
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    metrics = {
        "train_r2": round(r2_score(y_train, train_pred), 4),
        "test_r2": round(r2_score(y_test, test_pred), 4),
        "test_rmse": round(mean_squared_error(y_test, test_pred, squared=False), 4),
    }

    feature_importances = dict(sorted(zip(features, model.feature_importances_), key=lambda x: x[1], reverse=True))

    return model, metrics, feature_importances


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
