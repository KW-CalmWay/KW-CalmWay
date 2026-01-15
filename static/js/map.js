window.getSegmentLineColor = window.getSegmentLineColor || function (line, type) {
    const raw = String(line || '').trim();
    const resolvedType = type ? String(type).trim() : '';
    if (!raw || raw === 'walk' || resolvedType === 'walk') return '#9ca3af';
    if (resolvedType === 'subway' || raw.includes('호선') || raw.includes('수도권')) {
        const match = raw.match(/\d+/);
        return match ? '#2563eb' : '#9ca3af';
    }
    return '#84cc16';
};

window.tmapState = window.tmapState || {
    map: null,
    overlays: [],
    polylines: []
};

function clearTmapOverlays() {
    window.tmapState.overlays.forEach(overlay => overlay.setMap(null));
    window.tmapState.polylines.forEach(line => line.setMap(null));
    window.tmapState.overlays = [];
    window.tmapState.polylines = [];
}

function ensureTmap(center) {
    if (!window.Tmapv2) {
        alert('Tmap JavaScript API를 불러오지 못했습니다.');
        return null;
    }

    if (!window.tmapState.map) {
        window.tmapState.map = new Tmapv2.Map("map_div", {
            center,
            width: "100%",
            height: "100%",
            zoom: 15
        });
    } else if (center) {
        window.tmapState.map.setCenter(center);
    }

    return window.tmapState.map;
}

function fitMapToPoints(map, points) {
    if (!points.length || !map || !window.Tmapv2 || !window.Tmapv2.LatLngBounds) return;
    const bounds = new Tmapv2.LatLngBounds();
    points.forEach(point => {
        bounds.extend(new Tmapv2.LatLng(point.lat, point.lon));
    });
    if (map.fitBounds) {
        map.fitBounds(bounds);
    } else if (map.panToBounds) {
        map.panToBounds(bounds);
    }
}

function buildMarkerIcon(color) {
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
            <path d="M14 1C7.9 1 3 5.9 3 12c0 8.6 8.7 20.9 10.3 23 0.3 0.4 0.8 0.4 1.1 0 1.6-2.1 10.3-14.4 10.3-23C25 5.9 20.1 1 14 1z" fill="${color}" stroke="#1f2937" stroke-width="1"/>
            <circle cx="14" cy="12" r="4.5" fill="#ffffff"/>
        </svg>
    `;
    return "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg);
}

function getMarkerColor(marker) {
    if (marker.type === 'transfer') return window.getSegmentLineColor(marker.line, marker.lineType);
    if (marker.type === 'start') return '#7dc41b';
    return '#ef4444';
}

window.openMap = function (routeId) {
    const route = window.routesData.find(r => r.id === routeId);
    if (!route) return;

    document.getElementById('map-route-title').innerText = route.pathSummary;
    document.getElementById('map-route-desc').innerText = `총 ${route.totalTime}분 | 환승 ${route.transferCount}회 | 요금 ${route.fare}원`;

    const legend = document.getElementById('map-legend');

    legend.style.display = 'none';

    const fallbackCenter = new Tmapv2.LatLng(37.566481622437934, 126.98502302169841);
    const firstPoint = route.mapPoints && route.mapPoints.length ? route.mapPoints[0] : null;
    const center = firstPoint ? new Tmapv2.LatLng(firstPoint.lat, firstPoint.lon) : fallbackCenter;
    const map = ensureTmap(center);
    if (!map) return;

    clearTmapOverlays();

    const segments = Array.isArray(route.mapSegments) ? route.mapSegments : [];
    segments.forEach(seg => {
        const strokeColor = window.getSegmentLineColor(seg.line, seg.type);
        const line = new Tmapv2.Polyline({
            path: [
                new Tmapv2.LatLng(seg.start.lat, seg.start.lon),
                new Tmapv2.LatLng(seg.end.lat, seg.end.lon)
            ],
            strokeColor,
            strokeWeight: 5,
            map
        });
        window.tmapState.polylines.push(line);
    });

    const mapMarkers = Array.isArray(route.mapMarkers) ? route.mapMarkers : [];
    mapMarkers.forEach(marker => {
        const color = getMarkerColor(marker);
        const textColor = marker.type === 'start' ? '#1f2937' : '#ffffff';
        const label = `<span style="background-color: ${color}; color: ${textColor}; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; white-space: nowrap;">${marker.label || ''}</span>`;
        const icon = buildMarkerIcon(color);
        const tmapMarker = new Tmapv2.Marker({
            position: new Tmapv2.LatLng(marker.lat, marker.lon),
            map,
            icon,
            label
        });
        window.tmapState.overlays.push(tmapMarker);
    });

    const fitPoints = [];
    mapMarkers.forEach(marker => fitPoints.push({ lat: marker.lat, lon: marker.lon }));
    segments.forEach(seg => {
        fitPoints.push({ lat: seg.start.lat, lon: seg.start.lon });
        fitPoints.push({ lat: seg.end.lat, lon: seg.end.lon });
    });
    fitMapToPoints(map, fitPoints);

    document.getElementById('map-modal').classList.add('open');
};

window.closeMap = function () {
    document.getElementById('map-modal').classList.remove('open');
};
