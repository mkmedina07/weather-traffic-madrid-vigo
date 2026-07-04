"""Descarga datos históricos meteorológicos desde Open-Meteo y los guarda en la BD.

Usa el endpoint de archivo: https://archive-api.open-meteo.com/v1/archive
"""
import requests
from datetime import datetime, timedelta
from utils.database import crear_base_de_datos, guardar_clima


CIUDADES = {
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Vigo": {"lat": 42.2406, "lon": -8.7207},
}


def fetch_period(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(["temperature_2m", "relativehumidity_2m", "windspeed_10m", "precipitation", "cloudcover"]),
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def save_city_history(ciudad, lat, lon, start_date, end_date):
    data = fetch_period(lat, lon, start_date, end_date)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    hums = hourly.get("relativehumidity_2m", [])
    winds = hourly.get("windspeed_10m", [])
    precs = hourly.get("precipitation", [])
    clouds = hourly.get("cloudcover", [])

    registros = []
    for i, ts in enumerate(times):
        descripcion = "cielo claro"
        if i < len(precs) and precs[i] and precs[i] > 0:
            descripcion = "lluvia"
        elif i < len(clouds) and clouds[i] and clouds[i] > 50:
            descripcion = "nublado"

        precipitation = 0.0
        if i < len(precs) and precs[i] is not None:
            try:
                precipitation = float(precs[i])
            except (TypeError, ValueError):
                precipitation = 0.0

        clima = {
            "ciudad": ciudad,
            "descripcion": descripcion,
            "temperatura": temps[i] if i < len(temps) else None,
            "humedad": int(hums[i]) if i < len(hums) and hums[i] is not None else None,
            "viento": winds[i] if i < len(winds) else None,
            "presion": None,
            "precipitation": precipitation,
            "raw": {},
            "created_at": ts,
        }

        # guardar directamente el clima (sin trafico aún)
        guardar_clima(clima)


def fetch_last_years(ciudades=None, years=2):
    if ciudades is None:
        ciudades = CIUDADES
    crear_base_de_datos()
    end = datetime.utcnow().date()
    start = end - timedelta(days=365 * years)

    # Open-Meteo acepta rangos amplios, pero para seguridad pedimos por meses
    for ciudad, loc in ciudades.items():
        cur_start = start
        while cur_start <= end:
            cur_end = min(end, cur_start + timedelta(days=30))
            print(f"Fetching {ciudad} {cur_start} -> {cur_end}")
            save_city_history(ciudad, loc["lat"], loc["lon"], cur_start.isoformat(), cur_end.isoformat())
            cur_start = cur_end + timedelta(days=1)


if __name__ == "__main__":
    fetch_last_years(years=2)
