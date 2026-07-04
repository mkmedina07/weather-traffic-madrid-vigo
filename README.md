# weather-traffic-madrid-vigo

Proyecto de análisis de datos que ingiere clima histórico real (Open-Meteo), genera una relación entre clima y congestión de tráfico, calcula medias por año/mes, y ofrece predicciones para los meses restantes de 2026 con una interfaz interactiva en Streamlit.

## Estructura del proyecto

- `app.py`: aplicación principal de Streamlit.
- `etl.py`: script para obtener datos actuales de clima y tráfico y guardarlos en SQLite.
- `utils/weather.py`: consulta a OpenWeather para obtener datos meteorológicos.
- `utils/traffic.py`: genera un nivel de tráfico estimado por ciudad.
- `utils/database.py`: maneja la base de datos local SQLite.
- `utils/ml_utils.py`: utilidades para entrenamiento y predicción ML.
- `utils/ml_model.py`: definición del modelo y entrenamiento.
- `scripts/`: scripts adicionales de historiales y predicciones.
- `requirements.txt`: dependencias del proyecto.
- `.env.example`: plantilla para variables de entorno.

## Setup

1. Activa el entorno virtual:

```sh
source venv/bin/activate
```

2. Instala dependencias:

```sh
pip install -r requirements.txt
```

3. Crea el archivo de configuración de entorno:

```sh
cp .env.example .env
```

4. Añade tu clave de OpenWeather en `.env`:

```env
OPENWEATHER_API_KEY=tu_api_key_aqui
```

## Uso

- Ejecutar el script ETL para obtener datos de clima y tráfico:

```sh
python etl.py
```

- Ejecutar la app de Streamlit:

```sh
streamlit run app.py
```

## Características

- Ingesta de clima histórico real vía Open-Meteo.
- Cálculo de agregados por año y mes.
- Variables: temperatura, humedad, viento y precipitación.
- Modelo ML para predecir congestión futura.
- Interfaz interactiva con descarga de resultados.

## Notas

- La base de datos SQLite se guarda en `db/clima_trafico.db`.
- Las variables sensibles y artefactos se ignoran en `.gitignore`.
- Usa `streamlit run app.py` para abrir la aplicación localmente.

