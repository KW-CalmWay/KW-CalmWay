window.togglePref = function (key) {
    if (!window.AppState) return;
    window.AppState.prefs[key] = !window.AppState.prefs[key];
};
