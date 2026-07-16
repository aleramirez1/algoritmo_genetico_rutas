ANIMATION_CSS = """
.truck-popup .leaflet-popup-content-wrapper {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    padding: 0;
}
.truck-popup .leaflet-popup-content { margin: 8px 10px; }
.truck-popup .leaflet-popup-tip { background: rgba(255, 255, 255, 0.95); }
.truck-marker { transition: transform 0.15s linear; }
"""

CONTROL_BAR_TEMPLATE = """
<div style="background: rgba(255,255,255,0.97); border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    padding: 10px 16px; min-width: 380px; pointer-events: all; border-left: 5px solid {color};">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <span style="font-weight:bold; font-size:13px; color:{color};">{zona} {turno}</span>
        <span style="color:#888; font-size:11px; margin-left:auto;">{distancia_km} km</span>
    </div>
    <div style="display:flex; align-items:center; gap:6px;">
        <button id="play-btn-{rid}" onclick="window['anim_toggle_{rid}'] && window['anim_toggle_{rid}']()"
            style="width:36px;height:36px;border-radius:50%;border:none;background:{color};color:white;
            font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;">&gt;</button>
        <button onclick="window['anim_reset_{rid}']()"
            style="width:30px;height:30px;border-radius:50%;border:none;background:#e9ecef;color:#444;
            font-size:13px;cursor:pointer;">R</button>
        <div style="flex:1; position:relative; height:20px; display:flex; align-items:center;">
            <div style="width:100%;height:6px;background:#e9ecef;border-radius:3px;overflow:hidden;">
                <div id="progress-bar-{rid}" style="height:100%;width:0%;background:{color};
                     border-radius:3px;transition:width 0.1s linear;"></div>
            </div>
            <input id="seek-{rid}" type="range" min="0" max="100" value="0" step="0.1"
                oninput="window['anim_seek_{rid}'](this.value)"
                style="position:absolute;width:100%;opacity:0;cursor:pointer;height:20px;">
        </div>
        <select onchange="window['anim_speed_{rid}'](this.value)"
            style="border:1px solid #ddd;border-radius:6px;padding:3px 4px;font-size:12px;cursor:pointer;">
            <option value="0.25">0.25x</option><option value="0.5">0.5x</option>
            <option value="1" selected>1x</option><option value="2">2x</option>
            <option value="4">4x</option><option value="8">8x</option>
        </select>
        <span id="speed-label-{rid}" style="font-size:11px;color:#888;min-width:24px;">1x</span>
    </div>
</div>
"""
