import folium

from map_colors import color_for

_PANEL_HEADER = """
<div id="route-panel" style="position: fixed; top: 10px; right: 10px; z-index: 1000;
    background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    max-height: 80vh; width: 320px; overflow-y: auto; font-family: Arial, sans-serif; font-size: 13px;">
    <div style="padding:12px 16px; background:#264653; color:white; border-radius:8px 8px 0 0;
                display:flex; justify-content:space-between; align-items:center;">
        <b>Instrucciones de Ruta</b>
        <button onclick="document.getElementById('route-panel').style.display='none'"
                style="background:none;border:none;color:white;cursor:pointer;font-size:16px;">X</button>
    </div>
"""


def _route_header(route, color):
    return (f"<div style='border-left:4px solid {color}; margin:8px; padding:8px; "
            f"border-radius:4px; background:#f8f9fa;'>"
            f"<b>{route.get('zona', '')} {route.get('turno', '')}</b><br>"
            f"<span style='color:#666;'>Distancia total: {route.get('distancia_total_km', 0)} km</span></div>")


def _step_row(num, paso, color):
    return (f"<div style='margin:2px 8px; padding:5px 8px; border-left:3px solid {color};'>"
            f"<span style='font-size:12px;'>{num}. <b>{paso['calle']}</b> "
            f"<span style='color:#888;'>({paso['distancia_m']} m)</span></span></div>")


def add_instructions_panel(m, decoded_routes):
    html = _PANEL_HEADER
    for route_idx, route in enumerate(decoded_routes):
        color = color_for(route_idx)
        html += _route_header(route, color)
        num = 1
        for seg in route.get("segmentos", []):
            for paso in seg.get("pasos", []):
                html += _step_row(num, paso, color)
                num += 1
    html += "</div>"
    m.get_root().html.add_child(folium.Element(html))
