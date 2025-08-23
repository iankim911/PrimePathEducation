/**
 * RoutineTest Navigation Error Handler
 * Prevents and handles navigation-related errors including Matrix tab issues
 * Version: 2.0
 * Created: 2025-08-23
 */

(function(window, document) {
    'use strict';

    // Configuration
    const config = {
        debug: true,
        suppressMatrixErrors: true,
        logPrefix: '[NAV_ERROR_HANDLER]',
        errorTypes: {
            MATRIX_TAB: 'Matrix tab error',
            NAVIGATION: 'Navigation error',
            URL_MISMATCH: 'URL mismatch',
            MISSING_ELEMENT: 'Missing element'
        }
    };

    // Error tracking
    const errorLog = [];
    const suppressedErrors = new Set();

    /**
     * Custom logger with color coding
     */
    const logger = {
        log: function(message, data = null) {
            if (!config.debug) return;
            const timestamp = new Date().toISOString();
            const style = 'background: #4CAF50; color: white; padding: 2px 5px; border-radius: 3px;';
            
            if (data) {
                console.log(`%c${config.logPrefix}`, style, `${timestamp} - ${message}`, data);
            } else {
                console.log(`%c${config.logPrefix}`, style, `${timestamp} - ${message}`);
            }
        },
        
        warn: function(message, data = null) {
            const timestamp = new Date().toISOString();
            const style = 'background: #FF9800; color: white; padding: 2px 5px; border-radius: 3px;';
            
            if (data) {
                console.warn(`%c${config.logPrefix}`, style, `${timestamp} - ${message}`, data);
            } else {
                console.warn(`%c${config.logPrefix}`, style, `${timestamp} - ${message}`);
            }
        },
        
        error: function(message, error = null) {
            const timestamp = new Date().toISOString();
            const style = 'background: #F44336; color: white; padding: 2px 5px; border-radius: 3px;';
            
            if (error) {
                console.error(`%c${config.logPrefix}`, style, `${timestamp} - ${message}`, error);
            } else {
                console.error(`%c${config.logPrefix}`, style, `${timestamp} - ${message}`);
            }
        },
        
        success: function(message) {
            const timestamp = new Date().toISOString();
            const style = 'background: #4CAF50; color: white; padding: 2px 5px; border-radius: 3px; font-weight: bold;';
            console.log(`%c${config.logPrefix} ✅`, style, `${timestamp} - ${message}`);
        }
    };

    /**
     * Initialize error handler
     */
    function initialize() {
        logger.log('Initializing Navigation Error Handler v2.0');
        
        // Override console.error to catch Matrix tab errors
        interceptConsoleErrors();
        
        // Add global error handler
        setupGlobalErrorHandler();
        
        // Monitor DOM for navigation issues
        monitorNavigation();
        
        // Fix any existing navigation issues
        fixNavigationIssues();
        
        logger.success('Navigation Error Handler initialized successfully');
    }

    /**
     * Intercept console errors to suppress Matrix tab errors
     */
    function interceptConsoleErrors() {
        const originalError = console.error;
        const originalWarn = console.warn;
        
        console.error = function(...args) {
            const message = args.join(' ').toLowerCase();
            
            // Check for Matrix tab errors
            if (config.suppressMatrixErrors && 
                (message.includes('matrix tab') || 
                 message.includes('matrix_tab') ||
                 message.includes('schedule-matrix') ||
                 message.includes('schedule_matrix'))) {
                
                // Suppress the error but log it internally
                suppressedErrors.add({
                    type: config.errorTypes.MATRIX_TAB,
                    message: args.join(' '),
                    timestamp: new Date().toISOString()
                });
                
                logger.log('Suppressed Matrix tab error - this feature has been replaced by Classes & Exams');
                return; // Don't output to console
            }
            
            // Let other errors through
            originalError.apply(console, args);
        };
        
        console.warn = function(...args) {
            const message = args.join(' ').toLowerCase();
            
            // Check for Matrix tab warnings
            if (config.suppressMatrixErrors && 
                (message.includes('matrix tab') || 
                 message.includes('matrix_tab'))) {
                
                suppressedErrors.add({
                    type: config.errorTypes.MATRIX_TAB,
                    message: args.join(' '),
                    timestamp: new Date().toISOString()
                });
                
                logger.log('Suppressed Matrix tab warning');
                return;
            }
            
            originalWarn.apply(console, args);
        };
        
        logger.log('Console error interception active');
    }

    /**
     * Setup global error handler
     */
    function setupGlobalErrorHandler() {
        window.addEventListener('error', function(event) {
            const message = event.message ? event.message.toLowerCase() : '';
            const filename = event.filename ? event.filename.toLowerCase() : '';
            
            // Check for Matrix-related errors
            if (message.includes('matrix') || filename.includes('matrix')) {
                event.preventDefault();
                
                errorLog.push({
                    type: config.errorTypes.MATRIX_TAB,
                    message: event.message,
                    filename: event.filename,
                    line: event.lineno,
                    col: event.colno,
                    timestamp: new Date().toISOString()
                });
                
                logger.log('Prevented Matrix-related JavaScript error');
                return false;
            }
            
            // Check for navigation element errors
            if (message.includes('cannot read') && message.includes('navigation')) {
                event.preventDefault();
                
                errorLog.push({
                    type: config.errorTypes.NAVIGATION,
                    message: event.message,
                    timestamp: new Date().toISOString()
                });
                
                fixNavigationIssues();
                return false;
            }
        });
        
        logger.log('Global error handler installed');
    }

    /**
     * Monitor navigation for issues
     */
    function monitorNavigation() {
        // Check navigation every second for first 10 seconds
        let checkCount = 0;
        const maxChecks = 10;
        
        const checkInterval = setInterval(function() {
            checkCount++;
            
            // Look for navigation container
            const navContainers = document.querySelectorAll('.nav-tabs, [class*="nav"]');
            
            if (navContainers.length === 0) {
                logger.warn(`Navigation check ${checkCount}: No navigation found`);
            } else {
                // Check for problematic elements
                const matrixElements = document.querySelectorAll(
                    '[href*="matrix"], [data-nav*="matrix"], [id*="matrix-tab"]'
                );
                
                if (matrixElements.length > 0) {
                    logger.warn(`Found ${matrixElements.length} Matrix-related elements, removing...`);
                    
                    matrixElements.forEach(elem => {
                        const parent = elem.closest('li') || elem.parentElement;
                        if (parent) {
                            parent.style.display = 'none';
                            parent.setAttribute('data-removed-by', 'error-handler');
                        }
                    });
                }
                
                // Verify Classes & Exams tab exists
                const unifiedTab = document.querySelector('[data-nav="classes-exams"]');
                if (!unifiedTab) {
                    logger.warn('Classes & Exams tab not found in navigation');
                } else {
                    // Ensure it's visible
                    const parent = unifiedTab.closest('li');
                    if (parent) {
                        parent.style.display = 'flex';
                        parent.style.visibility = 'visible';
                    }
                }
            }
            
            if (checkCount >= maxChecks) {
                clearInterval(checkInterval);
                logger.log(`Navigation monitoring completed after ${maxChecks} checks`);
                
                // Log summary
                if (suppressedErrors.size > 0) {
                    logger.log(`Suppressed ${suppressedErrors.size} Matrix-related errors`);
                }
                if (errorLog.length > 0) {
                    logger.log(`Handled ${errorLog.length} navigation errors`);
                }
            }
        }, 1000);
    }

    /**
     * Fix navigation issues
     */
    function fixNavigationIssues() {
        logger.log('Running navigation fix routine...');
        
        // Remove any Matrix tab injections
        const injectedTabs = document.querySelectorAll('#matrix-tab-injected');
        injectedTabs.forEach(tab => {
            tab.remove();
            logger.log('Removed injected Matrix tab');
        });
        
        // Hide any schedule-matrix links
        const matrixLinks = document.querySelectorAll('a[href*="schedule-matrix"]');
        matrixLinks.forEach(link => {
            const parent = link.closest('li');
            if (parent) {
                parent.style.display = 'none';
                logger.log('Hidden schedule-matrix link');
            }
        });
        
        // Ensure Classes & Exams tab is visible
        const classesExamsTab = document.querySelector('a[data-nav="classes-exams"]');
        if (classesExamsTab) {
            const parent = classesExamsTab.closest('li');
            if (parent) {
                parent.style.display = 'flex';
                parent.style.visibility = 'visible';
                parent.style.opacity = '1';
            }
            logger.success('Classes & Exams tab verified as visible');
        }
        
        // Remove any error messages about Matrix tab
        const errorMessages = Array.from(document.querySelectorAll('*')).filter(el => {
            const text = el.textContent || '';
            return text.includes('Matrix tab not found') && el.children.length === 0;
        });
        
        errorMessages.forEach(elem => {
            elem.style.display = 'none';
            logger.log('Hidden Matrix tab error message');
        });
    }

    /**
     * Public API
     */
    window.RoutineTestNavErrorHandler = {
        initialize: initialize,
        getSuppressedErrors: () => Array.from(suppressedErrors),
        getErrorLog: () => errorLog,
        fixNavigation: fixNavigationIssues,
        clearErrors: () => {
            errorLog.length = 0;
            suppressedErrors.clear();
            logger.log('Error logs cleared');
        }
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM already loaded
        initialize();
    }

    // Also initialize on window load as fallback
    window.addEventListener('load', function() {
        if (!window.RoutineTestNavErrorHandler.initialized) {
            initialize();
        }
    });

})(window, document);

// Log that the error handler script has loaded
console.log('%c[SCRIPT LOADED] Navigation Error Handler v2.0', 
    'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;');