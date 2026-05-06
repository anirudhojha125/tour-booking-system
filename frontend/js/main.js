/**
 * TourBook - Main JavaScript File
 * Core functionality for the Tour Recommendation & Booking System
 */

// ==========================================
// CONFIGURATION
// ==========================================
const API_BASE_URL = '/api';

// ==========================================
// AUTHENTICATION & NAVIGATION
// ==========================================

// Check if user is logged in and update navigation
function updateNavigation() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const navButtons = document.getElementById('navAuthButtons');
    
    if (!navButtons) return;
    
    if (token && user.role) {
        // User is logged in - show user menu
        let dashboardLink = '';
        if (user.role === 'admin') {
            dashboardLink = '<li><a href="admin-dashboard.html">Admin Dashboard</a></li>';
        } else if (user.role === 'agent') {
            dashboardLink = '<li><a href="agent-dashboard.html">Dashboard</a></li>';
        }
        
        navButtons.innerHTML = `
            <div style="position: relative;">
                <button onclick="toggleUserMenu()" style="display: flex; align-items: center; gap: 10px; background: var(--light); border: none; padding: 10px 20px; border-radius: var(--radius-xl); cursor: pointer; font-weight: 600;">
                    <div style="width: 35px; height: 35px; background: var(--gradient-primary); border-radius: var(--radius-full); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                        ${user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <span>${user.first_name || 'User'}</span>
                    <i class="fas fa-chevron-down" style="font-size: 0.8rem;"></i>
                </button>
                <div id="userMenu" style="display: none; position: absolute; top: 100%; right: 0; margin-top: 10px; background: white; border-radius: var(--radius-md); box-shadow: var(--shadow-lg); min-width: 200px; z-index: 1000;">
                    <div style="padding: 15px 20px; border-bottom: 1px solid var(--gray-lighter);">
                        <p style="font-weight: 600; color: var(--dark);">${user.first_name} ${user.last_name}</p>
                        <p style="font-size: 0.85rem; color: var(--gray);">${user.email}</p>
                    </div>
                    <ul style="list-style: none; padding: 10px 0;">
                        ${user.role === 'traveler' ? `
                            <li><a href="wishlist.html" style="display: block; padding: 10px 20px; color: var(--dark); text-decoration: none; hover: background: var(--light);"><i class="fas fa-heart" style="width: 20px;"></i> My Wishlist</a></li>
                            <li><a href="bookings.html" style="display: block; padding: 10px 20px; color: var(--dark); text-decoration: none;"><i class="fas fa-calendar-check" style="width: 20px;"></i> My Bookings</a></li>
                        ` : ''}
                        ${dashboardLink ? `<li>${dashboardLink.replace('href=', 'style="display: block; padding: 10px 20px; color: var(--dark); text-decoration: none;" href=')}</li>` : ''}
                        <li><a href="#" onclick="logout(); return false;" style="display: block; padding: 10px 20px; color: var(--error-color); text-decoration: none;"><i class="fas fa-sign-out-alt" style="width: 20px;"></i> Logout</a></li>
                    </ul>
                </div>
            </div>
        `;
    } else {
        // User is not logged in - show sign in/up buttons
        navButtons.innerHTML = `
            <a href="login.html" class="btn btn-outline btn-sm">Sign In</a>
            <a href="register.html" class="btn btn-primary btn-sm">Sign Up</a>
        `;
    }
}

// Toggle user menu
function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (menu) {
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
}

// Close user menu when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById('userMenu');
    const button = e.target.closest('button');
    if (menu && menu.style.display === 'block' && !e.target.closest('#userMenu') && !button?.onclick?.toString().includes('toggleUserMenu')) {
        menu.style.display = 'none';
    }
});

// Logout function
async function logout() {
    const token = localStorage.getItem('token');
    
    if (token) {
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================

function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px; padding: 16px 24px; background: ${getToastColor(type)}; color: white; border-radius: var(--radius-md); box-shadow: var(--shadow-lg); position: fixed; top: 90px; right: 20px; z-index: 3000; animation: slideIn 0.3s ease;">
            <i class="fas ${getToastIcon(type)}"></i>
            <span style="font-weight: 500;">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer; margin-left: 10px;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add animation styles
    if (!document.getElementById('toastStyles')) {
        const style = document.createElement('style');
        style.id = 'toastStyles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        const toastEl = toast.querySelector('div');
        if (toastEl) {
            toastEl.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

function getToastColor(type) {
    const colors = {
        success: '#28A745',
        error: '#DC3545',
        warning: '#FFC107',
        info: '#17A2B8'
    };
    return colors[type] || colors.info;
}

function getToastIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format relative time
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' years ago';
    
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' months ago';
    
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' days ago';
    
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' hours ago';
    
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' minutes ago';
    
    return 'Just now';
}

// Generate star rating HTML
function getStarRatingHTML(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let html = '';
    
    for (let i = 0; i < fullStars; i++) {
        html += '<i class="fas fa-star" style="color: var(--accent-color);"></i>';
    }
    if (hasHalfStar) {
        html += '<i class="fas fa-star-half-alt" style="color: var(--accent-color);"></i>';
    }
    for (let i = fullStars + (hasHalfStar ? 1 : 0); i < 5; i++) {
        html += '<i class="far fa-star" style="color: var(--gray-light);"></i>';
    }
    
    return html;
}

// ==========================================
// API HELPERS
// ==========================================

// Make authenticated API request
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });
    
    return response;
}

// ==========================================
// INITIALIZATION
// ==========================================

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateNavigation();
});
