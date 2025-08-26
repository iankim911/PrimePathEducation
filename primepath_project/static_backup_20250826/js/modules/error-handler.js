/**
 * Error Handler Module
 * Provides comprehensive error handling, retry logic, and user notifications
 * Fixes silent failures after 9000+ sessions
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    class ErrorHandler {
        constructor(options = {}) {
            this.options = {
                maxRetries: 3,
                retryDelay: 1000,
                exponentialBackoff: true,
                notifyUser: true,
                logToServer: true,
                enableBrowserCompatibility: true,
                enablePerformanceMonitoring: true,
                enableMatrixSpecificHandling: true,
                debugMode: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
                ...options
            };
            
            // Error queue for batch reporting
            this.errorQueue = [];
            this.retryQueue = new Map();
            
            // Browser compatibility tracking
            this.browserInfo = this.detectBrowserInfo();
            
            // Performance monitoring
            this.performanceMetrics = {
                errorCount: 0,
                avgResponseTime: 0,
                slowOperations: [],
                memoryUsage: []
            };
            
            // RoutineTest specific error patterns
            this.routineTestPatterns = {
                matrixErrors: [],
                examErrors: [],
                sessionErrors: [],
                audioErrors: []
            };
            
            // Setup global error handlers
            this.setupGlobalHandlers();
            
            // Setup periodic error reporting
            this.setupErrorReporting();
            
            // Setup browser compatibility checks
            if (this.options.enableBrowserCompatibility) {
                this.setupBrowserCompatibility();
            }
            
            // Setup performance monitoring
            if (this.options.enablePerformanceMonitoring) {
                this.setupPerformanceMonitoring();
            }
            
            console.log('%c[ErrorHandler] Enhanced error handling initialized', 
                       'background: #28a745; color: white; padding: 2px 6px; border-radius: 3px;', 
                       this.browserInfo);
        }

        /**
         * Setup global error handlers
         */
        setupGlobalHandlers() {
            // Handle uncaught errors
            window.addEventListener('error', (event) => {
                this.handleError({
                    type: 'uncaught',
                    message: event.message,
                    filename: event.filename,
                    line: event.lineno,
                    column: event.colno,
                    error: event.error
                });
            });
            
            // Handle unhandled promise rejections
            window.addEventListener('unhandledrejection', (event) => {
                this.handleError({
                    type: 'unhandled_promise',
                    reason: event.reason,
                    promise: event.promise
                });
                event.preventDefault();
            });
        }

        /**
         * Handle an error with logging and optional retry
         */
        handleError(error, context = {}, retryable = false) {
            // Log error
            console.error('ErrorHandler:', error, context);
            
            // Add to error queue
            this.errorQueue.push({
                error,
                context,
                timestamp: Date.now(),
                url: window.location.href,
                userAgent: navigator.userAgent
            });
            
            // Notify user if enabled
            if (this.options.notifyUser) {
                this.notifyUser(error, context);
            }
            
            // Handle retry if applicable
            if (retryable && context.retryFunction) {
                return this.retry(context.retryFunction, context);
            }
            
            return Promise.reject(error);
        }

        /**
         * Retry a failed operation with exponential backoff
         */
        async retry(fn, context = {}) {
            const key = context.key || fn.toString();
            
            if (!this.retryQueue.has(key)) {
                this.retryQueue.set(key, { count: 0, lastAttempt: 0 });
            }
            
            const retryInfo = this.retryQueue.get(key);
            
            if (retryInfo.count >= this.options.maxRetries) {
                this.retryQueue.delete(key);
                throw new Error(`Max retries (${this.options.maxRetries}) exceeded`);
            }
            
            retryInfo.count++;
            
            // Calculate delay with exponential backoff
            let delay = this.options.retryDelay;
            if (this.options.exponentialBackoff) {
                delay = this.options.retryDelay * Math.pow(2, retryInfo.count - 1);
            }
            
// REMOVED:             console.log(`ErrorHandler: Retrying operation (attempt ${retryInfo.count}/${this.options.maxRetries}) after ${delay}ms`);
            
            // Show retry notification
            if (this.options.notifyUser) {
                this.showRetryNotification(retryInfo.count, this.options.maxRetries);
            }
            
            // Wait before retry
            await this.sleep(delay);
            
            try {
                const result = await fn();
                // Success - clear retry info
                this.retryQueue.delete(key);
                if (this.options.notifyUser) {
                    this.showSuccessNotification('Operation succeeded after retry');
                }
                return result;
            } catch (error) {
                // Failed again
                if (retryInfo.count >= this.options.maxRetries) {
                    this.retryQueue.delete(key);
                    this.showErrorNotification('Operation failed after multiple retries. Please refresh the page.');
                    throw error;
                }
                // Try again
                return this.retry(fn, context);
            }
        }

        /**
         * Retry an AJAX request with enhanced error handling
         */
        async retryAjax(url, options = {}, context = {}) {
            const maxRetries = context.maxRetries || this.options.maxRetries;
            let lastError = null;
            
            for (let attempt = 1; attempt <= maxRetries; attempt++) {
                try {
                    // Add retry headers
                    options.headers = options.headers || {};
                    options.headers['X-Retry-Attempt'] = attempt;
                    
                    const response = await fetch(url, options);
                    
                    // Check for server errors
                    if (!response.ok) {
                        if (response.status >= 500) {
                            // Server error - retry
                            throw new Error(`Server error: ${response.status}`);
                        } else if (response.status === 403) {
                            // CSRF token might be expired
                            await this.refreshCSRFToken();
                            // Update headers with new token
                            options.headers['X-CSRFToken'] = this.getCSRFToken();
                            throw new Error('CSRF token refreshed, retrying...');
                        } else {
                            // Client error - don't retry
                            throw new Error(`Client error: ${response.status}`);
                        }
                    }
                    
                    // Success
                    if (attempt > 1) {
// REMOVED:                         console.log(`ErrorHandler: AJAX request succeeded on attempt ${attempt}`);
                    }
                    return response;
                    
                } catch (error) {
                    lastError = error;
                    console.warn(`ErrorHandler: AJAX attempt ${attempt} failed:`, error);
                    
                    // Don't retry on client errors (4xx)
                    if (error.message.includes('Client error')) {
                        throw error;
                    }
                    
                    // Calculate delay for next retry
                    if (attempt < maxRetries) {
                        const delay = this.options.exponentialBackoff 
                            ? this.options.retryDelay * Math.pow(2, attempt - 1)
                            : this.options.retryDelay;
                        
                        await this.sleep(delay);
                    }
                }
            }
            
            // All retries failed
            this.handleError(lastError, { url, options, context });
            throw lastError;
        }

        /**
         * Refresh CSRF token
         */
        async refreshCSRFToken() {
            try {
                const response = await fetch('/api/csrf-token/');
                const data = await response.json();
                if (data.token) {
                    // Update token in APP_CONFIG
                    if (window.APP_CONFIG) {
                        window.APP_CONFIG.csrf = data.token;
                    }
                    // Update meta tag
                    const metaTag = document.querySelector('meta[name="csrf-token"]');
                    if (metaTag) {
                        metaTag.content = data.token;
                    }
// REMOVED:                     console.log('ErrorHandler: CSRF token refreshed');
                }
            } catch (error) {
                console.error('ErrorHandler: Failed to refresh CSRF token:', error);
            }
        }

        /**
         * Get current CSRF token
         */
        getCSRFToken() {
            // Try multiple sources
            if (window.APP_CONFIG && window.APP_CONFIG.csrf) {
                return window.APP_CONFIG.csrf;
            }
            
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            if (metaTag) {
                return metaTag.content;
            }
            
            // Try cookie
            const cookie = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='));
            if (cookie) {
                return cookie.split('=')[1];
            }
            
            return null;
        }

        /**
         * Notify user of error
         */
        notifyUser(error, context) {
            const message = this.getErrorMessage(error, context);
            this.showErrorNotification(message);
        }

        /**
         * Get user-friendly error message
         */
        getErrorMessage(error, context) {
            if (context.userMessage) {
                return context.userMessage;
            }
            
            if (error.message) {
                if (error.message.includes('Network')) {
                    return 'Network connection lost. Please check your internet connection.';
                }
                if (error.message.includes('Server error')) {
                    return 'Server is temporarily unavailable. Please try again in a moment.';
                }
                if (error.message.includes('timeout')) {
                    return 'Request timed out. Please try again.';
                }
            }
            
            return 'An unexpected error occurred. Please refresh the page and try again.';
        }

        /**
         * Show error notification to user
         */
        showErrorNotification(message) {
            this.showNotification(message, 'error');
        }

        /**
         * Show success notification to user
         */
        showSuccessNotification(message) {
            this.showNotification(message, 'success');
        }

        /**
         * Show retry notification
         */
        showRetryNotification(attempt, maxAttempts) {
            this.showNotification(
                `Retrying... (Attempt ${attempt}/${maxAttempts})`,
                'info'
            );
        }

        /**
         * Show notification to user
         */
        showNotification(message, type = 'info') {
            // Remove any existing notification
            const existing = document.querySelector('.primepath-notification');
            if (existing) {
                existing.remove();
            }
            
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `primepath-notification primepath-notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-message">${message}</span>
                    <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;
            
            // Style the notification
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 10000;
                max-width: 400px;
                animation: slideIn 0.3s ease-out;
                background: ${type === 'error' ? '#ff4444' : type === 'success' ? '#44ff44' : '#4444ff'};
                color: white;
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 5 seconds for non-error notifications
            if (type !== 'error') {
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 5000);
            }
        }

        /**
         * Setup periodic error reporting to server
         */
        setupErrorReporting() {
            // Report errors every 30 seconds
            setInterval(() => {
                if (this.errorQueue.length > 0) {
                    this.reportErrors();
                }
            }, 30000);
        }

        /**
         * Report errors to server
         */
        async reportErrors() {
            if (!this.options.logToServer || this.errorQueue.length === 0) {
                return;
            }
            
            const errors = [...this.errorQueue];
            this.errorQueue = [];
            
            try {
                const response = await fetch('/api/errors/report/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ errors })
                });
                
                if (!response.ok) {
                    // Put errors back in queue
                    this.errorQueue.push(...errors);
                }
            } catch (error) {
                // Put errors back in queue
                this.errorQueue.push(...errors);
                console.error('ErrorHandler: Failed to report errors:', error);
            }
        }

        /**
         * Sleep utility
         */
        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        /**
         * Detect browser information for compatibility tracking
         */
        detectBrowserInfo() {
            const ua = navigator.userAgent;
            const info = {
                browser: 'Unknown',
                version: 'Unknown',
                mobile: /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua),
                features: {
                    fetch: typeof fetch !== 'undefined',
                    promise: typeof Promise !== 'undefined',
                    arrow: false,
                    const: false,
                    let: false,
                    async: false
                }
            };
            
            // Detect browser
            if (ua.indexOf('Chrome') > -1) {
                info.browser = 'Chrome';
                const match = ua.match(/Chrome\/(\d+)/);
                info.version = match ? match[1] : 'Unknown';
            } else if (ua.indexOf('Firefox') > -1) {
                info.browser = 'Firefox';
                const match = ua.match(/Firefox\/(\d+)/);
                info.version = match ? match[1] : 'Unknown';
            } else if (ua.indexOf('Safari') > -1) {
                info.browser = 'Safari';
                const match = ua.match(/Version\/(\d+)/);
                info.version = match ? match[1] : 'Unknown';
            } else if (ua.indexOf('Edge') > -1) {
                info.browser = 'Edge';
                const match = ua.match(/Edge\/(\d+)/);
                info.version = match ? match[1] : 'Unknown';
            }
            
            // Test JavaScript features
            try {
                eval('const test = 1;');
                info.features.const = true;
            } catch (e) { /* ignored */ }
            
            try {
                eval('let test = 1;');
                info.features.let = true;
            } catch (e) { /* ignored */ }
            
            try {
                eval('() => {}');
                info.features.arrow = true;
            } catch (e) { /* ignored */ }
            
            try {
                eval('async function test() {}');
                info.features.async = true;
            } catch (e) { /* ignored */ }
            
            return info;
        }
        
        /**
         * Setup browser compatibility checks
         */
        setupBrowserCompatibility() {
            const incompatibilities = [];
            
            // Check for required features
            if (!this.browserInfo.features.fetch) {
                incompatibilities.push('fetch API not supported');
            }
            
            if (!this.browserInfo.features.promise) {
                incompatibilities.push('Promise not supported');
            }
            
            if (incompatibilities.length > 0) {
                this.showCompatibilityWarning(incompatibilities);
            }
            
            // Log browser info for debugging
            if (this.options.debugMode) {
                console.log('%c[ErrorHandler] Browser Compatibility Check', 
                           'background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px;');
                console.table(this.browserInfo);
                
                if (incompatibilities.length > 0) {
                    console.warn('%c[ErrorHandler] Compatibility Issues:', 
                                'background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px;',
                                incompatibilities);
                }
            }
        }
        
        /**
         * Setup performance monitoring
         */
        setupPerformanceMonitoring() {
            // Monitor memory usage periodically
            if (performance.memory) {
                setInterval(() => {
                    this.performanceMetrics.memoryUsage.push({
                        timestamp: Date.now(),
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    });
                    
                    // Keep only last 100 measurements
                    if (this.performanceMetrics.memoryUsage.length > 100) {
                        this.performanceMetrics.memoryUsage.shift();
                    }
                }, 30000); // Every 30 seconds
            }
            
            // Monitor slow operations
            this.originalFetch = window.fetch;
            window.fetch = (...args) => {
                const start = performance.now();
                return this.originalFetch.apply(this, args).then(response => {
                    const duration = performance.now() - start;
                    
                    if (duration > 2000) { // Slower than 2 seconds
                        this.performanceMetrics.slowOperations.push({
                            url: args[0],
                            duration: duration,
                            timestamp: Date.now()
                        });
                        
                        if (this.options.debugMode) {
                            console.warn(`%c[ErrorHandler] Slow operation detected: ${duration.toFixed(0)}ms`, 
                                        'background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px;',
                                        args[0]);
                        }
                    }
                    
                    return response;
                }).catch(error => {
                    const duration = performance.now() - start;
                    this.handleError(error, {
                        operation: 'fetch',
                        url: args[0],
                        duration: duration,
                        category: 'network'
                    });
                    throw error;
                });
            };
        }
        
        /**
         * Handle RoutineTest specific errors
         */
        handleRoutineTestError(error, context = {}) {
            const category = context.category || 'general';
            
            // Categorize by RoutineTest components
            switch (category) {
                case 'matrix':
                    this.routineTestPatterns.matrixErrors.push({
                        error: error,
                        context: context,
                        timestamp: Date.now()
                    });
                    break;
                case 'exam':
                    this.routineTestPatterns.examErrors.push({
                        error: error,
                        context: context,
                        timestamp: Date.now()
                    });
                    break;
                case 'session':
                    this.routineTestPatterns.sessionErrors.push({
                        error: error,
                        context: context,
                        timestamp: Date.now()
                    });
                    break;
                case 'audio':
                    this.routineTestPatterns.audioErrors.push({
                        error: error,
                        context: context,
                        timestamp: Date.now()
                    });
                    break;
            }
            
            // Limit arrays to prevent memory leaks
            Object.keys(this.routineTestPatterns).forEach(key => {
                if (this.routineTestPatterns[key].length > 50) {
                    this.routineTestPatterns[key].shift();
                }
            });
            
            // Enhanced error handling for specific patterns
            if (category === 'matrix' && error.message.includes('ExamScheduleMatrix')) {
                context.userMessage = 'Schedule matrix is temporarily unavailable. Please refresh the page.';
                context.retryable = true;
            } else if (category === 'audio' && error.message.includes('AudioContext')) {
                context.userMessage = 'Audio playback failed. Please check your browser settings.';
                context.retryable = false;
            }
            
            return this.handleError(error, context);
        }
        
        /**
         * Show compatibility warning
         */
        showCompatibilityWarning(incompatibilities) {
            const message = `Your browser may not support all features. Issues detected: ${incompatibilities.join(', ')}. Please consider updating your browser.`;
            this.showNotification(message, 'warning', 10000); // Show for 10 seconds
        }
        
        /**
         * Enhanced notification with warning type
         */
        showNotification(message, type = 'info', duration = 5000) {
            // Remove any existing notification
            const existing = document.querySelector('.primepath-notification');
            if (existing) {
                existing.remove();
            }
            
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `primepath-notification primepath-notification-${type}`;
            
            // Icon based on type
            const icons = {
                error: '❌',
                success: '✅',
                info: 'ℹ️',
                warning: '⚠️'
            };
            
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-icon">${icons[type] || 'ℹ️'}</span>
                    <span class="notification-message">${message}</span>
                    <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;
            
            // Enhanced styling
            const colors = {
                error: { bg: '#dc3545', text: 'white' },
                success: { bg: '#28a745', text: 'white' },
                info: { bg: '#17a2b8', text: 'white' },
                warning: { bg: '#ffc107', text: 'black' }
            };
            
            const color = colors[type] || colors.info;
            
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                max-width: 400px;
                animation: slideIn 0.3s ease-out;
                background: ${color.bg};
                color: ${color.text};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                line-height: 1.4;
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove based on type and duration
            if (type !== 'error') {
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.style.animation = 'slideOut 0.3s ease-out forwards';
                        setTimeout(() => notification.remove(), 300);
                    }
                }, duration);
            }
        }
        
        /**
         * Get comprehensive error statistics
         */
        getStats() {
            return {
                queuedErrors: this.errorQueue.length,
                retryQueue: this.retryQueue.size,
                totalErrors: this.performanceMetrics.errorCount,
                browserInfo: this.browserInfo,
                performanceMetrics: {
                    avgResponseTime: this.performanceMetrics.avgResponseTime,
                    slowOperationsCount: this.performanceMetrics.slowOperations.length,
                    memoryUsagePoints: this.performanceMetrics.memoryUsage.length
                },
                routineTestPatterns: {
                    matrixErrors: this.routineTestPatterns.matrixErrors.length,
                    examErrors: this.routineTestPatterns.examErrors.length,
                    sessionErrors: this.routineTestPatterns.sessionErrors.length,
                    audioErrors: this.routineTestPatterns.audioErrors.length
                }
            };
        }
        
        /**
         * Generate comprehensive error report
         */
        generateErrorReport() {
            const report = {
                timestamp: new Date().toISOString(),
                browserInfo: this.browserInfo,
                stats: this.getStats(),
                recentErrors: this.errorQueue.slice(-10), // Last 10 errors
                performanceIssues: this.performanceMetrics.slowOperations.slice(-5), // Last 5 slow operations
                routineTestIssues: {
                    matrixErrors: this.routineTestPatterns.matrixErrors.slice(-3),
                    examErrors: this.routineTestPatterns.examErrors.slice(-3),
                    sessionErrors: this.routineTestPatterns.sessionErrors.slice(-3),
                    audioErrors: this.routineTestPatterns.audioErrors.slice(-3)
                }
            };
            
            if (this.options.debugMode) {
                console.log('%c[ErrorHandler] Comprehensive Error Report', 
                           'background: #6f42c1; color: white; padding: 2px 6px; border-radius: 3px;');
                console.log(report);
            }
            
            return report;
        }
    }

    // Create singleton instance
    window.PrimePath.errorHandler = new ErrorHandler();

    // Export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ErrorHandler;
    }

})(window);