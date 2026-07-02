// Main application logic

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const currentPath = window.location.pathname;

    // Public pages (no auth required)
    const publicPages = ['/', '/login', '/register'];

    // Private pages (auth required)
    const privatePages = ['/dashboard', '/transactions', '/advisor', '/settings'];

    if (publicPages.includes(currentPath)) {
        if (token) {
            // If logged in and on public page, redirect to dashboard
            window.location.href = '/dashboard';
        }
    } else if (privatePages.includes(currentPath)) {
        if (!token) {
            // If not logged in and on private page, redirect to login
            window.location.href = '/login';
        }
    }
});

// Global logout function
function logout() {
    localStorage.clear();
    window.location.href = '/login';
}

// Format currency
function formatMoney(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format month string
function formatMonth(date) {
    return new Date(date).toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long'
    });
}
