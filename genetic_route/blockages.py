import json

from geo import point_to_segment_dist


def load_blockages(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("puntos", data.get("bloqueos", []))
    if isinstance(data, list):
        return data
    return []


def _nearest_edge(graph, nodes, lat, lng):
    best_edge = None
    best_dist = float("inf")
    for u, v in graph.edges():
        u_c, v_c = nodes.get(u), nodes.get(v)
        if not u_c or not v_c:
            continue
        d = point_to_segment_dist(lat, lng, u_c["lat"], u_c["lon"], v_c["lat"], v_c["lon"])
        if d < best_dist:
            best_dist = d
            best_edge = (u, v)
    return best_edge, best_dist


def _cut_edge(graph, edge):
    u, v = edge
    removed = 0
    for a, b in ((u, v), (v, u)):
        if graph.has_edge(a, b):
            graph.remove_edge(a, b)
            removed += 1
    return removed


def apply_blockages(graph, nodes, blockages, radius_m=25.0):
    if not blockages:
        return 0

    total_removed = 0
    for blk in blockages:
        lat, lng = blk.get("lat"), blk.get("lng")
        if lat is None or lng is None:
            continue

        edge, dist = _nearest_edge(graph, nodes, lat, lng)
        removed = _cut_edge(graph, edge) if edge else 0
        total_removed += removed

        print(f"  [Bloqueo] {blk.get('id', '?')} en ({lat:.5f}, {lng:.5f}) "
              f"-> segmento cortado a {dist:.1f} m ({removed} sentido/s). {blk.get('reporte', '')}")

    print(f"[Bloqueos] {len(blockages)} bloqueo(s) aplicado(s), "
          f"{total_removed} arista(s) eliminada(s) del grafo")
    return total_removed
