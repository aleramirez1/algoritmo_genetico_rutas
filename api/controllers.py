from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from config import state
from schemas import OptimizarRequest, HealthResponse
from services import run_optimization, build_response, render_map

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["sistema"])
def health():
    return {
        "status": "ok" if state.ready else "cargando",
        "grafo_cargado": state.ready,
        "nodos": state.graph.number_of_nodes() if state.ready else 0,
        "aristas": state.graph.number_of_edges() if state.ready else 0,
    }


@router.post("/optimizar", tags=["rutas"])
def optimizar(req: OptimizarRequest):
    decoded = run_optimization(req)
    return build_response(decoded)


@router.post("/optimizar/mapa", response_class=HTMLResponse, tags=["rutas"])
def optimizar_mapa(req: OptimizarRequest):
    decoded = run_optimization(req)
    blockages = [b.model_dump() for b in req.bloqueos]
    return HTMLResponse(content=render_map(decoded, blockages))
