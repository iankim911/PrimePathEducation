/**
 * Timer Module
 * Handles exam timer functionality with countdown and auto-submit
 * Replaces inline timer functions from student_test.html
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    const BaseModule = window.PrimePath.modules.BaseModule;

    /**
     * Timer Module
     * Manages countdown timer, warnings, and auto-submission
     */
    class Timer extends BaseModule {
        constructor(options = {}) {
            super('Timer', options);
            
            // Timer state
            this.interval = null;
            this.timeRemaining = 0;
            this.totalTime = 0;
            this.isRunning = false;
            this.isPaused = false;
            
            // Display element
            this.displayElement = null;
            
            // Warning thresholds (in seconds)
            this.warnings = options.warnings || [
                { time: 300, message: '5 minutes remaining', class: 'warning' },     // 5 min
                { time: 60, message: '1 minute remaining', class: 'danger' },        // 1 min
                { time: 30, message: '30 seconds remaining', class: 'critical' }     // 30 sec
            ];
            this.warningsShown = new Set();
            
            // Callbacks
            this.onExpire = options.onExpire || null;
            this.onWarning = options.onWarning || null;
            
            // Settings
            this.updateInterval = options.updateInterval || 1000; // Update every second
            this.format = options.format || 'mm:ss'; // Display format
            this.showHours = options.showHours || false;
            
            // Persistence
            this.persistKey = options.persistKey || 'exam-timer';
            this.enablePersistence = options.enablePersistence !== false;
        }

        /**
         * Initialize timer
         * @param {number} seconds Total time in seconds
         * @param {string|HTMLElement} displayElement Element to show time
         */
        init(seconds, displayElement) {
            console.log('[Timer.init] Called with seconds:', seconds, 'displayElement:', displayElement);
            
            // NULL SAFETY: Validate input parameters
            if (seconds === undefined || seconds === null) {
                console.warn('[Timer.init] No seconds provided, timer will not be initialized');
                this.log('warn', 'Timer init called without seconds value');
                return false;
            }
            
            // Convert to number and validate
            seconds = Number(seconds);
            if (isNaN(seconds)) {
                console.error('[Timer.init] Invalid seconds value:', seconds);
                this.log('error', 'Invalid timer seconds value');
                return false;
            }
            
            // Check if already initialized
            if (this.initialized && this.isRunning) {
                this.log('warn', 'Timer already running');
                return true;
            }
            
            // Set display element with null safety
            if (displayElement) {
                if (typeof displayElement === 'string') {
                    this.displayElement = document.querySelector(displayElement);
                    if (!this.displayElement) {
                        console.warn('[Timer.init] Display element not found:', displayElement);
                    }
                } else {
                    this.displayElement = displayElement;
                }
            } else {
                console.warn('[Timer.init] No display element provided');
            }
            
            // Restore from storage if available with comprehensive validation
            if (this.enablePersistence) {
                console.log('[Timer.init] Attempting to restore state from persistence...');
                const saved = this.restoreState();
                if (saved) {
                    // CRITICAL FIX: Additional validation before using restored state
                    if (saved.timeRemaining > 0 && saved.timeRemaining <= saved.totalTime) {
                        const originalSeconds = seconds;
                        seconds = saved.timeRemaining;
                        console.log(`[Timer.init] State restored successfully: ${originalSeconds}s -> ${seconds}s remaining`);
                        this.log('info', `Restored timer with ${seconds} seconds remaining (was ${originalSeconds})`);
                    } else {
                        console.warn('[Timer.init] Restored state invalid, using original timer value');
                        console.warn(`[Timer.init] Restored timeRemaining: ${saved.timeRemaining}, totalTime: ${saved.totalTime}`);
                        this.clearState(); // Clear invalid state
                    }
                } else {
                    console.log('[Timer.init] No valid state to restore, using fresh timer');
                }
            }
            
            this.totalTime = seconds;
            this.timeRemaining = seconds;
            
            // Check if timer is already expired on init
            if (this.timeRemaining <= 0) {
                this.log('warn', 'Timer initialized with 0 seconds - already expired');
                this.timeRemaining = 0;
                
                // Display 00:00
                this.updateDisplay();
                
                // Don't immediately call onExpire - give user a moment to see what's happening
                // The expire will be called when start() is called
                this.isExpired = true;
            } else {
                // Initial display
                this.updateDisplay();
            }
            
            super.init();
            console.log('[Timer.init] Timer initialization complete');
            return true;
        }

        /**
         * Start the timer
         */
        start() {
            console.group('[Timer.start] Starting timer');
            console.log('[Timer.start] Initial state:', {
                initialized: this.initialized,
                isRunning: this.isRunning,
                isPaused: this.isPaused,
                timeRemaining: this.timeRemaining,
                persistKey: this.persistKey
            });
            
            // NULL SAFETY: Check if timer was properly initialized
            if (!this.initialized) {
                console.warn('[Timer.start] Timer not initialized, cannot start');
                this.log('warn', 'Attempted to start uninitialized timer');
                console.groupEnd();
                return false;
            }
            
            if (this.isRunning && !this.isPaused) {
                console.log('[Timer.start] Timer already running, no action needed');
                this.log('warn', 'Timer already running');
                console.groupEnd();
                return true;
            }
            
            if (this.isPaused) {
                console.log('[Timer.start] Timer paused, resuming instead');
                this.resume();
                console.groupEnd();
                return true;
            }
            
            // Check if timer was already expired on init
            if (this.isExpired || this.timeRemaining <= 0) {
                console.warn('[Timer.start] CRITICAL: Timer already expired at start');
                console.log('[Timer.start] Expired timer details:', {
                    isExpired: this.isExpired,
                    timeRemaining: this.timeRemaining,
                    totalTime: this.totalTime
                });
                
                this.log('warn', 'Timer is already expired, showing expiry message');
                
                // Show a message to the user before auto-submitting
                if (this.displayElement) {
                    this.displayElement.innerHTML = '<span style="color: red; font-weight: bold;">Time Expired - Submitting...</span>';
                    console.log('[Timer.start] Updated display element to show expiry message');
                }
                
                // Give user 2 seconds to see the message before triggering expiry
                console.log('[Timer.start] Scheduling expiry in 2 seconds');
                setTimeout(() => {
                    this.expire();
                }, 2000);
                
                console.groupEnd();
                return;
            }
            
            console.log('[Timer.start] Starting timer normally');
            this.isRunning = true;
            this.isPaused = false;
            
            // Save start time for persistence
            if (this.enablePersistence) {
                console.log('[Timer.start] Saving initial state to persistence');
                this.saveState();
            }
            
            this.interval = setInterval(() => {
                this.tick();
            }, this.updateInterval);
            
            console.log('[Timer.start] Timer interval created, ID:', this.interval);
            
            this.emit('start', {
                timeRemaining: this.timeRemaining,
                totalTime: this.totalTime
            });
            
            this.log('info', `Timer started with ${this.timeRemaining} seconds`);
            console.log('[Timer.start] Timer start completed successfully');
            console.groupEnd();
        }

        /**
         * Pause the timer
         */
        pause() {
            if (!this.isRunning || this.isPaused) return;
            
            this.isPaused = true;
            clearInterval(this.interval);
            this.interval = null;
            
            if (this.enablePersistence) {
                this.saveState();
            }
            
            this.emit('pause', { timeRemaining: this.timeRemaining });
            this.log('info', 'Timer paused');
        }

        /**
         * Resume the timer
         */
        resume() {
            if (!this.isPaused) return;
            
            this.isPaused = false;
            
            this.interval = setInterval(() => {
                this.tick();
            }, this.updateInterval);
            
            this.emit('resume', { timeRemaining: this.timeRemaining });
            this.log('info', 'Timer resumed');
        }

        /**
         * Stop the timer
         */
        stop() {
            if (!this.isRunning) return;
            
            this.isRunning = false;
            this.isPaused = false;
            
            if (this.interval) {
                clearInterval(this.interval);
                this.interval = null;
            }
            
            if (this.enablePersistence) {
                this.clearState();
            }
            
            this.emit('stop', {
                timeRemaining: this.timeRemaining,
                timeElapsed: this.totalTime - this.timeRemaining
            });
            
            this.log('info', 'Timer stopped');
        }

        /**
         * Reset the timer
         * @param {number} seconds New total time (optional)
         */
        reset(seconds) {
            this.stop();
            
            if (seconds !== undefined) {
                this.totalTime = seconds;
            }
            
            this.timeRemaining = this.totalTime;
            this.warningsShown.clear();
            
            this.updateDisplay();
            
            this.emit('reset', { totalTime: this.totalTime });
            this.log('info', 'Timer reset');
        }

        /**
         * Timer tick - called every interval
         */
        tick() {
            this.timeRemaining--;
            
            // Update display
            this.updateDisplay();
            
            // Check for warnings
            this.checkWarnings();
            
            // Save state for persistence
            if (this.enablePersistence && this.timeRemaining % 5 === 0) {
                // Save every 5 seconds to reduce storage writes
                this.saveState();
            }
            
            // Emit tick event
            this.emit('tick', {
                timeRemaining: this.timeRemaining,
                timeElapsed: this.totalTime - this.timeRemaining,
                progress: ((this.totalTime - this.timeRemaining) / this.totalTime) * 100
            });
            
            // Check if expired
            if (this.timeRemaining <= 0) {
                this.expire();
            }
        }

        /**
         * Handle timer expiration
         */
        expire() {
            console.group('[Timer.expire] Timer expiration handling');
            console.log('[Timer.expire] Timer state at expiry:', {
                timeRemaining: this.timeRemaining,
                totalTime: this.totalTime,
                isRunning: this.isRunning,
                isPaused: this.isPaused,
                persistKey: this.persistKey
            });
            
            // Check for open modals before expiry
            const difficultyModal = document.getElementById('difficulty-choice-modal');
            if (difficultyModal) {
                const modalVisible = difficultyModal.style.display !== 'none';
                console.log('[Timer.expire] Difficulty modal state:', {
                    exists: true,
                    visible: modalVisible,
                    display: difficultyModal.style.display
                });
                
                if (modalVisible) {
                    console.warn('[Timer.expire] CRITICAL: Modal is open during timer expiry - race condition detected');
                    
                    // Clear timer monitoring interval if exists
                    const intervalId = difficultyModal.dataset.timerCheckInterval;
                    if (intervalId) {
                        console.log('[Timer.expire] Clearing modal timer monitoring interval:', intervalId);
                        clearInterval(parseInt(intervalId));
                        delete difficultyModal.dataset.timerCheckInterval;
                    }
                    
                    // Hide modal
                    difficultyModal.style.display = 'none';
                    console.log('[Timer.expire] Modal hidden due to timer expiry');
                }
            } else {
                console.log('[Timer.expire] No difficulty modal found - normal expiry');
            }
            
            this.stop();
            
            console.log('[Timer.expire] Emitting expire event');
            this.emit('expire', {
                totalTime: this.totalTime,
                timeElapsed: this.totalTime
            });
            
            // Call expiration callback with detailed logging
            if (this.onExpire) {
                console.log('[Timer.expire] Calling onExpire callback');
                try {
                    this.onExpire();
                    console.log('[Timer.expire] onExpire callback completed successfully');
                } catch (error) {
                    console.error('[Timer.expire] Error in onExpire callback:', error);
                }
            } else {
                console.warn('[Timer.expire] No onExpire callback defined');
            }
            
            this.log('warn', 'Timer expired!');
            console.groupEnd();
        }

        /**
         * Check and show warnings
         */
        checkWarnings() {
            for (const warning of this.warnings) {
                if (this.timeRemaining <= warning.time && !this.warningsShown.has(warning.time)) {
                    this.warningsShown.add(warning.time);
                    this.showWarning(warning);
                }
            }
        }

        /**
         * Show warning message
         * @param {Object} warning Warning configuration
         */
        showWarning(warning) {
            this.emit('warning', {
                timeRemaining: this.timeRemaining,
                message: warning.message,
                class: warning.class
            });
            
            // Update display element class if provided
            if (this.displayElement && warning.class) {
                this.displayElement.classList.add(`timer-${warning.class}`);
            }
            
            // Call warning callback
            if (this.onWarning) {
                this.onWarning(warning);
            }
            
            this.log('warn', warning.message);
        }

        /**
         * Update timer display
         */
        updateDisplay() {
            if (!this.displayElement) return;
            
            const formatted = this.formatTime(this.timeRemaining);
            this.displayElement.textContent = formatted;
            
            // Update color based on time remaining
            if (this.timeRemaining <= 30) {
                this.displayElement.style.color = '#dc3545'; // Red
            } else if (this.timeRemaining <= 60) {
                this.displayElement.style.color = '#fd7e14'; // Orange
            } else if (this.timeRemaining <= 300) {
                this.displayElement.style.color = '#ffc107'; // Yellow
            } else {
                this.displayElement.style.color = ''; // Default
            }
        }

        /**
         * Format time for display
         * @param {number} seconds Time in seconds
         * @returns {string} Formatted time string
         */
        formatTime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            
            if (this.showHours || hours > 0) {
                return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            } else {
                return `${minutes}:${secs.toString().padStart(2, '0')}`;
            }
        }

        /**
         * Add time to the timer
         * @param {number} seconds Seconds to add
         */
        addTime(seconds) {
            this.timeRemaining += seconds;
            this.updateDisplay();
            
            this.emit('timeAdded', {
                added: seconds,
                timeRemaining: this.timeRemaining
            });
        }

        /**
         * Get timer statistics
         * @returns {Object} Timer stats
         */
        getStats() {
            const stats = {
                timeRemaining: this.timeRemaining,
                timeElapsed: this.totalTime - this.timeRemaining,
                totalTime: this.totalTime,
                progress: ((this.totalTime - this.timeRemaining) / this.totalTime) * 100,
                isRunning: this.isRunning,
                isPaused: this.isPaused,
                isExpired: this.timeRemaining <= 0,
                formattedTime: this.formatTime(this.timeRemaining),
                persistKey: this.persistKey
            };
            
            // Enhanced debugging for race condition detection
            if (stats.isExpired) {
                console.log('[Timer.getStats] EXPIRED TIMER DETECTED:', {
                    timeRemaining: stats.timeRemaining,
                    isRunning: stats.isRunning,
                    persistKey: stats.persistKey,
                    caller: (new Error()).stack.split('\n')[2].trim() // Show who called getStats
                });
            }
            
            return stats;
        }

        /**
         * Save timer state to localStorage
         */
        saveState() {
            if (!this.enablePersistence) return;
            
            const state = {
                timeRemaining: this.timeRemaining,
                totalTime: this.totalTime,
                timestamp: Date.now(),
                isRunning: this.isRunning,
                isPaused: this.isPaused
            };
            
            try {
                localStorage.setItem(this.persistKey, JSON.stringify(state));
            } catch (e) {
                this.log('error', 'Failed to save timer state', e);
            }
        }

        /**
         * Restore timer state from localStorage with comprehensive validation
         * @returns {Object|null} Saved state or null
         */
        restoreState() {
            if (!this.enablePersistence) return null;
            
            try {
                const saved = localStorage.getItem(this.persistKey);
                if (!saved) {
                    console.log('[Timer.restoreState] No saved state found for key:', this.persistKey);
                    return null;
                }
                
                const state = JSON.parse(saved);
                console.log('[Timer.restoreState] Raw saved state:', state);
                
                // CRITICAL FIX: Validate saved state structure
                if (!state || typeof state !== 'object') {
                    console.warn('[Timer.restoreState] Invalid state structure, clearing saved state');
                    this.clearState();
                    return null;
                }
                
                // Validate required fields
                const requiredFields = ['timeRemaining', 'totalTime', 'timestamp'];
                for (const field of requiredFields) {
                    if (state[field] === undefined || state[field] === null) {
                        console.warn(`[Timer.restoreState] Missing required field: ${field}, clearing saved state`);
                        this.clearState();
                        return null;
                    }
                }
                
                // Validate timestamp is reasonable (not too old)
                const now = Date.now();
                const timeSinceSave = now - state.timestamp;
                const maxAgeHours = 24; // Don't restore state older than 24 hours
                const maxAgeMs = maxAgeHours * 60 * 60 * 1000;
                
                if (timeSinceSave > maxAgeMs) {
                    console.warn(`[Timer.restoreState] Saved state too old (${Math.round(timeSinceSave / 1000 / 60)} minutes), clearing`);
                    this.clearState();
                    return null;
                }
                
                // Calculate time elapsed since save with validation
                if (state.isRunning && !state.isPaused) {
                    const elapsed = Math.floor(timeSinceSave / 1000);
                    console.log(`[Timer.restoreState] Time elapsed since save: ${elapsed} seconds`);
                    
                    // Apply elapsed time but ensure it doesn't go negative
                    state.timeRemaining = Math.max(0, state.timeRemaining - elapsed);
                    
                    console.log(`[Timer.restoreState] Adjusted time remaining: ${state.timeRemaining} seconds`);
                }
                
                // ADDITIONAL VALIDATION: Check if the restored timer would be expired
                if (state.timeRemaining <= 0) {
                    console.warn('[Timer.restoreState] Restored timer would be expired, clearing saved state');
                    this.clearState();
                    return null;
                }
                
                console.log('[Timer.restoreState] Successfully restored valid state:', state);
                return state;
                
            } catch (e) {
                console.error('[Timer.restoreState] Error restoring state:', e);
                this.log('error', 'Failed to restore timer state', e);
                this.clearState(); // Clear corrupted state
                return null;
            }
        }

        /**
         * Clear saved timer state
         */
        clearState() {
            if (!this.enablePersistence) return;
            
            console.group('[Timer.clearState] Clearing timer state');
            console.log('[Timer.clearState] Clearing state for key:', this.persistKey);
            
            try {
                // Check if state exists before clearing
                const existingState = localStorage.getItem(this.persistKey);
                if (existingState) {
                    console.log('[Timer.clearState] Existing state found, clearing:', JSON.parse(existingState));
                } else {
                    console.log('[Timer.clearState] No existing state to clear');
                }
                
                localStorage.removeItem(this.persistKey);
                console.log('[Timer.clearState] State cleared successfully');
            } catch (e) {
                console.error('[Timer.clearState] Error clearing state:', e);
                this.log('error', 'Failed to clear timer state', e);
            }
            
            console.groupEnd();
        }

        /**
         * Destroy timer and cleanup
         */
        destroy() {
            this.stop();
            this.clearState();
            this.displayElement = null;
            this.warningsShown.clear();
            
            super.destroy();
        }
    }

    // Export to PrimePath namespace
    window.PrimePath.modules.Timer = Timer;

    // Create global timer instance for backward compatibility
    window.examTimer = null;

    window.startTimer = function() {
        if (!window.examTimer) {
            // Get time from global variable if set
            const timeRemaining = window.timeRemaining || 3600; // Default 1 hour
            
            window.examTimer = new Timer({
                onExpire: () => {
                    if (typeof window.submitTest === 'function') {
                        window.submitTest();
                    }
                },
                enablePersistence: true,
                persistKey: `exam-timer-${window.sessionId || 'default'}`
            });
            
            window.examTimer.init(timeRemaining, '#timer');
        }
        
        window.examTimer.start();
    };

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = Timer;
    }

})(window);