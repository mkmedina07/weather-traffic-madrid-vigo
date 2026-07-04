from datetime import datetime


def obtener_trafico(ciudad: str) -> dict:
    hora_actual = datetime.now().hour
    base = sum(ord(letra) for letra in ciudad) % 20
    congestion = min(95, base + hora_actual * 2)

    if congestion < 35:
        nivel = "Bajo"
        mensaje = "Tráfico fluido. Es un buen momento para desplazarte."
    elif congestion < 60:
        nivel = "Medio"
        mensaje = "Condiciones normales de tráfico. Mantén precaución."
    elif congestion < 80:
        nivel = "Alto"
        mensaje = "Tráfico pesado. Planea un poco más de tiempo para tu viaje."
    else:
        nivel = "Muy alto"
        mensaje = "Tráfico muy congestionado. Evita las horas punta si puedes."

    return {
        "ciudad": ciudad,
        "nivel": nivel,
        "congestion": congestion,
        "mensaje": mensaje
    }


def calcular_trafico_desde_clima(clima: dict) -> dict:
    """Genera una estimación de tráfico a partir de un registro de clima.

    Espera que `clima` contenga al menos: `ciudad`, `created_at` (ISO), `descripcion` y opcionalmente `temperatura`, `humedad`, `viento`.
    """
    # extraer hora
    try:
        hora = datetime.fromisoformat(clima.get("created_at")).hour
    except Exception:
        hora = datetime.utcnow().hour

    base = sum(ord(letra) for letra in clima.get("ciudad", "")) % 20
    # horario: picos mañana/tarde
    if hora in (7, 8, 9):
        base += 40
    elif hora in (16, 17, 18):
        base += 45
    else:
        base += 10

    desc = (clima.get("descripcion") or "").lower()
    if "lluv" in desc or "rain" in desc or clima.get("precipitation", 0) > 0:
        base += 12
    if "nieve" in desc or "snow" in desc:
        base += 25

    # ajustar por viento (vientos fuertes pueden empeorar tráfico ligero)
    viento = clima.get("viento") or clima.get("windspeed") or 0
    try:
        viento_val = float(viento)
    except Exception:
        viento_val = 0
    if viento_val > 10:
        base += 5

    congestion = min(95, int(base))

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
        "ciudad": clima.get("ciudad"),
        "nivel": nivel,
        "congestion": congestion,
        "mensaje": mensaje
    }
