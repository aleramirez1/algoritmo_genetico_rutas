import os

from osm_graph import load_osm_graph
from .settings import settings


class GraphState:
    def __init__(self):
        self.graph = None
        self.nodes = None

    def load(self):
        base_dir = os.path.dirname(__file__)
        path = settings.resolve_osm_path(base_dir)
        print(f"[API] Cargando grafo OSM desde {path}...")
        self.graph, self.nodes = load_osm_graph(path)
        print("[API] Grafo listo. Servidor operativo.")

    def clear(self):
        self.graph = None
        self.nodes = None

    @property
    def ready(self) -> bool:
        return self.graph is not None


state = GraphState()
