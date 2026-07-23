import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENETIC_DIR = os.path.join(BASE_DIR, "..", "genetic_route")
MAPA_DIR = os.path.join(GENETIC_DIR, "mapa")

for path in (BASE_DIR, GENETIC_DIR, MAPA_DIR):
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)

if __name__ == "__main__":
    import uvicorn
    from app import app

    uvicorn.run(app, host="0.0.0.0", port=8003)
