from utils.weather import obtener_clima
from utils.traffic import obtener_trafico
from utils.database import crear_base_de_datos, guardar_registros


def sincronizar_ciudades(ciudades):
    crear_base_de_datos()
    registros = []
    for ciudad in ciudades:
        clima = obtener_clima(ciudad)
        trafico = obtener_trafico(ciudad)
        registros.append({"clima": clima, "trafico": trafico})
    guardar_registros(registros)
    return registros


if __name__ == "__main__":
    ciudades = ["Madrid", "Vigo"]
    registros = sincronizar_ciudades(ciudades)
    for registro in registros:
        print(f"{registro['clima']['ciudad']}: clima={registro['clima'].get('temperatura')}°C, tráfico={registro['trafico']['nivel']}")
