/**
 * Memory Manager Module
 * Handles cleanup and memory management for all modules
 * Fixes memory leaks after 9000+ sessions
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    class MemoryManager {
        constructor() {
            this.modules = new Map();
            this.timers = new Set();
            this.eventListeners = new Map();
            this.intervals = new Set();
            this.observers = new Set();
            
            // Track performance
            this.performanceMarks = new Map();
            
            // Auto cleanup on page unload
            this.setupUnloadHandler();
            
            // Periodic garbage collection
            this.setupGarbageCollection();
        }

        /**
         * Register a module for memory management
         */
        registerModule(name, module) {
            this.modules.set(name, module);
            console.log(`MemoryManager: Registered module ${name}`);
        }

        /**
         * Register a timer for cleanup
         */
        registerTimer(timerId) {
            this.timers.add(timerId);
            return timerId;
        }

        /**
         * Register an interval for cleanup
         */
        registerInterval(intervalId) {
            this.intervals.add(intervalId);
            return intervalId;
        }

        /**
         * Register an event listener for cleanup
         */
        registerEventListener(element, event, handler, options) {
            const key = `${element.id || 'unknown'}_${event}`;
            if (!this.eventListeners.has(key)) {
                this.eventListeners.set(key, []);
            }
            this.eventListeners.get(key).push({ element, event, handler, options });
            element.addEventListener(event, handler, options);
        }

        /**
         * Clean up all registered resources
         */
        cleanup() {
            console.log('MemoryManager: Starting cleanup...');
            
            // Clear all timers
            this.timers.forEach(timerId => {
                clearTimeout(timerId);
            });
            this.timers.clear();
            
            // Clear all intervals
            this.intervals.forEach(intervalId => {
                clearInterval(intervalId);
            });
            this.intervals.clear();
            
            // Remove all event listeners
            this.eventListeners.forEach((listeners, key) => {
                listeners.forEach(({ element, event, handler, options }) => {
                    if (element && element.removeEventListener) {
                        element.removeEventListener(event, handler, options);
                    }
                });
            });
            this.eventListeners.clear();
            
            // Disconnect all observers
            this.observers.forEach(observer => {
                if (observer && observer.disconnect) {
                    observer.disconnect();
                }
            });
            this.observers.clear();
            
            // Call cleanup on all registered modules
            this.modules.forEach((module, name) => {
                if (module && typeof module.destroy === 'function') {
                    try {
                        module.destroy();
                        console.log(`MemoryManager: Cleaned up module ${name}`);
                    } catch (error) {
                        console.error(`MemoryManager: Error cleaning up module ${name}:`, error);
                    }
                }
            });
            this.modules.clear();
            
            // Clean up localStorage for old sessions
            this.cleanupLocalStorage();
            
            console.log('MemoryManager: Cleanup complete');
        }

        /**
         * Clean up localStorage for old sessions
         */
        cleanupLocalStorage() {
            const now = Date.now();
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            
            const keysToRemove = [];
            
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                
                // Check if it's a session-related key
                if (key && (key.includes('exam-timer-') || key.includes('session-'))) {
                    try {
                        const data = localStorage.getItem(key);
                        const parsed = JSON.parse(data);
                        
                        // Check if data has timestamp and is old
                        if (parsed.timestamp && (now - parsed.timestamp) > maxAge) {
                            keysToRemove.push(key);
                        }
                    } catch (e) {
                        // If we can't parse it, it's probably old/corrupted
                        keysToRemove.push(key);
                    }
                }
            }
            
            // Remove old keys
            keysToRemove.forEach(key => {
                localStorage.removeItem(key);
                console.log(`MemoryManager: Removed old localStorage key: ${key}`);
            });
            
            if (keysToRemove.length > 0) {
                console.log(`MemoryManager: Cleaned up ${keysToRemove.length} old localStorage entries`);
            }
        }

        /**
         * Setup automatic cleanup on page unload
         */
        setupUnloadHandler() {
            window.addEventListener('beforeunload', () => {
                this.cleanup();
            });
            
            // Also handle visibility change for mobile browsers
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    // Page is being hidden, might not come back
                    this.partialCleanup();
                }
            });
        }

        /**
         * Partial cleanup for temporary page hiding
         */
        partialCleanup() {
            // Just clear timers and intervals, keep data
            this.timers.forEach(timerId => clearTimeout(timerId));
            this.intervals.forEach(intervalId => clearInterval(intervalId));
            console.log('MemoryManager: Partial cleanup on page hide');
        }

        /**
         * Setup periodic garbage collection
         */
        setupGarbageCollection() {
            // Run garbage collection every 5 minutes
            this.gcInterval = setInterval(() => {
                this.runGarbageCollection();
            }, 5 * 60 * 1000);
        }

        /**
         * Run garbage collection
         */
        runGarbageCollection() {
            console.log('MemoryManager: Running garbage collection...');
            
            // Clean up old localStorage entries
            this.cleanupLocalStorage();
            
            // Check memory usage if available
            if (performance.memory) {
                const memoryInfo = {
                    usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
                    totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
                    jsHeapSizeLimit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
                };
                console.log('MemoryManager: Memory usage:', memoryInfo);
                
                // If memory usage is high, trigger more aggressive cleanup
                const usagePercent = (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100;
                if (usagePercent > 80) {
                    console.warn(`MemoryManager: High memory usage (${usagePercent.toFixed(1)}%), triggering aggressive cleanup`);
                    this.aggressiveCleanup();
                }
            }
        }

        /**
         * Aggressive cleanup for high memory situations
         */
        aggressiveCleanup() {
            // Clear all caches
            if ('caches' in window) {
                caches.keys().then(names => {
                    names.forEach(name => {
                        caches.delete(name);
                    });
                });
            }
            
            // Clear all localStorage except critical data
            const criticalKeys = ['user-preferences', 'auth-token'];
            const keysToKeep = new Set(criticalKeys);
            
            const allKeys = [];
            for (let i = 0; i < localStorage.length; i++) {
                allKeys.push(localStorage.key(i));
            }
            
            allKeys.forEach(key => {
                if (!keysToKeep.has(key)) {
                    localStorage.removeItem(key);
                }
            });
            
            // Force garbage collection if available
            if (window.gc) {
                window.gc();
            }
            
            console.log('MemoryManager: Aggressive cleanup complete');
        }

        /**
         * Get memory statistics
         */
        getMemoryStats() {
            const stats = {
                modules: this.modules.size,
                timers: this.timers.size,
                intervals: this.intervals.size,
                eventListeners: this.eventListeners.size,
                observers: this.observers.size,
                localStorageSize: this.getLocalStorageSize()
            };
            
            if (performance.memory) {
                stats.memory = {
                    used: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
                    total: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
                    limit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB',
                    percentage: ((performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100).toFixed(1) + '%'
                };
            }
            
            return stats;
        }

        /**
         * Get localStorage size
         */
        getLocalStorageSize() {
            let size = 0;
            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key)) {
                    size += localStorage[key].length + key.length;
                }
            }
            return (size / 1024).toFixed(2) + ' KB';
        }

        /**
         * Performance monitoring
         */
        markPerformance(label) {
            this.performanceMarks.set(label, performance.now());
        }

        measurePerformance(label, startLabel) {
            const start = this.performanceMarks.get(startLabel);
            const end = performance.now();
            if (start) {
                const duration = end - start;
                console.log(`Performance: ${label} took ${duration.toFixed(2)}ms`);
                return duration;
            }
            return null;
        }
    }

    // Create singleton instance
    window.PrimePath.memoryManager = new MemoryManager();

    // Export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = MemoryManager;
    }

})(window);