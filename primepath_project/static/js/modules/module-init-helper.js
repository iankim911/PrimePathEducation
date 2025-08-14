/**
 * Module Initialization Helper
 * Provides defensive initialization for all modules
 * This is a shared helper that all modules can use
 */

(function(window) {
    'use strict';
    
    // Create namespace helper function
    window.createPrimePathNamespace = function(moduleName) {
        console.log(`[${moduleName}] Initializing module`);
        
        // Defensive namespace creation
        if (typeof window.PrimePath === 'undefined') {
            console.warn(`[${moduleName}] PrimePath namespace not found, creating it`);
            window.PrimePath = {};
        }
        
        if (typeof window.PrimePath.modules === 'undefined') {
            console.log(`[${moduleName}] Creating PrimePath.modules namespace`);
            window.PrimePath.modules = {};
        }
        
        // Return BaseModule with fallback
        return window.PrimePath.modules.BaseModule || class FallbackBaseModule {
            constructor(name, options) {
                this.name = name;
                this.options = options || {};
                this.initialized = false;
                this.config = (window.PrimePath && window.PrimePath.config) || {};
                console.warn(`[${moduleName}] Using BaseModule fallback`);
            }
            
            init() { 
                this.initialized = true;
                console.log(`[${this.name}] Initialized (fallback mode)`);
            }
            
            destroy() {
                this.initialized = false;
            }
            
            log(level, ...args) { 
                const prefix = `[${this.name}]`;
                console[level](prefix, ...args);
            }
            
            emit(event, data) {
                if (window.PrimePath && window.PrimePath.emit) {
                    window.PrimePath.emit(`${this.name}:${event}`, data);
                }
            }
            
            on(event, callback) { 
                if (window.PrimePath && window.PrimePath.on) {
                    return window.PrimePath.on(`${this.name}:${event}`, callback);
                }
                return function() {};
            }
            
            isDebugMode() {
                return window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
            }
            
            async ajax(url, options = {}) {
                if (!options.headers) {
                    options.headers = {};
                }
                
                // Add CSRF token if available
                if (this.config && this.config.getCsrfToken) {
                    options.headers['X-CSRFToken'] = this.config.getCsrfToken();
                } else {
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                    if (csrfToken) {
                        options.headers['X-CSRFToken'] = csrfToken;
                    }
                }
                
                return fetch(url, options).then(response => response.json());
            }
        };
    };
    
    // Export module helper
    window.exportPrimePathModule = function(moduleName, ModuleClass) {
        try {
            if (window.PrimePath && window.PrimePath.modules) {
                window.PrimePath.modules[moduleName] = ModuleClass;
                console.log(`[${moduleName}] ✓ Module exported to PrimePath.modules.${moduleName}`);
                
                // Track initialization if bootstrap is available
                if (window.PrimePath.trackInit) {
                    window.PrimePath.trackInit(moduleName, true);
                }
                
                // Register module if module loader is available
                if (window.PrimePath.registerModule) {
                    window.PrimePath.registerModule(moduleName, ModuleClass);
                }
                
                return true;
            } else {
                console.error(`[${moduleName}] Cannot export - namespace not available`);
                return false;
            }
        } catch (error) {
            console.error(`[${moduleName}] Export failed:`, error);
            if (window.PrimePath && window.PrimePath.trackInit) {
                window.PrimePath.trackInit(moduleName, false, error.message);
            }
            return false;
        }
    };
    
    console.log('[ModuleInitHelper] ✓ Module initialization helper loaded');
    
})(window);