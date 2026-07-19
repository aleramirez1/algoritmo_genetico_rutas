import copy
import numpy as np

from osm_graph import snap_to_graph
from blockages import apply_blockages
from distance_matrix import build_distance_matrix
from genetic import GeneticTSP
from route_decoder import decode_full_route


def default_base(osm_nodes):
    lats = [n["lat"] for n in osm_nodes.values()]
    lons = [n["lon"] for n in osm_nodes.values()]
    return {
        "lat": sum(lats) / len(lats),
        "lng": sum(lons) / len(lons),
        "nombre": "Base (centroide)",
    }


def _prepare_graph(base_graph, osm_nodes, blockages, radius_m):
    if not blockages:
        return base_graph
    graph = copy.deepcopy(base_graph)
    apply_blockages(graph, osm_nodes, blockages, radius_m=radius_m)
    return graph


def _split_reachable(points, dist_matrix, n_total):
    reachable, unreachable = [], []
    for local_idx in range(1, n_total - 1):
        d_in = dist_matrix[0][local_idx]
        d_out = dist_matrix[local_idx][n_total - 1]
        if d_in == float("inf") or d_out == float("inf"):
            unreachable.append(points[local_idx - 1])
        else:
            reachable.append(local_idx)
    return reachable, unreachable


def optimize_route(base_graph, osm_nodes, points, base_inicio, base_fin, params,
                   blockages=None, radius_m=25.0, zona="Sin zona", turno="Sin turno", verbose=False):
    graph = _prepare_graph(base_graph, osm_nodes, blockages, radius_m)

    base_i = snap_to_graph(base_inicio["lat"], base_inicio["lng"], osm_nodes)
    base_f = snap_to_graph(base_fin["lat"], base_fin["lng"], osm_nodes)
    collection_nodes = [snap_to_graph(pt["lat"], pt["lng"], osm_nodes) for pt in points]
    all_nodes = [base_i] + collection_nodes + [base_f]

    dist_matrix, _ = build_distance_matrix(all_nodes, graph)

    reachable, unreachable = _split_reachable(points, dist_matrix, len(all_nodes))
    kept = [0] + reachable + [len(all_nodes) - 1]
    all_nodes = [all_nodes[i] for i in kept]
    kept_points = [points[i - 1] for i in reachable]
    dist_matrix = dist_matrix[np.ix_(kept, kept)]

    ag = GeneticTSP(dist_matrix, params)
    best_route, best_dist, history = ag.run(verbose=verbose)

    decoded = decode_full_route  (
        graph, osm_nodes, best_route, all_nodes, kept_points, base_inicio, base_fin, zona, turno
    )
    decoded["puntos_inaccesibles"] = unreachable
    decoded["convergencia"] = {
        "generaciones_ejecutadas": len(history),
        "distancia_final_m": round(best_dist, 1),
    }
    return decoded
