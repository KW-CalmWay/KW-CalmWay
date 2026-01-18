// 탭 전환: 콘텐츠/네비 활성 상태 동기화
window.switchTab = function (tabId, btnElement) {
    document.querySelectorAll('.tab-content')
        .forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');

    document.querySelectorAll('.nav-item')
        .forEach(el => el.classList.remove('active'));
    btnElement.classList.add('active');

    if (tabId === 'analysis') {
        applyFilter();
    }
};

// 초기 렌더링: 경로 목록과 그래프 필터 적용
window.onload = function () {
    renderRoutes();
    applyFilter();
};
