import folium

import map_layers
from map_panel import add_instructions_panel
from map_animation import add_truck_animation

_DEFAULT_CENTER = [16.622, -93.104]


def _map_center(decoded_routes):
    coords = []
    for route in decoded_routes:
        coords.extend(route.get("todas_las_coords", []))
    if not coords:
        return _DEFAULT_CENTER
    return [sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords)]


def build_route_map(decoded_routes, output_path="ruta_resultado.html", blockages=None):
    if not decoded_routes:
        print("[Mapa] Sin rutas para mostrar")
        return output_path

    m = folium.Map(location=_map_center(decoded_routes), zoom_start=15, tiles="OpenStreetMap")

    for route_idx, route in enumerate(decoded_routes):
        map_layers.add_route_group(m, route, route_idx)

    if blockages:
        map_layers.add_blockages(m, blockages)
    map_layers.add_unreachable_points(m, decoded_routes)

    add_instructions_panel(m, decoded_routes)
    add_truck_animation(m, decoded_routes)

    m.save(output_path)
    print(f"[Mapa] Guardado en: {output_path}")
    return output_path
