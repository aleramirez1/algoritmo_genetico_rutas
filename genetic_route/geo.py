import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def point_to_segment_dist(plat, plng, alat, alng, blat, blng):
    m_per_deg_lat = 111320.0
    m_per_deg_lng = 111320.0 * math.cos(math.radians(plat))

    px, py = plng * m_per_deg_lng, plat * m_per_deg_lat
    ax, ay = alng * m_per_deg_lng, alat * m_per_deg_lat
    bx, by = blng * m_per_deg_lng, blat * m_per_deg_lat

    dx, dy = bx - ax, by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - ax, py - ay)

    t = ((px - ax) * dx + (py - ay) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


DIRECTIONS = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]


def cardinal_direction(lat1, lon1, lat2, lon2):
    angle = math.degrees(math.atan2(lon2 - lon1, lat2 - lat1))
    if -22.5 <= angle < 22.5:
        return "Norte"
    if 22.5 <= angle < 67.5:
        return "Noreste"
    if 67.5 <= angle < 112.5:
        return "Este"
    if 112.5 <= angle < 157.5:
        return "Sureste"
    if angle >= 157.5 or angle < -157.5:
        return "Sur"
    if -157.5 <= angle < -112.5:
        return "Suroeste"
    if -112.5 <= angle < -67.5:
        return "Oeste"
    return "Noroeste"


def turn_instruction(prev_dir, curr_dir):
    if prev_dir is None:
        return f"Continua hacia {curr_dir}"
    if prev_dir not in DIRECTIONS or curr_dir not in DIRECTIONS:
        return f"Dirigete hacia {curr_dir}"

    diff = (DIRECTIONS.index(curr_dir) - DIRECTIONS.index(prev_dir)) % 8
    if diff == 0:
        return "Continua recto"
    if diff in (1, 2):
        return f"Gira ligeramente a la derecha hacia {curr_dir}"
    if diff == 3:
        return f"Gira a la derecha hacia {curr_dir}"
    if diff == 4:
        return f"Da vuelta en U hacia {curr_dir}"
    if diff == 5:
        return f"Gira a la izquierda hacia {curr_dir}"
    return f"Gira ligeramente a la izquierda hacia {curr_dir}"
