import os
import tempfile

from fastapi import HTTPException

from ag_params import AGParams
from optimizer import optimize_route, default_base
from map_builder import build_route_map
from config import state
from schemas import OptimizarRequest


def _params_from_request(p) -> AGParams:
    return AGParams(
        pop_size=p.poblacion,
        generations=p.generaciones,
        mutation_rate=p.mutacion,
        crossover_rate=p.cruce,
        elite_size=p.elite,
        mutation_type=p.tipo_mutacion,
        patience=p.patience,
        min_improvement=p.mejora_minima,
        seed=p.semilla,
        log_interval=p.log_cada,
    )


def run_optimization(req: OptimizarRequest) -> dict:
    if not state.ready:
        raise HTTPException(status_code=503, detail="El grafo aun no esta cargado")

    points = [p.model_dump() for p in req.puntos]
    base_inicio = req.base_inicio.model_dump() if req.base_inicio else default_base(state.nodes)
    base_fin = req.base_fin.model_dump() if req.base_fin else base_inicio.copy()
    blockages = [b.model_dump() for b in req.bloqueos]

    try:
        return optimize_route(
            base_graph=state.graph,
            osm_nodes=state.nodes,
            points=points,
            base_inicio=base_inicio,
            base_fin=base_fin,
            params=_params_from_request(req.params_ag),
            blockages=blockages,
            radius_m=req.radio_bloqueo,
            zona="Ruta",
            turno="",
            verbose=False,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al optimizar: {exc}")


def build_response(decoded: dict) -> dict:
    return {
        "base_inicio": decoded["base_inicio"],
        "base_fin": decoded["base_fin"],
        "distancia_total_km": decoded["distancia_total_km"],
        "distancia_total_m": decoded["distancia_total_m"],
        "convergencia": decoded.get("convergencia", {}),
        "puntos_inaccesibles": decoded.get("puntos_inaccesibles", []),
        "segmentos": decoded["segmentos"],
        "todas_las_coords": decoded.get("todas_las_coords", []),
    }


def render_map(decoded: dict, blockages: list) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.close()
    build_route_map([decoded], output_path=tmp.name, blockages=blockages)
    with open(tmp.name, "r", encoding="utf-8") as f:
        html = f.read()
    os.unlink(tmp.name)
    return html
