/**
 * PrimePath Bootstrap Script
 * CRITICAL: This MUST load before ALL other scripts
 * Creates and initializes the complete namespace structure
 * Provides error recovery and logging infrastructure
 */

(function(window, document) {
    'use strict';
    
    // ============================================================
    // STEP 1: Create Console Logger with Timestamp
    // ============================================================
    const log = function(level, ...args) {
        const timestamp = new Date().toISOString();
        const prefix = `[${timestamp}] [PRIMEPATH]`;
        
        switch(level) {
            case 'error':
                console.error(prefix, ...args);
                break;
            case 'warn':
                console.warn(prefix, ...args);
                break;
            case 'info':
                console.info(prefix, ...args);
                break;
            default:
                console.log(prefix, ...args);
        }
    };
    
    log('info', '========================================');
    log('info', 'PRIMEPATH BOOTSTRAP INITIALIZING');
    log('info', '========================================');
    
    // ============================================================
    // STEP 2: Create Root Namespace with Safety Checks
    // ============================================================
    if (typeof window.PrimePath !== 'undefined') {
        log('warn', 'PrimePath namespace already exists, preserving existing data');
    }
    
    // Create or preserve root namespace
    window.PrimePath = window.PrimePath || {};
    
    // ============================================================
    // STEP 3: Create All Required Sub-Namespaces
    // ============================================================
    const requiredNamespaces = [
        'utils',
        'modules', 
        'config',
        'services',
        'helpers',
        'validators',
        'constants',
        'state',
        'events',
        'errors'
    ];
    
    log('info', 'Creating namespaces:', requiredNamespaces.join(', '));
    
    requiredNamespaces.forEach(namespace => {
        if (!window.PrimePath[namespace]) {
            window.PrimePath[namespace] = {};
            log('info', `✓ Created namespace: PrimePath.${namespace}`);
        } else {
            log('info', `✓ Namespace exists: PrimePath.${namespace}`);
        }
    });
    
    // ============================================================
    // STEP 4: Create Core Utility Functions
    // ============================================================
    
    /**
     * Safe namespace creator
     * Creates nested namespaces safely
     */
    window.PrimePath.createNamespace = function(path) {
        const parts = path.split('.');
        let current = window;
        
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            current[part] = current[part] || {};
            current = current[part];
        }
        
        log('info', `✓ Namespace ensured: ${path}`);
        return current;
    };
    
    /**
     * Safe property setter
     * Sets a property on an object, creating path if needed
     */
    window.PrimePath.safeSet = function(path, value) {
        const parts = path.split('.');
        const property = parts.pop();
        const namespace = parts.join('.');
        
        const target = window.PrimePath.createNamespace(namespace);
        target[property] = value;
        
        log('info', `✓ Property set: ${path}`);
        return value;
    };
    
    /**
     * Safe property getter
     * Gets a property value or returns undefined
     */
    window.PrimePath.safeGet = function(path, defaultValue = undefined) {
        const parts = path.split('.');
        let current = window;
        
        for (let i = 0; i < parts.length; i++) {
            if (!current[parts[i]]) {
                return defaultValue;
            }
            current = current[parts[i]];
        }
        
        return current;
    };
    
    // ============================================================
    // STEP 5: Create Module Registry
    // ============================================================
    window.PrimePath.state.modules = {
        registered: {},
        initialized: {},
        failed: {},
        loading: {}
    };
    
    /**
     * Register a module
     */
    window.PrimePath.registerModule = function(name, module) {
        window.PrimePath.state.modules.registered[name] = module;
        log('info', `✓ Module registered: ${name}`);
        return module;
    };
    
    /**
     * Check if module is available
     */
    window.PrimePath.isModuleAvailable = function(name) {
        return !!window.PrimePath.state.modules.initialized[name];
    };
    
    // ============================================================
    // STEP 6: Create Event System
    // ============================================================
    window.PrimePath.events.listeners = {};
    
    /**
     * Emit an event
     */
    window.PrimePath.emit = function(event, data) {
        const listeners = window.PrimePath.events.listeners[event] || [];
        listeners.forEach(listener => {
            try {
                listener(data);
            } catch (error) {
                log('error', `Event listener error for ${event}:`, error);
            }
        });
    };
    
    /**
     * Listen for an event
     */
    window.PrimePath.on = function(event, callback) {
        if (!window.PrimePath.events.listeners[event]) {
            window.PrimePath.events.listeners[event] = [];
        }
        window.PrimePath.events.listeners[event].push(callback);
        return () => {
            const index = window.PrimePath.events.listeners[event].indexOf(callback);
            if (index > -1) {
                window.PrimePath.events.listeners[event].splice(index, 1);
            }
        };
    };
    
    // ============================================================
    // STEP 7: Create Error Handling System
    // ============================================================
    window.PrimePath.errors.log = [];
    
    /**
     * Log an error
     */
    window.PrimePath.logError = function(context, error) {
        const errorEntry = {
            timestamp: new Date().toISOString(),
            context: context,
            message: error.message || error,
            stack: error.stack || null
        };
        
        window.PrimePath.errors.log.push(errorEntry);
        log('error', `[${context}]`, error);
        
        // Emit error event
        window.PrimePath.emit('error', errorEntry);
        
        return errorEntry;
    };
    
    /**
     * Get error log
     */
    window.PrimePath.getErrors = function() {
        return window.PrimePath.errors.log;
    };
    
    // ============================================================
    // STEP 8: Create Debug/Development Helpers
    // ============================================================
    window.PrimePath.debug = {
        enabled: window.location.hostname === 'localhost' || 
                 window.location.hostname === '127.0.0.1' ||
                 window.location.search.includes('debug=true'),
        
        log: function(...args) {
            if (window.PrimePath.debug.enabled) {
                log('info', '[DEBUG]', ...args);
            }
        },
        
        trace: function(message) {
            if (window.PrimePath.debug.enabled) {
                console.trace(`[TRACE] ${message}`);
            }
        },
        
        time: function(label) {
            if (window.PrimePath.debug.enabled) {
                console.time(`[TIMER] ${label}`);
            }
        },
        
        timeEnd: function(label) {
            if (window.PrimePath.debug.enabled) {
                console.timeEnd(`[TIMER] ${label}`);
            }
        }
    };
    
    // ============================================================
    // STEP 9: Create Initialization State Tracker
    // ============================================================
    window.PrimePath.state.initialization = {
        started: new Date().toISOString(),
        completed: false,
        steps: [],
        errors: []
    };
    
    /**
     * Track initialization step
     */
    window.PrimePath.trackInit = function(step, success = true, details = null) {
        const entry = {
            step: step,
            success: success,
            timestamp: new Date().toISOString(),
            details: details
        };
        
        window.PrimePath.state.initialization.steps.push(entry);
        
        if (success) {
            log('info', `✓ INIT: ${step}`);
        } else {
            log('error', `✗ INIT: ${step}`, details);
            window.PrimePath.state.initialization.errors.push(entry);
        }
        
        return entry;
    };
    
    // ============================================================
    // STEP 10: Create Health Check System
    // ============================================================
    window.PrimePath.healthCheck = function() {
        const health = {
            timestamp: new Date().toISOString(),
            namespaces: {},
            modules: {
                registered: Object.keys(window.PrimePath.state.modules.registered).length,
                initialized: Object.keys(window.PrimePath.state.modules.initialized).length,
                failed: Object.keys(window.PrimePath.state.modules.failed).length
            },
            errors: window.PrimePath.errors.log.length,
            initialization: window.PrimePath.state.initialization
        };
        
        // Check namespaces
        requiredNamespaces.forEach(ns => {
            health.namespaces[ns] = !!window.PrimePath[ns];
        });
        
        // Calculate health score
        const namespaceScore = Object.values(health.namespaces).filter(v => v).length / requiredNamespaces.length;
        const moduleScore = health.modules.initialized / Math.max(1, health.modules.registered);
        const errorScore = health.errors === 0 ? 1 : Math.max(0, 1 - (health.errors / 10));
        
        health.score = Math.round(((namespaceScore + moduleScore + errorScore) / 3) * 100);
        health.status = health.score >= 80 ? 'healthy' : health.score >= 50 ? 'degraded' : 'critical';
        
        return health;
    };
    
    // ============================================================
    // STEP 11: Create Compatibility Layer
    // ============================================================
    
    // Ensure backward compatibility with old code
    window.PrimePath.utils.EventDelegation = window.PrimePath.utils.EventDelegation || null;
    window.PrimePath.utils.ModuleLoader = window.PrimePath.utils.ModuleLoader || null;
    window.PrimePath.modules.PDFViewer = window.PrimePath.modules.PDFViewer || null;
    window.PrimePath.modules.Timer = window.PrimePath.modules.Timer || null;
    window.PrimePath.modules.AudioPlayer = window.PrimePath.modules.AudioPlayer || null;
    window.PrimePath.modules.AnswerManager = window.PrimePath.modules.AnswerManager || null;
    window.PrimePath.modules.NavigationModule = window.PrimePath.modules.NavigationModule || null;
    
    // ============================================================
    // STEP 12: Setup Global Error Handler
    // ============================================================
    window.addEventListener('error', function(event) {
        window.PrimePath.logError('window.error', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error
        });
    });
    
    window.addEventListener('unhandledrejection', function(event) {
        window.PrimePath.logError('unhandledrejection', {
            reason: event.reason,
            promise: event.promise
        });
    });
    
    // ============================================================
    // STEP 13: Mark Bootstrap as Complete
    // ============================================================
    window.PrimePath.state.bootstrapComplete = true;
    window.PrimePath.state.bootstrapTimestamp = new Date().toISOString();
    
    // Track successful bootstrap
    window.PrimePath.trackInit('Bootstrap', true, {
        namespaces: requiredNamespaces,
        timestamp: window.PrimePath.state.bootstrapTimestamp
    });
    
    // Emit bootstrap complete event
    window.PrimePath.emit('bootstrap:complete', {
        namespaces: requiredNamespaces,
        health: window.PrimePath.healthCheck()
    });
    
    log('info', '========================================');
    log('info', 'PRIMEPATH BOOTSTRAP COMPLETE');
    log('info', `Health Score: ${window.PrimePath.healthCheck().score}%`);
    log('info', '========================================');
    
    // ============================================================
    // STEP 14: Export Bootstrap Version
    // ============================================================
    window.PrimePath.version = {
        bootstrap: '2.0.0',
        timestamp: '2024-08-14',
        environment: window.PrimePath.debug.enabled ? 'development' : 'production'
    };
    
})(window, document);