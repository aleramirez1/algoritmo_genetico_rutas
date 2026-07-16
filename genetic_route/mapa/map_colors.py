ROUTE_COLORS = [
    "#e63946", "#2a9d8f", "#e9c46a", "#f4a261", "#264653",
    "#8338ec", "#3a86ff", "#fb5607", "#06d6a0", "#ff006e",
]


def color_for(route_idx):
    return ROUTE_COLORS[route_idx % len(ROUTE_COLORS)]
