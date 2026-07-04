import random
from datetime import datetime, timedelta
from utils.database import crear_base_de_datos, guardar_registros


def generar_temperatura(ciudad, date):
    # Valores medios aproximados por mes (España, simplificado)
    month_avg = {
        1: 8, 2: 9, 3: 11, 4: 13, 5: 16, 6: 20,
        7: 24, 8: 24, 9: 21, 10: 16, 11: 12, 12: 9
    }
    base = month_avg.get(date.month, 15)
    # ligera diferencia entre ciudades
    city_bias = -1 if ciudad.lower() == "vigo" else 0
    return round(base + city_bias + random.gauss(0, 3), 1)


def generar_humedad(temp):
    # humedad inversamente relacionada con temperatura (simplificado)
    hum = 75 - (temp - 10) * 1.5 + random.gauss(0, 8)
    return int(max(5, min(100, hum)))


def generar_viento(date):
    return round(max(0, random.gauss(3, 1.5)), 2)


def elegir_descripcion(date):
    # Probabilidad de lluvia más alta en otoño/invierno
    rain_prob_by_month = {1: 0.25, 2: 0.22, 3: 0.18, 4: 0.15, 5: 0.12, 6: 0.08,
                         7: 0.05, 8: 0.06, 9: 0.10, 10: 0.18, 11: 0.22, 12: 0.24}
    p = rain_prob_by_month.get(date.month, 0.12)
    r = random.random()
    if r < p:
        return "lluvia"
    if r < p + 0.15:
        return "nublado"
    return "cielo claro"


def calcular_trafico_sintetico(ciudad, date, descripcion):
    hour = date.hour
    # base de congestión según hora: picos por la mañana y tarde
    if hour in (7, 8, 9):
        base = random.randint(55, 80)
    elif hour in (16, 17, 18):
        base = random.randint(60, 85)
    else:
        base = random.randint(20, 50)

    # ajustar por condiciones meteorológicas
    if descripcion == "lluvia":
        base += 12
    if descripcion == "nieve":
        base += 25

    congestion = min(95, base)
    if congestion < 35:
        nivel = "Bajo"
        mensaje = "Tráfico fluido."
    elif congestion < 60:
        nivel = "Medio"
        mensaje = "Condiciones normales de tráfico."
    elif congestion < 80:
        nivel = "Alto"
        mensaje = "Tráfico pesado."
    else:
        nivel = "Muy alto"
        mensaje = "Tráfico muy congestionado."

    return {
        "ciudad": ciudad,
        "nivel": nivel,
        "congestion": int(congestion),
        "mensaje": mensaje
    }


def backfill(ciudades=None, years=2, observations_per_day=(8, 17)):
    if ciudades is None:
        ciudades = ["Madrid", "Vigo"]
    crear_base_de_datos()
    end = datetime.utcnow()
    start = end - timedelta(days=365 * years)
    total_days = (end.date() - start.date()).days + 1
    inserted = 0

    for day_offset in range(total_days):
        current_day = start + timedelta(days=day_offset)
        for hour in observations_per_day:
            dt = datetime(current_day.year, current_day.month, current_day.day, hour)
            iso = dt.isoformat()
            registros = []
            for ciudad in ciudades:
                temp = generar_temperatura(ciudad, dt)
                hum = generar_humedad(temp)
                viento = generar_viento(dt)
                descripcion = elegir_descripcion(dt)

                clima = {
                    "ciudad": ciudad,
                    "descripcion": descripcion,
                    "temperatura": temp,
                    "sensacion_termica": None,
                    "humedad": hum,
                    "viento": viento,
                    "presion": None,
                    "raw": {},
                    "created_at": iso
                }

                trafico = calcular_trafico_sintetico(ciudad, dt, descripcion)
                trafico["created_at"] = iso

                registros.append({"clima": clima, "trafico": trafico})

            guardar_registros(registros)
            inserted += len(registros)

    print(f"Inserted ~{inserted} synthetic records ({len(ciudades)} ciudades, {years} años).")


if __name__ == "__main__":
    backfill()
