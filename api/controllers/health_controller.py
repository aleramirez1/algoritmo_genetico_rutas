from fastapi import APIRouter

from ..config import state
from ..schemas import HealthResponse

router = APIRouter(tags=["sistema"])


@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok" if state.ready else "cargando",
        "grafo_cargado": state.ready,
        "nodos": state.graph.number_of_nodes() if state.ready else 0,
        "aristas": state.graph.number_of_edges() if state.ready else 0,
    }
