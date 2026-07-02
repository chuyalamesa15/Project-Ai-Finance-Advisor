/* API helper functions */

const API_BASE = '';

export async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        }
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}

export async function login(email, password) {
    return apiCall('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
}

export async function register(userData) {
    return apiCall('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}

export async function getCurrentUser() {
    return apiCall('/api/auth/me');
}

export async function getTransactions(filters = {}) {
    const params = new URLSearchParams(filters);
    return apiCall(`/api/transactions?${params}`);
}

export async function addTransaction(transaction) {
    return apiCall('/api/transactions', {
        method: 'POST',
        body: JSON.stringify(transaction)
    });
}

export async function updateTransaction(id, transaction) {
    return apiCall(`/api/transactions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(transaction)
    });
}

export async function deleteTransaction(id) {
    return apiCall(`/api/transactions/${id}`, {
        method: 'DELETE'
    });
}

export async function getFinancialSummary(month = null) {
    const params = month ? `?month=${month}` : '';
    return apiCall(`/api/metrics/summary${params}`);
}

export async function getCategoryBreakdown(filters = {}) {
    const params = new URLSearchParams(filters);
    return apiCall(`/api/metrics/category-breakdown?${params}`);
}

export async function getMonthlyTrend() {
    return apiCall('/api/metrics/monthly-trend');
}

export async function getFinancialAdvice(question) {
    return apiCall('/api/advisor/advice', {
        method: 'POST',
        body: JSON.stringify({ question })
    });
}

export async function updateApiKey(apiKey) {
    return apiCall('/api/metrics/update-api-key', {
        method: 'POST',
        body: JSON.stringify({ api_key: apiKey })
    });
}

export function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

export function formatDate(date) {
    return new Date(date).toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}
