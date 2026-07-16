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


def _segment_block(seg, color, start_num):
    html = (f"<div style='margin:4px 8px; padding:6px 8px; background:#e9ecef; border-radius:4px;'>"
            f"<b style='color:#264653;'>{seg['de']}</b><br>"
            f"<small style='color:#888;'>a: {seg['a']} ({seg['distancia_m']} m)</small></div>")
    num = start_num
    for paso in seg.get("pasos", []):
        html += (f"<div style='margin:2px 16px; padding:4px 6px; border-left:2px solid {color};'>"
                 f"<span style='font-size:11px;'>{num}. {paso['instruccion']}<br>"
                 f"<b>{paso['calle']}</b><span style='color:#888;'> - {paso['direccion']} "
                 f"- {paso['distancia_m']} m</span></span></div>")
        num += 1
    return html, num


def add_instructions_panel(m, decoded_routes):
    html = _PANEL_HEADER
    for route_idx, route in enumerate(decoded_routes):
        color = color_for(route_idx)
        html += _route_header(route, color)
        num = 1
        for seg in route.get("segmentos", []):
            block, num = _segment_block(seg, color, num)
            html += block
    html += "</div>"
    m.get_root().html.add_child(folium.Element(html))
