from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Datos de ejemplo por 100 g. Sustituir/verificar con la tabla oficial
# de composición de alimentos exigida por el curso.
ALIMENTOS = {
    "Avena": [333, 13.3, 72.2, 4.0],
    "Pan francés": [277, 8.4, 62.9, 0.2],
    "Huevo": [156, 12.7, 0.0, 11.1],
    "Palta": [160, 2.0, 8.5, 14.7],
    "Leche": [61, 3.2, 4.8, 3.3],
    "Arroz blanco cocido": [115, 2.4, 25.2, 0.1],
    "Pollo cocido sin piel": [165, 31.0, 0.0, 3.6],
    "Papa sancochada": [87, 1.9, 20.1, 0.1],
    "Lentejas cocidas": [116, 9.0, 20.1, 0.4],
    "Carne de res cocida": [250, 26.0, 0.0, 15.0],
    "Fideos cocidos": [131, 5.0, 25.0, 1.1],
    "Zanahoria": [41, 0.9, 9.6, 0.2],
    "Lechuga": [15, 1.4, 2.9, 0.2],
    "Tomate": [18, 0.9, 3.9, 0.2],
    "Manzana": [52, 0.3, 13.8, 0.2],
    "Plátano": [89, 1.1, 22.8, 0.3],
    "Aceite vegetal": [884, 0.0, 0.0, 100.0],
    "Yogur natural": [61, 3.5, 4.7, 3.3],
    "Camote sancochado": [90, 2.0, 20.7, 0.2],
    "Pescado cocido": [128, 26.0, 0.0, 2.7],
    "Caldo de gallina": [45, 2.9, 7.2, 0.6],
    "Galletas de soda": [433, 10.1, 68.0, 14.7],
}
FACTORES = {"Baja": 25, "Moderada": 30, "Alta": 35}
COMIDAS = {"Desayuno", "Media mañana", "Almuerzo", "Media tarde", "Cena"}

@app.get("/")
def inicio():
    return render_template("index.html", alimentos=sorted(ALIMENTOS.keys()))

@app.post("/api/calcular")
def calcular():
    data = request.get_json(silent=True) or {}
    try:
        peso = float(data.get("peso", 0))
        talla_cm = float(data.get("talla", 0))
        edad = int(data.get("edad", 0))
        actividad = data.get("actividad", "Moderada")
        registros = data.get("alimentos", [])

        if peso <= 0 or talla_cm <= 0 or edad <= 0:
            raise ValueError("Ingresa edad, peso y talla válidos.")
        if actividad not in FACTORES:
            raise ValueError("Selecciona una actividad física válida.")
        if not isinstance(registros, list):
            raise ValueError("El registro de alimentos no es válido.")

        imc = peso / ((talla_cm / 100) ** 2)
        meta = peso * FACTORES[actividad]
        total = {"kcal": 0.0, "proteinas": 0.0, "carbohidratos": 0.0, "lipidos": 0.0}
        por_comida = {}

        for item in registros:
            nombre = item.get("nombre")
            comida = item.get("comida")
            servido = float(item.get("servido", 0))
            sobrante = float(item.get("sobrante", 0))
            if nombre not in ALIMENTOS:
                raise ValueError(f"Alimento no reconocido: {nombre}")
            if comida not in COMIDAS:
                raise ValueError("Tiempo de comida no válido.")
            if servido <= 0 or sobrante < 0 or sobrante > servido:
                raise ValueError("Revisa gramos servidos y sobrantes.")

            consumido = servido - sobrante
            kcal, prot, carb, lip = ALIMENTOS[nombre]
            aporte = {
                "kcal": kcal * consumido / 100,
                "proteinas": prot * consumido / 100,
                "carbohidratos": carb * consumido / 100,
                "lipidos": lip * consumido / 100,
            }
            for key in total:
                total[key] += aporte[key]
            if comida not in por_comida:
                por_comida[comida] = {key: 0.0 for key in total}
            for key in total:
                por_comida[comida][key] += aporte[key]

        balance = total["kcal"] - meta
        adecuacion = total["kcal"] / meta * 100
        if adecuacion < 95:
            estado = "Consumo por debajo de la meta estimada"
        elif adecuacion > 105:
            estado = "Consumo por encima de la meta estimada"
        else:
            estado = "Consumo cercano a la meta estimada"

        return jsonify({
            "imc": round(imc, 2),
            "meta_kcal": round(meta, 1),
            "total": {k: round(v, 1) for k, v in total.items()},
            "balance": round(balance, 1),
            "adecuacion": round(adecuacion, 1),
            "estado": estado,
            "por_comida": {c: {k: round(v, 1) for k, v in vals.items()}
                           for c, vals in por_comida.items()}
        })
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400

if __name__ == "__main__":
    app.run(debug=True)
