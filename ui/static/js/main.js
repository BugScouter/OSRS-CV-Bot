/**
 * OSRS Bot Manager UI - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar toggle
    initializeSidebarToggle();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize color pickers
    initializeColorPickers();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize server status monitoring
    initializeServerStatusMonitoring();
});

/**
 * Initialize sidebar toggle functionality
 */
function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');
    
    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener('click', function() {
            wrapper.classList.toggle('toggled');
        });
    }
}

/**
 * Initialize color picker functionality for RGB parameters
 */
function initializeColorPickers() {
    const rgbInputs = document.querySelectorAll('input[type="number"][name$="_r"], input[type="number"][name$="_g"], input[type="number"][name$="_b"]');
    
    rgbInputs.forEach(input => {
        input.addEventListener('input', function() {
            updateColorPreview(this);
        });
    });
}

/**
 * Update color preview when RGB values change
 */
function updateColorPreview(input) {
    const name = input.name;
    const paramName = name.substring(0, name.lastIndexOf('_'));
    
    const rInput = document.querySelector(`input[name="${paramName}_r"]`);
    const gInput = document.querySelector(`input[name="${paramName}_g"]`);
    const bInput = document.querySelector(`input[name="${paramName}_b"]`);
    const colorInput = document.querySelector(`input[name="${paramName}_color"]`);
    const preview = document.querySelector(`[data-param="${paramName}"] .color-preview`);
    
    if (rInput && gInput && bInput) {
        const r = parseInt(rInput.value) || 0;
        const g = parseInt(gInput.value) || 0;
        const b = parseInt(bInput.value) || 0;
        
        // Update preview background
        if (preview) {
            preview.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        }
        
        // Update color picker
        if (colorInput) {
            const hex = rgbToHex(r, g, b);
            colorInput.value = hex;
        }
    }
}

/**
 * Convert RGB values to hex string
 */
function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

/**
 * Convert hex color to RGB values
 */
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
}

/**
 * Validate form inputs
 */
function validateForm(form) {
    let isValid = true;
    
    // Validate number inputs
    const numberInputs = form.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        const min = parseFloat(input.getAttribute('min'));
        const max = parseFloat(input.getAttribute('max'));
        const value = parseFloat(input.value);
        
        if (!isNaN(min) && value < min) {
            showValidationError(input, `Value must be at least ${min}`);
            isValid = false;
        } else if (!isNaN(max) && value > max) {
            showValidationError(input, `Value must be at most ${max}`);
            isValid = false;
        } else {
            clearValidationError(input);
        }
    });
    
    // Validate range parameters (min < max)
    const rangeParams = form.querySelectorAll('[data-param]');
    rangeParams.forEach(param => {
        const paramName = param.getAttribute('data-param');
        const minInput = param.querySelector(`input[name="${paramName}_min"]`);
        const maxInput = param.querySelector(`input[name="${paramName}_max"]`);
        
        if (minInput && maxInput) {
            const minValue = parseFloat(minInput.value);
            const maxValue = parseFloat(maxInput.value);
            
            if (minValue >= maxValue) {
                showValidationError(maxInput, 'Maximum value must be greater than minimum value');
                isValid = false;
            } else {
                clearValidationError(maxInput);
            }
        }
    });
    
    return isValid;
}

/**
 * Show validation error for an input
 */
function showValidationError(input, message) {
    input.classList.add('is-invalid');
    
    let feedback = input.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.appendChild(feedback);
    }
    
    feedback.textContent = message;
}

/**
 * Clear validation error for an input
 */
function clearValidationError(input) {
    input.classList.remove('is-invalid');
    
    const feedback = input.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

/**
 * Show loading state for an element
 */
function showLoading(element, text = 'Loading...') {
    element.classList.add('loading');
    element.disabled = true;
    
    const originalText = element.textContent;
    element.setAttribute('data-original-text', originalText);
    element.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>${text}`;
}

/**
 * Hide loading state for an element
 */
function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
    
    const originalText = element.getAttribute('data-original-text');
    if (originalText) {
        element.textContent = originalText;
        element.removeAttribute('data-original-text');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Initialize and show toast
    if (typeof bootstrap !== 'undefined') {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    } else {
        // Fallback without Bootstrap
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
}

/**
 * Format time duration in seconds to human readable format
 */
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

/**
 * Debounce function to limit how often a function can be called
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Make an API request with error handling
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showToast(`API Error: ${error.message}`, 'danger');
        throw error;
    }
}

/**
 * Export configuration as JSON file
 */
function exportConfigAsFile(config, filename) {
    const dataStr = JSON.stringify(config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = filename || 'bot_config.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

/**
 * Import configuration from JSON file
 */
function importConfigFromFile(callback) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.style.display = 'none';
    
    input.onchange = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const config = JSON.parse(e.target.result);
                callback(config);
            } catch (error) {
                showToast('Error parsing configuration file: ' + error.message, 'danger');
            }
        };
        reader.readAsText(file);
    };
    
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

/**
 * Initialize server status monitoring
 */
function initializeServerStatusMonitoring() {
    const statusElement = document.getElementById('serverStatus');
    if (!statusElement) return;
    
    let isConnected = true;
    
    function updateServerStatus(connected) {
        const statusText = statusElement.querySelector('.status-text');
        const statusElement_ = statusElement;
        
        if (connected && !isConnected) {
            // Reconnected
            statusElement_.classList.remove('disconnected');
            statusText.textContent = 'UI Server Running';
            isConnected = true;
        } else if (!connected && isConnected) {
            // Disconnected
            statusElement_.classList.add('disconnected');
            statusText.textContent = 'Server Disconnected';
            isConnected = false;
        }
    }
    
    function checkServerStatus() {
        fetch('/api/bots', { method: 'HEAD' })
            .then(response => {
                updateServerStatus(response.ok);
            })
            .catch(() => {
                updateServerStatus(false);
            });
    }
    
    // Check server status every 30 seconds to reduce network traffic
    setInterval(checkServerStatus, 30000);
    
    // Initial check after 1 second
    setTimeout(checkServerStatus, 1000);
}

// Global utility functions
window.BotUI = {
    showLoading,
    hideLoading,
    showToast,
    formatDuration,
    debounce,
    apiRequest,
    exportConfigAsFile,
    importConfigFromFile,
    rgbToHex,
    hexToRgb
};