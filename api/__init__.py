import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_AG_DIR = os.path.join(_ROOT, "genetic_route")
_MAPA_DIR = os.path.join(_AG_DIR, "mapa")

for _path in (_HERE, _AG_DIR, _MAPA_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)
