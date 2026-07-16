ANIMATION_JS = """
var animStates = {};

(function () {
    var ROUTES = window.__ROUTES__ || [];
    var MAP_VAR = window.__MAP_VAR__;

    function waitForMap(cb) {
        var t = setInterval(function () {
            var candidate = window[MAP_VAR];
            if (candidate && candidate.getCenter) {
                clearInterval(t);
                cb(candidate);
            }
        }, 100);
    }

    function truckIcon(color) {
        return L.divIcon({
            html: '<div class="truck-marker" style="font-size:26px;line-height:1;">\\uD83D\\uDE9B</div>',
            iconSize: [30, 30], iconAnchor: [15, 15], className: ''
        });
    }

    function bearing(lat1, lng1, lat2, lng2) {
        var dLng = (lng2 - lng1) * Math.PI / 180;
        var lat1r = lat1 * Math.PI / 180;
        var lat2r = lat2 * Math.PI / 180;
        var y = Math.sin(dLng) * Math.cos(lat2r);
        var x = Math.cos(lat1r) * Math.sin(lat2r) - Math.sin(lat1r) * Math.cos(lat2r) * Math.cos(dLng);
        return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
    }

    function lerp(a, b, t) {
        return { lat: a.lat + (b.lat - a.lat) * t, lng: a.lng + (b.lng - a.lng) * t };
    }

    function updateProgress(id, ratio) {
        var bar = document.getElementById('progress-bar-' + id);
        var seek = document.getElementById('seek-' + id);
        if (bar) bar.style.width = (ratio * 100).toFixed(1) + '%';
        if (seek) seek.value = (ratio * 100).toFixed(1);
    }

    function updateControlBar(id) {
        var state = animStates[id];
        if (!state) return;
        var btn = document.getElementById('play-btn-' + id);
        if (btn) btn.textContent = state.playing ? 'II' : '>';
    }

    function setupRoute(map, route) {
        if (!route.coords || route.coords.length < 2) return;

        var state = {
            playing: false, segIdx: 0, t: 0, speed: 1,
            trailCoords: [], animFrame: null, lastTime: null,
            totalSegments: route.coords.length - 1, stops: route.stops || [],
            popupOpen: false
        };
        animStates[route.id] = state;

        state.marker = L.marker([route.coords[0].lat, route.coords[0].lng],
            { icon: truckIcon(route.color), zIndexOffset: 1000 }).addTo(map);
        state.trailLine = L.polyline([], { color: '#1565ff', weight: 7, opacity: 0.95 }).addTo(map);
        state.popup = L.popup({ closeButton: false, autoClose: false, closeOnClick: false,
            className: 'truck-popup', offset: [0, -20] });

        function updateStops(currentIndex) {
            state.stops.forEach(function (stop) {
                var el = document.getElementById('collection-' + route.id + '-' + stop.order);
                if (!el) return;
                if (stop.coordIndex <= currentIndex) {
                    el.style.background = '#2ecc71';
                    el.style.transform = 'scale(1.15)';
                    el.innerHTML = 'OK';
                } else {
                    el.style.background = el.getAttribute('data-base-color');
                    el.style.transform = 'scale(1)';
                    el.innerHTML = stop.order;
                }
            });
        }

        function updateInfoPanel(coord) {
            state.popup.setLatLng([coord.lat, coord.lng]).setContent(
                '<div style="font-size:11px;line-height:1.4;min-width:140px;">' +
                '<b style="color:' + route.color + '">' + route.zona + ' ' + route.turno + '</b><br>' +
                '<span>' + coord.instruccion + '</span><br>' +
                '<b>' + coord.calle + '</b> <span style="color:#888;">' + coord.direccion + '</span></div>'
            );
            if (!state.popupOpen) { state.popup.openOn(map); state.popupOpen = true; }
        }

        function animate(timestamp) {
            if (!state.playing) return;
            if (!state.lastTime) state.lastTime = timestamp;
            var dt = (timestamp - state.lastTime) / 1000;
            state.lastTime = timestamp;

            var total = state.totalSegments;
            state.t += dt * (total / 180) * state.speed;

            while (state.t >= 1 && state.segIdx < total - 1) {
                state.trailCoords.push([route.coords[state.segIdx].lat, route.coords[state.segIdx].lng]);
                state.trailLine.setLatLngs(state.trailCoords);
                state.segIdx++;
                state.t -= 1;
            }

            if (state.segIdx >= total - 1 && state.t >= 1) {
                var last = route.coords[route.coords.length - 1];
                state.marker.setLatLng([last.lat, last.lng]);
                state.trailCoords.push([last.lat, last.lng]);
                state.trailLine.setLatLngs(state.trailCoords);
                state.playing = false;
                updateControlBar(route.id);
                updateInfoPanel(last);
                updateStops(route.coords.length - 1);
                updateProgress(route.id, 1.0);
                return;
            }

            var from = route.coords[state.segIdx];
            var to = route.coords[state.segIdx + 1];
            var pos = lerp(from, to, state.t);

            state.marker.setLatLng([pos.lat, pos.lng]);
            updateInfoPanel(from);

            var trail = state.trailCoords.slice();
            trail.push([pos.lat, pos.lng]);
            state.trailLine.setLatLngs(trail);
            updateStops(state.segIdx);
            updateProgress(route.id, (state.segIdx + state.t) / total);

            state.animFrame = requestAnimationFrame(animate);
        }

        function play() {
            state.playing = true; state.lastTime = null;
            state.animFrame = requestAnimationFrame(animate);
            updateControlBar(route.id);
        }
        function pause() {
            state.playing = false;
            if (state.animFrame) cancelAnimationFrame(state.animFrame);
            updateControlBar(route.id);
        }
        function reset() {
            pause();
            state.segIdx = 0; state.t = 0; state.trailCoords = [];
            state.trailLine.setLatLngs([]);
            state.marker.setLatLng([route.coords[0].lat, route.coords[0].lng]);
            state.popupOpen = false;
            map.closePopup(state.popup);
            updateStops(-1);
            updateProgress(route.id, 0);
            updateControlBar(route.id);
        }

        window['anim_toggle_' + route.id] = function () { state.playing ? pause() : play(); };
        window['anim_reset_' + route.id] = reset;
        window['anim_speed_' + route.id] = function (v) {
            state.speed = parseFloat(v);
            document.getElementById('speed-label-' + route.id).textContent = v + 'x';
        };
        window['anim_seek_' + route.id] = function (v) {
            var ratio = parseFloat(v) / 100;
            pause();
            state.segIdx = Math.min(Math.floor(ratio * state.totalSegments), state.totalSegments - 1);
            state.t = 0; state.trailCoords = [];
            for (var i = 0; i <= state.segIdx; i++) {
                state.trailCoords.push([route.coords[i].lat, route.coords[i].lng]);
            }
            state.trailLine.setLatLngs(state.trailCoords);
            state.marker.setLatLng([route.coords[state.segIdx].lat, route.coords[state.segIdx].lng]);
            updateStops(state.segIdx);
            updateProgress(route.id, ratio);
        };

        updateStops(-1);
    }

    waitForMap(function (map) {
        ROUTES.forEach(function (route) { setupRoute(map, route); });
    });
})();
"""
