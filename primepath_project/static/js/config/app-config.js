/**
 * Application Configuration Module
 * Provides centralized access to Django template variables
 * and application configuration
 */

(function(window) {
    'use strict';

    // Create namespace if it doesn't exist
    window.PrimePath = window.PrimePath || {};

    /**
     * Configuration manager for the application
     * Accesses configuration injected by Django templates
     */
    class AppConfig {
        constructor() {
            // Get configuration from window.APP_CONFIG
            // This is injected by Django templates
            this.config = window.APP_CONFIG || {};
            
            // Log initialization status (only in debug mode)
            if (this.isDebugMode()) {
                if (this.config && Object.keys(this.config).length > 0) {
// REMOVED:                     console.log('AppConfig initialized with configuration');
                } else {
                    console.warn('AppConfig initialized without configuration - APP_CONFIG may not be set yet');
                }
            }
        }

        /**
         * Check if we're in debug mode
         * @returns {boolean} True if in debug mode
         */
        isDebugMode() {
            // Check multiple sources for debug status
            if (this.config && this.config.debug !== undefined) {
                return this.config.debug;
            }
            
            // Fallback: check if hostname is localhost or contains 'dev'
            return window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname.includes('dev') ||
                   window.location.search.includes('debug=true');
        }

        /**
         * Get CSRF token for AJAX requests
         * @returns {string} CSRF token
         */
        getCsrfToken() {
            // Try multiple sources for CSRF token
            if (this.config.csrf) {
                return this.config.csrf;
            }
            
            // Try meta tag
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            if (metaTag) {
                return metaTag.getAttribute('content');
            }
            
            // Try cookie (Django default)
            const cookieValue = this.getCookie('csrftoken');
            if (cookieValue) {
                return cookieValue;
            }
            
            console.warn('CSRF token not found');
            return '';
        }

        /**
         * Get cookie value by name
         * @param {string} name Cookie name
         * @returns {string|null} Cookie value or null
         */
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        /**
         * Get exam configuration
         * @returns {Object} Exam configuration
         */
        getExamConfig() {
            return this.config.exam || {};
        }

        /**
         * Get session configuration
         * @returns {Object} Session configuration
         */
        getSessionConfig() {
            return this.config.session || {};
        }

        /**
         * Get URL by key
         * @param {string} key URL key
         * @param {Object} params Parameters to replace in URL
         * @returns {string} Formatted URL
         */
        getUrl(key, params = {}) {
            const urls = this.config.urls || {};
            let url = urls[key] || '';
            
            // Replace parameters in URL
            Object.keys(params).forEach(param => {
                url = url.replace(`{${param}}`, params[param]);
            });
            
            return url;
        }

        /**
         * Get questions data
         * @returns {Array} Questions array
         */
        getQuestions() {
            return this.config.questions || [];
        }

        /**
         * Get specific configuration value
         * @param {string} path Dot-separated path (e.g., 'exam.id')
         * @returns {*} Configuration value
         */
        get(path) {
            const keys = path.split('.');
            let value = this.config;
            
            for (const key of keys) {
                if (value && typeof value === 'object') {
                    value = value[key];
                } else {
                    return undefined;
                }
            }
            
            return value;
        }

        /**
         * Check if configuration exists
         * @param {string} path Dot-separated path
         * @returns {boolean} True if exists
         */
        has(path) {
            return this.get(path) !== undefined;
        }
    }

    // Create singleton instance
    window.PrimePath.config = new AppConfig();
    
    // Also export the class for creating new instances
    window.PrimePath.config.AppConfig = AppConfig;

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = AppConfig;
    }

})(window);