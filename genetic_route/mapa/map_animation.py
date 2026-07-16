import json
import folium

from map_colors import color_for
from animation_assets import ANIMATION_CSS, CONTROL_BAR_TEMPLATE
from animation_script import ANIMATION_JS


def _annotate_coords(route):
    coords = []
    segmentos = route.get("segmentos", [])
    for seg_idx, seg in enumerate(segmentos):
        is_stop = seg_idx < len(segmentos) - 1
        for paso in seg.get("pasos", []):
            for c in paso.get("coords", []):
                coords.append({
                    "lat": c[0], "lng": c[1],
                    "calle": paso.get("calle", "Sin nombre"),
                    "direccion": paso.get("direccion", ""),
                    "instruccion": paso.get("instruccion", ""),
                    "is_stop_end": False,
                })
        if is_stop and coords:
            coords[-1]["is_stop_end"] = True
    return coords


def _dedupe(coords):
    result = []
    for c in coords:
        if not result or c["lat"] != result[-1]["lat"] or c["lng"] != result[-1]["lng"]:
            result.append(c)
        elif c["is_stop_end"]:
            result[-1]["is_stop_end"] = True
    return result


def _extract_stops(coords):
    stops = []
    order = 1
    for i, c in enumerate(coords):
        if c.get("is_stop_end"):
            stops.append({"coordIndex": i, "order": order})
            order += 1
    return stops


def _build_route_payload(decoded_routes):
    payload = []
    for route_idx, route in enumerate(decoded_routes):
        coords = _dedupe(_annotate_coords(route))
        payload.append({
            "id": route_idx,
            "color": color_for(route_idx),
            "zona": route.get("zona", f"Ruta {route_idx + 1}"),
            "turno": route.get("turno", ""),
            "coords": coords,
            "stops": _extract_stops(coords),
            "distancia_km": route.get("distancia_total_km", 0),
        })
    return payload


def _controls_html(payload):
    bars = "".join(
        CONTROL_BAR_TEMPLATE.format(
            color=r["color"], rid=r["id"], zona=r["zona"],
            turno=r["turno"], distancia_km=r["distancia_km"],
        )
        for r in payload
    )
    return (f"<div id='animation-controls' style='position: fixed; bottom: 20px; left: 50%; "
            f"transform: translateX(-50%); z-index: 2000; display: flex; flex-direction: column; "
            f"gap: 8px; align-items: center; pointer-events: none;'>{bars}</div>")


def add_truck_animation(m, decoded_routes):
    payload = _build_route_payload(decoded_routes)
    data_script = (
        f"<script>window.__ROUTES__ = {json.dumps(payload, ensure_ascii=False)};"
        f"window.__MAP_VAR__ = \"{m.get_name()}\";</script>"
    )
    html = (
        data_script
        + _controls_html(payload)
        + f"<style>{ANIMATION_CSS}</style>"
        + f"<script>{ANIMATION_JS}</script>"
    )
    m.get_root().html.add_child(folium.Element(html))
