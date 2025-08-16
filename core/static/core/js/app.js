/* Maieutix Application JavaScript */

// Global configuration
window.Maieutix = {
    config: {
        theme: {
            primary: '#2D4B73',
            secondary: '#253C59',
            accent: '#99B4BF',
            highlight: '#D9BA23',
            warning: '#BF8D30'
        }
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Maieutix application initialized');
    
    // Initialize HTMX custom configurations if needed
    if (window.htmx) {
        // HTMX event listeners
        document.body.addEventListener('htmx:beforeRequest', function(event) {
            console.log('HTMX request starting', event.detail);
        });
        
        document.body.addEventListener('htmx:afterRequest', function(event) {
            console.log('HTMX request completed', event.detail);
        });
    }
    
    // Initialize Alpine.js components
    if (window.Alpine) {
        console.log('Alpine.js is available');
    }
});

// Utility functions
window.Maieutix.utils = {
    // Show notification
    notify: function(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // TODO: Implement proper notification system
    },
    
    // Confirm dialog
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Format date
    formatDate: function(date) {
        return new Intl.DateTimeFormat('fr-FR').format(new Date(date));
    }
};