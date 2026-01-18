window.routesData = [];

const routeList = document.getElementById('route-list');
const startInput = document.getElementById('start-input');
const endInput = document.getElementById('end-input');
const departInput = document.getElementById('depart-dt');
const startResults = document.getElementById('start-results');
const endResults = document.getElementById('end-results');

window.currentSortMode = 'crowd';

const searchState = {
    start: { selected: null, timer: null },
    end: { selected: null, timer: null },
    lastSearch: { startName: '', endName: '', departTime: '' }
};

function setDepartNow() {
    if (!departInput) return;
    const now = new Date();
    const pad = value => String(value).padStart(2, '0');
    const local = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
    departInput.value = local;
}

function clearResults(container) {
    if (!container) return;
    container.innerHTML = '';
    container.classList.add('hidden');
}

function renderResults(container, items, onSelect) {
    if (!container) return;
    container.innerHTML = '';
    if (!items.length) {
        container.classList.add('hidden');
        return;
    }

    items.forEach(item => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'w-full text-left px-3 py-2 hover:bg-gray-50';
        btn.innerHTML = `
            <div class="text-sm font-semibold text-gray-800">${item.name}</div>
            <div class="text-[10px] text-gray-500">${item.address || ''}</div>
        `;
        btn.addEventListener('click', () => onSelect(item));
        container.appendChild(btn);
    });

    container.classList.remove('hidden');
}

function setSelected(targetKey, item) {
    searchState[targetKey].selected = item;
    if (targetKey === 'start' && startInput) {
        startInput.value = item.name;
    }
    if (targetKey === 'end' && endInput) {
        endInput.value = item.name;
    }
    if (targetKey === 'start') {
        clearResults(startResults);
    } else {
        clearResults(endResults);
    }
}

function parseCoordPair(text) {
    const match = text.match(/(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)/);
    if (!match) return null;
    return { x: match[1], y: match[2] };
}

function formatSearchDttm(value) {
    if (!value) return '';
    const digits = value.replace(/\D/g, '');
    return digits.slice(0, 12);
}

function formatDepartLabel(value) {
    if (!value) return '';
    if (value.includes('T')) {
        return value.replace('T', ' ').slice(0, 16);
    }
    return value;
}

function formatDuration(totalMinutes) {
    if (!Number.isFinite(totalMinutes)) return '';
    const hours = Math.floor(totalMinutes / 60);
    const mins = totalMinutes % 60;
    if (hours > 0) {
        return `${hours}시간 ${mins}분`;
    }
    return `${mins}분`;
}

const DEFAULT_LINE_COLOR = '#9ca3af';
const SUBWAY_LINE_COLORS = {
    '1': '#0052a4',
    '2': '#00a84d',
    '3': '#ef7c1c',
    '4': '#00a5de',
    '5': '#996cac',
    '6': '#cd7c2f',
    '7': '#747f00',
    '8': '#e6186c',
    '9': '#bdb092'
};
const BUS_COLORS = {
    trunk: '#2b6cb0',
    branch: '#4caf50',
    express: '#e53935',
    circulation: '#f4b400',
    night: '#1e3a8a'
};

function getBusColor(line) {
    const raw = String(line || '').trim();
    if (!raw) return BUS_COLORS.branch;

    const upper = raw.toUpperCase();
    if (raw.includes('심야') || upper.startsWith('N')) return BUS_COLORS.night;
    if (raw.includes('광역')) return BUS_COLORS.express;
    if (raw.includes('간선')) return BUS_COLORS.trunk;
    if (raw.includes('지선')) return BUS_COLORS.branch;
    if (raw.includes('순환')) return BUS_COLORS.circulation;

    const match = raw.match(/\d+/);
    if (!match) return BUS_COLORS.branch;
    const num = Number.parseInt(match[0], 10);
    if (!Number.isFinite(num)) return BUS_COLORS.branch;
    if (num < 10) return BUS_COLORS.circulation;
    if (num >= 900) return BUS_COLORS.express;
    if (num >= 1000) return BUS_COLORS.branch;
    return BUS_COLORS.trunk;
}

function getLineColor(stop) {
    if (!stop) return DEFAULT_LINE_COLOR;
    if (stop.type === 'walk') return DEFAULT_LINE_COLOR;
    if (stop.type === 'bus') return getBusColor(stop.line);
    if (stop.type === 'subway') {
        return SUBWAY_LINE_COLORS[stop.line] || DEFAULT_LINE_COLOR;
    }
    return DEFAULT_LINE_COLOR;
}

function getSegmentLineColor(line, type) {
    const raw = String(line || '').trim();
    const resolvedType = type ? String(type).trim() : '';
    if (!raw || raw === 'walk' || resolvedType === 'walk') return DEFAULT_LINE_COLOR;
    if (resolvedType === 'subway' || raw.includes('호선') || raw.includes('수도권')) {
        const match = raw.match(/\d+/);
        if (match) return SUBWAY_LINE_COLORS[match[0]] || DEFAULT_LINE_COLOR;
        return DEFAULT_LINE_COLOR;
    }
    return getBusColor(raw);
}

window.getLineColor = getLineColor;
window.getSegmentLineColor = getSegmentLineColor;

function getStopLabel(stop) {
    if (!stop) return '';

    if (stop.type === 'subway') {
        return `${stop.line}호선`;
    }

    if (stop.type === 'bus') {
        if (!stop.line) return '버스';

        const parts = String(stop.line).split(':');
        if (parts.length === 2) {
            const [kind, num] = parts;
            return `버스 · ${num}`;
        }

        return `버스 · ${stop.line}`;
    }

    if (stop.type === 'walk') return '도보';

    return stop.type || '';
}


function normalizeStopName(stop) {
    if (!stop || !stop.name) return '';
    const name = String(stop.name);
    if (stop.type === 'subway') {
        return name.endsWith('역') ? name : `${name}역`;
    }
    return name;
}

async function fetchPoiResults(targetKey, query) {
    const container = targetKey === 'start' ? startResults : endResults;
    try {
        const data = await Api.post('/api/poi/search', { query, count: 5 });
        const items = data && Array.isArray(data.items) ? data.items : [];
        renderResults(container, items, item => setSelected(targetKey, item));
    } catch (err) {
        console.error(err);
        clearResults(container);
    }
}

function scheduleSearch(targetKey, query) {
    const state = searchState[targetKey];
    if (state.timer) {
        clearTimeout(state.timer);
    }

    if (query.length < 2) {
        clearResults(targetKey === 'start' ? startResults : endResults);
        return;
    }

    state.timer = setTimeout(() => {
        fetchPoiResults(targetKey, query);
    }, 300);
}

async function resolveCoordFromInput(targetKey, value) {
    const selected = searchState[targetKey].selected;
    if (selected && selected.name === value) {
        return { coord: { x: String(selected.lon), y: String(selected.lat) }, name: selected.name };
    }

    const direct = parseCoordPair(value);
    if (direct) {
        return { coord: direct, name: value };
    }

    const data = await Api.post('/api/poi/search', { query: value, count: 1 });
    const item = data && Array.isArray(data.items) ? data.items[0] : null;
    if (!item) return null;

    return { coord: { x: String(item.lon), y: String(item.lat) }, name: item.name };
}

if (startInput) {
    startInput.addEventListener('input', () => {
        searchState.start.selected = null;
        scheduleSearch('start', startInput.value.trim());
    });
    startInput.addEventListener('focus', () => {
        const value = startInput.value.trim();
        if (value.length >= 2) scheduleSearch('start', value);
    });
}

if (endInput) {
    endInput.addEventListener('input', () => {
        searchState.end.selected = null;
        scheduleSearch('end', endInput.value.trim());
    });
    endInput.addEventListener('focus', () => {
        const value = endInput.value.trim();
        if (value.length >= 2) scheduleSearch('end', value);
    });
}

setDepartNow();

window.onClickSearch = async function () {
    const startValue = startInput ? startInput.value.trim() : '';
    const endValue = endInput ? endInput.value.trim() : '';

    if (!startValue) {
        alert('출발지를 입력해주세요.');
        return;
    }
    if (!endValue) {
        alert('도착지를 입력해주세요.');
        return;
    }

    let startResolved;
    let endResolved;

    try {
        startResolved = await resolveCoordFromInput('start', startValue);
        if (!startResolved) {
            alert('출발지를 찾을 수 없습니다.');
            return;
        }
        endResolved = await resolveCoordFromInput('end', endValue);
        if (!endResolved) {
            alert('도착지를 찾을 수 없습니다.');
            return;
        }
    } catch (err) {
        console.error(err);
        alert('장소 검색에 실패했습니다.');
        return;
    }

    const departLabel = formatDepartLabel(departInput ? departInput.value : '');
    searchState.lastSearch = {
        startName: startResolved.name,
        endName: endResolved.name,
        departTime: departLabel
    };

    const searchDttm = formatSearchDttm(departInput ? departInput.value : '');

    const payload = {
        startX: startResolved.coord.x,
        startY: startResolved.coord.y,
        endX: endResolved.coord.x,
        endY: endResolved.coord.y,
        count: 5,
        lang: 0,
        format: 'json'
    };

    if (searchDttm) {
        payload.searchDttm = searchDttm;
    }

    try {
        const data = await Api.post('/api/routes', payload);
        if (data && Array.isArray(data.routes) && data.routes.length) {
            window.routesData = data.routes;
            renderRoutes();
        } else {
            alert('경로 결과가 없습니다.');
        }
    } catch (err) {
        console.error(err);
        alert('경로 조회에 실패했습니다.');
    }
};

window.setSortMode = function (mode, btnElement) {
    window.currentSortMode = mode;
    document.querySelectorAll('.sort-chip').forEach(el => el.classList.remove('active'));
    btnElement.classList.add('active');
    renderRoutes();
};

function normalizeCrowdScore(value) {
    if (value === null || value === undefined || value === '') return null;

    if (typeof value === 'string') {
        const cleaned = value.replace(/[^\d.-]/g, '');
        value = cleaned;
    }
    const score = Number(value);
    if (!Number.isFinite(score)) return null;
    return score;
}


function getCrowdBadge(score) {
    // null/undefined/NaN => 혼잡도 없음 배지
    if (score === null || score === undefined || !Number.isFinite(score) || score < 0) {
        return `<span class="crowd-none text-[10px] px-2 py-0.5 rounded-full font-bold bg-gray-200 text-gray-600">혼잡도 데이터 없음</span>`;
    }

    const rounded = Math.round(score);

    if (rounded >= 80) return `<span class="crowd-high text-[10px] px-2 py-0.5 rounded-full font-bold">혼잡도 ${rounded}%</span>`;
    if (rounded >= 40) return `<span class="crowd-medium text-[10px] px-2 py-0.5 rounded-full font-bold">혼잡도 ${rounded}%</span>`;
    return `<span class="crowd-low text-[10px] px-2 py-0.5 rounded-full font-bold">혼잡도 ${rounded}%</span>`;
}


function getSearchMetaText() {
    const meta = searchState.lastSearch;
    if (!meta.startName || !meta.endName) return '';
    const base = `${meta.startName} → ${meta.endName}`;
    if (!meta.departTime) return base;
    return `${base} · ${meta.departTime} 출발`;
}

function renderRouteCards(routes, metaText) {
    const metaBlock = metaText
        ? `<div class="text-[11px] text-gray-500 mb-2">${metaText}</div>`
        : '';

    return routes.map((route, index) => {
        const isTop = index === 0;
        const borderClass = isTop ? 'border-2 border-blue-500' : 'border border-gray-100';
        const topPaddingClass = isTop ? 'pt-6' : '';

        const pathVisuals = (route.pathDisplay || []).map((stop, i) => {
            const isLast = i === route.pathDisplay.length - 1;
            const lineColor = getLineColor(stop);
            const label = getStopLabel(stop);
            const stopName = normalizeStopName(stop);
            return `
                <div class="flex items-start">
                    <div class="flex flex-col items-center mr-2">
                        <div class="w-2.5 h-2.5 rounded-full" style="background-color: ${lineColor};"></div>
                        ${!isLast ? '<div class="w-px h-5 bg-gray-200 mt-1"></div>' : ''}
                    </div>
                    <div class="flex flex-col">
                        <span class="text-xs font-semibold text-gray-800">${stopName}</span>
                        ${label ? `<span class="text-[10px] text-gray-400">${label}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        const crowdScore = normalizeCrowdScore(route.crowdScore);

        return `
        <div onclick="openMap(${route.id})" class="bg-white ${borderClass} ${topPaddingClass} rounded-xl p-4 shadow-sm relative overflow-hidden transition-transform active:scale-95 cursor-pointer hover:shadow-md">
            ${isTop ? `<div class="absolute top-0 right-0 bg-blue-500 text-white text-[10px] px-2 py-1 rounded-bl-lg font-bold">추천 1순위</div>` : ''}

            <div class="flex justify-between items-start mb-3">
                <div class="flex items-center">
                    <span class="text-2xl font-bold text-gray-800 mr-2">${formatDuration(route.totalTime)}</span>
                    ${getCrowdBadge(crowdScore)}
                </div>
                <div class="text-right">
                    <div class="text-sm font-bold text-gray-800">${route.arrivalTime} 도착</div>
                    <div class="text-xs text-gray-400">${route.fare}원</div>
                </div>
            </div>

            ${metaBlock}

            <div class="flex flex-col gap-2 mb-3 bg-gray-50 p-2 rounded-lg">
                ${pathVisuals}
            </div>

            <div class="flex items-center text-xs text-gray-500 justify-between border-t border-gray-100 pt-2">
                <div><i class="fas fa-walking mr-1"></i>도보 ${route.walkTime}분</div>
                <div><i class="fas fa-exchange-alt mr-1"></i>환승 ${route.transferCount}회</div>
                <div><i class="fas fa-Won-sign mr-1"></i>${route.fare}</div>
            </div>
        </div>
        `;
    }).join('');
}

window.renderRoutes = function () {
    const allRoutes = [...window.routesData];

    // crowdScore 유효: 숫자이고 0 이상
    const validCrowdRoutes = allRoutes.filter(route => {
        const score = normalizeCrowdScore(route.crowdScore);
        return score !== null && score >= 0;
    });

    const allCrowdMissing = allRoutes.length > 0 && validCrowdRoutes.length === 0;

    // - sortMode=crowd 이고, 일부라도 crowdScore 없으면 → 그 경로 카드는 삭제(=필터링)
    // - 모두 없으면 → "혼잡도 데이터가 없습니다" 표시
    const metaText = getSearchMetaText();
    const crowdNotice = (window.currentSortMode === 'crowd' && allCrowdMissing)
        ? `<div class="text-xs text-gray-500 mb-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">혼잡도 데이터가 없습니다.</div>`
        : '';

    let routesToRender = [];

    if (window.currentSortMode === 'crowd') {
        if (!allCrowdMissing) {
            // 일부라도 유효한 혼잡도가 있으면: 유효한 것만 남기고 정렬
            routesToRender = validCrowdRoutes.sort((a, b) => {
                const aScore = normalizeCrowdScore(a.crowdScore);
                const bScore = normalizeCrowdScore(b.crowdScore);
                return aScore - bScore;
            });
        } else {
            // 전부 없으면: "최소 혼잡"에서는 카드 자체를 보여주지 않음
            routesToRender = [];
        }
    } else if (window.currentSortMode === 'time') {
        routesToRender = allRoutes.sort((a, b) => a.totalTime - b.totalTime);
    } else if (window.currentSortMode === 'transfer') {
        routesToRender = allRoutes.sort((a, b) => a.transferCount - b.transferCount);
    } else if (window.currentSortMode === 'walk') {
        routesToRender = allRoutes.sort((a, b) => a.walkTime - b.walkTime);
    }

    routeList.innerHTML = crowdNotice + renderRouteCards(routesToRender, metaText);
};
