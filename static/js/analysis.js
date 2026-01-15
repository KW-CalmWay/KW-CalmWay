window.chartInstance = null;
window.currentChartType = 'time';
window.currentFilter = 'all';

const chartDataSets = {
    time: {
        label: '시간대별 평균 혼잡도',
        labels: ['07시', '09시', '12시', '15시', '18시', '20시', '23시'],
        data: {
            all: [60, 85, 40, 50, 95, 60, 30],
            line1: [65, 90, 45, 55, 98, 65, 35],
            line2: [70, 95, 50, 60, 99, 70, 40],
            line3: [60, 85, 40, 50, 90, 60, 30],
            line4: [65, 88, 45, 55, 95, 65, 35],
            line5: [55, 80, 35, 45, 85, 55, 25],
            line6: [50, 75, 30, 40, 80, 50, 20],
            line7: [60, 85, 40, 50, 92, 60, 30],
            line8: [55, 80, 35, 45, 88, 55, 25],
            line9: [75, 98, 55, 65, 100, 75, 45],
            airport: [40, 60, 30, 40, 70, 50, 20],
            gyeongui: [50, 70, 35, 45, 80, 55, 25],
            bundang: [55, 75, 40, 50, 85, 60, 30]
        }
    },
    day: {
        label: '요일별 평균 혼잡도',
        labels: ['월', '화', '수', '목', '금', '토', '일'],
        data: {
            all: [75, 76, 74, 78, 85, 60, 40]
        }
    },
    top: {
        label: '상위 10개 혼잡역 (필터 미적용)',
        labels: ['강남', '잠실', '홍대입구', '신림', '구로디지털', '역삼', '고속터미널', '서울역', '신도림', '삼성'],
        data: {
            all: [98, 95, 93, 91, 90, 88, 87, 86, 85, 84]
        }
    }
};

const allKeys = ['line1', 'line2', 'line3', 'line4', 'line5', 'line6', 'line7', 'line8', 'line9', 'airport', 'gyeongui', 'bundang'];
allKeys.forEach(key => {
    chartDataSets.day.data[key] = chartDataSets.day.data.all.map(v => Math.min(100, Math.max(10, v + (Math.random() * 10 - 5))));
});

window.applyFilter = function () {
    window.currentFilter = document.getElementById('line-filter').value;
    renderChart(window.currentChartType);
};

window.updateChartType = function (type) {
    window.currentChartType = type;

    const btns = ['btn-chart-time', 'btn-chart-day', 'btn-chart-top'];
    btns.forEach(id => {
        const el = document.getElementById(id);
        if (id === 'btn-chart-' + type) {
            el.classList.remove('text-gray-500', 'hover:text-gray-700', 'bg-white');
            el.classList.add('bg-white', 'text-blue-600', 'shadow-sm', 'font-bold');
        } else {
            el.classList.remove('bg-white', 'text-blue-600', 'shadow-sm', 'font-bold');
            el.classList.add('text-gray-500', 'hover:text-gray-700');
        }
    });

    const filterEl = document.getElementById('line-filter');
    if (type === 'top') {
        filterEl.disabled = true;
        filterEl.classList.add('opacity-50', 'bg-gray-100');
        document.getElementById('chart-desc').innerText = '상위 10개 혼잡역은 필터와 관계없이 전체 데이터 기준입니다.';
    } else {
        filterEl.disabled = false;
        filterEl.classList.remove('opacity-50', 'bg-gray-100');
        document.getElementById('chart-desc').innerText = type === 'time' ?
            '퇴근 시간대(18~19시) 평균 혼잡도가 가장 높게 예측됩니다.' :
            '금요일 오후 시간대가 가장 혼잡한 것으로 분석됩니다.';
    }

    renderChart(type);
};

function renderChart(type) {
    const ctx = document.getElementById('congestionChart').getContext('2d');
    const dataSet = chartDataSets[type];

    const displayData = type === 'top' ? dataSet.data.all : dataSet.data[window.currentFilter];

    if (window.chartInstance) window.chartInstance.destroy();

    const isBar = type === 'top' || type === 'day';
    const bgColor = displayData.map(val => val >= 80 ? 'rgba(239, 68, 68, 0.7)' : 'rgba(59, 130, 246, 0.7)');

    window.chartInstance = new Chart(ctx, {
        type: isBar ? 'bar' : 'line',
        data: {
            labels: dataSet.labels,
            datasets: [{
                label: '혼잡도 (%)',
                data: displayData,
                borderColor: '#2563eb',
                backgroundColor: isBar ? bgColor : 'rgba(37, 99, 235, 0.1)',
                borderWidth: isBar ? 0 : 2,
                tension: 0.4,
                fill: !isBar,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: type === 'top' ? 'y' : 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { display: type !== 'top' },
                    ticks: { display: type !== 'top' }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } },
                    max: 100
                }
            }
        }
    });
}
