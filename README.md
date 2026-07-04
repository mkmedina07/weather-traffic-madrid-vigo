# Clima y Tráfico Madrid - Vigo

Proyecto de demostración que integra datos de clima y tráfico para Madrid y Vigo usando Streamlit y SQLite.

## Estructura del proyecto

- `app.py`: aplicación principal de Streamlit.
- `etl.py`: script para obtener datos actuales de clima y tráfico y guardarlos en SQLite.
- `utils/weather.py`: consulta a OpenWeather para obtener datos meteorológicos.
- `utils/traffic.py`: genera un nivel de tráfico simulado por ciudad.
- `utils/database.py`: maneja la base de datos local SQLite.
- `db/clima_trafico.db`: base de datos SQLite generada automáticamente.
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

- Ejecutar el script ETL para obtener datos y guardarlos en la base de datos:

```sh
python etl.py
```

- Ejecutar la app de Streamlit:

```sh
streamlit run app.py
```

## Notas

- La base de datos SQLite se guarda en `db/clima_trafico.db`.
- Si no tienes clave de OpenWeather, la app mostrará un mensaje de error.
- `utils/traffic.py` genera valores de tráfico simulados basados en la ciudad y la hora actual.
