// Global state
let accessToken = localStorage.getItem('accessToken');
let currentUser = localStorage.getItem('currentUser');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    if (accessToken && currentUser) {
        showMainApp();
    } else {
        showAuthSection();
    }
});

// Auth functions
function showLogin() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
}

function showRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
}

async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    setLoading(submitBtn, true);
    
    try {
        console.log('Attempting registration for:', username);
        
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        console.log('Registration response status:', response.status);
        
        const data = await response.json();
        console.log('Registration response data:', data);
        
        if (response.ok) {
            showToast('Account created successfully! Please login.', 'success');
            showLogin();
            document.getElementById('loginUsername').value = username;
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast(`Network error: ${error.message}. Please try again.`, 'error');
    } finally {
        setLoading(submitBtn, false);
    }
}

async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    setLoading(submitBtn, true);
    
    try {
        console.log('Attempting login for:', username);
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/token', {
            method: 'POST',
            body: formData
        });
        
        console.log('Login response status:', response.status);
        
        const data = await response.json();
        console.log('Login response data:', data);
        
        if (response.ok) {
            accessToken = data.access_token;
            currentUser = username;
            
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('currentUser', currentUser);
            
            showToast('Login successful!', 'success');
            showMainApp();
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast(`Network error: ${error.message}. Please try again.`, 'error');
    } finally {
        setLoading(submitBtn, false);
    }
}

function logout() {
    accessToken = null;
    currentUser = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('currentUser');
    
    showAuthSection();
    showToast('Logged out successfully', 'success');
}

// Main app functions
function showAuthSection() {
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('userInfo').style.display = 'none';
}

function showMainApp() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('userInfo').style.display = 'flex';
    document.getElementById('welcomeText').textContent = `Welcome, ${currentUser}!`;
    
    // Reset forms
    resetForm();
}

async function shortenUrl(event) {
    event.preventDefault();
    
    const targetUrl = document.getElementById('targetUrl').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    setLoading(submitBtn, true);
    
    try {
        const response = await fetch('/shorten', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ target_url: targetUrl })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult(data, targetUrl);
            showToast('URL shortened successfully!', 'success');
        } else {
            if (response.status === 401) {
                showToast('Session expired. Please login again.', 'error');
                logout();
            } else {
                showToast(data.detail || 'Failed to shorten URL', 'error');
            }
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        setLoading(submitBtn, false);
    }
}

function displayResult(data, originalUrl) {
    const shortUrl = `${window.location.origin}/${data.short_key}`;
    
    document.getElementById('shortUrl').value = shortUrl;
    document.getElementById('originalUrl').textContent = originalUrl;
    document.getElementById('resultsSection').style.display = 'block';
    
    // Hide the form
    document.querySelector('.shortener-card').style.display = 'none';
}

function resetForm() {
    document.getElementById('targetUrl').value = '';
    document.getElementById('resultsSection').style.display = 'none';
    document.querySelector('.shortener-card').style.display = 'block';
}

async function copyToClipboard() {
    const shortUrl = document.getElementById('shortUrl').value;
    
    try {
        await navigator.clipboard.writeText(shortUrl);
        showToast('URL copied to clipboard!', 'success');
    } catch (error) {
        // Fallback for older browsers
        const input = document.getElementById('shortUrl');
        input.select();
        document.execCommand('copy');
        showToast('URL copied to clipboard!', 'success');
    }
}

// Utility functions
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.classList.add('loading');
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

// Handle browser back/forward
window.addEventListener('popstate', function() {
    if (accessToken && currentUser) {
        showMainApp();
    } else {
        showAuthSection();
    }
});