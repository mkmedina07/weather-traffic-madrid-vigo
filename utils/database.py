import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "db" / "clima_trafico.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def crear_base_de_datos() -> None:
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clima (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciudad TEXT NOT NULL,
                temperatura REAL,
                descripcion TEXT,
                humedad INTEGER,
                viento REAL,
                presion INTEGER,
                precipitation REAL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trafico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciudad TEXT NOT NULL,
                nivel TEXT,
                congestion INTEGER,
                mensaje TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(clima)")]
        if "precipitation" not in existing_columns:
            cursor.execute("ALTER TABLE clima ADD COLUMN precipitation REAL")
        cursor.execute("UPDATE clima SET precipitation = 0 WHERE precipitation IS NULL")
        conexion.commit()


def guardar_clima(clima: dict) -> None:
    if clima.get("error"):
        return
    created_at = clima.get("created_at") or datetime.utcnow().isoformat()
    precipitation = clima.get("precipitation", 0)
    if precipitation is None:
        precipitation = 0
    try:
        precipitation = float(precipitation)
    except (TypeError, ValueError):
        precipitation = 0

    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE clima SET temperatura=?, descripcion=?, humedad=?, viento=?, presion=?, precipitation=? WHERE ciudad=? AND created_at=?",
            (
                clima.get("temperatura"),
                clima.get("descripcion"),
                clima.get("humedad"),
                clima.get("viento"),
                clima.get("presion"),
                precipitation,
                clima["ciudad"],
                created_at,
            )
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO clima (ciudad, temperatura, descripcion, humedad, viento, presion, precipitation, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    clima["ciudad"],
                    clima.get("temperatura"),
                    clima.get("descripcion"),
                    clima.get("humedad"),
                    clima.get("viento"),
                    clima.get("presion"),
                    precipitation,
                    created_at
                )
            )
        conexion.commit()


def guardar_trafico(trafico: dict) -> None:
    created_at = trafico.get("created_at") or datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO trafico (ciudad, nivel, congestion, mensaje, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                trafico["ciudad"],
                trafico.get("nivel"),
                trafico.get("congestion"),
                trafico.get("mensaje"),
                created_at
            )
        )
        conexion.commit()


def guardar_registros(registros: list[dict]) -> None:
    for registro in registros:
        guardar_clima(registro["clima"])
        guardar_trafico(registro["trafico"])


def obtener_climas_recientes(limit: int = 10) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT ciudad, temperatura, descripcion, humedad, viento, presion, precipitation, created_at FROM clima ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        filas = cursor.fetchall()
    return [dict(fila) for fila in filas]


def obtener_climas_por_rango(start_iso: str, end_iso: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT ciudad, temperatura, descripcion, humedad, viento, presion, precipitation, created_at FROM clima WHERE created_at BETWEEN ? AND ? ORDER BY created_at",
            (start_iso, end_iso)
        )
        filas = cursor.fetchall()
    return [dict(fila) for fila in filas]


def obtener_traficos_recientes(limit: int = 10) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT ciudad, nivel, congestion, mensaje, created_at FROM trafico ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        filas = cursor.fetchall()
    return [dict(fila) for fila in filas]


def obtener_traficos_por_rango(start_iso: str, end_iso: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT ciudad, nivel, congestion, mensaje, created_at FROM trafico WHERE created_at BETWEEN ? AND ? ORDER BY created_at",
            (start_iso, end_iso)
        )
        filas = cursor.fetchall()
    return [dict(fila) for fila in filas]
