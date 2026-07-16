import os


class Settings:
    def __init__(self):
        self.osm_path = os.environ.get("OSM_PATH", "suchiapa.json")
        self.cors_origins = os.environ.get("CORS_ORIGINS", "*").strip()
        self.title = "Optimizador de Rutas de Recoleccion"
        self.description = "AG + Dijkstra sobre grafo OSM de Suchiapa"
        self.version = "1.0.0"

    def resolve_osm_path(self, base_dir: str) -> str:
        path = self.osm_path
        if not os.path.isabs(path) and not os.path.exists(path):
            root = os.path.join(base_dir, "..", "..")
            alt = os.path.join(root, path)
            if os.path.exists(alt):
                return alt
        return path

    @property
    def allow_all_origins(self) -> bool:
        return self.cors_origins == "*"

    @property
    def allowed_origins(self) -> list:
        if self.allow_all_origins:
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
