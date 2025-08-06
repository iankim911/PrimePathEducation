/**
 * PrimePath Debug System - Comprehensive Logging for Chrome DevTools
 * Usage: Include this script first, then use PrimeDebug methods throughout your code
 */

window.PrimeDebug = (function() {
    'use strict';
    
    // Configuration
    const config = {
        enabled: true,
        maxLogHistory: 1000,
        logLevels: {
            ERROR: { priority: 1, color: '#ff4444', bgColor: '#fff0f0' },
            WARN: { priority: 2, color: '#ff8800', bgColor: '#fff8f0' },
            INFO: { priority: 3, color: '#0088ff', bgColor: '#f0f8ff' },
            DEBUG: { priority: 4, color: '#00aa00', bgColor: '#f0fff0' },
            TRACE: { priority: 5, color: '#888888', bgColor: '#f8f8f8' }
        },
        categories: {
            INIT: 'System Initialization',
            LOAD: 'Page/Component Loading',
            USER: 'User Interactions',
            API: 'API Calls & Responses',
            PDF: 'PDF Operations',
            AUDIO: 'Audio Operations',
            FORM: 'Form Processing',
            NAV: 'Navigation',
            TIMER: 'Timer Operations',
            SAVE: 'Save Operations',
            ERROR: 'Error Handling',
            DB: 'Database Operations',
            TEMPLATE: 'Template Rendering'
        }
    };
    
    // Internal state
    let logHistory = [];
    let sessionId = Date.now();
    let startTime = performance.now();
    
    // Utility functions
    function getTimestamp() {
        const elapsed = performance.now() - startTime;
        const seconds = (elapsed / 1000).toFixed(3);
        return `[+${seconds}s]`;
    }
    
    function formatMessage(level, category, message, data = null) {
        const timestamp = getTimestamp();
        const prefix = `🔍 PRIME-${level} ${timestamp} [${category}]`;
        return {
            prefix,
            message,
            data,
            fullMessage: data ? `${prefix} ${message}` : `${prefix} ${message}`
        };
    }
    
    function addToHistory(level, category, message, data, trace) {
        logHistory.push({
            timestamp: new Date().toISOString(),
            sessionTime: performance.now() - startTime,
            level,
            category,
            message,
            data,
            trace,
            url: window.location.href,
            userAgent: navigator.userAgent.substring(0, 100)
        });
        
        // Trim history if too long
        if (logHistory.length > config.maxLogHistory) {
            logHistory = logHistory.slice(-config.maxLogHistory);
        }
    }
    
    function log(level, category, message, data = null) {
        if (!config.enabled) return;
        
        const formatted = formatMessage(level, category, message, data);
        const levelConfig = config.logLevels[level];
        const trace = new Error().stack;
        
        // Add to history
        addToHistory(level, category, message, data, trace);
        
        // Console output with styling
        const style = `color: ${levelConfig.color}; background: ${levelConfig.bgColor}; padding: 2px 4px; border-radius: 3px; font-weight: bold;`;
        
        if (data) {
            console.groupCollapsed(`%c${formatted.prefix}%c ${message}`, style, 'color: #333;');
            console.log('📊 Data:', data);
            if (level === 'ERROR') {
                console.log('📍 Stack trace:', trace);
            }
            console.groupEnd();
        } else {
            console.log(`%c${formatted.prefix}%c ${message}`, style, 'color: #333;');
        }
    }
    
    // Public API
    return {
        // Logging methods
        error: (category, message, data) => log('ERROR', category, message, data),
        warn: (category, message, data) => log('WARN', category, message, data),
        info: (category, message, data) => log('INFO', category, message, data),
        debug: (category, message, data) => log('DEBUG', category, message, data),
        trace: (category, message, data) => log('TRACE', category, message, data),
        
        // Specialized logging methods
        userAction: (action, details) => log('INFO', 'USER', `User Action: ${action}`, details),
        apiCall: (method, url, data) => log('INFO', 'API', `${method} ${url}`, data),
        apiResponse: (method, url, response, success) => {
            const level = success ? 'INFO' : 'ERROR';
            log(level, 'API', `Response: ${method} ${url}`, response);
        },
        formSubmit: (formName, data) => log('INFO', 'FORM', `Form Submit: ${formName}`, data),
        formError: (formName, error) => log('ERROR', 'FORM', `Form Error: ${formName}`, error),
        pageLoad: (pageName, data) => log('INFO', 'LOAD', `Page Loaded: ${pageName}`, data),
        componentInit: (componentName, data) => log('DEBUG', 'INIT', `Component Init: ${componentName}`, data),
        timerEvent: (event, data) => log('DEBUG', 'TIMER', `Timer: ${event}`, data),
        saveOperation: (operation, success, data) => {
            const level = success ? 'INFO' : 'ERROR';
            log(level, 'SAVE', `Save ${operation}: ${success ? 'SUCCESS' : 'FAILED'}`, data);
        },
        
        // Additional specialized logging for PrimePath functionality
        pdfOperation: (operation, success, data) => {
            const level = success ? 'INFO' : 'ERROR';
            log(level, 'PDF', `PDF ${operation}: ${success ? 'SUCCESS' : 'FAILED'}`, data);
        },
        audioOperation: (operation, audioId, data) => log('INFO', 'AUDIO', `Audio ${operation}: ${audioId}`, data),
        fileUpload: (fileName, size, type, success, error = null) => {
            const level = success ? 'INFO' : 'ERROR';
            log(level, 'FORM', `File Upload: ${fileName}`, {
                fileName,
                fileSize: size,
                fileType: type,
                success,
                error
            });
        },
        examOperation: (operation, examId, data) => log('INFO', 'EXAM', `Exam ${operation}: ${examId}`, data),
        studentSession: (operation, sessionId, data) => log('INFO', 'SESSION', `Student Session ${operation}: ${sessionId}`, data),
        placementResult: (studentName, level, score, data) => log('INFO', 'PLACEMENT', `Placement Result: ${studentName} -> ${level}`, {
            studentName,
            placementLevel: level,
            score,
            ...data
        }),
        databaseOperation: (operation, table, success, data) => {
            const level = success ? 'INFO' : 'ERROR';
            log(level, 'DB', `DB ${operation} on ${table}: ${success ? 'SUCCESS' : 'FAILED'}`, data);
        },
        
        // Utility methods
        startGroup: (title) => {
            if (!config.enabled) return;
            console.group(`🔍 PRIME-GROUP: ${title}`);
        },
        endGroup: () => {
            if (!config.enabled) return;
            console.groupEnd();
        },
        
        // Performance monitoring
        startTimer: (timerName) => {
            if (!config.enabled) return;
            console.time(`PRIME-TIMER: ${timerName}`);
            log('DEBUG', 'TIMER', `Started timer: ${timerName}`);
        },
        endTimer: (timerName) => {
            if (!config.enabled) return;
            console.timeEnd(`PRIME-TIMER: ${timerName}`);
            log('DEBUG', 'TIMER', `Ended timer: ${timerName}`);
        },
        
        // System info
        getSystemInfo: () => ({
            sessionId,
            startTime: new Date(Date.now() - (performance.now() - startTime)).toISOString(),
            currentTime: new Date().toISOString(),
            sessionDuration: performance.now() - startTime,
            url: window.location.href,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            logCount: logHistory.length
        }),
        
        // Get log history (safe access)
        getLogHistory: () => logHistory || [],
        
        // Export logs
        exportLogs: () => {
            const systemInfo = PrimeDebug.getSystemInfo();
            const exportData = {
                systemInfo,
                config,
                logs: logHistory
            };
            
            console.log('📋 PrimePath Debug Export:', exportData);
            
            // Create downloadable file
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `primepath-debug-${sessionId}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            return exportData;
        },
        
        // Clear logs
        clearLogs: () => {
            logHistory = [];
            console.clear();
            log('INFO', 'INIT', 'Debug logs cleared');
        },
        
        // Toggle debugging
        enable: () => {
            config.enabled = true;
            log('INFO', 'INIT', 'Debug logging enabled');
        },
        disable: () => {
            config.enabled = false;
            console.log('🔍 PRIME-INFO: Debug logging disabled');
        },
        
        // Configuration
        setLogLevel: (minLevel) => {
            // Implementation for filtering by log level
            log('INFO', 'INIT', `Log level set to: ${minLevel}`);
        },
        
        // Error boundary
        captureError: (error, context = 'Unknown') => {
            const errorInfo = {
                message: error.message,
                stack: error.stack,
                name: error.name,
                context,
                url: window.location.href,
                timestamp: new Date().toISOString()
            };
            
            log('ERROR', 'ERROR', `Uncaught error in ${context}`, errorInfo);
            
            // Send to server if needed (implement later)
            return errorInfo;
        }
    };
})();

// Global error handler
window.addEventListener('error', function(event) {
    PrimeDebug.captureError(event.error || new Error(event.message), 'Global Error Handler');
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    PrimeDebug.captureError(new Error(event.reason), 'Unhandled Promise Rejection');
});

// Initialize debug system
document.addEventListener('DOMContentLoaded', function() {
    PrimeDebug.info('INIT', 'PrimePath Debug System Initialized', PrimeDebug.getSystemInfo());
    
    // Add debug panel to page (optional, for quick access)  
    if (window.PrimeDebug && window.PrimeDebug.getSystemInfo) {
        const debugPanel = document.createElement('div');
        debugPanel.innerHTML = `
            <div id="prime-debug-panel" style="position: fixed; top: 10px; right: 10px; z-index: 9999; background: rgba(0,0,0,0.9); color: white; padding: 12px; border-radius: 8px; font-family: 'Consolas', 'Monaco', monospace; font-size: 11px; max-width: 350px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid #444;">
                <div style="font-weight: bold; margin-bottom: 8px; color: #4fc3f7; font-size: 13px;">🔍 PrimePath Debug Console</div>
                <div style="margin-bottom: 3px;">Session: <span style="color: #81c784;">${PrimeDebug.getSystemInfo().sessionId}</span></div>
                <div style="margin-bottom: 3px;">Logs: <span id="debug-log-count" style="color: #ffb74d;">0</span></div>
                <div style="margin-bottom: 3px;">Errors: <span id="debug-error-count" style="color: #f06292;">0</span></div>
                <div style="margin-bottom: 8px;">Uptime: <span id="debug-uptime" style="color: #a5d6a7;">0s</span></div>
                <div style="margin-bottom: 8px; font-size: 10px; border-top: 1px solid #555; padding-top: 8px;">
                    <div>Page: <span id="debug-page-name" style="color: #ce93d8;">Loading...</span></div>
                    <div>URL: <span id="debug-current-url" style="color: #90a4ae; word-break: break-all;">${window.location.pathname}</span></div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 3px; margin-bottom: 8px;">
                    <button id="debug-btn-export" onclick="PrimeDebug.exportLogs()" style="padding: 3px 6px; font-size: 9px; background: #2196f3; color: white; border: none; border-radius: 3px; cursor: pointer;">📋 Export</button>
                    <button id="debug-btn-clear" onclick="PrimeDebug.clearLogs()" style="padding: 3px 6px; font-size: 9px; background: #ff9800; color: white; border: none; border-radius: 3px; cursor: pointer;">🗑️ Clear</button>
                    <button id="debug-btn-console" onclick="console.log('=== PRIME DEBUG LOGS ===', PrimeDebug.logHistory || [])" style="padding: 3px 6px; font-size: 9px; background: #4caf50; color: white; border: none; border-radius: 3px; cursor: pointer;">📊 Console</button>
                    <button id="debug-btn-info" onclick="console.log('=== PRIME DEBUG INFO ===', PrimeDebug.getSystemInfo())" style="padding: 3px 6px; font-size: 9px; background: #9c27b0; color: white; border: none; border-radius: 3px; cursor: pointer;">ℹ️ Info</button>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 9px; color: #999;">F12 → Console for details</div>
                    <button onclick="document.getElementById('prime-debug-panel').style.display='none'" style="padding: 2px 5px; font-size: 9px; background: #666; color: white; border: none; border-radius: 3px; cursor: pointer;">✖</button>
                </div>
            </div>
        `;
        document.body.appendChild(debugPanel);
        
        // Update debug panel periodically
        setInterval(() => {
            const countEl = document.getElementById('debug-log-count');
            const errorCountEl = document.getElementById('debug-error-count');
            const uptimeEl = document.getElementById('debug-uptime');
            const pageNameEl = document.getElementById('debug-page-name');
            
            if (countEl) {
                const logs = window.PrimeDebug ? window.PrimeDebug.getLogHistory() : [];
                countEl.textContent = logs.length.toString();
            }
            
            if (errorCountEl) {
                const logs = window.PrimeDebug ? window.PrimeDebug.getLogHistory() : [];
                const errorCount = logs.filter(log => log.level === 'ERROR').length;
                errorCountEl.textContent = errorCount.toString();
            }
            
            if (uptimeEl) {
                const systemInfo = window.PrimeDebug ? window.PrimeDebug.getSystemInfo() : null;
                if (systemInfo) {
                    const uptime = Math.floor(systemInfo.sessionDuration / 1000);
                    uptimeEl.textContent = `${uptime}s`;
                } else {
                    uptimeEl.textContent = '0s';
                }
            }
            
            if (pageNameEl) {
                pageNameEl.textContent = document.title || 'Unknown Page';
            }
        }, 1000);
    }
});

// Export for global use
window.PrimeDebug = PrimeDebug;