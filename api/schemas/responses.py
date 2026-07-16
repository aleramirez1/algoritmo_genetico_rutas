from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    grafo_cargado: bool
    nodos: int
    aristas: int
