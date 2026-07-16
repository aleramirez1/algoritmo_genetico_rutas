import numpy as np
import networkx as nx


def build_distance_matrix(node_ids, graph):
    n = len(node_ids)
    matrix = np.full((n, n), float("inf"))
    np.fill_diagonal(matrix, 0)
    node_to_idx = {nid: i for i, nid in enumerate(node_ids)}

    print(f"[Matriz] Calculando distancias para {n} nodos con Dijkstra...")

    for i, src in enumerate(node_ids):
        try:
            lengths = nx.single_source_dijkstra_path_length(graph, src, weight="distance")
        except nx.NetworkXError:
            continue
        for j, dst in enumerate(node_ids):
            if dst in lengths:
                matrix[i][j] = lengths[dst]

    inf_count = np.sum(matrix == float("inf")) - np.trace(matrix == float("inf"))
    if inf_count > 0:
        print(f"  [Advertencia] {inf_count} pares sin ruta encontrada en el grafo")

    return matrix, node_to_idx
