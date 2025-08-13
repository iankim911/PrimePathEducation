/**
 * Base Module Class
 * Foundation for all PrimePath modules
 * Provides common functionality and patterns
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    /**
     * Base class for all modules
     */
    class BaseModule {
        constructor(name, options = {}) {
            this.name = name;
            this.options = options;
            this.initialized = false;
            this.events = {};
            this.config = window.PrimePath.config;
            this.debug = options.debug || false;
        }

        /**
         * Initialize module
         * Override in subclasses
         */
        init() {
            if (this.initialized) {
                this.log('warn', `Module ${this.name} already initialized`);
                return;
            }

            // Only log initialization in debug mode
            if (this.isDebugMode()) {
                this.log('info', `Initializing module: ${this.name}`);
            }
            this.initialized = true;
        }

        /**
         * Destroy module and cleanup
         */
        destroy() {
            this.log('info', `Destroying module: ${this.name}`);
            this.off(); // Remove all event listeners
            this.initialized = false;
        }

        /**
         * Log message with module context
         * @param {string} level Log level (info, warn, error)
         * @param {string} message Log message
         * @param {*} data Additional data
         */
        log(level, message, data) {
            if (!this.debug && level === 'info') return;

            const prefix = `[${this.name}]`;
            
            switch(level) {
                case 'error':
                    console.error(prefix, message, data || '');
                    break;
                case 'warn':
                    console.warn(prefix, message, data || '');
                    break;
                default:
// REMOVED:                     console.log(prefix, message, data || '');
            }
        }

        /**
         * Check if we're in debug mode
         * @returns {boolean} True if in debug mode
         */
        isDebugMode() {
            // Check if AppConfig is available and has debug info
            if (window.PrimePath && window.PrimePath.config && window.PrimePath.config.isDebugMode) {
                return window.PrimePath.config.isDebugMode();
            }
            
            // Fallback: check URL and hostname
            return window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname.includes('dev') ||
                   window.location.search.includes('debug=true');
        }

        /**
         * Emit event
         * @param {string} eventName Event name
         * @param {*} data Event data
         */
        emit(eventName, data) {
            const handlers = this.events[eventName];
            if (!handlers) return;

            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    this.log('error', `Error in event handler for ${eventName}:`, error);
                }
            });

            // Also emit as DOM event for cross-module communication
            const event = new CustomEvent(`primepath:${this.name}:${eventName}`, {
                detail: data,
                bubbles: true
            });
            document.dispatchEvent(event);
        }

        /**
         * Subscribe to event
         * @param {string} eventName Event name
         * @param {Function} handler Event handler
         * @returns {Function} Unsubscribe function
         */
        on(eventName, handler) {
            if (!this.events[eventName]) {
                this.events[eventName] = [];
            }

            this.events[eventName].push(handler);

            return () => {
                const index = this.events[eventName].indexOf(handler);
                if (index > -1) {
                    this.events[eventName].splice(index, 1);
                }
            };
        }

        /**
         * Unsubscribe from event
         * @param {string} eventName Event name (optional, removes all if not specified)
         * @param {Function} handler Event handler (optional, removes all for event if not specified)
         */
        off(eventName, handler) {
            if (!eventName) {
                // Remove all events
                this.events = {};
                return;
            }

            if (!handler) {
                // Remove all handlers for event
                delete this.events[eventName];
                return;
            }

            // Remove specific handler
            const handlers = this.events[eventName];
            if (handlers) {
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            }
        }

        /**
         * Subscribe to event once
         * @param {string} eventName Event name
         * @param {Function} handler Event handler
         */
        once(eventName, handler) {
            const unsubscribe = this.on(eventName, (data) => {
                handler(data);
                unsubscribe();
            });
        }

        /**
         * Get configuration value
         * @param {string} key Configuration key
         * @param {*} defaultValue Default value
         * @returns {*} Configuration value
         */
        getConfig(key, defaultValue) {
            return this.options[key] !== undefined 
                ? this.options[key] 
                : defaultValue;
        }

        /**
         * Set configuration value
         * @param {string} key Configuration key
         * @param {*} value Configuration value
         */
        setConfig(key, value) {
            this.options[key] = value;
        }

        /**
         * Make AJAX request with CSRF token
         * @param {string} url Request URL
         * @param {Object} options Fetch options
         * @returns {Promise} Fetch promise
         */
        async ajax(url, options = {}) {
            // Add CSRF token to headers
            if (!options.headers) {
                options.headers = {};
            }
            
            if (!options.headers['X-CSRFToken']) {
                // Try to get CSRF token from config or APP_CONFIG
                let csrfToken = '';
                if (this.config && typeof this.config.getCsrfToken === 'function') {
                    csrfToken = this.config.getCsrfToken();
                } else if (window.APP_CONFIG && window.APP_CONFIG.csrf) {
                    csrfToken = window.APP_CONFIG.csrf;
                } else {
                    // Try to get from cookie as fallback
                    const match = document.cookie.match(/csrftoken=([^;]+)/);
                    if (match) {
                        csrfToken = match[1];
                    }
                }
                
                if (!csrfToken) {
                    console.warn('CSRF token not found for AJAX request');
                }
                
                options.headers['X-CSRFToken'] = csrfToken;
            }

            // Add default content type for JSON
            if (options.method && options.method !== 'GET' && !options.headers['Content-Type']) {
                options.headers['Content-Type'] = 'application/json';
            }

            try {
                const response = await fetch(url, options);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // Try to parse as JSON, fallback to text
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }
            } catch (error) {
                this.log('error', `AJAX request failed: ${url}`, error);
                throw error;
            }
        }

        /**
         * Get DOM element(s)
         * @param {string} selector CSS selector
         * @param {HTMLElement} context Context element (default: document)
         * @returns {HTMLElement|NodeList} Element(s)
         */
        $(selector, context = document) {
            const elements = context.querySelectorAll(selector);
            return elements.length === 1 ? elements[0] : elements;
        }

        /**
         * Check if element exists
         * @param {string} selector CSS selector
         * @returns {boolean} True if exists
         */
        exists(selector) {
            return document.querySelector(selector) !== null;
        }

        /**
         * Wait for element to exist
         * @param {string} selector CSS selector
         * @param {number} timeout Timeout in ms
         * @returns {Promise<HTMLElement>} Element promise
         */
        waitForElement(selector, timeout = 5000) {
            return new Promise((resolve, reject) => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    return;
                }

                const observer = new MutationObserver((mutations, obs) => {
                    const element = document.querySelector(selector);
                    if (element) {
                        obs.disconnect();
                        resolve(element);
                    }
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });

                // Timeout
                setTimeout(() => {
                    observer.disconnect();
                    reject(new Error(`Element ${selector} not found after ${timeout}ms`));
                }, timeout);
            });
        }
    }

    // Export to PrimePath namespace
    window.PrimePath.modules.BaseModule = BaseModule;

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = BaseModule;
    }

})(window);