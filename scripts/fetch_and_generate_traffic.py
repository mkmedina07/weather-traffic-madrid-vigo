"""Descarga historial meteorológico real y genera registros de tráfico estimados asociados.

Este script depende de `utils.traffic.calcular_trafico_desde_clima` y `utils.database.guardar_registros`.
"""
from datetime import datetime
from scripts.fetch_weather_open_meteo import fetch_last_years
from utils.database import crear_base_de_datos, obtener_climas_por_rango, guardar_registros
from utils.traffic import calcular_trafico_desde_clima


def generate_traffic_from_weather(years=2):
    # Primero asegura que la BD contenga climas (llamada fetch_last_years previamente)
    crear_base_de_datos()
    end = datetime.utcnow()
    start = end.replace(year=end.year - years)
    start_iso = start.isoformat()
    end_iso = end.isoformat()

    climas = obtener_climas_por_rango(start_iso, end_iso)
    registros = []
    for clima in climas:
        trafico = calcular_trafico_desde_clima(clima)
        trafico["created_at"] = clima["created_at"]
        registros.append({"clima": clima, "trafico": trafico})
        if len(registros) >= 500:
            guardar_registros(registros)
            registros = []
    if registros:
        guardar_registros(registros)


if __name__ == "__main__":
    print("Primero fetch de clima desde Open-Meteo (puede tardar unos minutos)...")
    fetch_last_years(years=2)
    print("Generando estimaciones de tráfico basadas en clima real...")
    generate_traffic_from_weather(years=2)
    print("Terminado.")
