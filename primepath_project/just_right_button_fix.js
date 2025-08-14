/**
 * Just Right Button Race Condition Fix
 * 
 * This fix addresses the issue where the "Just Right" button can conflict with
 * timer expiry when they occur simultaneously. The fix adds:
 * 
 * 1. Timer state validation before showing modal
 * 2. Auto-close modal if timer expires while visible
 * 3. Enhanced state synchronization
 * 4. Defensive programming for edge cases
 */

// ENHANCEMENT 1: Add timer validation to modal display logic
// Insert this code into answer-manager.js before line 667

if (response.show_difficulty_choice) {
    // CRITICAL FIX: Check if timer has expired since test was submitted
    if (window.examTimer && window.examTimer.getStats) {
        const timerStats = window.examTimer.getStats();
        
        // If timer is expired, don't show modal regardless of backend response
        if (timerStats.isExpired) {
            this.log('warn', 'Timer expired after submission - skipping difficulty choice modal');
            
            // Clear any timer state and redirect directly
            if (window.examTimer.clearState) {
                window.examTimer.clearState();
            }
            
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
            }
            return true;
        }
    }
    
    this.log('info', 'Showing difficulty modal after test submission');
    this.showDifficultyChoiceModal(sessionId, response.redirect_url);
    return true;
}

// ENHANCEMENT 2: Auto-close modal if timer expires while visible
// Add this to the showDifficultyChoiceModal method after line 461

// Set up timer expiry monitoring for modal
const checkTimerInterval = setInterval(() => {
    if (window.examTimer && window.examTimer.getStats) {
        const timerStats = window.examTimer.getStats();
        
        if (timerStats.isExpired) {
            this.log('warn', 'Timer expired while modal was open - auto-closing');
            
            // Clear interval
            clearInterval(checkTimerInterval);
            
            // Hide modal
            modal.style.display = 'none';
            
            // Clear timer state
            if (window.examTimer.clearState) {
                window.examTimer.clearState();
            }
            
            // Show message and redirect
            alert('Test time has expired. Redirecting to your results...');
            window.location.href = defaultRedirectUrl;
        }
    }
}, 1000); // Check every second

// Store interval ID so we can clean it up
modal.dataset.timerCheckInterval = checkTimerInterval;

// ENHANCEMENT 3: Clear timer monitoring when modal is closed
// Add this cleanup to all modal close events

function cleanupTimerMonitoring() {
    const intervalId = modal.dataset.timerCheckInterval;
    if (intervalId) {
        clearInterval(parseInt(intervalId));
        delete modal.dataset.timerCheckInterval;
    }
}

// Add cleanup to existing close handlers:
// - Skip button click
// - Overlay click  
// - Difficulty choice button clicks

// ENHANCEMENT 4: Enhanced handleDifficultyChoice with timer validation
// Replace the existing handleDifficultyChoice method with this enhanced version

async handleDifficultyChoice(sessionId, adjustment) {
    const modal = document.getElementById('difficulty-choice-modal');
    
    // CRITICAL FIX: Validate timer state before processing choice
    if (window.examTimer && window.examTimer.getStats) {
        const timerStats = window.examTimer.getStats();
        
        if (timerStats.isExpired) {
            this.log('warn', 'Timer expired - canceling difficulty choice');
            
            // Clear timer state
            if (window.examTimer.clearState) {
                window.examTimer.clearState();
            }
            
            // Hide modal and redirect to results
            modal.style.display = 'none';
            alert('Test time has expired. Showing your results...');
            window.location.href = modal.dataset.defaultRedirectUrl;
            return;
        }
    }
    
    // Show loading state
    const buttons = modal.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);
    
    // Clear timer monitoring
    const intervalId = modal.dataset.timerCheckInterval;
    if (intervalId) {
        clearInterval(parseInt(intervalId));
        delete modal.dataset.timerCheckInterval;
    }
    
    try {
        const endpoint = `/PlacementTest/session/${sessionId}/post-submit-difficulty/`;
        const response = await this.ajax(endpoint, {
            method: 'POST',
            body: JSON.stringify({
                adjustment: adjustment
            })
        });
        
        if (response.success) {
            // Hide modal
            modal.style.display = 'none';
            
            // Clear timer state since we're done
            if (window.examTimer && window.examTimer.clearState) {
                window.examTimer.clearState();
            }
            
            // Redirect based on action
            if (response.redirect_url) {
                if (response.action === 'start_new_test') {
                    // Show message before redirecting to new test
                    if (response.message) {
                        // Brief message for new test
                        console.log(response.message);
                    }
                }
                window.location.href = response.redirect_url;
            }
        } else {
            throw new Error(response.error || 'Failed to process difficulty choice');
        }
    } catch (error) {
        this.log('error', 'Failed to process difficulty choice:', error);
        alert('Failed to process your choice. Redirecting to results...');
        modal.style.display = 'none';
        window.location.href = modal.dataset.defaultRedirectUrl;
    } finally {
        // Re-enable buttons
        buttons.forEach(btn => btn.disabled = false);
    }
}

// ENHANCEMENT 5: Timer expiry enhancement
// Add this to timer.js onExpire callback to handle modal cleanup

onExpire: function() {
    console.warn('[Timer] Timer expired, checking for open modals');
    
    // Check if difficulty modal is open
    const difficultyModal = document.getElementById('difficulty-choice-modal');
    if (difficultyModal && difficultyModal.style.display !== 'none') {
        console.warn('[Timer] Closing difficulty modal due to timer expiry');
        
        // Clear timer monitoring interval
        const intervalId = difficultyModal.dataset.timerCheckInterval;
        if (intervalId) {
            clearInterval(parseInt(intervalId));
        }
        
        // Hide modal
        difficultyModal.style.display = 'none';
        
        // Show message
        alert('Test time has expired. Your test will be submitted automatically.');
    }
    
    console.log('[Timer] Clearing session-specific timer state on expiry');
    
    // Clear this session's timer state when expired
    if (timer && timer.clearState) {
        timer.clearState();
    }
    
    if (window.answerManager) {
        window.answerManager.submitTest(true, true);
    } else {
        console.error('[Timer] Cannot submit - answerManager not available');
    }
}

// ENHANCEMENT 6: Defensive programming for edge cases
// Add this validation to APP_CONFIG initialization

// Validate timer state on page load
if (window.examTimer && window.examTimer.getStats) {
    const timerStats = window.examTimer.getStats();
    
    if (timerStats.isExpired) {
        console.warn('[INIT] Timer already expired on page load - possible stale state');
        
        // Check if this is a completed session
        const sessionCompleted = APP_CONFIG.session && APP_CONFIG.session.completed_at;
        
        if (!sessionCompleted) {
            console.warn('[INIT] Session not completed but timer expired - auto-submitting');
            
            // Auto-submit if timer expired but session not completed
            setTimeout(() => {
                if (window.answerManager) {
                    window.answerManager.submitTest(true, true);
                }
            }, 2000); // 2 second delay to allow initialization
        }
    }
}