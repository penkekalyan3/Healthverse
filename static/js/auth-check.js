// Authentication verification check for client-side pages
(function() {
    const userId = localStorage.getItem('hv_user_id');
    const path = window.location.pathname;
    const isAuthPage = path.endsWith('login.html') || path.endsWith('register.html') || path.endsWith('index.html') || path === '/' || path.endsWith('/');

    if (!userId && !isAuthPage) {
        window.location.href = 'login.html';
    } else if (userId && (path.endsWith('login.html') || path.endsWith('register.html'))) {
        window.location.href = 'dashboard.html';
    }
})();
