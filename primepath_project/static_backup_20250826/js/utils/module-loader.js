/**
 * Module Loader System
 * Ensures all modules load properly with error recovery
 * Solves module dependency and initialization issues
 */

(function(window) {
    'use strict';
    
    console.log('[ModuleLoader] Initializing module loader');
    
    // Defensive namespace creation
    if (typeof window.PrimePath === 'undefined') {
        console.warn('[ModuleLoader] PrimePath namespace not found, creating it');
        window.PrimePath = {};
    }
    
    if (typeof window.PrimePath.utils === 'undefined') {
        console.log('[ModuleLoader] Creating PrimePath.utils namespace');
        window.PrimePath.utils = {};
    }

    /**
     * Module loader with dependency management and error recovery
     */
    class ModuleLoader {
        constructor() {
            this.modules = new Map();
            this.loadAttempts = new Map();
            this.maxRetries = 3;
            this.retryDelay = 100; // ms
            this.initialized = false;
            
            // Track initialization status
            this.status = {
                core: false,
                modules: {},
                errors: []
            };
            
            console.log('[ModuleLoader] Initializing module loader system');
        }

        /**
         * Register a module for initialization
         * @param {string} name Module name
         * @param {Function} initFn Initialization function
         * @param {Array} dependencies Module dependencies
         */
        register(name, initFn, dependencies = []) {
            console.log(`[ModuleLoader] Registering module: ${name}`, dependencies.length > 0 ? `Dependencies: ${dependencies.join(', ')}` : 'No dependencies');
            
            this.modules.set(name, {
                name,
                initFn,
                dependencies,
                initialized: false,
                instance: null
            });
        }

        /**
         * Check if a module is available
         * @param {string} name Module name
         * @returns {boolean} True if module is initialized
         */
        isAvailable(name) {
            const module = this.modules.get(name);
            return module && module.initialized;
        }

        /**
         * Get module instance
         * @param {string} name Module name
         * @returns {*} Module instance or null
         */
        getInstance(name) {
            const module = this.modules.get(name);
            return module ? module.instance : null;
        }

        /**
         * Initialize a specific module
         * @param {string} name Module name
         * @returns {Promise} Initialization promise
         */
        async initModule(name) {
            const module = this.modules.get(name);
            if (!module) {
                console.error(`[ModuleLoader] Module not registered: ${name}`);
                return null;
            }

            if (module.initialized) {
                console.log(`[ModuleLoader] Module already initialized: ${name}`);
                return module.instance;
            }

            // Check dependencies
            for (const dep of module.dependencies) {
                if (!this.isAvailable(dep)) {
                    console.log(`[ModuleLoader] Initializing dependency ${dep} for ${name}`);
                    await this.initModule(dep);
                }
            }

            // Try to initialize the module
            const attempts = this.loadAttempts.get(name) || 0;
            
            try {
                console.log(`[ModuleLoader] Initializing module: ${name} (attempt ${attempts + 1})`);
                
                const instance = await module.initFn();
                
                module.instance = instance;
                module.initialized = true;
                this.status.modules[name] = true;
                
                console.log(`[ModuleLoader] ✅ Module initialized successfully: ${name}`);
                return instance;
                
            } catch (error) {
                console.error(`[ModuleLoader] ❌ Failed to initialize module ${name}:`, error);
                this.status.errors.push({
                    module: name,
                    error: error.message,
                    stack: error.stack
                });
                
                this.loadAttempts.set(name, attempts + 1);
                
                if (attempts < this.maxRetries) {
                    console.log(`[ModuleLoader] Retrying module ${name} in ${this.retryDelay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                    return this.initModule(name);
                }
                
                console.error(`[ModuleLoader] Module ${name} failed after ${this.maxRetries} attempts`);
                return null;
            }
        }

        /**
         * Initialize all registered modules
         * @returns {Promise} Initialization promise
         */
        async initAll() {
            console.log('[ModuleLoader] Starting full initialization...');
            console.log(`[ModuleLoader] Registered modules: ${Array.from(this.modules.keys()).join(', ')}`);
            
            // Sort modules by dependency order
            const sorted = this.topologicalSort();
            console.log(`[ModuleLoader] Initialization order: ${sorted.join(' → ')}`);
            
            // Initialize in order
            for (const name of sorted) {
                await this.initModule(name);
            }
            
            this.initialized = true;
            this.printStatus();
            
            return this.status;
        }

        /**
         * Topological sort for dependency order
         * @returns {Array} Sorted module names
         */
        topologicalSort() {
            const visited = new Set();
            const sorted = [];
            
            const visit = (name) => {
                if (visited.has(name)) return;
                visited.add(name);
                
                const module = this.modules.get(name);
                if (module) {
                    for (const dep of module.dependencies) {
                        visit(dep);
                    }
                    sorted.push(name);
                }
            };
            
            for (const name of this.modules.keys()) {
                visit(name);
            }
            
            return sorted;
        }

        /**
         * Print initialization status
         */
        printStatus() {
            console.group('[ModuleLoader] Initialization Status');
            
            const successful = [];
            const failed = [];
            
            for (const [name, module] of this.modules) {
                if (module.initialized) {
                    successful.push(name);
                } else {
                    failed.push(name);
                }
            }
            
            if (successful.length > 0) {
                console.log(`✅ Successful (${successful.length}):`, successful.join(', '));
            }
            
            if (failed.length > 0) {
                console.error(`❌ Failed (${failed.length}):`, failed.join(', '));
            }
            
            if (this.status.errors.length > 0) {
                console.group('Errors:');
                this.status.errors.forEach(err => {
                    console.error(`${err.module}: ${err.error}`);
                });
                console.groupEnd();
            }
            
            console.groupEnd();
        }

        /**
         * Create fallback for critical modules
         * @param {string} modulePath Path to module in window object
         * @param {*} fallback Fallback implementation
         */
        createFallback(modulePath, fallback) {
            const parts = modulePath.split('.');
            let current = window;
            
            for (let i = 0; i < parts.length - 1; i++) {
                const part = parts[i];
                current[part] = current[part] || {};
                current = current[part];
            }
            
            const lastPart = parts[parts.length - 1];
            if (!current[lastPart]) {
                console.warn(`[ModuleLoader] Creating fallback for ${modulePath}`);
                current[lastPart] = fallback;
            }
        }

        /**
         * Health check for all modules
         * @returns {Object} Health status
         */
        healthCheck() {
            const health = {
                timestamp: new Date().toISOString(),
                healthy: true,
                modules: {}
            };
            
            for (const [name, module] of this.modules) {
                const moduleHealth = {
                    registered: true,
                    initialized: module.initialized,
                    hasInstance: !!module.instance,
                    attempts: this.loadAttempts.get(name) || 0
                };
                
                health.modules[name] = moduleHealth;
                
                if (!module.initialized) {
                    health.healthy = false;
                }
            }
            
            return health;
        }

        /**
         * Attempt recovery for failed modules
         */
        async attemptRecovery() {
            console.log('[ModuleLoader] Attempting recovery of failed modules...');
            
            const failed = [];
            for (const [name, module] of this.modules) {
                if (!module.initialized) {
                    failed.push(name);
                }
            }
            
            if (failed.length === 0) {
                console.log('[ModuleLoader] No failed modules to recover');
                return;
            }
            
            console.log(`[ModuleLoader] Attempting to recover: ${failed.join(', ')}`);
            
            // Reset attempts counter
            for (const name of failed) {
                this.loadAttempts.set(name, 0);
            }
            
            // Try to reinitialize
            for (const name of failed) {
                await this.initModule(name);
            }
            
            this.printStatus();
        }
    }

    // Create singleton instance with error handling
    let moduleLoader;
    
    try {
        moduleLoader = new ModuleLoader();
        console.log('[ModuleLoader] ✓ Instance created successfully');
    } catch (error) {
        console.error('[ModuleLoader] Failed to create instance:', error);
        // Create minimal fallback
        moduleLoader = {
            register: function(name) { console.warn(`[ModuleLoader] Cannot register ${name} - using fallback`); },
            initModule: function(name) { console.warn(`[ModuleLoader] Cannot init ${name} - using fallback`); return Promise.resolve(null); },
            initAll: function() { return Promise.resolve({ status: 'fallback' }); },
            healthCheck: function() { return { healthy: false, status: 'fallback' }; },
            modules: new Map()
        };
    }

    // Export to PrimePath namespace with safety check
    if (window.PrimePath && window.PrimePath.utils) {
        window.PrimePath.utils.ModuleLoader = moduleLoader;
        console.log('[ModuleLoader] ✓ Module exported to PrimePath.utils.ModuleLoader');
    } else {
        console.error('[ModuleLoader] Cannot export - namespace not available');
    }

    // Create convenience methods with safety checks
    if (window.PrimePath && moduleLoader) {
        window.PrimePath.registerModule = moduleLoader.register ? moduleLoader.register.bind(moduleLoader) : function() {};
        window.PrimePath.initModules = moduleLoader.initAll ? moduleLoader.initAll.bind(moduleLoader) : function() { return Promise.resolve(); };
        window.PrimePath.moduleHealth = moduleLoader.healthCheck ? moduleLoader.healthCheck.bind(moduleLoader) : function() { return {}; };
        window.PrimePath.recoverModules = moduleLoader.attemptRecovery ? moduleLoader.attemptRecovery.bind(moduleLoader) : function() {};
        console.log('[ModuleLoader] ✓ Convenience methods registered');
    }

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ModuleLoader;
    }

    console.log('[ModuleLoader] Module loader system ready');

})(window);