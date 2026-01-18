window.currentLineFilter = 'line1';
window.currentDayFilter = 'weekdays';

// 상위 그래프 이미지 목록 (요일/호선/역)
const TOP_GRAPH_FILES = [
    '/static/images/topGraph/weekdays/line1/1호선_청량리_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_종로5가_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_종로3가_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_종각_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_제기동_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_신설동_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_시청_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_서울역_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_동묘앞_평일.jpg',
    '/static/images/topGraph/weekdays/line1/1호선_동대문_평일.jpg',
    '/static/images/topGraph/weekend/line1/1호선_청량리_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_종로5가_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_종로3가_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_종각_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_제기동_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_신설동_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_시청_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_서울역_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_동묘앞_주말.jpg',
    '/static/images/topGraph/weekend/line1/1호선_동대문_주말.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_신도림_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_선릉_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_홍대입구_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_잠실_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_을지로입구_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_역삼_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_신림_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_구로디지털단지_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_강남_평일.jpg',
    '/static/images/topGraph/weekdays/line2/2호선_삼성_평일.jpg',
    '/static/images/topGraph/weekend/line2/2호선_홍대입구_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_잠실_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_을지로입구_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_역삼_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_신림_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_신도림_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_선릉_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_삼성_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_구로디지털단지_주말.jpg',
    '/static/images/topGraph/weekend/line2/2호선_강남_주말.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_연신내_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_양재_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_압구정_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_안국_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_신사_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_수서_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_남부터미널_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_구파발_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_고속터미널_평일.jpg',
    '/static/images/topGraph/weekdays/line3/3호선_경복궁_평일.jpg',
    '/static/images/topGraph/weekend/line3/3호선_연신내_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_양재_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_압구정_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_안국_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_신사_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_수서_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_남부터미널_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_구파발_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_고속터미널_주말.jpg',
    '/static/images/topGraph/weekend/line3/3호선_경복궁_주말.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_회현_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_혜화_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_충무로_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_창동_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_쌍문_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_수유_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_사당_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_미아사거리_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_명동_평일.jpg',
    '/static/images/topGraph/weekdays/line4/4호선_노원_평일.jpg',
    '/static/images/topGraph/weekend/line4/4호선_회현_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_사당_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_미아사거리_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_명동_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_노원_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_혜화_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_충무로_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_창동_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_쌍문_주말.jpg',
    '/static/images/topGraph/weekend/line4/4호선_수유_주말.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_화곡_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_천호_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_장한평_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_오목교_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_여의도_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_서대문_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_발산_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_미사_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_까치산_평일.jpg',
    '/static/images/topGraph/weekdays/line5/5호선_광화문_평일.jpg',
    '/static/images/topGraph/weekend/line5/5호선_화곡_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_천호_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_장한평_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_오목교_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_여의도_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_서대문_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_발산_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_미사_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_까치산_주말.jpg',
    '/static/images/topGraph/weekend/line5/5호선_광화문_주말.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_합정_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_이태원_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_응암_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_안암_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_석계_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_새절_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_망원_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_마포구청_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_디지털미디어시티_평일.jpg',
    '/static/images/topGraph/weekdays/line6/6호선_공덕_평일.jpg',
    '/static/images/topGraph/weekend/line6/6호선_합정_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_이태원_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_응암_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_안암_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_석계_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_새절_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_망원_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_마포구청_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_디지털미디어시티_주말.jpg',
    '/static/images/topGraph/weekend/line6/6호선_공덕_주말.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_학동_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_하계_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_청담_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_철산_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_상봉_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_논현_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_노원_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_광명사거리_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_고속터미널_평일.jpg',
    '/static/images/topGraph/weekdays/line7/7호선_가산디지털단지_평일.jpg',
    '/static/images/topGraph/weekend/line7/7호선_학동_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_하계_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_청담_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_철산_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_상봉_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_논현_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_노원_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_광명사거리_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_고속터미널_주말.jpg',
    '/static/images/topGraph/weekend/line7/7호선_가산디지털단지_주말.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_천호_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_장지_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_잠실_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_암사_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_송파_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_석촌_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_문정_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_단대오거리_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_남한산성입구_평일.jpg',
    '/static/images/topGraph/weekdays/line8/8호선_강동구청_평일.jpg',
    '/static/images/topGraph/weekend/line8/8호선_천호_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_장지_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_잠실_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_암사_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_송파_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_석촌_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_문정_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_단대오거리_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_남한산성입구_주말.jpg',
    '/static/images/topGraph/weekend/line8/8호선_강동구청_주말.jpg'
];

// 표시 순서 및 라벨 캐시
const LINE_ORDER = ['line1', 'line2', 'line3', 'line4', 'line5', 'line6', 'line7', 'line8'];
const DAY_LABELS = { weekdays: '평일', weekend: '주말' };
const lineLabels = {};
const topGraphIndex = {};
const MAP_LINES = [1, 2, 3, 4, 5, 6, 7, 8];
const MAP_DIRECTIONS = {
    up: '상선',
    down: '하선',
    line2: {
        up: '내선',
        down: '외선'
    }
};

// 파일 경로를 인덱스로 변환
TOP_GRAPH_FILES.forEach(path => {
    const parts = path.split('/');
    const dayKey = parts[4];
    const lineKey = parts[5];
    const filename = parts[6] || '';
    const match = filename.match(/^(\d+호선)_(.+)_(평일|주말)\.jpg$/);
    const lineLabel = match ? match[1] : lineKey;
    const station = match ? match[2] : filename.replace('.jpg', '');

    if (!topGraphIndex[lineKey]) {
        topGraphIndex[lineKey] = { weekdays: [], weekend: [] };
    }
    if (!lineLabels[lineKey]) {
        lineLabels[lineKey] = lineLabel;
    }
    if (topGraphIndex[lineKey][dayKey]) {
        topGraphIndex[lineKey][dayKey].push({ path, station });
    }
});

// 필터 변경 시 목록 재렌더
window.applyFilter = function () {
    window.currentLineFilter = document.getElementById('line-filter').value;
    window.currentDayFilter = document.getElementById('day-filter').value;
    renderTopGraphs();
};

// 그래프 이미지 모달 열기
window.openGraphModal = function (src, alt) {
    const modal = document.getElementById('graph-modal');
    const image = document.getElementById('graph-modal-image');
    if (!modal || !image) {
        return;
    }
    image.src = src;
    image.alt = alt || '';
    modal.classList.remove('hidden');
};

// 그래프 이미지 모달 닫기
window.closeGraphModal = function () {
    const modal = document.getElementById('graph-modal');
    const image = document.getElementById('graph-modal-image');
    if (image) {
        image.src = '';
        image.alt = '';
    }
    if (modal) {
        modal.classList.add('hidden');
    }
};

// 필터 기준으로 카드 목록 구성
window.renderTopGraphs = function () {
    const lineFilter = window.currentLineFilter;
    const dayFilter = window.currentDayFilter;
    const container = document.getElementById('top-graph-list');
    const emptyEl = document.getElementById('top-graph-empty');
    const summaryEl = document.getElementById('top-graph-summary');

    container.innerHTML = '';

    const orderedLines = LINE_ORDER.filter(key => topGraphIndex[key]);
    const extraLines = Object.keys(topGraphIndex).filter(key => !LINE_ORDER.includes(key));
    const linesToShow = lineFilter === 'all' ? [...orderedLines, ...extraLines] : [lineFilter];
    let totalItems = 0;

    linesToShow.forEach(lineKey => {
        const lineData = topGraphIndex[lineKey];
        if (!lineData) {
            return;
        }

        const items = lineData[dayFilter] || [];
        if (!items.length) {
            return;
        }

        totalItems += items.length;

        if (lineFilter === 'all') {
            const header = document.createElement('div');
            header.className = 'col-span-2 text-xs font-semibold text-gray-600 mt-2';
            header.textContent = lineLabels[lineKey] || lineKey;
            container.appendChild(header);
        }

        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'top-graph-card bg-white rounded-lg border border-gray-100 shadow-sm overflow-hidden cursor-pointer';
            card.addEventListener('click', () => {
                window.openGraphModal(item.path, item.station);
            });

            const img = document.createElement('img');
            img.src = item.path;
            img.alt = item.station;
            img.className = 'top-graph-preview';

            const caption = document.createElement('div');
            caption.className = 'p-2 text-[11px] text-gray-600';
            caption.textContent = item.station;

            card.appendChild(img);
            card.appendChild(caption);
            container.appendChild(card);
        });
    });

    if (summaryEl) {
        const dayLabel = DAY_LABELS[dayFilter] || dayFilter;
        if (lineFilter === 'all') {
            summaryEl.textContent = `호선별 상위 10개 그래프 (${dayLabel})`;
        } else {
            const lineLabel = lineLabels[lineFilter] || lineFilter;
            summaryEl.textContent = `${lineLabel} 상위 10개 그래프 (${dayLabel})`;
        }
    }

    if (emptyEl) {
        emptyEl.classList.toggle('hidden', totalItems > 0);
    }
};

function buildMapPath(line, direction) {
    return `/static/data/mapHtml/${direction}/map${line}${direction}.html`;
}

function getLineLabel(line) {
    return lineLabels[`line${line}`] || `${line}호선`;
}

function getDirectionLabel(line, direction) {
    if (line === 2 && MAP_DIRECTIONS.line2) {
        return MAP_DIRECTIONS.line2[direction] || direction;
    }
    return MAP_DIRECTIONS[direction] || direction;
}

window.setAnalysisView = function (view, btnElement) {
    const graphPanel = document.getElementById('analysis-graphs-panel');
    const mapPanel = document.getElementById('analysis-maps-panel');
    document.querySelectorAll('.analysis-toggle').forEach(el => el.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }
    if (view === 'maps') {
        if (graphPanel) graphPanel.classList.add('hidden');
        if (mapPanel) mapPanel.classList.remove('hidden');
    } else {
        if (mapPanel) mapPanel.classList.add('hidden');
        if (graphPanel) graphPanel.classList.remove('hidden');
    }
};

window.openAnalysisMapModal = function (line, direction) {
    const modal = document.getElementById('analysis-map-modal');
    const frame = document.getElementById('analysis-map-frame');
    const title = document.getElementById('analysis-map-modal-title');
    if (!modal || !frame) return;
    const dirLabel = getDirectionLabel(line, direction);
    const lineLabel = getLineLabel(line);
    if (title) {
        title.textContent = `${lineLabel} ${dirLabel} 혼잡도 지도`;
    }
    frame.src = buildMapPath(line, direction);
    modal.classList.remove('hidden');
};

window.closeAnalysisMapModal = function () {
    const modal = document.getElementById('analysis-map-modal');
    const frame = document.getElementById('analysis-map-frame');
    const title = document.getElementById('analysis-map-modal-title');
    if (frame) {
        frame.src = '';
    }
    if (title) {
        title.textContent = '';
    }
    if (modal) {
        modal.classList.add('hidden');
    }
};

window.renderMapCards = function () {
    const container = document.getElementById('analysis-map-list');
    if (!container) return;
    container.innerHTML = '';

    MAP_LINES.forEach(line => {
        const card = document.createElement('div');
        card.className = 'bg-gray-50 border border-gray-200 rounded-lg p-3 flex flex-col gap-2';

        const header = document.createElement('div');
        header.className = 'text-xs font-semibold text-gray-700';
        header.textContent = getLineLabel(line);

        const buttonRow = document.createElement('div');
        buttonRow.className = 'grid grid-cols-2 gap-2';

        const upBtn = document.createElement('button');
        upBtn.type = 'button';
        upBtn.className = 'text-xs font-semibold py-2 rounded-lg border border-blue-200 text-blue-600 bg-white hover:bg-blue-50';
        upBtn.textContent = `${getDirectionLabel(line, 'up')} 지도`;
        upBtn.addEventListener('click', () => window.openAnalysisMapModal(line, 'up'));

        const downBtn = document.createElement('button');
        downBtn.type = 'button';
        downBtn.className = 'text-xs font-semibold py-2 rounded-lg border border-gray-200 text-gray-600 bg-white hover:bg-gray-50';
        downBtn.textContent = `${getDirectionLabel(line, 'down')} 지도`;
        downBtn.addEventListener('click', () => window.openAnalysisMapModal(line, 'down'));

        buttonRow.appendChild(upBtn);
        buttonRow.appendChild(downBtn);

        card.appendChild(header);
        card.appendChild(buttonRow);
        container.appendChild(card);
    });
};

window.renderMapCards();
