import os
from pathlib import Path
import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def obtener_clima(ciudad: str) -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {
            "ciudad": ciudad,
            "error": "No se encontró OPENWEATHER_API_KEY en .env. Copia .env.example a .env y agrega tu clave."
        }

    params = {
        "q": ciudad,
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }

    try:
        respuesta = requests.get(BASE_URL, params=params, timeout=10)
        respuesta.raise_for_status()
        data = respuesta.json()
        clima = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})
        rain_data = data.get("rain", {})
        snow_data = data.get("snow", {})
        rain = rain_data.get("1h", rain_data.get("3h", 0)) or 0
        snow = snow_data.get("1h", snow_data.get("3h", 0)) or 0

        return {
            "ciudad": ciudad,
            "descripcion": clima["description"],
            "temperatura": main.get("temp"),
            "sensacion_termica": main.get("feels_like"),
            "humedad": main.get("humidity"),
            "viento": wind.get("speed", 0),
            "presion": main.get("pressure"),
            "precipitation": rain + snow,
            "raw": data
        }

    except requests.RequestException as error:
        return {
            "ciudad": ciudad,
            "error": f"Error al consultar OpenWeather: {error}"
        }
