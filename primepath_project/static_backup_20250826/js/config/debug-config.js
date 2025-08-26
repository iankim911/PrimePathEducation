/**
 * Debug Configuration System
 * Controls logging verbosity throughout the application
 * 
 * This provides centralized control over debug output to prevent
 * console pollution in production while maintaining debugging capabilities
 * in development environments.
 */

(function(window) {
    'use strict';
    
    // Create namespace
    window.PrimePath = window.PrimePath || {};
    window.PrimePath.config = window.PrimePath.config || {};
    
    /**
     * Debug Configuration Object
     * Controls what gets logged and at what verbosity level
     */
    const DebugConfig = {
        // Master debug flag - set to false in production
        enabled: window.location.hostname === 'localhost' || 
                 window.location.hostname === '127.0.0.1' ||
                 window.location.search.includes('debug=true'),
        
        // Verbosity levels
        levels: {
            ERROR: 0,    // Always log errors
            WARN: 1,     // Warnings in dev mode
            INFO: 2,     // General information
            DEBUG: 3,    // Detailed debug info
            TRACE: 4     // Excessive detail (stack traces, etc.)
        },
        
        // Current verbosity level
        currentLevel: 2, // Default to INFO level
        
        // Module-specific debug flags
        modules: {
            timer: true,
            modal: true,
            eventDelegation: false,  // Disable HTML logging
            answerManager: true,
            navigation: true,
            bootstrap: true
        },
        
        // What to log for each module
        logOptions: {
            // Never log these in any mode
            neverLog: [
                'htmlContent',       // Raw HTML content
                'domElements',       // DOM element references
                'stackTraces',       // Stack traces (unless TRACE level)
                'mutationRecords'    // DOM mutation records
            ],
            
            // Only log in development
            devOnly: [
                'ajaxRequests',
                'ajaxResponses',
                'timerCalculations',
                'modalStateChanges'
            ],
            
            // Always log these (even in production)
            alwaysLog: [
                'criticalErrors',
                'securityWarnings',
                'dataIntegrityIssues'
            ]
        },
        
        /**
         * Check if a module should log
         * @param {string} moduleName - Name of the module
         * @param {number} level - Log level (0-4)
         * @returns {boolean}
         */
        shouldLog: function(moduleName, level = 2) {
            // Never log if globally disabled
            if (!this.enabled) {
                // But always log errors
                return level === this.levels.ERROR;
            }
            
            // Check module-specific flag
            if (this.modules[moduleName] === false) {
                return false;
            }
            
            // Check verbosity level
            return level <= this.currentLevel;
        },
        
        /**
         * Conditional logging wrapper
         * @param {string} moduleName - Module doing the logging
         * @param {string} level - Log level (ERROR, WARN, INFO, DEBUG, TRACE)
         * @param {string} message - Log message
         * @param {*} data - Optional data to log
         */
        log: function(moduleName, level, message, data) {
            const levelValue = this.levels[level] || this.levels.INFO;
            
            if (!this.shouldLog(moduleName, levelValue)) {
                return;
            }
            
            // Format the message with module name
            const prefix = `[${moduleName}]`;
            const formattedMessage = `${prefix} ${message}`;
            
            // Choose console method based on level
            switch(level) {
                case 'ERROR':
                    console.error(formattedMessage, data || '');
                    break;
                case 'WARN':
                    console.warn(formattedMessage, data || '');
                    break;
                case 'DEBUG':
                case 'TRACE':
                    console.debug ? console.debug(formattedMessage, data || '') : 
                                   console.log(formattedMessage, data || '');
                    break;
                default:
                    console.log(formattedMessage, data || '');
            }
        },
        
        /**
         * Create a logger for a specific module
         * @param {string} moduleName - Name of the module
         * @returns {Object} Logger object with level methods
         */
        createLogger: function(moduleName) {
            const self = this;
            return {
                error: (msg, data) => self.log(moduleName, 'ERROR', msg, data),
                warn: (msg, data) => self.log(moduleName, 'WARN', msg, data),
                info: (msg, data) => self.log(moduleName, 'INFO', msg, data),
                debug: (msg, data) => self.log(moduleName, 'DEBUG', msg, data),
                trace: (msg, data) => self.log(moduleName, 'TRACE', msg, data),
                
                // Special method to check if should log
                isEnabled: (level = 'INFO') => self.shouldLog(moduleName, self.levels[level])
            };
        },
        
        /**
         * Update debug settings at runtime
         * @param {Object} settings - New settings to apply
         */
        updateSettings: function(settings) {
            if (settings.enabled !== undefined) {
                this.enabled = settings.enabled;
            }
            if (settings.level !== undefined) {
                this.currentLevel = this.levels[settings.level] || this.currentLevel;
            }
            if (settings.modules) {
                Object.assign(this.modules, settings.modules);
            }
            
            console.log('[DebugConfig] Settings updated:', {
                enabled: this.enabled,
                level: Object.keys(this.levels).find(k => this.levels[k] === this.currentLevel),
                modules: this.modules
            });
        },
        
        /**
         * Get current debug status
         * @returns {Object} Current debug configuration
         */
        getStatus: function() {
            return {
                enabled: this.enabled,
                level: Object.keys(this.levels).find(k => this.levels[k] === this.currentLevel),
                levelValue: this.currentLevel,
                modules: { ...this.modules },
                environment: window.location.hostname
            };
        }
    };
    
    // Export to PrimePath namespace
    window.PrimePath.config.debug = DebugConfig;
    
    // Create global shortcut for easy access
    window.PrimePathDebug = DebugConfig;
    
    // Log initial status (but only if enabled)
    if (DebugConfig.enabled) {
        console.log('[DebugConfig] Debug system initialized:', DebugConfig.getStatus());
    }
    
    // Expose methods to control debug at runtime from console
    window.enableDebug = function(moduleName) {
        if (moduleName) {
            DebugConfig.modules[moduleName] = true;
            console.log(`[DebugConfig] Enabled debugging for: ${moduleName}`);
        } else {
            DebugConfig.enabled = true;
            console.log('[DebugConfig] Global debugging enabled');
        }
    };
    
    window.disableDebug = function(moduleName) {
        if (moduleName) {
            DebugConfig.modules[moduleName] = false;
            console.log(`[DebugConfig] Disabled debugging for: ${moduleName}`);
        } else {
            DebugConfig.enabled = false;
            console.log('[DebugConfig] Global debugging disabled');
        }
    };
    
    window.setDebugLevel = function(level) {
        DebugConfig.updateSettings({ level: level.toUpperCase() });
    };
    
})(window);