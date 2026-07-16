from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..schemas import OptimizarRequest
from ..services import run_optimization, build_response, render_map

router = APIRouter(tags=["rutas"])


@router.post("/optimizar")
def optimizar(req: OptimizarRequest):
    decoded = run_optimization(req)
    return build_response(decoded)


@router.post("/optimizar/mapa", response_class=HTMLResponse)
def optimizar_mapa(req: OptimizarRequest):
    decoded = run_optimization(req)
    blockages = [b.model_dump() for b in req.bloqueos]
    html = render_map(decoded, blockages)
    return HTMLResponse(content=html)
