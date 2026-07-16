import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mapa"))

from osm_graph import load_osm_graph
from blockages import load_blockages, apply_blockages
from ag_params import AGParams
from optimizer import optimize_route, default_base
from route_decoder import print_route_instructions
from map_builder import build_route_map


def parse_args():
    parser = argparse.ArgumentParser(
        description="Optimizador de rutas de recoleccion con Algoritmo Genetico"
    )
    parser.add_argument("--osm", required=True)
    parser.add_argument("--ruta", required=True, nargs="+")
    parser.add_argument("--base-inicio", default=None)
    parser.add_argument("--base-fin", default=None)
    parser.add_argument("--inicio-lat", type=float, default=None)
    parser.add_argument("--inicio-lng", type=float, default=None)
    parser.add_argument("--inicio-nombre", default="Base Inicio")
    parser.add_argument("--fin-lat", type=float, default=None)
    parser.add_argument("--fin-lng", type=float, default=None)
    parser.add_argument("--fin-nombre", default="Base Fin")
    parser.add_argument("--bloqueos", default=None)
    parser.add_argument("--radio-bloqueo", type=float, default=25.0)
    parser.add_argument("--poblacion", type=int, default=150)
    parser.add_argument("--generaciones", type=int, default=500)
    parser.add_argument("--mutacion", type=float, default=0.02)
    parser.add_argument("--cruce", type=float, default=0.9)
    parser.add_argument("--elite", type=int, default=20)
    parser.add_argument("--tipo-mutacion", choices=["swap", "inversion"], default="swap")
    parser.add_argument("--patience", type=int, default=0)
    parser.add_argument("--mejora-minima", type=float, default=1.0)
    parser.add_argument("--semilla", type=int, default=None)
    parser.add_argument("--log-cada", type=int, default=50)
    parser.add_argument("--output", default="ruta_resultado.html")
    return parser.parse_args()


def _params_from_args(args):
    return AGParams(
        pop_size=args.poblacion,
        generations=args.generaciones,
        mutation_rate=args.mutacion,
        crossover_rate=args.cruce,
        elite_size=args.elite,
        mutation_type=args.tipo_mutacion,
        patience=args.patience,
        min_improvement=args.mejora_minima,
        seed=args.semilla,
        log_interval=args.log_cada,
    )


def _resolve_base(lat, lng, nombre, base_json, osm_nodes, fallback):
    if lat is not None and lng is not None:
        base = {"lat": lat, "lng": lng, "nombre": nombre}
        print(f"[Info] Base: {base['nombre']} ({lat:.5f}, {lng:.5f})")
        return base
    if base_json:
        return json.loads(base_json)
    if fallback is not None:
        return fallback
    base = default_base(osm_nodes)
    print(f"[Info] Base por centroide: {base['lat']:.4f}, {base['lng']:.4f}")
    return base


def _load_route(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _process_route(route_data, graph, osm_nodes, base_inicio, base_fin, params):
    zona = route_data.get("zona", "Sin zona")
    turno = route_data.get("turno", "Sin turno")
    points = route_data.get("puntos", [])

    print(f"\n{'='*60}\nProcesando: {zona} | {turno} | {len(points)} puntos\n{'='*60}")

    decoded = optimize_route(
        base_graph=graph, osm_nodes=osm_nodes, points=points,
        base_inicio=base_inicio, base_fin=base_fin, params=params,
        blockages=None, zona=zona, turno=turno, verbose=True,
    )

    unreachable = decoded.get("puntos_inaccesibles", [])
    if unreachable:
        print(f"[Bloqueos] {len(unreachable)} punto(s) inaccesible(s), excluidos:")
        for pt in unreachable:
            print(f"    - {pt['id']} ({pt.get('nombre', '')})")

    print_route_instructions(decoded)
    return decoded


def run():
    args = parse_args()

    print(f"\n[Cargando] Grafo OSM desde {args.osm}...")
    graph, osm_nodes = load_osm_graph(args.osm)

    blockages = []
    if args.bloqueos:
        print(f"\n[Bloqueos] Cargando bloqueos desde {args.bloqueos}...")
        blockages = load_blockages(args.bloqueos)
        apply_blockages(graph, osm_nodes, blockages, radius_m=args.radio_bloqueo)

    base_inicio = _resolve_base(
        args.inicio_lat, args.inicio_lng, args.inicio_nombre, args.base_inicio, osm_nodes, None
    )
    base_fin = _resolve_base(
        args.fin_lat, args.fin_lng, args.fin_nombre, args.base_fin, osm_nodes, base_inicio.copy()
    )

    params = _params_from_args(args)

    decoded_routes = [
        _process_route(_load_route(path), graph, osm_nodes, base_inicio, base_fin, params)
        for path in args.ruta
    ]

    print(f"\n[Mapa] Generando mapa interactivo...")
    output_path = build_route_map(decoded_routes, output_path=args.output, blockages=blockages)
    print(f"\nListo. Abre el archivo en tu navegador: {output_path}")
