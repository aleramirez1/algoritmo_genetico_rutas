import json
import sys
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

with open("ruta_ejemplo.json", encoding="utf-8") as f:
    ruta = json.load(f)
with open("bloqueos.json", encoding="utf-8") as f:
    bloq = json.load(f)

payload = {
    "puntos": ruta["puntos"],
    "base_inicio": {"lat": 16.624418, "lng": -93.102281, "nombre": "Deposito central parque"},
    "base_fin": {"lat": 16.626758, "lng": -93.107130, "nombre": "Deposito final Rio"},
    "bloqueos": bloq["puntos"],
    "radio_bloqueo": 25.0,
    "params_ag": {
        "poblacion": 200,
        "generaciones": 2000,
        "patience": 80,
        "semilla": 300,
        "tipo_mutacion": "inversion",
    },
}


def post(endpoint):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read().decode("utf-8")


def test_optimizar():
    result = json.loads(post("/optimizar"))
    print("=== /optimizar (JSON) ===")
    print("Base inicio:", result["base_inicio"]["nombre"])
    print("Base fin:", result["base_fin"]["nombre"])
    print("Distancia total:", result["distancia_total_km"], "km")
    print("Convergencia:", result["convergencia"])
    print("Puntos inaccesibles:", len(result["puntos_inaccesibles"]))
    print("Segmentos en la ruta:", len(result["segmentos"]))


def test_mapa():
    html = post("/optimizar/mapa")
    out = "ruta_api.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("=== /optimizar/mapa (HTML) ===")
    print(f"Mapa guardado en {out} ({len(html)} chars)")


if __name__ == "__main__":
    if "--mapa" in sys.argv:
        test_mapa()
    else:
        test_optimizar()
