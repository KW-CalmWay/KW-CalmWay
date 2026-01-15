window.switchTab = function (tabId, btnElement) {
    document.querySelectorAll('.tab-content')
        .forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');

    document.querySelectorAll('.nav-item')
        .forEach(el => el.classList.remove('active'));
    btnElement.classList.add('active');

    if (tabId === 'analysis') {
        updateChartType(window.currentChartType);
    }
};

window.onload = function () {
    renderRoutes();
    updateChartType('time');
};
