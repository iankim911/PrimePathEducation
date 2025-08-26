/**
 * Configuration Module for PrimePath
 * Centralizes all configuration and eliminates hardcoding
 * Created: August 26, 2025
 * 
 * This module provides:
 * - Dynamic date/year management
 * - Environment-based URL resolution
 * - Academic year calculations
 * - System-wide constants
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};

    class ConfigService {
        constructor() {
            this.cache = new Map();
            this.cacheTimeout = 3600000; // 1 hour in milliseconds
            
            // Academic year starts in September
            this.ACADEMIC_YEAR_START_MONTH = 9;
            
            // Initialize with server-provided config if available
            this.serverConfig = window.APP_CONFIG || {};
            
            // Debug mode
            this.debugMode = this.serverConfig.DEBUG || false;
            
            this.log('CONFIG', 'Configuration Service initialized');
        }

        /**
         * Get current calendar year
         * @returns {number} Current year
         */
        getCurrentYear() {
            const year = new Date().getFullYear();
            this.log('CONFIG', `Current year resolved: ${year}`);
            return year;
        }

        /**
         * Get current academic year string (e.g., "2025-2026")
         * Academic year runs September to August
         * @returns {string} Academic year string
         */
        getCurrentAcademicYear() {
            const cacheKey = 'academic_year';
            
            if (this.cache.has(cacheKey)) {
                const cached = this.cache.get(cacheKey);
                if (Date.now() - cached.timestamp < this.cacheTimeout) {
                    return cached.value;
                }
            }

            const now = new Date();
            let academicYear;
            
            if (now.getMonth() >= this.ACADEMIC_YEAR_START_MONTH - 1) { // JS months are 0-based
                // September-December: current year - next year
                academicYear = `${now.getFullYear()}-${now.getFullYear() + 1}`;
            } else {
                // January-August: previous year - current year
                academicYear = `${now.getFullYear() - 1}-${now.getFullYear()}`;
            }

            this.cache.set(cacheKey, {
                value: academicYear,
                timestamp: Date.now()
            });

            this.log('CONFIG', `Academic year calculated: ${academicYear}`);
            return academicYear;
        }

        /**
         * Get academic year start
         * @returns {number} Start year of academic year
         */
        getAcademicYearStart() {
            const academicYear = this.getCurrentAcademicYear();
            return parseInt(academicYear.split('-')[0]);
        }

        /**
         * Get academic year end
         * @returns {number} End year of academic year
         */
        getAcademicYearEnd() {
            const academicYear = this.getCurrentAcademicYear();
            return parseInt(academicYear.split('-')[1]);
        }

        /**
         * Get base URL dynamically
         * @returns {string} Base URL
         */
        getBaseUrl() {
            // Priority order:
            // 1. Server-provided config
            // 2. Current window location
            // 3. Default fallback
            
            if (this.serverConfig.base_url) {
                return this.serverConfig.base_url;
            }
            
            const protocol = window.location.protocol;
            const host = window.location.host;
            const baseUrl = `${protocol}//${host}`;
            
            this.log('CONFIG', `Base URL resolved: ${baseUrl}`);
            return baseUrl;
        }

        /**
         * Get API base URL
         * @returns {string} API base URL
         */
        getApiBaseUrl() {
            if (this.serverConfig.api_base_url) {
                return this.serverConfig.api_base_url;
            }
            return `${this.getBaseUrl()}/api`;
        }

        /**
         * Get media URL
         * @returns {string} Media files URL
         */
        getMediaUrl() {
            if (this.serverConfig.media_url) {
                return this.serverConfig.media_url;
            }
            return `${this.getBaseUrl()}/media`;
        }

        /**
         * Get static URL
         * @returns {string} Static files URL
         */
        getStaticUrl() {
            if (this.serverConfig.static_url) {
                return this.serverConfig.static_url;
            }
            return `${this.getBaseUrl()}/static`;
        }

        /**
         * Get timeout values
         * @param {string} key - Timeout type
         * @returns {number} Timeout in seconds
         */
        getTimeout(key = 'default') {
            const timeouts = {
                default: 30,
                api: this.serverConfig.timeouts?.api || 30,
                session: this.serverConfig.timeouts?.session || 1800,
                test_duration: this.serverConfig.timeouts?.test_duration || 7200,
                audio_duration: this.serverConfig.timeouts?.audio_duration || 300,
                file_upload: 120,
            };
            
            const timeout = timeouts[key] || timeouts.default;
            this.log('CONFIG', `Timeout for '${key}': ${timeout} seconds`);
            return timeout;
        }

        /**
         * Get pagination limits
         * @param {string} key - Pagination type
         * @returns {number} Pagination limit
         */
        getPaginationLimit(key = 'default') {
            const limits = {
                default: 20,
                students: this.serverConfig.pagination?.students || 20,
                exams: this.serverConfig.pagination?.exams || 10,
                questions: this.serverConfig.pagination?.questions || 20,
                results: this.serverConfig.pagination?.results || 50,
                api: 100,
            };
            
            const limit = limits[key] || limits.default;
            this.log('CONFIG', `Pagination limit for '${key}': ${limit}`);
            return limit;
        }

        /**
         * Get max file size in MB
         * @param {string} fileType - Type of file
         * @returns {number} Max size in bytes
         */
        getMaxFileSize(fileType = 'default') {
            const sizes = {
                default: 10,
                pdf: 50,
                audio: 100,
                image: 10,
                excel: 20,
                csv: 10,
            };
            
            const sizeMB = sizes[fileType] || sizes.default;
            this.log('CONFIG', `Max file size for '${fileType}': ${sizeMB}MB`);
            return sizeMB * 1024 * 1024; // Return in bytes
        }

        /**
         * Get feature flag
         * @param {string} flagName - Feature flag name
         * @param {boolean} defaultValue - Default value if not found
         * @returns {boolean} Feature flag value
         */
        getFeatureFlag(flagName, defaultValue = false) {
            if (this.serverConfig.features && flagName in this.serverConfig.features) {
                const value = this.serverConfig.features[flagName];
                this.log('CONFIG', `Feature flag '${flagName}': ${value}`);
                return value;
            }
            
            this.log('CONFIG', `Feature flag '${flagName}': ${defaultValue} (default)`);
            return defaultValue;
        }

        /**
         * Validate year value
         * @param {number|string} yearValue - Year to validate
         * @returns {boolean} True if valid
         */
        validateYear(yearValue) {
            try {
                const year = parseInt(yearValue);
                const currentYear = this.getCurrentYear();
                
                // Allow years within reasonable range (past 10 years to next 5 years)
                const minYear = currentYear - 10;
                const maxYear = currentYear + 5;
                
                if (minYear <= year && year <= maxYear) {
                    return true;
                } else {
                    this.log('CONFIG', `Year validation failed: ${year} not in range ${minYear}-${maxYear}`, 'warn');
                    return false;
                }
            } catch (e) {
                this.log('CONFIG', `Year validation failed: Invalid year value ${yearValue}`, 'error');
                return false;
            }
        }

        /**
         * Get environment
         * @returns {string} Current environment
         */
        getEnvironment() {
            if (this.serverConfig.environment) {
                return this.serverConfig.environment;
            }
            
            // Detect based on URL
            const host = window.location.hostname;
            if (host === 'localhost' || host === '127.0.0.1' || host.includes('.local')) {
                return 'development';
            } else if (host.includes('staging') || host.includes('test')) {
                return 'staging';
            } else {
                return 'production';
            }
        }

        /**
         * Format date for API
         * @param {Date} date - Date object
         * @returns {string} Formatted date string
         */
        formatDateForAPI(date = new Date()) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        /**
         * Parse date from API
         * @param {string} dateString - Date string from API
         * @returns {Date} Date object
         */
        parseDateFromAPI(dateString) {
            return new Date(dateString);
        }

        /**
         * Get system constants for debugging
         * @returns {Object} All system constants
         */
        getSystemConstants() {
            return {
                current_year: this.getCurrentYear(),
                academic_year: this.getCurrentAcademicYear(),
                academic_year_start: this.getAcademicYearStart(),
                academic_year_end: this.getAcademicYearEnd(),
                base_url: this.getBaseUrl(),
                api_base_url: this.getApiBaseUrl(),
                environment: this.getEnvironment(),
                timeouts: {
                    api: this.getTimeout('api'),
                    session: this.getTimeout('session'),
                    test_duration: this.getTimeout('test_duration'),
                },
                features: {
                    v2_templates: this.getFeatureFlag('v2_templates'),
                    debug_mode: this.debugMode,
                    allow_audio: this.getFeatureFlag('allow_audio', true),
                    allow_pdf: this.getFeatureFlag('allow_pdf', true),
                }
            };
        }

        /**
         * Clear configuration cache
         */
        clearCache() {
            this.cache.clear();
            this.log('CONFIG', 'Configuration cache cleared');
        }

        /**
         * Log configuration usage
         * @param {string} component - Component name
         * @param {string} message - Log message
         * @param {string} level - Log level (info, warn, error)
         */
        log(component, message, level = 'info') {
            if (!this.debugMode && level === 'info') return;
            
            const timestamp = new Date().toISOString();
            const logMessage = `[${timestamp}] [${component}] ${message}`;
            
            switch(level) {
                case 'error':
                    console.error(logMessage);
                    break;
                case 'warn':
                    console.warn(logMessage);
                    break;
                default:
                    console.log(logMessage);
            }
        }

        /**
         * Make API request with proper configuration
         * @param {string} endpoint - API endpoint
         * @param {Object} options - Fetch options
         * @returns {Promise} API response
         */
        async apiRequest(endpoint, options = {}) {
            const url = `${this.getApiBaseUrl()}${endpoint}`;
            const timeout = this.getTimeout('api') * 1000; // Convert to milliseconds
            
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            };
            
            const mergedOptions = { ...defaultOptions, ...options };
            
            // Add CSRF token if available
            const csrfToken = this.getCSRFToken();
            if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(mergedOptions.method)) {
                mergedOptions.headers['X-CSRFToken'] = csrfToken;
            }
            
            this.log('CONFIG', `API Request: ${mergedOptions.method || 'GET'} ${url}`);
            
            // Add timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            mergedOptions.signal = controller.signal;
            
            try {
                const response = await fetch(url, mergedOptions);
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`API Error: ${response.status} ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                clearTimeout(timeoutId);
                this.log('CONFIG', `API Request failed: ${error.message}`, 'error');
                throw error;
            }
        }

        /**
         * Get CSRF token from cookies
         * @returns {string|null} CSRF token
         */
        getCSRFToken() {
            const name = 'csrftoken';
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
    }

    // Create singleton instance
    const configService = new ConfigService();

    // Export to PrimePath namespace
    window.PrimePath.ConfigService = configService;

    // Export convenience functions
    window.PrimePath.config = {
        getCurrentYear: () => configService.getCurrentYear(),
        getAcademicYear: () => configService.getCurrentAcademicYear(),
        getBaseUrl: () => configService.getBaseUrl(),
        getApiUrl: () => configService.getApiBaseUrl(),
        getTimeout: (key) => configService.getTimeout(key),
        getFeatureFlag: (flag, defaultValue) => configService.getFeatureFlag(flag, defaultValue),
        validateYear: (year) => configService.validateYear(year),
        apiRequest: (endpoint, options) => configService.apiRequest(endpoint, options),
        log: (component, message, level) => configService.log(component, message, level),
    };

    // Log initialization
    console.log('[CONFIG] PrimePath Configuration Service loaded successfully');
    if (configService.debugMode) {
        console.log('[CONFIG] System Constants:', configService.getSystemConstants());
    }

})(window);