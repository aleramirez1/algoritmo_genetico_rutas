import os

from osm_graph import load_osm_graph


class Settings:
    def __init__(self):
        self.osm_path = os.environ.get("OSM_PATH", "suchiapa.json")
        self.cors_origins = os.environ.get("CORS_ORIGINS", "*").strip()
        self.title = "Optimizador de Rutas de Recoleccion"
        self.description = "AG + Dijkstra sobre grafo OSM de Suchiapa"
        self.version = "1.0.0"

    def resolve_osm_path(self, base_dir):
        path = self.osm_path
        if not os.path.isabs(path) and not os.path.exists(path):
            alt = os.path.join(base_dir, "..", path)
            if os.path.exists(alt):
                return alt
        return path

    @property
    def allow_all_origins(self):
        return self.cors_origins == "*"

    @property
    def allowed_origins(self):
        if self.allow_all_origins:
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()


class GraphState:
    def __init__(self):
        self.graph = None
        self.nodes = None

    def load(self):
        path = settings.resolve_osm_path(os.path.dirname(__file__))
        print(f"[API] Cargando grafo OSM desde {path}...")
        self.graph, self.nodes = load_osm_graph(path)
        print("[API] Grafo listo. Servidor operativo.")

    def clear(self):
        self.graph = None
        self.nodes = None

    @property
    def ready(self):
        return self.graph is not None


state = GraphState()
