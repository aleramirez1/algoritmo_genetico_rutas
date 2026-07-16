import networkx as nx

from geo import cardinal_direction, turn_instruction


class _SegmentAccumulator:

    def __init__(self):
        self.steps = []
        self.street = None
        self.dist = 0.0
        self.coords = []
        self.prev_dir = None
        self.start_coord = None

    def _flush(self, instruction):
        self.steps.append({
            "calle": self.street,
            "direccion": self.prev_dir,
            "distancia_m": round(self.dist, 1),
            "instruccion": instruction,
            "coords": list(self.coords),
            "coord_inicio": self.start_coord,
        })

    def add_edge(self, street, dist, u_coord, v_coord, direction):
        if self.street is None:
            self.street = street
            self.dist = dist
            self.coords = [u_coord, v_coord]
            self.start_coord = u_coord
            self.prev_dir = direction
        elif street == self.street:
            self.dist += dist
            self.coords.append(v_coord)
        else:
            self._flush(turn_instruction(self.prev_dir, direction))
            self.prev_dir = direction
            self.street = street
            self.dist = dist
            self.coords = [u_coord, v_coord]
            self.start_coord = u_coord

    def finish(self):
        if self.street is not None:
            self._flush(turn_instruction(None, self.prev_dir))
        return self.steps


def decode_path_segment(graph, osm_nodes, from_node, to_node):
    try:
        path_nodes = nx.dijkstra_path(graph, from_node, to_node, weight="distance")
        path_length = nx.dijkstra_path_length(graph, from_node, to_node, weight="distance")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return [], float("inf")

    if len(path_nodes) < 2:
        return [], 0.0

    acc = _SegmentAccumulator()
    for i in range(len(path_nodes) - 1):
        u, v = path_nodes[i], path_nodes[i + 1]
        edge = graph.get_edge_data(u, v, default={})
        u_d, v_d = osm_nodes.get(u, {}), osm_nodes.get(v, {})
        u_coord = (u_d.get("lat", 0), u_d.get("lon", 0))
        v_coord = (v_d.get("lat", 0), v_d.get("lon", 0))
        direction = cardinal_direction(u_coord[0], u_coord[1], v_coord[0], v_coord[1])
        acc.add_edge(edge.get("name", "Sin nombre"), edge.get("distance", 0.0), u_coord, v_coord, direction)

    return acc.finish(), path_length


def _build_labels(collection_points, node_ids_list, base_inicio, base_fin):
    labels = {0: f"Base Inicio ({base_inicio.get('nombre', 'Deposito')})"}
    for i, pt in enumerate(collection_points, start=1):
        labels[i] = f"{pt['id']} - {pt['nombre']}"
    labels[len(node_ids_list) - 1] = f"Base Fin ({base_fin.get('nombre', 'Deposito')})"
    return labels


def decode_full_route(graph, osm_nodes, route_indices, node_ids_list,
                      collection_points, base_inicio, base_fin, zona, turno):
    labels = _build_labels(collection_points, node_ids_list, base_inicio, base_fin)
    result = {
        "zona": zona,
        "turno": turno,
        "base_inicio": base_inicio,
        "base_fin": base_fin,
        "segmentos": [],
        "todas_las_coords": [],
    }

    total_dist = 0.0
    for seg_idx in range(len(route_indices) - 1):
        from_idx, to_idx = route_indices[seg_idx], route_indices[seg_idx + 1]
        steps, seg_dist = decode_path_segment(
            graph, osm_nodes, node_ids_list[from_idx], node_ids_list[to_idx]
        )
        if seg_dist == float("inf"):
            print(f"  [Advertencia] Sin ruta entre {labels[from_idx]} y {labels[to_idx]}")
            seg_dist = 0.0

        total_dist += seg_dist
        result["segmentos"].append({
            "de": labels[from_idx],
            "a": labels[to_idx],
            "distancia_m": round(seg_dist, 1),
            "pasos": steps,
        })
        for step in steps:
            result["todas_las_coords"].extend(step["coords"])

    result["distancia_total_m"] = round(total_dist, 1)
    result["distancia_total_km"] = round(total_dist / 1000, 3)
    return result


def print_route_instructions(route):
    print("\n" + "=" * 60)
    print(f"RUTA {route['zona'].upper()} | {route['turno'].upper()}")
    print(f"Distancia total: {route['distancia_total_km']} km")
    print("=" * 60)
    for seg in route["segmentos"]:
        print(f"\n-> DE: {seg['de']}")
        print(f"  A:  {seg['a']}  ({seg['distancia_m']} m)")
        for i, paso in enumerate(seg["pasos"], 1):
            print(f"  {i:2d}. {paso['instruccion']} por {paso['calle']} "
                  f"(direccion {paso['direccion']}, {paso['distancia_m']} m)")
    print("\n" + "=" * 60)
