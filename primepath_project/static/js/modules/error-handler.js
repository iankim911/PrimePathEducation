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
                ...options
            };
            
            // Error queue for batch reporting
            this.errorQueue = [];
            this.retryQueue = new Map();
            
            // Setup global error handlers
            this.setupGlobalHandlers();
            
            // Setup periodic error reporting
            this.setupErrorReporting();
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
         * Get error statistics
         */
        getStats() {
            return {
                queuedErrors: this.errorQueue.length,
                retryQueue: this.retryQueue.size,
                totalErrors: this.errorQueue.length
            };
        }
    }

    // Create singleton instance
    window.PrimePath.errorHandler = new ErrorHandler();

    // Export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ErrorHandler;
    }

})(window);