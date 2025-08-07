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
            if (this.initialized && this.isRunning) {
                this.log('warn', 'Timer already running');
                return;
            }
            
            // Set display element
            if (typeof displayElement === 'string') {
                this.displayElement = document.querySelector(displayElement);
            } else {
                this.displayElement = displayElement;
            }
            
            // Restore from storage if available
            if (this.enablePersistence) {
                const saved = this.restoreState();
                if (saved) {
                    seconds = saved.timeRemaining;
                    this.log('info', `Restored timer with ${seconds} seconds remaining`);
                }
            }
            
            this.totalTime = seconds;
            this.timeRemaining = seconds;
            
            // Initial display
            this.updateDisplay();
            
            super.init();
        }

        /**
         * Start the timer
         */
        start() {
            if (this.isRunning && !this.isPaused) {
                this.log('warn', 'Timer already running');
                return;
            }
            
            if (this.isPaused) {
                this.resume();
                return;
            }
            
            this.isRunning = true;
            this.isPaused = false;
            
            // Save start time for persistence
            if (this.enablePersistence) {
                this.saveState();
            }
            
            this.interval = setInterval(() => {
                this.tick();
            }, this.updateInterval);
            
            this.emit('start', {
                timeRemaining: this.timeRemaining,
                totalTime: this.totalTime
            });
            
            this.log('info', `Timer started with ${this.timeRemaining} seconds`);
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
            this.stop();
            
            this.emit('expire', {
                totalTime: this.totalTime,
                timeElapsed: this.totalTime
            });
            
            // Call expiration callback
            if (this.onExpire) {
                this.onExpire();
            }
            
            this.log('warn', 'Timer expired!');
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
            return {
                timeRemaining: this.timeRemaining,
                timeElapsed: this.totalTime - this.timeRemaining,
                totalTime: this.totalTime,
                progress: ((this.totalTime - this.timeRemaining) / this.totalTime) * 100,
                isRunning: this.isRunning,
                isPaused: this.isPaused,
                formattedTime: this.formatTime(this.timeRemaining)
            };
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
         * Restore timer state from localStorage
         * @returns {Object|null} Saved state or null
         */
        restoreState() {
            if (!this.enablePersistence) return null;
            
            try {
                const saved = localStorage.getItem(this.persistKey);
                if (!saved) return null;
                
                const state = JSON.parse(saved);
                
                // Calculate time elapsed since save
                if (state.isRunning && !state.isPaused) {
                    const elapsed = Math.floor((Date.now() - state.timestamp) / 1000);
                    state.timeRemaining = Math.max(0, state.timeRemaining - elapsed);
                }
                
                return state;
                
            } catch (e) {
                this.log('error', 'Failed to restore timer state', e);
                return null;
            }
        }

        /**
         * Clear saved timer state
         */
        clearState() {
            if (!this.enablePersistence) return;
            
            try {
                localStorage.removeItem(this.persistKey);
            } catch (e) {
                this.log('error', 'Failed to clear timer state', e);
            }
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

    // Backward compatibility functions
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