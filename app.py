from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
API_KEY = "eae6144461e641fd81d251a12dd10f15" # Mi API Key de football-data.org

headers = {
    "X-Auth-Token": API_KEY #conexión a la API con el token de autenticación
}

grupos_mundial = {
    "A": [
        {"nombre": "Mexico", "tla": "MEX"},
        {"nombre": "South Africa", "tla": "RSA"},
        {"nombre": "South Korea", "tla": "KOR"},
        {"nombre": "Czechia", "tla": "CZE"}
    ],
    "B": [
        {"nombre": "Canada", "tla": "CAN"},
        {"nombre": "Bosnia and Herzegovina", "tla": "BIH"},
        {"nombre": "Qatar", "tla": "QAT"},
        {"nombre": "Switzerland", "tla": "SUI"}
    ],
    "C": [
        {"nombre": "Brazil", "tla": "BRA"},
        {"nombre": "Morocco", "tla": "MAR"},
        {"nombre": "Haiti", "tla": "HAI"},
        {"nombre": "Scotland", "tla": "SCO"}
    ],
    "D": [
        {"nombre": "United States", "tla": "USA"},
        {"nombre": "Paraguay", "tla": "PAR"},
        {"nombre": "Australia", "tla": "AUS"},
        {"nombre": "Turkey", "tla": "TUR"}
    ],
    "E": [
        {"nombre": "Germany", "tla": "GER"},
        {"nombre": "Curacao", "tla": "CUW"},
        {"nombre": "Ivory Coast", "tla": "CIV"},
        {"nombre": "Ecuador", "tla": "ECU"}
    ],
    "F": [
        {"nombre": "Netherlands", "tla": "NED"},
        {"nombre": "Japan", "tla": "JPN"},
        {"nombre": "Sweden", "tla": "SWE"},
        {"nombre": "Tunisia", "tla": "TUN"}
    ],
    "G": [
        {"nombre": "Belgium", "tla": "BEL"},
        {"nombre": "Egypt", "tla": "EGY"},
        {"nombre": "Iran", "tla": "IRN"},
        {"nombre": "New Zealand", "tla": "NZL"}
    ],
    "H": [
        {"nombre": "Spain", "tla": "ESP"},
        {"nombre": "Cape Verde", "tla": "CPV"},
        {"nombre": "Saudi Arabia", "tla": "KSA"},
        {"nombre": "Uruguay", "tla": "URU"}
    ],
    "I": [
        {"nombre": "France", "tla": "FRA"},
        {"nombre": "Senegal", "tla": "SEN"},
        {"nombre": "Iraq", "tla": "IRQ"},
        {"nombre": "Norway", "tla": "NOR"}
    ],
    "J": [
        {"nombre": "Argentina", "tla": "ARG"},
        {"nombre": "Algeria", "tla": "DZA"},
        {"nombre": "Austria", "tla": "AUT"},
        {"nombre": "Jordan", "tla": "JOR"}
    ],
    "K": [
        {"nombre": "Portugal", "tla": "POR"},
        {"nombre": "DR Congo", "tla": "COD"},
        {"nombre": "Uzbekistan", "tla": "UZB"},
        {"nombre": "Colombia", "tla": "COL"}
    ],
    "L": [
        {"nombre": "England", "tla": "ENG"},
        {"nombre": "Croatia", "tla": "CRO"},
        {"nombre": "Ghana", "tla": "GHA"},
        {"nombre": "Panama", "tla": "PAN"}
    ]
}

fuerza = { # Fuerza de cada equipo basada en su desempeño histórico y ranking FIFA
    "MEX": 85, "RSA": 65, "KOR": 78, "CZE": 72,
    "CAN": 75, "BIH": 70, "QAT": 68, "SUI": 82,
    "BRA": 95, "MAR": 84, "HAI": 60, "SCO": 76,
    "USA": 83, "PAR": 74, "AUS": 73, "TUR": 80,
    "GER": 91, "CUW": 58, "CIV": 79, "ECU": 81,
    "NED": 90, "JPN": 84, "SWE": 82, "TUN": 72,
    "BEL": 88, "EGY": 78, "IRN": 75, "NZL": 62,
    "ESP": 92, "CPV": 66, "KSA": 70, "URU": 86,
    "FRA": 94, "SEN": 83, "IRQ": 67, "NOR": 81,
    "ARG": 93, "DZA": 79, "AUT": 80, "JOR": 65,
    "POR": 91, "COD": 73, "UZB": 70, "COL": 84,
    "ENG": 90, "CRO": 85, "GHA": 76, "PAN": 68
}


@app.route("/")
def inicio():
    return render_template("predictor.html") 


def obtener_partidos_mundial():# Función para obtener los partidos del Mundial desde la API de football-data.org
    url = "https://api.football-data.org/v4/competitions/WC/matches"

    response = requests.get(url, headers=headers)
    datos = response.json()

    return datos.get("matches", []) #Ayuda para buscar la lista de partidos obtenida de la API


def sumar_resultado(tabla, local, visitante, goles_local, goles_visitante): # Función para sumar los resultados de un partido a la tabla de posiciones
    tabla[local]["goles_favor"] += goles_local
    tabla[local]["goles_contra"] += goles_visitante

    tabla[visitante]["goles_favor"] += goles_visitante
    tabla[visitante]["goles_contra"] += goles_local

    if goles_local > goles_visitante:
        tabla[local]["puntos"] += 3
        tabla[local]["victorias"] += 1
        tabla[visitante]["derrotas"] += 1

    elif goles_visitante > goles_local:
        tabla[visitante]["puntos"] += 3
        tabla[visitante]["victorias"] += 1
        tabla[local]["derrotas"] += 1

    else:
        tabla[local]["puntos"] += 1
        tabla[visitante]["puntos"] += 1
        tabla[local]["empates"] += 1
        tabla[visitante]["empates"] += 1


def rendimiento_actual(tabla, equipo): # Función para calcular el rendimiento actual de un equipo basado en su fuerza, puntos y diferencia de goles
    diferencia = tabla[equipo]["goles_favor"] - tabla[equipo]["goles_contra"]

    return (
        fuerza.get(equipo, 70)
        + tabla[equipo]["puntos"] * 5
        + diferencia * 3
        + tabla[equipo]["goles_favor"]
    )


def predecir_partido(tabla, local, visitante): # Función para predecir el resultado de un partido no jugado basado en el rendimiento actual de ambos equipos
    rendimiento_local = rendimiento_actual(tabla, local)
    rendimiento_visitante = rendimiento_actual(tabla, visitante)

    if abs(rendimiento_local - rendimiento_visitante) <= 5:
        sumar_resultado(tabla, local, visitante, 1, 1)

    elif rendimiento_local > rendimiento_visitante:
        sumar_resultado(tabla, local, visitante, 2, 1)

    else:
        sumar_resultado(tabla, local, visitante, 1, 2)


@app.route("/predecir")
def predecir():
    grupo = request.args.get("grupo", "A")
    equipos = grupos_mundial[grupo]

    tabla = {}

    for equipo in equipos:
        tabla[equipo["tla"]] = {
            "equipo": equipo["nombre"],
            "tla": equipo["tla"],
            "puntos": 0,
            "victorias": 0,
            "empates": 0,
            "derrotas": 0,
            "goles_favor": 0,
            "goles_contra": 0,
            "probabilidad": 0
        }

    partidos = obtener_partidos_mundial()  # Obtiene los partidos del Mundial desde la API

    for partido in partidos:
        local = partido["homeTeam"].get("tla")
        visitante = partido["awayTeam"].get("tla")

        if local in tabla and visitante in tabla:
            goles_local = partido["score"]["fullTime"]["home"]
            goles_visitante = partido["score"]["fullTime"]["away"]

            if goles_local is not None and goles_visitante is not None:
                sumar_resultado(tabla, local, visitante, goles_local, goles_visitante)

    for partido in partidos:
        local = partido["homeTeam"].get("tla")
        visitante = partido["awayTeam"].get("tla")

        if local in tabla and visitante in tabla:
            goles_local = partido["score"]["fullTime"]["home"]
            goles_visitante = partido["score"]["fullTime"]["away"]

            if goles_local is None or goles_visitante is None:
                predecir_partido(tabla, local, visitante)

    tabla_final = list(tabla.values())

    for equipo in tabla_final:
        diferencia = equipo["goles_favor"] - equipo["goles_contra"]

        equipo["probabilidad"] = min(
            99,
            max(1, 50 + equipo["puntos"] * 5 + diferencia * 3)
        )

    tabla_final = sorted(
        tabla_final,
        key=lambda x: (
            x["puntos"],
            x["goles_favor"] - x["goles_contra"],
            x["goles_favor"]
        ),
        reverse=True
    )

    return jsonify({
        "grupo": grupo,
        "tabla": tabla_final,
        "clasificados": tabla_final[:2]
    })


if __name__ == "__main__":
    app.run(debug=True)