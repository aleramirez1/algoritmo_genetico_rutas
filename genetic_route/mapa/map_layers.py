import folium

from map_colors import color_for


def add_route_polyline(group, route, color):
    for seg in route.get("segmentos", []):
        for paso in seg.get("pasos", []):
            coords = paso.get("coords", [])
            if len(coords) >= 2:
                tooltip = (f"<b>{paso['calle']}</b><br>Direccion: {paso['direccion']}"
                           f"<br>Distancia: {paso['distancia_m']} m")
                folium.PolyLine(coords, color=color, weight=5, opacity=0.85,
                                tooltip=tooltip).add_to(group)


def add_base_markers(group, route):
    base_i = route.get("base_inicio", {})
    if base_i.get("lat") and base_i.get("lng"):
        folium.Marker([base_i["lat"], base_i["lng"]],
                      popup=folium.Popup(f"<b>BASE INICIO</b><br>{base_i.get('nombre','')}", max_width=200),
                      icon=folium.Icon(color="green", icon="home", prefix="fa"),
                      tooltip="Base Inicio").add_to(group)
    base_f = route.get("base_fin", {})
    if base_f.get("lat") and base_f.get("lng"):
        folium.Marker([base_f["lat"], base_f["lng"]],
                      popup=folium.Popup(f"<b>BASE FIN</b><br>{base_f.get('nombre','')}", max_width=200),
                      icon=folium.Icon(color="red", icon="flag", prefix="fa"),
                      tooltip="Base Fin").add_to(group)


def _collection_icon(route_idx, order, color):
    html = f"""
    <div id="collection-{route_idx}-{order}" class="collection-marker"
        data-base-color="{color}"
        style="background:{color};color:white;border-radius:50%;width:26px;height:26px;
        display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:12px;
        border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.4);
        transition:background 0.4s, transform 0.4s;">{order}</div>"""
    return folium.DivIcon(html=html, icon_size=(26, 26), icon_anchor=(13, 13))


def add_collection_markers(group, route, route_idx, color):
    order = 1
    segmentos = route.get("segmentos", [])
    for seg_idx, seg in enumerate(segmentos):
        if seg_idx == len(segmentos) - 1:
            break
        pasos = seg.get("pasos", [])
        if not pasos or not pasos[-1].get("coords"):
            continue
        dest = pasos[-1]["coords"][-1]
        popup = folium.Popup(
            f"<b>Punto #{order}</b><br>{seg['a']}<br>"
            f"Distancia acumulada: {seg['distancia_m']} m desde punto anterior", max_width=250)
        folium.Marker(dest, popup=popup, icon=_collection_icon(route_idx, order, color),
                      tooltip=f"Parada #{order}: {seg['a']}").add_to(group)
        order += 1


def add_route_group(m, route, route_idx):
    color = color_for(route_idx)
    label = f"{route.get('zona', f'Ruta {route_idx + 1}')} - {route.get('turno', '')}"
    group = folium.FeatureGroup(name=f"Camion {label}", show=True)
    add_route_polyline(group, route, color)
    add_base_markers(group, route)
    add_collection_markers(group, route, route_idx, color)
    group.add_to(m)


def add_blockages(m, blockages):
    group = folium.FeatureGroup(name="Bloqueos de calles", show=True)
    for blk in blockages:
        lat, lng = blk.get("lat"), blk.get("lng")
        if lat is None or lng is None:
            continue
        popup = folium.Popup(
            f"<div style='font-size:12px;min-width:160px;'><b style='color:#d90429;'>CALLE BLOQUEADA</b>"
            f"<br><b>{blk.get('id', 'Bloqueo')}</b><br>"
            f"<span style='color:#555;'>{blk.get('reporte', 'Calle bloqueada')}</span></div>", max_width=250)
        folium.Circle([lat, lng], radius=25, color="#d90429", fill=True,
                      fill_color="#d90429", fill_opacity=0.15, weight=2).add_to(group)
        icon_html = """
        <div style="background:#d90429;color:white;border-radius:50%;width:30px;height:30px;
            display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:bold;
            border:2px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.4);">X</div>"""
        folium.Marker([lat, lng], popup=popup,
                      icon=folium.DivIcon(html=icon_html, icon_size=(30, 30), icon_anchor=(15, 15)),
                      tooltip=f"Bloqueo: {blk.get('reporte', '')}").add_to(group)
    group.add_to(m)
    print(f"[Mapa] {len(blockages)} bloqueo(s) dibujado(s) en el mapa")


def add_unreachable_points(m, decoded_routes):
    group = folium.FeatureGroup(name="Puntos no recolectables", show=True)
    total = 0
    for route in decoded_routes:
        for pt in route.get("puntos_inaccesibles", []):
            lat, lng = pt.get("lat"), pt.get("lng")
            if lat is None or lng is None:
                continue
            popup = folium.Popup(
                f"<div style='font-size:12px;min-width:160px;'><b style='color:#6c757d;'>NO RECOLECTABLE</b>"
                f"<br><b>{pt.get('id', '')}</b> - {pt.get('nombre', '')}<br>"
                f"<span style='color:#a00;'>Aislado por bloqueos de calles</span></div>", max_width=250)
            icon_html = """
            <div style="background:#6c757d;color:white;border-radius:50%;width:26px;height:26px;
                display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:14px;
                border:2px dashed white;box-shadow:0 2px 4px rgba(0,0,0,0.4);opacity:0.85;">X</div>"""
            folium.Marker([lat, lng], popup=popup,
                          icon=folium.DivIcon(html=icon_html, icon_size=(26, 26), icon_anchor=(13, 13)),
                          tooltip=f"No recolectable: {pt.get('id', '')}").add_to(group)
            total += 1
    if total > 0:
        group.add_to(m)
        print(f"[Mapa] {total} punto(s) no recolectable(s) marcado(s) en el mapa")
