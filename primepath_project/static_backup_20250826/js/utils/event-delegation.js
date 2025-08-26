/**
 * Event Delegation System
 * Replaces inline event handlers with delegated events
 * Solves the problem of 157+ onclick attributes
 */

(function(window) {
    'use strict';
    
    // Use debug config if available, otherwise use simple check
    const logger = (window.PrimePathDebug && window.PrimePathDebug.createLogger) ? 
                   window.PrimePathDebug.createLogger('EventDelegation') :
                   {
                       info: (msg) => console.log('[EventDelegation] ' + msg),
                       warn: (msg) => console.warn('[EventDelegation] ' + msg),
                       error: (msg) => console.error('[EventDelegation] ' + msg),
                       debug: (msg) => { /* no-op */ },
                       trace: (msg) => { /* no-op */ }
                   };
    
    logger.debug('Initializing event delegation module');
    
    // Defensive namespace creation with comprehensive checks
    if (typeof window.PrimePath === 'undefined') {
        logger.info('PrimePath namespace not found, creating it');
        window.PrimePath = {};
    }
    
    if (typeof window.PrimePath.utils === 'undefined') {
        logger.debug('Creating PrimePath.utils namespace');
        window.PrimePath.utils = {};
    }

    /**
     * Event delegation manager
     * Handles events at document level to replace inline handlers
     */
    class EventDelegation {
        constructor() {
            this.handlers = new Map();
            this.initialized = false;
        }

        /**
         * Initialize event delegation system
         */
        init() {
            if (this.initialized) return;

            // Set up document-level event listeners
            ['click', 'change', 'input', 'submit'].forEach(eventType => {
                document.addEventListener(eventType, (e) => {
                    this.handleEvent(eventType, e);
                }, true);
            });

            this.initialized = true;
        }

        /**
         * Handle delegated event
         * @param {string} eventType Event type
         * @param {Event} event Event object
         */
        handleEvent(eventType, event) {
            const handlers = this.handlers.get(eventType);
            if (!handlers) return;

            // Check each handler
            handlers.forEach(handler => {
                const element = event.target.closest(handler.selector);
                if (element) {
                    // Call handler with element as context
                    handler.callback.call(element, event, element);
                }
            });
        }

        /**
         * Register event handler
         * @param {string} eventType Event type (click, change, etc.)
         * @param {string} selector CSS selector
         * @param {Function} callback Event handler
         * @returns {Function} Unregister function
         */
        on(eventType, selector, callback) {
            if (!this.initialized) {
                this.init();
            }

            if (!this.handlers.has(eventType)) {
                this.handlers.set(eventType, []);
            }

            const handler = { selector, callback };
            this.handlers.get(eventType).push(handler);

            return () => {
                const handlers = this.handlers.get(eventType);
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            };
        }

        /**
         * Register click handler
         * @param {string} selector CSS selector
         * @param {Function} callback Event handler
         * @returns {Function} Unregister function
         */
        onClick(selector, callback) {
            return this.on('click', selector, callback);
        }

        /**
         * Register change handler
         * @param {string} selector CSS selector
         * @param {Function} callback Event handler
         * @returns {Function} Unregister function
         */
        onChange(selector, callback) {
            return this.on('change', selector, callback);
        }

        /**
         * Register input handler
         * @param {string} selector CSS selector
         * @param {Function} callback Event handler
         * @returns {Function} Unregister function
         */
        onInput(selector, callback) {
            return this.on('input', selector, callback);
        }

        /**
         * Register submit handler
         * @param {string} selector CSS selector
         * @param {Function} callback Event handler
         * @returns {Function} Unregister function
         */
        onSubmit(selector, callback) {
            return this.on('submit', selector, callback);
        }

        /**
         * Migrate inline onclick to delegated event
         * @param {string} selector Elements with onclick
         */
        migrateOnclick(selector = '[onclick]') {
            document.querySelectorAll(selector).forEach(element => {
                const onclickStr = element.getAttribute('onclick');
                if (onclickStr) {
                    // Create unique data attribute
                    const id = 'click-' + Math.random().toString(36).substr(2, 9);
                    element.setAttribute('data-click-id', id);
                    
                    const handler = new Function('event', onclickStr);
                    
                    // Register delegated handler
                    this.onClick(`[data-click-id="${id}"]`, (e) => {
                        handler.call(element, e);
                    });
                    
                    // Remove inline onclick
                    element.removeAttribute('onclick');
                }
            });
        }

        /**
         * Convert data attributes to event parameters
         * Useful for replacing onclick="function({{ value }})"
         * @param {HTMLElement} element Element with data attributes
         * @returns {Object} Data attributes as object
         */
        getDataParams(element) {
            const params = {};
            Array.from(element.attributes).forEach(attr => {
                if (attr.name.startsWith('data-')) {
                    const key = attr.name.substring(5).replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                    params[key] = attr.value;
                }
            });
            return params;
        }
    }

    // Create singleton instance with error handling
    let eventDelegation;
    
    try {
        eventDelegation = new EventDelegation();
        logger.debug('Instance created successfully');
    } catch (error) {
        logger.error('Failed to create instance:', error);
        // Create minimal fallback
        eventDelegation = {
            init: function() { logger.warn('Using fallback implementation'); },
            on: function() { return function() {}; },
            onClick: function(sel, cb) { 
                document.addEventListener('click', function(e) {
                    const el = e.target.closest(sel);
                    if (el) cb.call(el, e);
                });
            },
            onChange: function(sel, cb) {
                document.addEventListener('change', function(e) {
                    const el = e.target.closest(sel);
                    if (el) cb.call(el, e);
                });
            }
        };
    }

    // Export to PrimePath namespace with safety check
    if (window.PrimePath && window.PrimePath.utils) {
        window.PrimePath.utils.EventDelegation = eventDelegation;
        logger.debug('Module exported to PrimePath.utils.EventDelegation');
    } else {
        logger.error('Cannot export - namespace not available');
    }

    // Convenience methods
    window.PrimePath.on = eventDelegation.on.bind(eventDelegation);
    window.PrimePath.onClick = eventDelegation.onClick.bind(eventDelegation);
    window.PrimePath.onChange = eventDelegation.onChange.bind(eventDelegation);
    window.PrimePath.onInput = eventDelegation.onInput.bind(eventDelegation);
    window.PrimePath.onSubmit = eventDelegation.onSubmit.bind(eventDelegation);

    // Auto-initialize on DOMContentLoaded with error handling
    const autoInit = function() {
        try {
            eventDelegation.init();
            logger.debug('Auto-initialization complete');
            
            // Track initialization if bootstrap is available
            if (window.PrimePath && window.PrimePath.trackInit) {
                window.PrimePath.trackInit('EventDelegation', true);
            }
        } catch (error) {
            logger.error('Auto-initialization failed:', error);
            if (window.PrimePath && window.PrimePath.trackInit) {
                window.PrimePath.trackInit('EventDelegation', false, error.message);
            }
        }
    };
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoInit);
    } else {
        autoInit();
    }

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = EventDelegation;
    }

})(window);