import json
import networkx as nx

from geo import haversine


HIGHWAY_TYPES = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential", "motorway_link", "trunk_link",
    "primary_link", "secondary_link", "tertiary_link", "living_street",
    "service", "road",
}


def _parse_elements(elements):
    nodes = {}
    ways = []
    for el in elements:
        if el["type"] == "node":
            nodes[el["id"]] = {"lat": el["lat"], "lon": el["lon"]}
        elif el["type"] == "way" and el.get("tags", {}).get("highway", "") in HIGHWAY_TYPES:
            ways.append(el)
    return nodes, ways


def _way_metadata(tags):
    name = tags.get("name") or tags.get("alt_name") or tags.get("ref") or "Sin nombre"
    highway = tags.get("highway", "unclassified")
    oneway_tag = tags.get("oneway", "no")
    return name, highway, oneway_tag in ("yes", "1", "true", "-1"), oneway_tag == "-1"


def _add_way_edges(graph, nodes, way):
    name, highway, is_oneway, reverse = _way_metadata(way.get("tags", {}))
    node_ids = way["nodes"]

    for i in range(len(node_ids) - 1):
        u, v = node_ids[i], node_ids[i + 1]
        if u not in nodes or v not in nodes:
            continue

        dist = haversine(nodes[u]["lat"], nodes[u]["lon"], nodes[v]["lat"], nodes[v]["lon"])
        attrs = {"distance": dist, "name": name, "highway": highway, "oneway": is_oneway}

        if reverse:
            graph.add_edge(v, u, **attrs)
        else:
            graph.add_edge(u, v, **attrs)
            if not is_oneway:
                graph.add_edge(v, u, **attrs)


def load_osm_graph(osm_path):
    with open(osm_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes, ways = _parse_elements(data.get("elements", []))

    graph = nx.DiGraph()
    for nid, coords in nodes.items():
        graph.add_node(nid, lat=coords["lat"], lon=coords["lon"])
    for way in ways:
        _add_way_edges(graph, nodes, way)

    print(f"[OSM] Grafo cargado: {graph.number_of_nodes()} nodos, {graph.number_of_edges()} aristas")
    return graph, nodes


def snap_to_graph(lat, lon, nodes):
    best_node = None
    best_dist = float("inf")
    for nid, coords in nodes.items():
        dlat = coords["lat"] - lat
        dlon = coords["lon"] - lon
        d = dlat * dlat + dlon * dlon
        if d < best_dist:
            best_dist = d
            best_node = nid
    return best_node
